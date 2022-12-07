# sirion.py
# Antenna Gain Pattern for SIRION-1
# Author: Erik
# Link to antenna pattern document:
# https://www.itu.int/en/ITU-R/software/Documents/ant-pattern/APL_DOC_BY_PATTERN_NAME/APSAUS612V01.pdf
import numpy as np
from numba import jit

# This function returns the co-polar gain of the antenna pattern
# The input is np array containing mirrored degress, 
# from 0 to 180 back down to 0
@jit(nopython = True, cache=True)
def sirion_mirrored(mirrored):
    '''
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
    '''
    if (mirrored <= 22):
        return (14-10*np.power((mirrored/19), 2))
    elif (mirrored < 80 and mirrored > 22):
        return np.float(0)
    elif (mirrored < 110 and mirrored > 80):
        return 16/900 *np.power((mirrored - 110), 2) - 16
    else:
        return np.float(-16)
