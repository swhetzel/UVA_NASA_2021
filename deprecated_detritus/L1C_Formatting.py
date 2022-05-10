# -*- coding: utf-8 -*-
"""
DEPRECATED:
    
This module shows the brute force conversion of PARASOL files to L1C format. 
This module is slow and creates output that is much larger than it needs to be 
on the order of dozens to hundreds of gigabytes. 
"""

import h5py
import os
import numpy as np
import copy
from netCDF4 import Dataset

# Set path for the h5 PARASOL file
h5_file_path = "PARASOL/L1_B-HDF.v1.00/2008/2008_06_01/POLDER3_L1B-BG1-080146M_2008-06-01T00-08-19_V1-00.h5"

# Set path for file output
nc_path = "example.nc"


f = h5py.File(h5_file_path)

# Initialize a dictionary to hold raw measurements from the H5
measurement_dict = {}


# Append intensity data for I, Q, & U to measurement_dict
for cat in ["I_np", "I_p", "Q", "U"]:

    # Set the tag name that will be used in the measurement dictionary and the
    # fields that will be included under that umbrella
    if cat == "I_np":
        tag = cat.replace("_np", "")
        fields = [
            field
            for field in list(f["Data_Directional_Fields"].keys())
            if (tag in field)
        ]
    else:
        tag = cat.replace("_p", "")
        fields = [
            field
            for field in list(f["Data_Directional_Fields"].keys())
            if (tag in field) and ("NP" not in field)
        ]
    fields.sort()

    arrays = []
    scales = []
    long_names = []
    fills = []
    units = []
    for field in fields:

        print(field, end=", ")

        scales.append(f["Data_Directional_Fields"][field].attrs["scale_factor"])
        long_names.append(f["Data_Directional_Fields"][field].attrs["long_name"])
        fills.append(f["Data_Directional_Fields"][field].attrs["_FillValue"])
        units.append(f["Data_Directional_Fields"][field].attrs["units"])

        arrays.append(np.array(f["Data_Directional_Fields"][field]))
    if len(np.unique(scales)) == 1:
        scales = scales[0]
    if len(np.unique(fills)) == 1:
        fills = fills[0]
    if len(np.unique(units)) == 1:
        units = units[0]
    measurement_dict[cat] = {}
    measurement_dict[cat]["fields"] = fields
    measurement_dict[cat]["scale"] = scales
    measurement_dict[cat]["long_name"] = long_names
    measurement_dict[cat]["fill"] = fills
    measurement_dict[cat]["units"] = units
    measurement_dict[cat]["data"] = np.stack(arrays, axis=3)
# Create the dictionary that will hold all of the processed data and metadata
final_dict = {}

# Set first layer of the dataset
final_dict["observation_data"] = {}

# Populate the I intensity measures from the raw data
final_dict["observation_data"]["I_PARASOL"] = copy.deepcopy(measurement_dict["I_np"])


# Add matrices for the polarized and unpolarized wavelengths as fields in the
# Final dictionary
for i in [True, False]:
    if i:
        print("polarized")
        tag = "I_p"
        field_name = "polarization_wavelengths"
        lambdas = [
            int(field.replace("I", "").replace("P", ""))
            for field in measurement_dict[tag]["fields"]
        ]
    else:
        print("non-polarized")
        tag = "I_np"
        field_name = "intensity_wavelengths"
        lambdas = [
            int(field.replace("I", "").replace("NP", "").replace("P", ""))
            for field in measurement_dict[tag]["fields"]
        ]
    shape = measurement_dict[tag]["data"].shape
    new_shape = []

    lambda_arrs = []

    for lam in lambdas:
        new_shape = []
        for dim in shape[:-1]:
            new_shape.append(dim)
        # new_shape.append(1)

        lambda_arrs.append(np.full(new_shape, fill_value=np.full(16, lam)))
        # break
    full_lambdas_arr = np.stack(lambda_arrs, axis=3)
    print(full_lambdas_arr.shape)

    final_dict["sensor_views_bands"] = {}
    final_dict["sensor_views_bands"][field_name] = {}
    final_dict["sensor_views_bands"][field_name]["scale"] = 1
    final_dict["sensor_views_bands"][field_name]["long_name"] = "field_name"
    final_dict["sensor_views_bands"][field_name]["fill"] = 32767
    final_dict["sensor_views_bands"][field_name]["units"] = "tbd"
    final_dict["sensor_views_bands"][field_name]["data"] = full_lambdas_arr
# Set the scaling and fill numbrs for the Q, U, and I
scale = measurement_dict["Q"]["scale"]
fill = measurement_dict["Q"]["fill"]

# Scal the arrays for I, Q, & U with the appropriate scaling factor
for key in measurement_dict.keys():
    if key == "I_p":
        I_arr = copy.deepcopy(measurement_dict[key]["data"]) * scale
        I_arr[np.abs(I_arr) == fill] = 1
    elif key == "Q":
        Q_arr = copy.deepcopy(measurement_dict[key]["data"]) * scale
        Q_arr[np.abs(Q_arr) == fill] = 1
    elif key == "U":
        U_arr = copy.deepcopy(measurement_dict[key]["data"]) * scale
        U_arr[np.abs(U_arr) == fill] = 1
    else:
        continue
# Perform the DOLP operation elementwise on these arrays
DOLP = np.divide(np.sqrt(np.add(np.square(Q_arr), np.square(U_arr))), I_arr)

# Set every index where the data originally had fill values back to the fill
# value after elementwise operations have been completed
DOLP[
    np.where(
        (measurement_dict["I_p"]["data"] == fill)
        | (measurement_dict["Q"]["data"] == fill)
        | (measurement_dict["U"]["data"] == fill)
    )
] = fill

