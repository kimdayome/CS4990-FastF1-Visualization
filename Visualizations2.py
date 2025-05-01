# Assignment #2, 
# Name: Group Assignment #2
# Due Date: Monday, October 7 2024

# Import necessary libraries
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Functions for visualizations 1 and 2:

def get_top5_drivers(df):
  "Given the dataframe, calculates and returns a series of the top 5 F1 drivers from 2018-2024."

  # Group the data by driver name and take sum from individual's total point
  total_points = df.groupby('Driver Name')['Race Point'].sum().reset_index()

  # Sort drivers by total points (top 5)
  top5_drivers = total_points.sort_values(by='Race Point', ascending=False).head(5).reset_index(drop=True) 

  return top5_drivers['Driver Name'] 

def normalizeWeather(weatherDf):
  "Normalizes each entry for the numerical weather attributes."

  columns = ['Air Temperature', 'Relative Humidity', 'Air Pressure', 'Track Temperature', 'Wind Speed']
  for column in columns:
    weatherDf[column] = (weatherDf[column] - weatherDf[column].min()) / (weatherDf[column].max() - weatherDf[column].min())

  return weatherDf


def get_race_positions(driver_name, df):
  "Given the driver names, returns their race positions from 2018-2024."

  driver_data = df[df['Driver Name'] == driver_name]
  return driver_data['Position'], driver_data['Race Name']


def get_weatherConditions(raceNames, df):
  "Given a series of race names, returns the normalized numerical weather conditions for the race."

  race_data = df[df['Race Name'] == raceNames]
  # For each race, the weather is the average temperature for the entirety of the race. 
  # Since rows for each driver in the race contain the same weather conditions, only take the first value.
  return race_data['Air Temperature'].iloc[0], race_data['Relative Humidity'].iloc[0], race_data['Air Pressure'].iloc[0], race_data['Track Temperature'].iloc[0], race_data['Wind Speed'].iloc[0]

def saveWeatherConditions(top5_drivers, weatherData):
  positions = []
  race_names = []
  # Normalize the position to map appropriately to normalized weather attributes.
  #weatherData['Position'] = (weatherData['Position'] - weatherData['Position'].min()) / (weatherData['Position'].max() - weatherData['Position'].min())
  for driver in top5_drivers:
    airTemp = []
    humidity = []
    airPress = []
    trackTemp = []
    windSpeed = []
    positions, race_names = get_race_positions(driver, weatherData)
    for race in race_names:
      aTemp, hum, press, tTemp, wSpeed = get_weatherConditions(race, weatherData)
      airTemp.append(aTemp)
      humidity.append(hum)
      airPress.append(press)
      trackTemp.append(tTemp)
      windSpeed.append(wSpeed)
    return airTemp, humidity, airPress, trackTemp, windSpeed

def plotWeatherCondition(top5_drivers, condition, conditionName, weatherData):
    positions = []
    race_names = []
    plt.figure(figsize=(25,10))

    # Plot the top 5 drivers' performance
    for driver in top5_drivers:
      positions, race_names = get_race_positions(driver, weatherData)
      plt.plot(race_names, positions, linestyle = ":")
    plt.plot(race_names, condition, color = "black", label = condition)

    # Add the selected weather condition.
    plt.title(conditionName + " vs. Race Positions for Top 5 Racers")
    plt.xlabel("Race Name")
    plt.ylabel("Normalized Weather Conditions & Positions")
    plt.yticks(range(0, 1), map(str, range(0, 1))) #1-20, 문자열로 변환
    plt.legend(top5_drivers, bbox_to_anchor=(1,1))
    plt.gca().invert_yaxis()
    plt.xticks(rotation='vertical') # 글자 수직정렬
    plt.show()
    
    

