from typing import NamedTuple


class HDFColumn:
    """ Class for holding the conversion dictionary column details"""
    outputName: str
    inputName: str
    unpack: bool
    list_str_unpack: list
    list_wavelength_unpack: list


list_caltrack = [
    HDFColumn(outputName='lats', inputName='Latitude', unpack=False, list_str_unpack=[], list_wavelenght_unpack=[]),
    HDFColumn(outputName='lons', inputName='Longitude', unpack=False, list_str_unpack=[], list_wavelenght_unpack=[]),
    # HDFColumn(outputName='i', inputName='Normalized_Radiance_', unpack=True,
    #             list_str_unpack=['P'],
    #             list_wavelenght_unpack=['490', '']),
    # HDFColumn(outputName='lats', inputName='Latitude', unpack=False, list_str_unpack=[], list_wavelenght_unpack=[]),
    # HDFColumn(outputName='lats', inputName='Latitude', unpack=False, list_str_unpack=[], list_wavelenght_unpack=[]),
    # HDFColumn(outputName='lats', inputName='Latitude', unpack=False, list_str_unpack=[], list_wavelenght_unpack=[]),
    # HDFColumn(outputName='lats', inputName='Latitude', unpack=False, list_str_unpack=[], list_wavelenght_unpack=[]),
    # HDFColumn(outputName='lats', inputName='Latitude', unpack=False, list_str_unpack=[], list_wavelenght_unpack=[]),
    #

]


# Output Name
# Input Listing
# Do we need to unpack? [yes/no]
# list of items to unpack (NP vs P, wavelengths)
# list to unpack

