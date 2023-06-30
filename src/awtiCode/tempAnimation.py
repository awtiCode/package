# -*- coding: utf-8 -*-
"""
Created on Fri Dec 30 11:01:39 2022

@author: jandirk
"""

import numpy as np
from matplotlib import pyplot as plt, animation

def animateLatLonNC(dataset,data_var='none',lonDim='lon',latDim='lat',timeDim='time',saveAni = False,**kwargs):
    """
    This function returns an animation of an xarray DataSet data variable, over time, for latitudes and longitudes. It is built for temperatures in Kelvin.

    Parameters
    ----------
    dataset : xarray Dataset
        A dataset with a data_variable to animate, that has dims time, latitude and longitude.
    data_var : str
        The name of the data variable that needs to be plotted. The default is 'none'; keep it 'none' if you provide a dataset of the datavariable itself.
        For example, dataset ds with data_var air can be inserted like 
            dataset=ds,data_var='air'
        or like
            dataset=ds.air,data_var='none'
    lonDim : str, optional
        The name of the longitude dimension in the dataset. The default is 'lon'.
    latDim : str, optional
        The name of the latitude dimension in the dataset. The default is 'lat'.
    timeDim : str, optional
        The name of the time dimension in the dataset. The default is 'time'.
    saveAni : boolean, optional
        If True, saves the animation on your laptop as 'animation.mp4'. The default is False.
    **kwargs : other settings
        Other settings that can be supplied are 'cmap', 'vmin', 'vmax' and 'cbar_label'.
        Default cmap is 'coolwarm'. To use for example the cmap 'jet', include cmap='jet'
        Default vmin and vmax (the ends of the color spectrum) are 280 and 310. To let the colorspectrum vary between 10 and 30 (for temperatures celcius), include vmin='10', vmax='30'
        Default label for the colorbar is 'Temperature (Kelvin)'. To put as label 'Celcius', include cbar_label='Celcius'

    Returns
    -------
    anim : The matplotlib animation

    """
    
    
    if 'cmap' in kwargs.keys():
        cmap = kwargs['cmap']
    else:
        cmap = 'coolwarm'
    
    if 'vmin' in kwargs.keys():
        vmin = kwargs['vmin']
    else:
        vmin = 280
    
    if 'vmax' in kwargs.keys():
        vmax = kwargs['vmax']
    else:
        vmax = 310
        
    if 'cbar_label' in kwargs.keys():
        cbarlabel = kwargs['cbar_label']
    else:
        cbarlabel = 'Temperature (Kelvin)'
    
    if data_var == 'none':
        dataset = dataset
    else:
        dataset = dataset[data_var]
    
    fig, ax = plt.subplots()
    cax = ax.contourf(dataset[lonDim], dataset[latDim], dataset[0], cmap=cmap,vmin=vmin,vmax=vmax)
    cbar=fig.colorbar(cax)
    cbar.set_label(cbarlabel)
    
    def animate(i):
        global cax
        if i>0:
            for c in cax.collections:
                c.remove()
        cax = ax.contourf(dataset[lonDim], dataset[latDim], dataset[i], cmap=cmap,vmin=vmin,vmax=vmax)
        ax.set_title(dataset[timeDim].dt.strftime('%B %Y')[i].values)

    anim = animation.FuncAnimation(fig, animate, interval=100, frames=len(dataset.time))
    fig.show()
    
    if saveAni==True:    
        anim.save('animation.mp4') 
    return anim