# ngso1.py
# Antenna Gain Pattern for USASAT-NGSO-8B for TGA1 & RGA1 Beams
# Author: Achintya
# Link to antenna pattern document:
# https://www.itu.int/en/ITU-R/software/Documents/ant-pattern/APL_DOC_BY_PATTERN_NAME/APSUSA607V01.pdf
import numpy as np

# This function returns the co-polar gain of the antenna pattern
# The input is np array containing mirrored degress, 
# from 0 to 180 back down to 0
def ngso_8b_1_mirrored(mirrored):
    Gmax = 60
    return np.piecewise(mirrored,
                [ 
                    mirrored <= 5.7, 
                    (mirrored < 20) & (mirrored > 5.7),
                    (mirrored <= 180) & (mirrored > 20)
                ],
                [
                    lambda mirrored: Gmax - 3 * (mirrored/2.85) ** 2,
                    lambda mirrored: 34 - 25 * np.log(mirrored),
                    1.5
                ])
