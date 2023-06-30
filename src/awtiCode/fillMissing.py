# -*- coding: utf-8 -*-
"""
This module contains three functions for filling missing data:
    - Arithmetic Mean method (functionname: AMM)
    - Normal Ratio Method (functionname: NRM)
    - Inverse distance method (functionname: IDM)
For a working example, see Estimation of Missing Data.py
@author: Israel
"""

import pandas as pd
import numpy as np

#1)Arithmetic Mean Method
def AMM(dataframe):
    """
    The provided dataframe should only have columns that you want filled. They will be filled on the average of the respective columns.

    Parameters
    ----------
    dataframe : pandas dataframe
        Dataframe with columns containing data (to use in filling) and missing data (to fill).

    Returns
    -------
    DataFrame with all missing values filled.

    """
    fillvalues = dataframe.mean(axis=1)
    colnames = dataframe.columns
    filldict = {}
    for colname in colnames:
        filldict[colname] = fillvalues
    dfFilled = dataframe.fillna(filldict)
    return dfFilled


#2) Normal Ratio Method
def NRM(dataframe):
    """
    The provided dataframe should only have columns that you want filled. Missing data of each column will be filled based on the normal ratio of the other columns.

    Parameters
    ----------
    dataframe : pandas dataframe
        Dataframe with columns containing data (to use in filling) and missing data (to fill).

    Returns
    -------
    DataFrame with all missing values filled.

    """

    #Normal ratio method requares the normal anual rain fall of each station (Ni) and 
    #the mean annual rain fall of all stations(Nx)
    Ni = dataframe.mean()
    Nx = Ni.mean()

    # code to calculate the normal ratio of each station    
    filldict = {}
    for column in dataframe.columns:
        othercolumns = dataframe.iloc[:,dataframe.columns!=column]
        NiOthers = Ni[Ni.index!=column]
        filldict[column] = (Nx/len(NiOthers))*((othercolumns/NiOthers).sum(axis=1))

    dfFilled = dataframe.fillna(filldict)
    return dfFilled

#3) Inverse distance method
def IDM(fillColumns,distances):
    """
    Calculate inverse distance weighed values for a certain point, based on provided columns and corresponding distances to that point.

    Parameters
    ----------
    fillColumns : Pandas DataFrames
        The columns based on which the inverse distance weighted values are calculated.
    distances : collection, array-like
        The distances 

    Returns
    -------
    fillData : Pandas Series
        The calculated values based on Inverse Distance Weighted method.

    """
    if len(fillColumns.columns)!=len(distances):
        print('THe number of provided columns is not equal to the number of provided distances. IDW cannot be calculated.')
        return
    
    distances = np.array(distances)
    invDist = 1/distances**2
    sumID = np.sum(invDist)
    
    #To make shure that the correct distance is matched with the correct column,
    # the array needs to be reshaped from (n,) to (1,n).
    distSquared = (distances**2).reshape(1,len(distances))
    
    fillData = (fillColumns/distSquared).sum(axis=1)/sumID
    return fillData