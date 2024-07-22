#!/usr/bin/env python
# coding: utf-8

# In[1]:




from bokeh.embed import file_html
import requests
import pandas as pd
#from bokeh.plotting import output_file, show
from bokeh.models import Select, Div, Button, ColumnDataSource, HTMLTemplateFormatter
from bokeh.models.widgets import DateRangePicker, DataTable, TableColumn, Div
from bokeh.layouts import column
from bokeh.io import show, curdoc
import plotly.express as px
import plotly.graph_objects as go


# In[2]:


# List of cities
cities = ['Athens', 'Corfu', 'Crete', 'Zante', 'Mykonos']
def get_airport_codes(city):
    api_url = 'https://api.api-ninjas.com/v1/airports?city={}'.format(city)
    headers = {'X-Api-Key': 'nrc3S/XZWbfao3LeySY9hg==I1u1i9JSOP6NSPFw'}
 
    response = requests.get(api_url, headers=headers)
    if response.status_code == requests.codes.ok:
        airport_data = response.json()
        airport_dict = {}  # Initialize an empty dictionary to store airport codes and names
        for airport in airport_data:
            airport_code = airport.get('iata')
            if airport_code:  # Check if airport code is not empty
                airport_name = airport.get('name')
                airport_dict[airport_code] = airport_name  # Add airport code and name to the dictionary
        return list(airport_dict.keys())  # Return a list of airport codes
    else:
        print("Error:", response.status_code, response.text)
 
 
airport_codes = get_airport_codes(cities[0])


# In[3]:


#city_select = Select(title="City:", value="Athens", options=list(airport_codes.keys()))


# In[4]:


# pip install amadeus


# In[5]:


def get_access_token():
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials",
        "client_id": 'gAJOLRiyFCjYVuCEIspShbBroNVLSgpw',
        "client_secret": 'ZDHiCX0h0NYIBm0B'
    }
 
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        # Extract the access token from the response JSON
        access_token = response.json()['access_token']
        print("Access Token:", access_token)
    else:
        # Print error message if the request was not successful
        print("Failed to obtain access token:", response.status_code, response.text)
    return access_token

# Get access token
access_token = get_access_token()


# In[6]:


def get_flight_details(access_token, originLocationCode, destinationLocationCode, departureDate):
    url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    headers = {
        "Authorization": f'Bearer {access_token}',
        "Content-Type": "application/json"
    }
    params = {
        "originLocationCode": originLocationCode,
        "destinationLocationCode": destinationLocationCode,
        "departureDate": departureDate,
        "adults": 1,
        "max": 1
    }
 
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to get flight details:", response.status_code, response.text)
        return None


# In[7]:


city_select = Select(title="City:", value=cities[0], options=cities)
initial_airport_codes = get_airport_codes(cities[0])
airport_select = Select(title="Airport:", value=initial_airport_codes[0] if initial_airport_codes else '', options=initial_airport_codes)
print(airport_select.options[2])
print(city_select.options)


# In[8]:


originLocationCode = 'ATH'
destinationLocationCode = 'JMK'
departureDate = '2024-06-13'
flight_offers_response = get_flight_details(access_token, originLocationCode, destinationLocationCode, departureDate)


# In[9]:


if flight_offers_response:
    # Extract flight details and create DataFrame
    flight_data = []
    for flight in flight_offers_response['data']:
        itinerary = flight['itineraries'][0]
        segment = itinerary['segments'][0]
        departure_airport = segment['departure']['iataCode']
        arrival_airport = segment['arrival']['iataCode']
        departure_time = segment['departure']['at'][-8:-3]
        arrival_time = segment['arrival']['at'][-8:-3]
        # Convert string time to hours and minutes
        departure_hour, departure_minute = map(int, departure_time.split(':'))
        arrival_hour, arrival_minute = map(int, arrival_time.split(':'))
 
        # Calculate duration in minutes
        duration_minutes = (arrival_hour * 60 + arrival_minute) - (departure_hour * 60 + departure_minute)
 
        # Convert duration to hours and minutes
        duration_hours = duration_minutes // 60
        duration_minutes = duration_minutes % 60
 
        duration_str = f"{duration_hours:02d}:{duration_minutes:02d}"
        price = float(flight['price']['total'])
        currency = flight['price']['currency']
        price_with_currency = f"{price} {currency}"
 
        # Combine price with currency
        flight_data.append([departure_airport, arrival_airport, departure_time, arrival_time, duration_str, price_with_currency])
 
    # Creating DataFrame
    df = pd.DataFrame(flight_data, columns=['DepartureAirport', 'ArrivalAirport', 'DepartureTime', 'ArrivalTime', 'Duration(hours)', 'PriceWithCurrency'])
    # display(df)


