#!/usr/bin/python3
# link_budget.py
# script to calculate link budget
# requires pandas, numpy, matplotlib, mpl_toolkits, poliastro
# and numba
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from poliastro.core.events import line_of_sight
from numba import jit
from numba.typed import List
import sirion as sirion
import ngso2 as ngso2
import math as m
import time

# CONSTANTS for whether or not to enable just in time compilation of the
# heavy duty calculation functions. This will significantly speed up
# calculations but may cause type errors.
USE_NOPYTHON = True
CACHE_FUNCTIONS = False

# -------------------Functions---------------------------------------------
@jit(nopython=USE_NOPYTHON, cache=CACHE_FUNCTIONS)
def decibels(value):
    return 10 * np.log10(value)


@jit(nopython=USE_NOPYTHON, cache=CACHE_FUNCTIONS)
def watts(decibel_watts):
    return 10 ** (decibel_watts / 10)


@jit(nopython=USE_NOPYTHON, cache=CACHE_FUNCTIONS)
def calc_sat_vector(sat_latitude, sat_longitude):
    # Convert Satellite to xyz coords
    x_sat = (
        (GEO_ALTITUDE + EARTH_RADIUS)
        * m.cos(m.radians(sat_latitude))
        * m.cos(m.radians(sat_longitude))
    )
    y_sat = (
        (GEO_ALTITUDE + EARTH_RADIUS)
        * m.cos(m.radians(sat_latitude))
        * m.sin(m.radians(sat_longitude))
    )
    z_sat = (GEO_ALTITUDE + EARTH_RADIUS) * m.sin(m.radians(sat_latitude))

    sat_vector = np.array([x_sat, y_sat, z_sat])
    return sat_vector


# assumes geostationary
def calc_beam_center(sat_longitude, beam_theta, beam_phi):
    # in the satellite frame
    r_beam = np.matrix(
        [
            [np.cos(np.radians(beam_phi)) * np.cos(np.radians(beam_theta))],
            [np.cos(np.radians(beam_phi)) * np.sin(np.radians(beam_theta))],
            [np.sin(np.radians(beam_phi))],
        ]
    )

    # the rotation between the satellite and the earth fame
    # e1 is at long, lat zero
    alpha = sat_longitude + 180

    # define rotation matrix
    # rotation from e to s
    # rotation about the z axis (e3 and s3)
    rotation_matrix = np.matrix(
        [
            [np.cos(np.radians(alpha)), np.sin(np.radians(alpha)), 0],
            [-np.sin(np.radians(alpha)), np.cos(np.radians(alpha)), 0],
            [0, 0, 1],
        ]
    )

    # matrix multiply the transpose of the rotation_matrix
    # with r_sat to get r_sat in the earth frame
    r_beam_xyz = rotation_matrix.transpose() @ r_beam
    r_beam_center = r_beam_xyz.transpose()  # unit vector of beam center
    return r_beam_center


@jit(nopython=USE_NOPYTHON, cache=CACHE_FUNCTIONS)
def calc_location_vector(longlat, i):
    """
    For spyder IDE, if we don't convert xyz to float32 and return it through the array
    array using JIT, the 3 float64 values seems to be too much memory for JIT so it
    automatically gets rid of 1 value by setting it to 0 and only return the first 2.
    """

    x = np.float32(
        EARTH_RADIUS
        * np.cos(np.radians(longlat[i, 1]))
        * np.cos(np.radians(longlat[i, 0]))
    )
    y = np.float32(
        EARTH_RADIUS
        * np.cos(np.radians(longlat[i, 1]))
        * np.sin(np.radians(longlat[i, 0]))
    )
    z = np.float32(EARTH_RADIUS * np.sin(np.radians(longlat[i, 1])))

    return np.array([x, y, z], dtype=np.float64)


@jit(nopython=USE_NOPYTHON, cache=CACHE_FUNCTIONS)
def calc_sat_to_earth(location_vector, sat_vector):
    return location_vector - sat_vector


@jit(nopython=USE_NOPYTHON, cache=CACHE_FUNCTIONS)
def calc_angle_beam(r_beam_center, sat_to_Earth):
    """
    Now we calculate the angle between the beam vector(r_beam_center) and the grid point vector(sat_to_Earth)
    Once we find the angle (eventually phi, theta) we compare to the field pattern
    to find the relative gain and multiply by max gain to find the actual gain
    """

    angle_beam = np.arccos(
        np.dot(r_beam_center, sat_to_Earth)
        / (np.linalg.norm(r_beam_center) * np.linalg.norm(sat_to_Earth))
    )  # angle between iterated location vector and beam center
    beam = np.degrees(angle_beam)
    return beam[0]


@jit(nopython=USE_NOPYTHON, cache=CACHE_FUNCTIONS)
def calc_distance(location_vector, sat_vector):
    return np.linalg.norm(location_vector - sat_vector)


@jit(nopython=USE_NOPYTHON, cache=CACHE_FUNCTIONS)
def calc_location_power(sat_vector, location_vector, pep_max, gain_field, distance):
    # reduce the radius of the earth by a slight amount to remove floating point error
    if line_of_sight(sat_vector, location_vector, EARTH_RADIUS - 0.001) >= 0:
        # calculate the between the point of maximum gain and the current point
        free_space_loss = decibels(1 / (4 * PI * np.power(distance, 2)))
        power = watts(gain_field + pep_max + free_space_loss)
        return power

    else:
        # out of sight so set to 0
        # we will change to None type later to avoid graphing it
        return 0


