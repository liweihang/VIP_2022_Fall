from mpl_toolkits.basemap import Basemap
import numpy as np
import matplotlib.pyplot as plt
# read in topo data (on a regular lat/lon grid)
etopo = np.loadtxt('etopo20data.gz')
lons  = np.loadtxt('etopo20lons.gz')
lats  = np.loadtxt('etopo20lats.gz')
# create Basemap instance for Robinson projection.
m = Basemap(projection='robin',lon_0=0.5*(lons[0]+lons[-1]))
# compute map projection coordinates for lat/lon grid.
x, y = m(*np.meshgrid(lons,lats))
# make filled contour plot.
print(x[10])
print(y[10])
print(etopo[10])
cs = m.contourf(x,y,etopo)
m.drawcoastlines() # draw coastlines
m.drawmapboundary() # draw a line around the map region
m.drawparallels(np.arange(-90.,120.,30.),labels=[1,0,0,0]) # draw parallels
m.drawmeridians(np.arange(0.,420.,60.),labels=[0,0,0,1]) # draw meridians
plt.title('Robinson Projection') # add a title
plt.show()