# In[10]:


flight_offers_response = get_flight_details(access_token, originLocationCode, destinationLocationCode, departureDate)
def process_flight_data(flight_offers_response):
    if flight_offers_response:
        # Extract flight details and create DataFrame
        flight_data = []
        for flight in flight_offers_response['data']:
            itinerary = flight['itineraries'][0]
            segment = itinerary['segments'][0]
            departure_airport = segment['departure']['iataCode']
            arrival_airport = segment['arrival']['iataCode']
            departure_time = segment['departure']['at'][-8:-3]
            arrival_time = segment['arrival']['at'][-8:-3]
 
            # Convert string time to hours and minutes
            departure_hour, departure_minute = map(int, departure_time.split(':'))
            arrival_hour, arrival_minute = map(int, arrival_time.split(':'))
 
            # Calculate duration in minutes
            duration_minutes = (arrival_hour * 60 + arrival_minute) - (departure_hour * 60 + departure_minute)
 
            # Convert duration to hours and minutes
            duration_hours = duration_minutes // 60
            duration_minutes = duration_minutes % 60
 
            duration_str = f"{duration_hours:02d}:{duration_minutes:02d}"
 
            price = float(flight['price']['total'])
            currency = flight['price']['currency']
            price_with_currency = f"{price} {currency}"
 
            # Combine price with currency
            flight_data.append([departure_airport, arrival_airport, departure_time, arrival_time, duration_str, price_with_currency])
 
        # Creating DataFrame
        df = pd.DataFrame(flight_data, columns=['DepartureAirport', 'ArrivalAirport', 'DepartureTime', 'ArrivalTime', 'Duration(hours)', 'PriceWithCurrency'])
        return df
    else:
        print("No flight offers data available.")
        return None


# In[11]:


df = process_flight_data(flight_offers_response)


# In[12]:


# Convert the DataFrame to a ColumnDataSource
source = ColumnDataSource(df)

# Define the columns for the DataTable
columns = [
    TableColumn(field='DepartureAirport', title='Departure Airport'),
    TableColumn(field='ArrivalAirport', title='Arrival Airport'),
    TableColumn(field='DepartureTime', title='Departure Time'),
    TableColumn(field='ArrivalTime', title='Arrival Time'),
    TableColumn(field='Duration(hours)', title='Duration (hours)'),
    TableColumn(field='PriceWithCurrency', title='Price')
]

# Create the DataTable
data_table = DataTable(source=source, columns=columns, width=800, height=280)

# Your existing code to create other widgets, e.g., city_select, airport_select, etc.

# Layout the widgets with city input, button, and result div
#inputs = column(city_select, airport_select, date_range_picker, update_button)
#header = column(logo_image, title_div)
#results = column(recommended_dates_temp, recommended_dates_humidity, recommended_dates_wind_speed, result_div, data_table)
#layout = column(header, inputs, results, sizing_mode='stretch_both', css_classes=['app-layout'])

# Display the plot
#show(layout)


# In[13]:


import plotly.express as px
import plotly.graph_objects as go
 
googleplaces_key = 'AIzaSyBj6rZ-ixkOR_Ht3yFDMWv_KO2aFKJBk8c'
 
api_key = googleplaces_key
 
 
def fetch_top_bars(city, category='bar'):
    ''' Function to request the top 10 bars from Google Places API in a given city.
    Input = city name and category type (default = 'bar').
    Output = return a dataframe with top 10 bar names, longitude and latitude in the city.
    '''
    url = 'https://maps.googleapis.com/maps/api/place/textsearch/json'
    params = {
        'query': f'top {category} in {city}',
        'key': api_key
    }
    response = requests.get(url, params=params)
    # Error handling to make sure API fetches correct information
    if response.status_code != 200:
        print(f"Failed to fetch data for {city}: {response.status_code} - {response.text}")
        return pd.DataFrame()
    # Convert data to JSON format
    data = response.json()
    if 'results' not in data:
        print(f"No results found in the response for {city}")
        return pd.DataFrame()
    results = data['results']
    # Extract required information from API data - longitude, latitude and name of bar
    extracted_data = []
    for result in results:
        name = result.get('name', 'N/A')
        location = result.get('geometry', {}).get('location', {})
        latitude = location.get('lat')
        longitude = location.get('lng')
        extracted_data.append({
            'city': city,
            'name': name,
            'latitude': latitude,
            'longitude': longitude,
            'type': category
        })
    return pd.DataFrame(extracted_data)
 
 
