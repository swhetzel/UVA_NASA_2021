from caltrack_dict import list_caltrack
import h5py
import os
import numpy as np
import copy
from netCDF4 import Dataset

def conv_stub():
    # This is used in Lats conversion

    # Set the number of pixels you want to look at
    pixels = 3

    # Validation on the pixel count, making sure it's an odd number
    if pixels <= 0 or pixels % 1 != 0:
        print("Error, enter a valid pixel number, pixels being set to 3")
        pixels = 3
    elif pixels % 2 == 0 and pixels > 2:
        print("Error, even number of pixels chosen. Pixels being reset")
        pixels -= 1

    with h5py.File(file_path, "r") as f:

        final_dict = {}

        for item in list_caltrack:
