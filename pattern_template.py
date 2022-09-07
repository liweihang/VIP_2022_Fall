# <filename>.py
# Antenna Gain Pattern for <Insert Name Here> 
# Author: <name>
# Link to antenna pattern document:
# <insert link>
import numpy as np

# This function returns the co-polar gain of the antenna pattern
# The input is np array containing mirrored degress, 
# from 0 to 180 back down to 0
def pattern_mirrored(mirrored):
    return np.piecewise(mirrored,
                [ 
                    mirrored <= 22, 
                    (mirrored < 80) & (mirrored > 22),
                    (mirrored < 110) & (mirrored > 80),
                    (mirrored <= 180) & (mirrored > 110)
                ],
                [
                    lambda mirrored: 14-10*(mirrored/19)**2,
                    0,
                    lambda mirrored: 16/900 * (mirrored - 110)**2 - 16,
                    -16
                ])