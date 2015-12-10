# Solar Panel Power Estimator
#   pv-estimate.py
#
#   Uses pvlib to estimate the amount of radiation a metre square solar panel will
#   receive over the course of a year.
#
#   Disclaimer: Do not use. I don't know what I'm doing.
#               In particular, I don't yet know how to include clouds in the simulation.
#
# Copyright (C) 2015 Oliver Wright
#    oli.wright.github@gmail.com
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program (file LICENSE); if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.import loggingimport datetime

import pvlib
import pandas

# Where is the panel, and how is it oriented?
latitude_deg = 53.234079 
longitude_deg = -2.594865
panel_tilt = 30
panel_azimuth = 90

year = 2016 # Shouldn't really matter what year we simulate
location = pvlib.location.Location( latitude_deg, longitude_deg, "GMT", 100, "MyLocation" )
start_datetime = datetime.datetime(year,1,1,0,0,0)

# We want a data point for every hour of the year
date_range = pandas.date_range( start_datetime, periods=24 * 365, freq="H" )
solarposition = pvlib.solarposition.get_solarposition( date_range, location )

# For each data point, get the angle of incidence of the sun on the panel
aoi = pvlib.irradiance.aoi( panel_tilt, 0, solarposition.zenith, solarposition.azimuth )

# Calculate direct normal irradiance (DNI) and diffuse horizontal irradiance (DHI)
# for a *clear* (cloudless) sky at our location.
# TODO: Figure out how to deal with clouds
clearksy = pvlib.clearsky.ineichen( date_range, location )
dni = clearksy.dni
dhi = clearksy.dhi

# Calculate the proportion of the dhi that the panel will receive
poa_sky_diffuse = pvlib.irradiance.isotropic( panel_tilt, dhi )
# TODO: Estimate diffuse radiation reflected from ground. pvlib provides functions to do this.
poa_ground_diffuse = 0

# Run the simulation
irradiance = pvlib.irradiance.globalinplane( aoi, dni, poa_sky_diffuse, poa_ground_diffuse )
#irradiance.to_csv( "output.csv" )

# Create data frames where the index (rows) is hour of the day (0-23) and the
# columns are months of the year (1-12)
global_radiation = pandas.DataFrame()
for month in range(1,13):
  # Extract the data for this month
  st = datetime.datetime(year,month,1,0,0,0)
  en = None
  if month == 12:
    en = datetime.datetime(year+1,1,1,0,0,0)
  else:
    en = datetime.datetime(year,month+1,1,0,0,0)
  month_irradiance = irradiance[st:en]
  
  # For each hour of the day, average the values over the month
  hours = []
  for hour in range(0,24):
    hours.append( month_irradiance[hour::24].mean() )
    
  # Add columns for this month
  df = pandas.DataFrame( hours )
  global_radiation[ month ] = df['poa_global']

# Write out a csv
global_radiation.to_csv( 'month_averages.csv', '\t' )        
    