def fetch_airports(city):
    ''' Function to fetch airport data for the cities using Google Places API.
    Input = city
    Ouput = return a data frame displaying airport name, longitude and latitude
    Error handling included to deal with API errors
    '''
    url = 'https://maps.googleapis.com/maps/api/place/textsearch/json'
    params = {
        'query': f'airports in {city}',
        'key': api_key
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Failed to fetch data for {city}: {response.status_code} - {response.text}")
        return pd.DataFrame()
    data = response.json()
    if 'results' not in data:
        print(f"No results found in the response for {city}")
        return pd.DataFrame()
    results = data['results']
    # Extract required information
    extracted_data = []
    for result in results:
        name = result.get('name', 'N/A')
        location = result.get('geometry', {}).get('location', {})
        latitude = location.get('lat')
        longitude = location.get('lng')
        extracted_data.append({
            'city': city,
            'name': name,
            'latitude': latitude,
            'longitude': longitude,
            'type': 'airport'
        })
    return pd.DataFrame(extracted_data)
 
# List of cities with location names
cities = [
    'Athens, Greece',
    'Corfu Island, Greece',
    'Heraklion, Crete, Greece',
    'Zakynthos, Ionian Islands, Greece',
    'Mykonos, Cyclades, Greece'
]
 
# Initialize an empty DataFrame to store the data
all_data_df = pd.DataFrame()
 
# Loop through each city and fetch the top bars and airports
for city in cities:
    city_bars_df = fetch_top_bars(city)
    city_airports_df = fetch_airports(city)
    # Combine the bars and airports data
    city_combined_df = pd.concat([city_bars_df, city_airports_df], ignore_index=True)
    all_data_df = pd.concat([all_data_df, city_combined_df], ignore_index=True)
 
 
# Check if the DataFrame is empty - error handling
if all_data_df.empty:
    print("No data found. Please check the API key and the cities list.")
else:
    # Assign colors based on location types
    type_colors = {'airport': 'black', 'bar': 'red'}
 
    # Use a color palette for different cities
    city_palette = px.colors.qualitative.Plotly
    city_colors = {city: city_palette[i % len(city_palette)] for i, city in enumerate(all_data_df['city'].unique())}
 
    # Combine the type and city colors
    all_data_df['marker_color'] = all_data_df.apply(lambda row: type_colors[row['type']] if row['type'] == 'airport' else city_colors[row['city']], axis=1)
 
    # Plot the data on a map using Plotly
    fig = go.Figure()
 
    for city in all_data_df['city'].unique():
        city_data = all_data_df[all_data_df['city'] == city]
        fig.add_trace(go.Scattermapbox(
            lat=city_data['latitude'],
            lon=city_data['longitude'],
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=10,
                color=city_data['marker_color']
            ),
            text=city_data['name'],
            hoverinfo='text',
            name=city
        ))
 
    fig.update_layout(
        mapbox_style='open-street-map',
        mapbox_zoom=5,
        mapbox_center={"lat": all_data_df['latitude'].mean(), "lon": all_data_df['longitude'].mean()},
        margin={"r":0,"t":0,"l":0,"b":0},
        legend=dict(
            title='View bars and aiports',
            itemsizing='constant'
        )
    )
 
    fig.show()

# Convert the Plotly figure to an HTML string
plotly_html = fig.to_html(full_html=False)

# Create a Div to hold the Plotly plot
plotly_div = Div(text=plotly_html, width=800, height=600)


# In[14]:


# WeatherAPI key
weather_key = "11da115d9a8d4556bd993522240506"

# Function to fetch weather data for the next 10 days for a single city
def fetch_10_day_forecast(city, api_key):
    base_url = 'http://api.weatherapi.com/v1'
    url = f"{base_url}/forecast.json?key={api_key}&q={city}&days=10"
    response = requests.get(url)
    data = response.json()
    
    # Check if the response contains the necessary forecast data
    if 'forecast' in data and 'forecastday' in data['forecast']:
        forecast_data = data['forecast']['forecastday']
        extracted_data = []
        
        for day in forecast_data:
            date = day['date']
            temp = day['day']['avgtemp_c']
            humidity = day['day']['avghumidity']
            cloudiness = day['day']['condition']['text']
            wind_speed = day['day']['maxwind_kph']
            
            extracted_data.append({
                'city': city,
                'date': date,
                'temp': temp,
                'humidity': humidity,
                'condition': cloudiness,
                'wind_speed': wind_speed
            })
        
        return pd.DataFrame(extracted_data)
    else:
        print(f"No forecast data available for {city}")
        return pd.DataFrame()

