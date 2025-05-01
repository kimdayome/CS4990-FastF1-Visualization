import fastf1
import pandas as pd
import csv
import argparse


def get_dataset(filename, rows=None):
    output_data = []
    #driver_country_data = {}

    for year in range(2018, 2025):
    #for year in [2024]:
        events = fastf1.get_event_schedule(year)

        for evnt in events['OfficialEventName']:
        #for idx, race_event in events.iterrows(): 
        #import pdb; pdb.set_trace()

            race_name = evnt
            # found directly from API to extra event data by name
            # probably could use pandas.df to make this simpler?
            race_event = events.get_event_by_name(evnt) # might not need
            race_country = race_event['Country']
            race_loc = race_event['Location']
            race_format = race_event['EventFormat']
            race_date = race_event['EventDate']

            # skip test events to only aggregate real race data
            is_test_event = race_event.is_testing()
            if is_test_event:
                continue

            #load up data for race stat
            race_stats = race_event.get_race()
            race_stats.load(laps=False, telemetry=False, messages=False)
            # this is the race start TIME (different from event date)
            race_ts = race_stats.date

            # extract driver race results
            race_results = race_stats.results

            # when the API adds new races we have no data for, we must skip!
            if race_results.empty:
                print("Skipping {} {}- there is no data.".format(race_name, race_stats.date))
                continue
            # weather data (code added on 10/1)
            weather_data = race_stats.weather_data
            weather_temp_avg = weather_data['AirTemp'].mean()
            weather_humidity_avg = weather_data['Humidity'].mean()
            weather_pressure_avg = weather_data['Pressure'].mean()
            weather_rain = True in weather_data['Rainfall'].values # if its raining during the race, it will be changed to 'True'
            weather_track_temp = weather_data['TrackTemp'].mean()
            weather_wind_speed_avg = weather_data['WindSpeed'].mean()

            # race results for EACH driver
            for idx, driver_info in race_results.iterrows():
                race_info = {} # dictionary for everything, per driver

                # set race information into race_info
                race_info['Race Name'] = race_name
                race_info['Race Location'] = "{},{}".format(race_loc, race_country)
                race_info['Race Date'] = race_date
                race_info['Race Format'] = race_format

                # add race start timestamp
                race_info['Race Start Time'] = race_ts

                # set weather information (code added on 10/1)
                race_info['Air Temperature'] = weather_temp_avg
                race_info['Relative Humidity'] = weather_humidity_avg
                race_info['Air Pressure'] = weather_pressure_avg
                race_info['Rainfall'] = weather_rain
                race_info['Track Temperature'] = weather_track_temp
                race_info['Wind Speed'] = weather_wind_speed_avg

                # add results and per driver info
                driver_number = driver_info['DriverNumber']
                driver_name = driver_info['DriverId']
                driver_team = driver_info['TeamName']
                #driver_nationality = driver_info['CountryCode'] # dropping country attribute
                driver_race_pos = driver_info['Position']
                driver_race_time = driver_info['Time']
                driver_race_points = driver_info['Points']
                driver_grid_pos = driver_info['GridPosition']

                race_info['Driver ID'] = driver_number
                race_info['Driver Name'] = driver_name
                race_info['Driver Number and Race Name'] = "{} : {}".format(driver_number, race_name)
                race_info['Driver Team'] = driver_team
                #race_info['Driver Country'] = driver_nationality
                race_info['Position'] = driver_race_pos
                race_info['Race Time'] = driver_race_time
                race_info['Race Point'] = driver_race_points
                race_info['Race Grid Position'] = driver_grid_pos # what number they were at when starting
                print("processing racer {} for {}".format(driver_name, race_name))

                # Add final race_info data into output_data
                output_data.append(race_info)
                # if rows EXISTS (is not None) and matches number of rows, exit.
                if rows and len(output_data) == rows:
                    _write_csv(output_data, filename)
                    return # EXIT IF the function reaches the specific number of rows

    _write_csv(output_data, filename) # write data to csv after all races

# csv file

def _write_csv(output_data, filename):
    fieldnames = output_data[0].keys()
    # Open the file in write mode
    with open(filename, mode='w', newline='') as file:
        # Create a DictWriter object
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        # Write the header
        writer.writeheader()
        # Write the rows
        writer.writerows(output_data)

# entry point

if __name__ == '__main__':
    aparser = argparse.ArgumentParser(
        description='Generate csv file for 2024 F1 season results')

    # filename handling, default filename will be f1_2024.csv
    aparser.add_argument(
        '--filename',
        default='weatherIncluded3.csv',
        required=False,
        help='filename to produce')

    # rows handling
    aparser.add_argument(
        '--rows',
        default=None,
        type=int,
        required=False,
        help='only generate data for number of rows')
    args = aparser.parse_args()
    get_dataset(args.filename, rows=args.rows)
    
# How to run the program

# pip or pip3 install pandas
# pip or pip3 install fastf1  
# python3 data_collect.py --filename yourfilename.csv --rows 10(or any number) (Also can be executed without filename or rows too)