def visualization12():
    # Load the CSV data file
    f1_data = pd.read_csv("weatherIncluded3.csv") # i will update the csv file (the one with 2018-2024)
    f1_data = normalizeWeather(f1_data)


    # Get the top 5 drivers dynamically based on points
    top5_drivers = get_top5_drivers(f1_data)
    positions = []
    race_names = []

    # Plot setup
    plt.figure(figsize=(30,6))
    plt.title("Top 5 F1 Drivers Performance (2020-2024)")

    # Make the first plotting with the top 5 drivers and their positions from 2018-2024
    for driver in top5_drivers:
        positions, race_names = get_race_positions(driver, f1_data)
        plt.scatter(race_names, positions)

    # Plot specifications
    plt.title("Top 5 Racer's Performance 2018-2024")
    plt.yticks(range(1, 21), map(str, range(1, 21))) 
    plt.gca().invert_yaxis()
    plt.grid()
    plt.ylabel("Positions") 
    plt.xlabel("Race Name") 
    plt.xticks(rotation='vertical') 
    plt.legend(top5_drivers, bbox_to_anchor=(1,1))
    plt.show()

    
    weatherData = pd.read_csv("weatherIncluded3.csv")
    normalizeWeather(weatherData)
    # Normalize position to plot values
    weatherData['Position'] = (weatherData['Position'] - weatherData['Position'].min()) / (weatherData['Position'].max() - weatherData['Position'].min())

    airTemp = []
    humidity = []
    airPress = []
    trackTemp = []
    windSpeed= []
    
    airTemp, humidity, airPress, trackTemp, windSpeed = saveWeatherConditions(top5_drivers, weatherData)
    conditionList = [airTemp, humidity, airPress, trackTemp, windSpeed]
    conditionNames = ["Air Temperature", "Relative Humidity", "Air Pressure", "Track Temperature", "Wind Speed"]

    # For each weather condition, create a plot to show how drivers perform 
    for i in range(0, len(conditionList)):
      plotWeatherCondition(top5_drivers, conditionList[i], conditionNames[i], weatherData)
    
    # Create a final plot with all weather conditions and driver performance
    plt.figure(figsize=(25,6))
    for driver in top5_drivers:
      positions, race_names = get_race_positions(driver, weatherData)
      plt.plot(race_names, positions, linestyle = ":")
    plt.title("Weather Conditions vs. Race Positions for Top 5 Racers")
    plt.xlabel("Race Name")
    plt.ylabel("Normalized Weather Conditions & Positions")
    plt.plot(race_names, airTemp, label = "Air Temperature")
    plt.plot(race_names, humidity, label = "Humidity")
    plt.plot(race_names, airPress, label = "Air Pressure")
    plt.plot(race_names, trackTemp, label = "Track Temperature")
    plt.plot(race_names, windSpeed, label = "Wind Speed")
    plt.legend()
    plt.xticks(rotation='vertical')
    plt.show()

visualization12()

# Functions for visualization 3:
def load_data():

    return pd.read_csv("weatherIncluded3.csv")

#Prepare the data for visualization
def prepare_data(df):
    # Convert the 'Race Date' to datetime for plt
    df['Race Date'] = pd.to_datetime(df['Race Date'])

    # Sort the dataframe by 'Race Date'
    df = df.sort_values(by='Race Date')

    return df

# Function to calculate total points for each driver and get the top 5 (like what we did)
def get_top5_drivers(df):
    total_points = df.groupby('Driver Name')['Race Point'].sum().reset_index()
    top5_drivers = total_points.sort_values(by='Race Point', ascending=False).head(5)
    return top5_drivers['Driver Name']

#Plot performance of a single driver over time
def plot_driver_performance(df, driver_name):
    driver_data = df[df['Driver Name'] == driver_name]

    plt.figure(figsize=(10, 6))
    plt.plot(driver_data['Race Date'], driver_data['Position'], marker='o', label=driver_name)

    plt.gca().invert_yaxis()  # Invert the y-axis - 1st position at the top
    plt.title(f"{driver_name}'s Performance Over Time (2018-2024)")
    plt.xlabel("Race Date")
    plt.ylabel("Race Position")
    plt.xticks(rotation=45)
    plt.yticks(range(1, 21), map(str, range(1, 21)))  # y goes from 1-20
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    # Show the plot
    plt.show()

