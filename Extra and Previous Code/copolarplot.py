import numpy as np
import matplotlib.pyplot as plt
import sirion as sirion
import s672 as s672

# define a mirrored theta
mirrored = np.concatenate((np.arange(0, 180, 0.5),np.arange(180, 0, -0.5)))
# compute the gain
with np.nditer(mirrored, op_flags=['readwrite']) as it:
    for x in it:
        x[...] = s672.mirrored(x)
#r = sirion.sirion_mirrored(mirrored)

#convert it to watts
r = mirrored
r = 10 ** r
#convert back to decibels
r = np.log10(r/np.max(r))

#redefine mirrored from 0
theta = np.arange(0, 2*np.pi, 2*np.pi/720)

#graph on a polar plot
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
ax.plot(theta, r)
ax.grid(True)
ax.set_title("Co-Polar Plot for SIRION-1 network (dB Gain)", va='bottom')
plt.show()