# Function to find the best 7 consecutive days based on specific filters
def find_best_7_days(forecast_df, criteria='temp'):
    best_city = None
    best_start_date = None
    best_average = float('-inf') if criteria == 'temp' else float('inf')
    
    for city in forecast_df['city'].unique():
        city_df = forecast_df[forecast_df['city'] == city]
        
        # Ensure the dates are sorted
        city_df = city_df.sort_values(by='date')
        
        # Iterate over possible 7-day windows
        for i in range(len(city_df) - 6):
            window = city_df.iloc[i:i+7]
            
            if criteria == 'temp':
                average = window['temp'].mean()
                if average > best_average:
                    best_average = average
                    best_city = city
                    best_start_date = window.iloc[0]['date']
            elif criteria == 'humidity':
                average = window['humidity'].mean()
                if average < best_average:
                    best_average = average
                    best_city = city
                    best_start_date = window.iloc[0]['date']
            elif criteria == 'wind_speed':
                average = window['wind_speed'].mean()
                if average < best_average:
                    best_average = average
                    best_city = city
                    best_start_date = window.iloc[0]['date']
    
    return best_city, best_start_date, best_average

# Function to get airport codes based on city -- already run in cell above(?)
'''def get_airport_codes(city):
    api_url = f'https://api.api-ninjas.com/v1/airports?city={city}'
    headers = {'X-Api-Key': 'nrc3S/XZWbfao3LeySY9hg==I1u1i9JSOP6NSPFw'}
 
    response = requests.get(api_url, headers=headers)
    if response.status_code == requests.codes.ok:
        airport_data = response.json()
        airport_dict = {}
        for airport in airport_data:
            airport_code = airport.get('iata')
            if airport_code:
                airport_name = airport.get('name')
                airport_dict[airport_code] = airport_name
        return list(airport_dict.keys())
    else:
        print("Error:", response.status_code, response.text)
        return []
'''
# List of cities
cities = ['Athens', 'Corfu', 'Crete', 'Zante', 'Mykonos']

# API key
api_key = weather_key

# Initialize an empty DataFrame to store the combined forecast data
all_forecast_df = pd.DataFrame()

# Loop through each city and fetch the forecast data
for city in cities:
    city_forecast_df = fetch_10_day_forecast(city, api_key)
    all_forecast_df = pd.concat([all_forecast_df, city_forecast_df], ignore_index=True)

# Function to apply color based on temperature
def apply_temp_color(temp):
    if temp < 20:
        return 'mediumaquamarine'
    elif 20 <= temp < 30:
        return 'lightsalmon'
    else:
        return 'brown'

# Function to apply color based on condition
condition_mapper = {
    'Sunny': 'gold',
    'Partly cloudy': 'lightblue',
    'Cloudy': 'gray',
    'Rain': 'blue',
    'Clear': 'white'
}

def apply_condition_color(condition):
    return condition_mapper.get(condition, 'white')

# Add columns for coloring
all_forecast_df['temp_color'] = all_forecast_df['temp'].apply(apply_temp_color)
all_forecast_df['condition_color'] = all_forecast_df['condition'].apply(apply_condition_color)

# Output to a new HTML file
#output_file("index.html")

# Find the best 7 consecutive days for high temperature, low humidity, and low wind speed
best_city_temp, best_start_date_temp, best_average_temp = find_best_7_days(all_forecast_df, 'temp')
best_city_humidity, best_start_date_humidity, best_average_humidity = find_best_7_days(all_forecast_df, 'humidity')
best_city_wind_speed, best_start_date_wind_speed, best_average_wind_speed = find_best_7_days(all_forecast_df, 'wind_speed')

# Format best_average_temp, best_average_humidity, and best_average_wind_speed to 1 decimal place
best_average_temp_formatted = f"{best_average_temp:.1f}"
best_average_humidity_formatted = f"{best_average_humidity:.1f}"
best_average_wind_speed_formatted = f"{best_average_wind_speed:.1f}"

# Create a Div to show recommended dates
recommended_dates_temp = Div(text=f"<b>Best week based on high temperature:</b> {best_city_temp}, starting from {best_start_date_temp} with average temp {best_average_temp_formatted}°C.<br>",
                             width=800, height=50)

recommended_dates_humidity = Div(text=f"<b>Best week based on low humidity:</b> {best_city_humidity}, starting from {best_start_date_humidity} with average humidity {best_average_humidity_formatted}%.<br>",
                                 width=800, height=50)