# Define the indexes where none of the arrays had fill values
indx = np.where(
    (np.abs(I_arr) != (fill * scale))
    & (np.abs(Q_arr) != (fill * scale))
    & (np.abs(U_arr) != (fill * scale))
)

# Add the DOLP data to the final_dict
final_dict["observation_data"]["DOLP_PARASOL"] = {}
final_dict["observation_data"]["DOLP_PARASOL"]["scale"] = 1
final_dict["observation_data"]["DOLP_PARASOL"]["long_name"] = "INSERT LONG NAME"
final_dict["observation_data"]["DOLP_PARASOL"]["fill"] = fill
final_dict["observation_data"]["DOLP_PARASOL"]["units"] = "INSERT UNITS"
final_dict["observation_data"]["DOLP_PARASOL"]["data"] = DOLP

# Calculate the Q over I and U over I fields
Q_over_I = np.divide(Q_arr, I_arr)
U_over_I = np.divide(U_arr, I_arr)

Q_over_I[
    np.where(
        (measurement_dict["I_p"]["data"] == fill)
        | (measurement_dict["Q"]["data"] == fill)
        | (measurement_dict["U"]["data"] == fill)
    )
] = fill

U_over_I[
    np.where(
        (measurement_dict["I_p"]["data"] == fill)
        | (measurement_dict["Q"]["data"] == fill)
        | (measurement_dict["U"]["data"] == fill)
    )
] = fill

# Add Q over I to the final dictionary
final_dict["observation_data"]["Q_over_I_PARASOL"] = {}
final_dict["observation_data"]["Q_over_I_PARASOL"]["scale"] = 1
final_dict["observation_data"]["Q_over_I_PARASOL"]["long_name"] = "INSERT LONG NAME"
final_dict["observation_data"]["Q_over_I_PARASOL"]["fill"] = fill
final_dict["observation_data"]["Q_over_I_PARASOL"]["units"] = "INSERT UNITS"
final_dict["observation_data"]["Q_over_I_PARASOL"]["data"] = Q_over_I

# Add U over I to the final dictionary
final_dict["observation_data"]["U_over_I_PARASOL"] = {}
final_dict["observation_data"]["U_over_I_PARASOL"]["scale"] = 1
final_dict["observation_data"]["U_over_I_PARASOL"]["long_name"] = "INSERT LONG NAME"
final_dict["observation_data"]["U_over_I_PARASOL"]["fill"] = fill
final_dict["observation_data"]["U_over_I_PARASOL"]["units"] = "INSERT UNITS"
final_dict["observation_data"]["U_over_I_PARASOL"]["data"] = U_over_I

# add a geolocation field to the final_dict
final_dict["geolocation_data"] = {}

# Add solar zenith, viewing zenith, and relative azimuth to the final dictionary
for field in ["thetas", "thetav", "phi"]:
    if field == "thetas":
        tag = "solar_zenith"
    elif field == "thetav":
        tag = "sensor_zenith"
    elif field == "phi":
        tag = "relative_azimuth"
    final_dict["geolocation_data"][tag] = {}
    final_dict["geolocation_data"][tag]["scale"] = f["Data_Directional_Fields"][
        field
    ].attrs["scale_factor"]
    final_dict["geolocation_data"][tag]["long_name"] = f["Data_Directional_Fields"][
        field
    ].attrs["long_name"]
    final_dict["geolocation_data"][tag]["fill"] = f["Data_Directional_Fields"][
        field
    ].attrs["_FillValue"]
    final_dict["geolocation_data"][tag]["units"] = f["Data_Directional_Fields"][
        field
    ].attrs["units"]
    final_dict["geolocation_data"][tag]["data"] = np.array(
        f["Data_Directional_Fields"][field]
    )
# Add Latitude, longitude, and altitude fields to the final dictionary
for field in ["Latitude", "Longitude", "surface_altitude"]:
    if field == "surface_altitude":
        tag = "altitude"
    else:
        tag = field
    final_dict["geolocation_data"][tag] = {}
    final_dict["geolocation_data"][tag]["scale"] = f["Geolocation_Fields"][field].attrs[
        "scale_factor"
    ]
    final_dict["geolocation_data"][tag]["long_name"] = f["Geolocation_Fields"][
        field
    ].attrs["long_name"]
    final_dict["geolocation_data"][tag]["fill"] = f["Geolocation_Fields"][field].attrs[
        "_FillValue"
    ]
    final_dict["geolocation_data"][tag]["units"] = f["Geolocation_Fields"][field].attrs[
        "units"
    ]
    final_dict["geolocation_data"][tag]["data"] = np.array(
        f["Geolocation_Fields"][field]
    )


def write_nc(variable_dict, filename):

    nc = Dataset(filename, mode="w", format="NETCDF4")

    for cat in variable_dict.keys():

        # Create the category group to store the variables
        nc.createGroup(cat)

        for var in variable_dict[cat].keys():
            print(var)

            # Fill the dimension with variables
            dimensions = []
            for i in range(len(variable_dict[cat][var]["data"].shape)):
                dim_name = f"{var}_{i}"
                nc.createDimension(dim_name, size=None)
                dimensions.append(dim_name)
            # Create the variable instance
            print("creating variable")
            nc[cat].createVariable(
                var,
                datatype="f4",
                dimensions=dimensions,
                fill_value=variable_dict[cat][var]["fill"],
            )

            # Create variable metadata
            print("creating the metaverse")
            nc[cat][var].long_name = variable_dict[cat][var]["long_name"]
            nc[cat][var].units = variable_dict[cat][var]["units"]
            nc[cat][var].scale_factor = variable_dict[cat][var]["scale"]

            # Create variable array
            print("create variable array")
            nc[cat][var][:] = variable_dict[cat][var]["data"]


write_nc(final_dict, nc_path)
