# LOOK FOR DAYS WHERE PRESSURE GRADIENT BETWEEN KGEG AND KSEA IS 8-10 MB OR HIGHER
from __future__ import print_function  # you may not need this

import requests
from datetime import datetime, timedelta
from numpy import mean

def process_observations(obs_tuple_list, input_dict, stations_position, station_name):
    print("start processing: {}".format(station_name))
    # the hours you're interested in - 7am to 8pm
    zulu_hour_range = {20, 21, 22, 23}
    count = 0
    for utc_time, obs in obs_tuple_list:

        # convert time string to datetime obj and corrected string for dictionary lookup
        dt_full = datetime.strptime(utc_time, '%Y-%m-%dT%H:%M:%SZ')
        dt_str =  dt_full.strftime("%Y-%m-%d")

        # check if zulu hour in correct time range
        if dt_full.hour in zulu_hour_range:
            # test for None value, this destroyed everything if a None gets in there
            if obs:
                input_dict[dt_str][stations_position].append(obs)
        else:
            # print("observation during zulu hour time: {} - rejected, not in hour range!".format(dt_full.hour))
            pass
        
        count += 1
        if count % 5000 == 0:
            print("{} - processed: {} observations".format(station_name, count))        
    print("completed: {} - total obs: {}".format(station_name, count))
    # end of process_observations function

# change these to adjust your range
start_date = '201901011500'
end_date = '202005110300'

api_url = 'https://api.synopticdata.com/v2/stations/timeseries'

api_arguments = {"token":'demotoken',
                 "stids":['KSEA', 'KGEG'],
                 "start":start_date,
                 "end":end_date,
                 "vars":'sea_level_pressure',
                 "units": 'pres|mb'
                 }

req = requests.get(api_url, params=api_arguments).json()

for stn in req['STATION']:
    if stn['STID'] == 'KSEA':
        ksea_obs = zip(stn['OBSERVATIONS']['date_time'], stn['OBSERVATIONS']['sea_level_pressure_set_1d'])
    else:
        kgeg_obs = zip(stn['OBSERVATIONS']['date_time'], stn['OBSERVATIONS']['sea_level_pressure_set_1d'])
 
start_datetime = datetime.strptime(start_date, '%Y%m%d%H%M')
end_datetime = datetime.strptime(end_date, '%Y%m%d%H%M')

time_range_delta = (end_datetime - start_datetime) + timedelta(days=1)

# build a blank value dictionary, the first position is for ksea_obs and the second position is for kgeg_obs
daily_values_dict = {(start_datetime + timedelta(days=i)).strftime("%Y-%m-%d"):[[],[]] for i in range(time_range_delta.days + 1)} 

# for dictionary value positioning
ksea_position = 0
kgeg_position = 1

# run the daily_values_dict thru to process observations - it was less code to run it thru a function
process_observations(ksea_obs, daily_values_dict, ksea_position, "KSEA")
process_observations(kgeg_obs, daily_values_dict, kgeg_position, "KGEG")

print("start summarizing")

# pull the averages for each day and each station
daily_averages_dict = {i:(mean(daily_values_dict[i][ksea_position]), mean(daily_values_dict[i][kgeg_position])) for i in daily_values_dict}

# return the days of interest who's average is less than or equal to -8 based on "KGEG - KSEA"
days_of_interest = sorted([(i, (daily_averages_dict[i][kgeg_position] - daily_averages_dict[i][ksea_position]))  for i in daily_averages_dict if (daily_averages_dict[i][ksea_position] - daily_averages_dict[i][kgeg_position]) <= -3])

print("found the following days of interest: ")
for day, difference_between_averages in days_of_interest:
    print("{} - Difference: {}".format(day, difference_between_averages))

print("found {} days of interest!".format(len(days_of_interest)))
print("done!")