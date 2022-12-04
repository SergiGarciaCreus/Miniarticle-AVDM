# -*- coding: utf-8 -*-
"""
Created on Thu Nov 17 16:01:04 2022

@author: sergi
"""

import pandas as pd
import matplotlib.pyplot as plt
import os
import matplotlib.colors as mplC
from matplotlib import cm
import geopandas as gpd

#Import the data we are going to use for this project.
Datos = pd.read_csv('.\datosO3_catalunya_whole.csv')
#Change the date format that the dataset uses to one that Pandas can work with.
Datos['date'] = pd.to_datetime(Datos.data)
#Calculate the daily concentration mean with the hourly mesurements
lista_horas = ['h01', 'h02', 'h03', 'h04', 'h05', 'h06', 'h07', 'h08', 'h09', 'h10', 'h11', 'h12', 'h13', 'h14', 'h15', 'h16', 'h17', 'h18', 'h19', 'h20', 'h21', 'h22', 'h23', 'h24']
Datos["DailyMean"] = Datos[lista_horas].mean(axis=1)
#Having the DailyMean remove most of the columns so it is easier to work with the DataFrame
DatosUse = Datos[['nom_comarca', 'date', 'DailyMean']]
DatosUse = DatosUse.set_index('date')

#Create a new simpler DataFrame for averages for each "Comaraca" of all the years and by year
DatosAveraged = DatosUse.groupby(by='nom_comarca').mean()
DatosAveraged = DatosAveraged.rename(columns={'DailyMean':'AllYears'})
years = ['2019-01-01', '2020-01-01', '2021-01-01', '2022-01-01', '2023-01-01']
for ii in range(len(years)-1):
    aaa = DatosUse[years[ii]:years[ii+1]].groupby(by='nom_comarca').mean()
    aaa = aaa.rename(columns={'DailyMean':years[ii][:4]})
    DatosAveraged = DatosAveraged.merge(aaa, how='left', on='nom_comarca')
    
#Create a new simpler DataFrame for maximum values.
DatosMax = DatosUse.groupby(by='nom_comarca').max()
DatosMax = DatosMax.rename(columns={'DailyMean':'AllYears'})
for ii in range(len(years)-1):
    aaa = DatosUse[years[ii]:years[ii+1]].groupby(by='nom_comarca').max()
    aaa = aaa.rename(columns={'DailyMean':years[ii][:4]})
    DatosMax = DatosMax.merge(aaa, how='left', on='nom_comarca')
   
#Create a new DataFrame with the average for the 6 month peak season
Datos6m = DatosUse.groupby(by='nom_comarca').mean()
Datos6m = Datos6m.rename(columns={'DailyMean':'AllYears'})
for ii in range(len(years)-1):
    aaa = DatosUse[years[ii]:years[ii+1]]
    aaa = aaa.reset_index()
    aaa = aaa[aaa['date'].dt.month > 3]
    aaa = aaa[aaa['date'].dt.month <= 9]
    aaa = aaa.groupby(by='nom_comarca').mean()
    aaa = aaa.rename(columns={'DailyMean':years[ii][:4]})
    Datos6m = Datos6m.merge(aaa, how='left', on='nom_comarca')
  
#Import the geopandas info for the Catalan "Comarques"
dir_list_cat = [x for x in os.listdir("./divisions_administratius/") if x[-4:]==".shp"] #Only shape files
dir_list_cat = [x for x in os.listdir("./divisions_administratius/") if x[-21:]=="-1000000-20220801.shp"] #Highest resulution
ids = {x:x[31:-21] for x in dir_list_cat}
cat_maps = {}
for maps in dir_list_cat:
    cat_maps[ids[maps]] = gpd.read_file("./divisions_administratius/"+maps, crs="EPSG:4326")   
gdfComarques = cat_maps['comarques']
gdfComarques = gdfComarques.rename({'NOMCOMAR':'nom_comarca'}, axis=1)

#Merge our data with the Geopandas information, note that here how='left' will mantain all the "Comarcas", even those that we don't have any data for O3. This way later we can draw those in a special way to denote that and not just leave a white space
DatosAveraged = gdfComarques.merge(DatosAveraged, how='left', on='nom_comarca')
DatosMax = gdfComarques.merge(DatosMax, how='left', on='nom_comarca')
Datos6m = gdfComarques.merge(Datos6m, how='left', on='nom_comarca')

#%% Generating the figures used for the presentation

#Create a cmap to be used to plot the data. The colors used are those used for the Air Quaility Index, but this is not what is measured here.
cmap = (mplC.ListedColormap(['green','yellow', 'orange', 'red']) # Was not used at the end but if needed the last colors of AQI in matplotlib are 'darkred' and 'palevioletred'
        .with_extremes(over='0.25', under='0.75'))

#The bounds are set following the World Health Organitzation guideline and interim levels for short term and long term exposure to O3
bounds = [0, 60, 70, 100, 130] #Long term exposure WHO levels
normAve = mplC.BoundaryNorm(bounds, cmap.N)
bounds = [0, 100, 120, 160, 200] #Short term exposure WHO levels
normMax = mplC.BoundaryNorm(bounds, cmap.N)

