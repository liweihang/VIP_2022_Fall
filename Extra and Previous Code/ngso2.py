# ngso2.py
# Antenna Gain Pattern for USASAT-NGSO-8B for TGA2 & RGA2 Beams
# Author: Achintya
# Link to antenna pattern document:
# https://www.itu.int/en/ITU-R/software/Documents/ant-pattern/APL_DOC_BY_PATTERN_NAME/APSUSA613V01.pdf
import numpy as np
from numba import jit

# This function returns the co-polar gain of the antenna pattern
# The input is np array containing mirrored degress, 
# from 0 to 180 back down to 0
@jit(nopython = True, cache = False)
def mirrored(mirrored):
    Gmax = 60
    '''
    return np.piecewise(mirrored,
                [ 
                    mirrored <= 4.54, 
                    (mirrored < 20) & (mirrored > 4.54),
                    (mirrored <= 180) & (mirrored > 20)
                ],
                [
                    lambda mirrored: Gmax - 3 * (mirrored/2.27) ** 2,
                    lambda mirrored: 34 - 25 * np.log(mirrored),
                    1.5
                ])
    '''

    if (mirrored <= 4.54):
        return (Gmax - 3 * (mirrored/2.27) ** 2)
    elif (mirrored < 20 and mirrored > 4.54):
        return (34 - 25 * np.log(mirrored))
    elif (mirrored <= 180 and mirrored > 20):
        return 1.5
    else:
        return 1.5   