recommended_dates_wind_speed = Div(text=f"<b>Best week based on low wind speed:</b> {best_city_wind_speed}, starting from {best_start_date_wind_speed} with average wind speed {best_average_wind_speed_formatted} kph.<br>",
                                  width=800, height=50)



# In[15]:


# Create Select for city input with the cities from the DataFrame
cities = all_forecast_df['city'].unique().tolist()
#city_select = Select(title="City:", value=cities[0], options=cities) ---already run in one a cell above

# Get initial airport codes ## these 2 already run ina  cell above^
#initial_airport_codes = get_airport_codes(cities[0])
#airport_select = Select(title="Airport:", value=initial_airport_codes[0] if initial_airport_codes else '', options=initial_airport_codes)



# Create a Button to update the recommended dates and table
update_button = Button(label="Discover this city", css_classes=['custom-button'])

# Create a DateRangePicker widget
date_range_picker = DateRangePicker(title="Select a date range:")

# Create a Div element for displaying the selected city and date range
result_div = Div()

# Create a DataTable to display the forecast data
columns = [
    TableColumn(field='city', title='City'),
    TableColumn(field='date', title='Date'),
    TableColumn(field='temp', title='Temperature', width=100, formatter=HTMLTemplateFormatter(template='<div style="background:<%= temp_color %>; color: black;"> <%= value %> </div>')),
    TableColumn(field='humidity', title='Humidity', width=100),
    TableColumn(field='condition', title='Condition', width=100, formatter=HTMLTemplateFormatter(template='<div style="background:<%= condition_color %>; color: black;"> <%= value %> </div>')),
    TableColumn(field='wind_speed', title='Wind Speed', width=100),
]

source = ColumnDataSource(all_forecast_df)
data_table = DataTable(source=source, columns=columns, width=800, height=280)




# In[16]:


# Logo and header
logo_image = Div(text="<img src='sunnylogo.png' style='width:100px;height:100px;'>")
title_div = Div(text="<h1 style='font-family: Cooper Black, sans-serif; font-size: 36px; color: teal;'><center>Holidays by Sunny Side Up</center></h1>",
                sizing_mode='stretch_width')


# In[17]:


# Function to handle city selection change
def update_selected_city(attr, old, new):
    # Update the airport select options based on the new city
    airport_codes = get_airport_codes(new)
    airport_select.options = airport_codes
    airport_select.value = airport_codes[0] if airport_codes else ''

    result_div.text = f"Selected city: {new}"

# Function to handle button click to update the recommended dates
def update_recommended_dates():
    selected_city = city_select.value
    start_date, end_date = date_range_picker.value_as_datetime
    
    filtered_df = all_forecast_df[(all_forecast_df['city'] == selected_city) & 
                                  (all_forecast_df['date'] >= start_date) & 
                                  (all_forecast_df['date'] <= end_date)]
    
    if not filtered_df.empty:
        avg_temp = filtered_df['temp'].mean()
        avg_humidity = filtered_df['humidity'].mean()
        result_div.text = f"Avg. temperature: {avg_temp:.2f}°C<br>Avg. humidity: {avg_humidity:.2f}%"
    else:
        result_div.text = f"No data available for {selected_city} in the selected date range."

# Function to handle date range picker change
def show_selected_date_range(attr, old, new):
    result_div.text = f"Selected city: {city_select.value}<br>Selected date range: {new[0]} to {new[1]}"





flight_source = ColumnDataSource(df)
flight_columns = [
    TableColumn(field='DepartureAirport', title='Departure Airport'),
    TableColumn(field='ArrivalAirport', title='Arrival Airport'),
    TableColumn(field='DepartureTime', title='Departure Time'),
    TableColumn(field='ArrivalTime', title='Arrival Time'),
    TableColumn(field='Duration(hours)', title='Duration (hours)'),
    TableColumn(field='PriceWithCurrency', title='Price')
]

flight_data_table = DataTable(source=flight_source, columns=flight_columns, width=800, height=280)



# In[18]:


# Attach the functions to the button click events
update_button.on_click(update_recommended_dates)
date_range_picker.on_change('value', show_selected_date_range)
originLocationCode = city_select.on_change('value', update_selected_city)

# Layout the widgets with city input, button, and result div
inputs = column(city_select, airport_select, date_range_picker, update_button)
header = column(logo_image, title_div)
results = column(recommended_dates_temp, recommended_dates_humidity, recommended_dates_wind_speed, result_div, data_table,flight_data_table)
layout = column(header, inputs, results, plotly_div, sizing_mode='stretch_both', css_classes=['app-layout'])

curdoc().add_root(layout)

# Display the plot
#show(layout)


# In[ ]:




