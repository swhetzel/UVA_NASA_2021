# -*- coding: utf-8 -*-
"""
Created on Fri Nov  5 11:13:34 2021

@author: whetz
"""

import pandas as pd
import h5py
from pyhdf.SD import SD, SDC
import matplotlib.pyplot as plt
import os
import seaborn as sns
import numpy as np

def get_tracked_parasol(
        file, step = 20, 
        north_tracks=2, 
        south_tracks=2, 
        lat=34.540852, 
        lon=-68.379303, 
        buffer=0.001
        ):
    """
    Creates a dataframe with all wavelength/polarization states/viewing angles
    from PARASOL files with normalized radiances and degrees of linear polarization. 
    Organizes by tracks centered around a point of interest

    Parameters
    ----------
    file : TYPE
        DESCRIPTION.
    step : TYPE, optional
        DESCRIPTION. The default is 20.
    north_tracks : TYPE, optional
        DESCRIPTION. The default is 2.
    south_tracks : TYPE, optional
        DESCRIPTION. The default is 2.
    lat : TYPE, optional
        DESCRIPTION. The default is 34.540852.
    lon : TYPE, optional
        DESCRIPTION. The default is -68.379303.
    buffer : TYPE, optional
        DESCRIPTION. The default is 0.001.

    Returns
    -------
    None.

    """

    rad_list = [
        'Normalized_Radiance_443NP',
        'Normalized_Radiance_490P',
        'Normalized_Radiance_1020NP',
        'Normalized_Radiance_565NP',
        'Normalized_Radiance_670P',
        'Normalized_Radiance_763NP',
        'Normalized_Radiance_765NP',
        'Normalized_Radiance_865P',
        'Normalized_Radiance_910NP'
    ]
    q_fields = [
        'Q_Stokes_490P',
        'Q_Stokes_670P',
        'Q_Stokes_865P'
    ]
    u_fields  = [
        'U_Stokes_490P',
        'U_Stokes_670P',
        'U_Stokes_865P'
    ]

    
    hdf = SD(file, SDC.READ)
    lats = (list(hdf.select('Latitude').get()))
    lons = (list(hdf.select('Longitude').get()))

    lat1 = lat - buffer
    lat2 = lat + buffer
    lon1 = lon - buffer
    lon2 = lon + buffer

    df_coord = pd.DataFrame({'lat':lats,'lon':lons})
    index = df_coord.query(F"lat > {lat1} & lat < {lat2} & lon > {lon1} & lon < {lon2}").index[0]

    master_df = pd.DataFrame()

    # Loop through each track based on initial index and specified step
    for i in range(-1*(south_tracks),north_tracks+1):
        ind = index + step*i
        
        # Get the coordinates & time
        lat = pd.DataFrame(hdf.select('Latitude').get()).loc[ind][0]
        lon = pd.DataFrame(hdf.select('Longitude').get()).loc[ind][0]
        time = pd.DataFrame(hdf.select('Time').get()).loc[ind][0]
#         print(ind, time)
                
        # Loop through each radiance 
        rad_df = pd.DataFrame()
        for rad in rad_list:
            temp = pd.DataFrame(hdf.select(rad).get()).loc[ind]
            transform = [round(i*(10**(-4)),5) if i > -1000 else i for i in list(temp)]
#             print(list(temp))
#             print(pd.DataFrame(transform).transpose())
            
            df_temp = (pd.DataFrame(transform).transpose())
            df_temp['Wavelength'] = (rad).replace('Normalized_Radiance_','')
            rad_df = pd.concat([rad_df,df_temp])

        
        # Rest index and rename the columns
        rad_df = rad_df.reset_index(drop=True)
        rad_cols = ([i for i in range(16)])
        rad_cols.append('wavelength')
        rad_df.columns = rad_cols
        
#         print(rad_df)    


        # Get q data and add to the dataframe
        q_df = pd.DataFrame()
        for q in q_fields:
            
            temp = pd.DataFrame(hdf.select(q).get()).loc[ind]
            transform = [round(i*(10**(-4)),5) if i > -1000 else i for i in list(temp)]
#             print(transform)
            
            df_temp = pd.DataFrame(transform).transpose()
            
#             df_temp = (pd.DataFrame(pd.DataFrame(hdf.select(q).get()).loc[ind]).transpose())
            df_temp['wavelength'] = q.replace('Q_Stokes_','')
            q_df = pd.concat([q_df, df_temp])

        qcols = [i for i in range(16)]
        qcols.append('wavelength')
        q_df.columns = qcols
        # print(q_df)

        # Get u data and add to the dataframe
        u_df = pd.DataFrame()
        for u in u_fields:
            
            temp = pd.DataFrame(hdf.select(q).get()).loc[ind]
            transform = [round(i*(10**(-4)),5) if i > -1000 else i for i in list(temp)]
#             print(transform)
            
            df_temp = pd.DataFrame(transform).transpose()
#             df_temp = (pd.DataFrame(pd.DataFrame(hdf.select(u).get()).loc[ind]).transpose())
            df_temp['wavelength'] = u.replace('U_Stokes_','')
            u_df = pd.concat([u_df, df_temp])
        ucols = [i for i in range(16)]
        ucols.append('wavelength')
        u_df.columns = ucols
        
#         print(u_df)

        # Melt the matrices
        rad_melt = rad_df.melt(id_vars='wavelength',value_vars=[i for i in range(16)], var_name='angle', value_name='norm_rad')
#         print(rad_melt)
        q_melt = q_df.melt(id_vars='wavelength',value_vars=[i for i in range(16)], var_name='angle', value_name='q')
        u_melt = u_df.melt(id_vars='wavelength',value_vars=[i for i in range(16)], var_name='angle', value_name='u')
        
        # join each matrix
        df_merge = pd.merge(left=rad_melt, right=q_melt, how='left',on=['wavelength', 'angle'])
        df_merge = pd.merge(left=df_merge, right=u_melt, how='left',on=['wavelength', 'angle'])
        
        # replace missing data with np.nan
        df_merge.replace(-32768, np.NaN)

        # Calclate Degree of linear polarization
        df_merge['dolp'] = round(np.sqrt(df_merge.q**2 + df_merge.u**2)/df_merge.norm_rad,3)
        
        # Add traack column
        df_merge['track'] = i

        # Filter for non-missing values
        df_merge = df_merge.query("norm_rad > -1000")
        
        # Add in coordinate values and time values
        df_merge['lat'] = [lat for i in range(len(df_merge))]
        df_merge['lon'] = [lon for i in range(len(df_merge))]
        df_merge['coord'] = [str(round(df_merge.loc[i].lat,5)) + ', ' + str(round(df_merge.loc[i].lon,5))  for i in range(len(df_merge))]
        df_merge['time'] = [time for i in range(len(df_merge))]
                                                                   
        # Add to master df and go to next track
        master_df = pd.concat([master_df, df_merge]).reset_index(drop=True)
    return master_df


def plot_tracked_parasol(master_df, np=True):
    """
    Creates visuals for the Normalized radiances and degrees of linear polarization
    for each track generated in get_tracked_parasol

    Parameters
    ----------
    master_df : TYPE
        DESCRIPTION.
    np : TYPE, optional
        DESCRIPTION. The default is True.

    Returns
    -------
    None.

    """
    
    non_pols = [
        '443NP',
        '1020NP',
        '565NP',
        '763NP',
        '765NP',
        '910NP'
    ]

    pols = [
        '490P',
        '670P',
        '865P'
    ]
    df_np = master_df[master_df.wavelength.isin(non_pols)]
    df_p = master_df[master_df.wavelength.isin(pols)]

    if np:
        g = sns.FacetGrid(df_np, col="coord", height=10, aspect=.75)
        g.map_dataframe(sns.lineplot, x="angle", y="norm_rad", hue='wavelength')
        g.fig.subplots_adjust(top=0.9)
        g.fig.suptitle(('Normalized Radiance for Non-Polarized Wavelenghts by Viewing Angle').upper())
        g.add_legend()
    else:
        g = sns.FacetGrid(df_p, col="coord", height=10, aspect=.75)
        g.map_dataframe(sns.lineplot, x="angle", y="dolp", hue='wavelength')
        g.fig.subplots_adjust(top=0.9)
        g.fig.suptitle(('Degree of Linear Polarization by Viewing Angle').upper())
        g.add_legend()