def visualization3():
  # Load the dataset
  f1_data = load_data()

  # Prepare the data (sort by Race Date)
  f1_data = prepare_data(f1_data)

  # Get the top 5 drivers based on points
  top5_drivers = get_top5_drivers(f1_data)

  # Plot each driver separately
  for driver in top5_drivers:
      plot_driver_performance(f1_data, driver)

visualization3()

#Plot performance of multiple drivers over time
def plot_top5_performance(df, top5_drivers):
    plt.figure(figsize=(12, 7))

    # Loop through each driver and plot their performance
    for driver_name in top5_drivers:
        driver_data = df[df['Driver Name'] == driver_name]
        plt.plot(driver_data['Race Date'], driver_data['Position'], marker='o', label=driver_name)

    plt.gca().invert_yaxis()  # Invert the y-axis - 1st position at the top
    plt.title("Top 5 Drivers' Performance Over Time (2018-2024)")
    plt.xlabel("Race Date")
    plt.ylabel("Race Position")
    plt.xticks(rotation=45)
    plt.yticks(range(1, 21), map(str, range(1, 21)))  # y goes from 1-20
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    # Show the plot
    plt.show()

def visualization3Complete():
   # Load the dataset
    f1_data = load_data()

    # Prepare the data (sort by Race Date)
    f1_data = prepare_data(f1_data)

    # Get the top 5 drivers based on points
    top5_drivers = get_top5_drivers(f1_data)

    # Plot performance of top 5 drivers over time
    plot_top5_performance(f1_data, top5_drivers)

visualization3Complete()

# Functions for visualization 4: 
#Prepare the data for visualization (convert date and sort)
#because this will be time-based (formatted and ordred for time-based visualization)
def prepare_data(df):
    df['Race Date'] = pd.to_datetime(df['Race Date'])
    df = df.sort_values(by='Race Date')
    #import pdb; pdb.set_trace()
    return df

#Separate races into rainy and dry based on weather
def categorize_weather(df):
    rainy_races = df[df['Rainfall'] == True]  # RAINED
    dry_races = df[df['Rainfall'] == False]   # DIDNT RAIN
    return rainy_races, dry_races

#Calculate average positions in rainy vs dry races for top 5 drivers (used the previous formula-summing up and taking 5 head)
def calculate_avg_position(df, driver_name):
    return df[df['Driver Name'] == driver_name]['Position'].mean()

def plot_rainy_vs_dry(df, top5_drivers):
    rainy_races, dry_races = categorize_weather(df)

    rainy_positions = []
    dry_positions = []

    #Calculate average position in rainy and dry conditions for each driver
    for driver in top5_drivers:
        rainy_avg = calculate_avg_position(rainy_races, driver)
        dry_avg = calculate_avg_position(dry_races, driver)
        rainy_positions.append(rainy_avg)
        dry_positions.append(dry_avg)

    #horizontal bar chart
    df_plot = pd.DataFrame({
        'Driver': top5_drivers,
        'Rainy': rainy_positions,
        'Dry': dry_positions
    }).set_index('Driver')

    #Plot the data
    df_plot.plot(kind='barh', figsize=(10,6))

    plt.title("Top 5 Drivers: Rainy vs Dry Races Average Positions (2018-2024)")
    plt.xlabel("Average Position")
    plt.ylabel("Drivers")
    plt.grid(True)
    plt.show()

def visualization4():
    # Load the dataset
    f1_data = load_data()

    # Prepare the data
    f1_data = prepare_data(f1_data)

    # Get the top 5 drivers based on points
    top5_drivers = get_top5_drivers(f1_data)

    # Plot Rainy vs Dry performance comparison
    plot_rainy_vs_dry(f1_data, top5_drivers)
visualization4()