@jit(nopython=USE_NOPYTHON, cache=CACHE_FUNCTIONS)
def calc_location_powers(longlat, sat_vector, beams, pep_max):

    location_power = np.zeros(longlat[:, 0].size)
    distance = np.zeros(longlat[:, 0].size)

    # lists of vectors
    location_vector = []
    sat_to_Earth = []
    for i in range(longlat[:, 0].size):
        location_vector.append(calc_location_vector(longlat, i))
        sat_to_Earth.append(calc_sat_to_earth(location_vector[i], sat_vector))

    for beam in beams:
        for i in range(longlat[:, 0].size):

            angle_beam = calc_angle_beam(beam, sat_to_Earth[i])
            # assume axisymmetic rad pattern
            # gain_field = sirion.sirion_mirrored(angle_beam)
            gain_field = ngso2.mirrored(angle_beam)

            distance[i] = calc_distance(location_vector[i], sat_vector)
            power = calc_location_power(
                sat_vector,
                location_vector[i],
                pep_max,
                gain_field,
                distance[i],
            )

            # Suming up power from each antenna
            location_power[i] += power

    return location_power


# ----------------------------Variable Definitions----------------------------
# Accuracy (for computing points on the Earth)
acc = 500

# altitude in km of a geostationary altitude (km)
GEO_ALTITUDE = 35785
# radius of the earth (km)
EARTH_RADIUS = 6378
PI = 3.14159265
# area of the receiver (1 m^2, assumption)
area_of_receiver = 1

# position of the satellite
sat_longitude = 0  # East to West
sat_latitude = 0  # North to South -> set 0 for now

# define beam vector relative to center of the earth
"""
NOTE: PHI IS MEAURED FROM THE XY PLANE NOT THE Z AXIS

beam_theta for x-y plane
beam_phi for Elevation from xy plane

beam_angles =[[antenna for sat 1],[antenna for sat 2],[antenna for sat 3]]
[theta,phi] for each antenna
"""
beam_angles = [[8, 0], [-7, 7], [-7, -7]]

# carrier frequency
freq = 10000000000
wavelength = 299792458 / freq

# maximum package envelope power output from the antenna in dBw
pep_max = 20

# ----------------------------Calculations----------------------------------
time_start = time.time()

beams = List()
sat_vector = calc_sat_vector(sat_latitude, sat_longitude)
for i in range(len(beam_angles)):
    r_beam_center = calc_beam_center(
        sat_longitude, beam_angles[i][0], beam_angles[i][1]
    )
    beams.append(r_beam_center)

# Makes longitude - latitude pairs for plotting
service_long = np.linspace(-180, 180, acc)
service_lat = np.linspace(-90, 90, acc)
grid_long, grid_lat = np.meshgrid(service_long, service_lat)
longlat = (
    np.array([grid_long, grid_lat]).reshape(2, -1).T
)  # Converts meshgrid into xy pairs

# Converts to Long Lat to xyz coords
x = np.zeros(longlat[:, 0].size)
y = np.zeros(longlat[:, 0].size)
z = np.zeros(longlat[:, 0].size)

location_power = calc_location_powers(
    longlat, sat_vector, beams, pep_max 
)

# Remove negative values since they are out of sight
with np.nditer(location_power, op_flags=["readwrite"]) as power:
    for location in power:
        if location == 0:
            location[...] = None

# Reshapes power_plot to be compatible with grid_long, grid_lat of meshgrid
cols = np.unique(longlat[:, 0]).shape[0]
power_plot = location_power.reshape(-1, cols)

# Summary of Data
d = {"Longitude": longlat[:, 0], "Latitude": longlat[:, 1], "Power": location_power}
data = pd.DataFrame(data=d)

print("Location of Max Power")
print(data.loc[data["Power"].idxmax()])

time_end = time.time()
print(f"Calc Time: {time_end - time_start}")

# -------------------Mapping Service Area onto Earth-----------------------
# create new figure, axes instances.
fig = plt.figure(figsize=(12, 6))
ax = plt.subplot2grid((1, 3), (0, 0), colspan=2)

# setup mercator map projection.
# Note: urcrnr/llcrnrlat cannot be 90 with mercator projection
map_output = Basemap(
    llcrnrlon=(-180),
    llcrnrlat=-80.0,
    urcrnrlon=(180),
    urcrnrlat=80.0,
    rsphere=(6378137.00, 6356752.3142),
    resolution="l",
    projection="merc",
    lat_0=0.0,
    lon_0=-0.0,
    lat_ts=20.0,
)

# Basemap Formatting
map_output.drawcoastlines()
# m.fillcontinents()
map_output.drawparallels(np.arange(-90, 90, 30), labels=[1, 1, 0, 1])
map_output.drawmeridians(np.arange(-180, 180, 30), labels=[1, 1, 0, 1])

plot_x, plot_y = map_output(
    *(grid_long, grid_lat)
)  # Turning meshgrid elements into plottable m.contour
map_output.contourf(plot_x, plot_y, power_plot, 20)

# Contour Map Formatting
cbar = plt.colorbar(orientation="horizontal", fraction=0.057, pad=0.05)
cbar.set_label("Power (W/m^2)")
ax.set_title("Link Power Map")

ax = plt.subplot2grid((1, 3), (0, 2))
map_output = Basemap(
    projection="ortho", lat_0=sat_latitude, lon_0=sat_longitude, resolution="l"
)

# Basemap Formatting
map_output.drawcoastlines()
map_output.drawparallels(np.arange(-90, 90, 30))
map_output.drawmeridians(np.arange(-180, 180, 30))

plot_x, plot_y = map_output(
    *(grid_long, grid_lat)
)  # Turning meshgrid elements into plottable m.contour
map_output.contourf(plot_x, plot_y, power_plot, 20)

# Contour Map Formatting
ax.set_title("Ortho Projection")
plt.show()
