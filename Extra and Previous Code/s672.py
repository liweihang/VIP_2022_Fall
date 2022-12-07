# sirion.py
# Antenna Gain Pattern for Recommendation S.672
# Author: Erik
# Link to antenna pattern document:
# https://www.itu.int/en/ITU-R/software/Documents/ant-pattern/APL_DOC_BY_PATTERN_NAME/APSAUS612V01.pdf
import numpy as np
from numba import jit

# This function returns the co-polar gain of the antenna pattern
# The input is np array containing mirrored degress, 
# from 0 to 180 back down to 0
@jit(nopython = True, cache=True)
def mirrored(mirrored):
    a = 1.83
    b = 6.32
    g_max = 35.5
    if (mirrored <= a/2):
        return (g_max-12*np.power((mirrored), 2))
    elif (mirrored < b/2 and mirrored > a/2):
        return g_max - 10
    elif (mirrored > b/2):
        return g_max - 10 + 20 - 25*np.log10(2*mirrored)
    else:
        return 0 