#Plot the results for all the years together and each one individualy in diferent figures. On each figure there is a subplot for average values and one for maximum values.
names_col = list(DatosAveraged.columns[-4:])
for col in names_col:
    fig, ax = plt.subplots(1,2)
    fig.suptitle('Study of $O_3$ concentration by region, year {}'.format(col), fontsize=16)
    DatosMax.plot(column=col, cmap=cmap, norm=normMax, edgecolor='Black', ax=ax[0], legend=True, legend_kwds={'spacing':'proportional', 'orientation':'horizontal', 'label':'$O_3$ concentration (\u03BCg/$m^3$)'}, missing_kwds={
            "color": "lightgrey",
            "label": "No Data"})
    ax[0].set_title('Maximum Value', fontsize=14)
    ax[0].set_axis_off()
    Datos6m.plot(column=col, cmap=cmap, norm=normAve, edgecolor='Black', ax=ax[1], legend=True, legend_kwds={'spacing':'proportional', 'orientation':'horizontal', 'label':'$O_3$ concentration (\u03BCg/$m^3$)'},  missing_kwds={
            "color": "lightgrey",
            "label": "No Data"})
    ax[1].set_title('Peak season Average', fontsize=14)
    ax[1].set_axis_off()
    
#%% Generating the figures for the miniarticle 
'''
The plots will be exactly the same the only thing diferent will be how the subplots are arranged.
For the presentation it was a plot for every year with its long term and short term exposure results.
Here it will be the other way around, the short term results of every year in a plot, and the same for the long term results.
'''

fig, axes = plt.subplots(2,2) #Create one figure with 4 subplots, one for each year
fig.suptitle('Study of $O_3$ long term exposure by year and "Comarca"',  fontsize=16)
ii = 0
for ax in axes.flat: #Plot on each subplot the results of the peak season average for each year
    Datos6m.plot(column=names_col[ii], cmap=cmap, norm=normAve, edgecolor='Black', ax=ax, missing_kwds={
            "color": "lightgrey",
            "label": "No Data"})
    ax.set_title(names_col[ii], fontsize=14)
    ax.set_axis_off()
    ii = ii + 1

fig.subplots_adjust(right=0.82) #Add only one colorbar for all 4 subplots
cbar_ax = fig.add_axes([0.85, 0.15, 0.04, 0.7])
fig.colorbar(cm.ScalarMappable(norm=normAve, cmap=cmap), cax=cbar_ax, spacing='proportional', label='$O_3$ concentration (\u03BCg/$m^3$)')

#%% Exactly the same for the short term exposure
fig, axes = plt.subplots(2,2) #Create one figure with 4 subplots, one for each year
fig.suptitle('Study of $O_3$ short term exposure by year and "Comarca"',  fontsize=16)
ii = 0
for ax in axes.flat: #Plot on each subplot the results of the peak season average for each year
    DatosMax.plot(column=names_col[ii], cmap=cmap, norm=normMax, edgecolor='Black', ax=ax, missing_kwds={
            "color": "lightgrey",
            "label": "No Data"})
    ax.set_title(names_col[ii], fontsize=14)
    ax.set_axis_off()
    ii = ii + 1

fig.subplots_adjust(right=0.82) #Add only one colorbar for all 4 subplots
cbar_ax = fig.add_axes([0.85, 0.15, 0.04, 0.7])
fig.colorbar(cm.ScalarMappable(norm=normMax, cmap=cmap), cax=cbar_ax, spacing='proportional', label='$O_3$ concentration (\u03BCg/$m^3$)')

#%% Temporal study some of the "Comarcas" with more detail (not used in the presentation but used in the mini article)

#Slice the data to have only that corresponding to Pallars Jussà
DatosJussa = DatosUse[DatosUse['nom_comarca']== 'Pallars Jussà'] 
#Do a move average to reduce the high variability of the data
DatosJussa["Moving Daily Average"] = DatosJussa['DailyMean'].rolling(30, min_periods=15, center=True).mean()

#Same for Barcelones comarca
DatosBar = DatosUse[DatosUse['nom_comarca']== 'Barcelonès']
#Barcelones has more than one station that measures daily, we average the results of all of them for every day
DatosBar = DatosBar.groupby('date').mean()
#And finally do the moving average.
DatosBar["Moving Daily Average"] = DatosBar['DailyMean'].rolling(30, min_periods=15, center=True).mean()

#Plot the results
fig, ax = plt.subplots()
DatosJussa.plot(y='Moving Daily Average', ax = ax, label='Pallars Jussà')
DatosBar.plot(y='Moving Daily Average', ax = ax, label='Barcelonès')
ax.set_ylabel('$O_3$ concentration (\u03BCg/$m^3$)')
ax.set_title('Study of the temporal evolution of $O_3$ concentration')
                
                
                
