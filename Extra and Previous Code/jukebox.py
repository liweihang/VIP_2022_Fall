# jukebox.py
# Antenna Gain Pattern for JUKEBOX
# Author: Achintya
# Link to antenna pattern document:
# https://www.itu.int/en/ITU-R/software/Documents/ant-pattern/APL_DOC_BY_PATTERN_NAME/APS__G623V01.pdf
import numpy as np

# This function returns the co-polar gain of the antenna pattern
# The input is np array containing mirrored degress, 
# from 0 to 180 back down to 0
def jukebox_mirrored(mirrored):
    return np.piecewise(mirrored,
                [ 
                    mirrored <= 165, 
                    (mirrored <= 180) & (mirrored > 165)
                ],
                [
                    lambda mirrored: 5.5 - (0.000004 * (mirrored ** 3)) - (0.0004 * (mirrored ** 2)) - (0.0376 * mirrored),
                    -30
                ])
