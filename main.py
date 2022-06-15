# Copyright 2022 Paul W. Graham

import json
import os

import requests
import flask
from flask import Flask
from flask_gopher import GopherExtension, GopherRequestHandler

app = Flask(__name__)
gopher = GopherExtension(app)

API_KEY = os.environ['WEATHER_API_KEY']
DOMAIN = os.environ['WEATHER_DOMAIN']
LOCAL_IP = os.environ['WEATHER_LOCAL_IP']
LOCAL_PORT = os.environ['WEATHER_LOCAL_PORT']

WEATHER_ENDPOINT = "http://api.weatherapi.com/v1/forecast.json?key={}&q={}&days=10&aqi=yes&alerts=no"

@app.route("/")
def index():
    menu = []
    menu.append(gopher.menu.info("WEATHER"))
    menu.append(gopher.menu.info(" "))
    menu.append(gopher.menu.query('Search Weather', selector = "/weather", host = DOMAIN))

    return gopher.render_menu(*menu)

@app.route("/weather")
def weather(search_term = None):
    if search_term is None:
        if not flask.request.environ['SEARCH_TEXT']:
            raise Exception()
        else :
            search_term = flask.request.environ['SEARCH_TEXT']

    menu = []
    response = requests.get(WEATHER_ENDPOINT.format(API_KEY, search_term))
    if response.status_code != 200:
        pass
    response_json = json.loads(response.text)
    epa_index = {
        1 : 'Good',
        2 : 'Moderate',
        3 : 'Unhealthy For Sensitive Group',
        4 : 'Unhealthy',
        5 : 'Very Unhealthy',
        6 : 'Hazardous'
    }
    uk_defra_index = {
        1 : ('Low','0-11'),
        2 : ('Low','12-23'),
        3 : ('Low','24-35'),
        4 : ('Moderate','36-41'),
        5 : ('Moderate','42-47'),
        6 : ('Moderate','48-53'),
        7 : ('High','54-58'),
        8 : ('High','59-64'),
        9 : ('High','65-70'),
        10 : ('Very High','71 or more')
    }

    menu.append(gopher.menu.info("LOCATION"))
    menu.append(gopher.menu.info(" "))
    menu.append(gopher.menu.info(response_json['location']['name']))
    menu.append(gopher.menu.info(response_json['location']['region']))
    menu.append(gopher.menu.info(response_json['location']['country']))
    menu.append(gopher.menu.info(f"Lat. {response_json['location']['lat']}"))
    menu.append(gopher.menu.info(f"Long. {response_json['location']['lon']}"))
    menu.append(gopher.menu.info(" "))
    menu.append(gopher.menu.info("CURRENT WEATHER"))
    menu.append(gopher.menu.info(" "))
    menu.append(gopher.menu.info(f"Condition: {response_json['current']['condition']['text']}"))
    menu.append(gopher.menu.info(f"Temp. (f): {response_json['current']['temp_f']}"))
    menu.append(gopher.menu.info(f"Temp. (c): {response_json['current']['temp_c']}"))
    menu.append(gopher.menu.info(f"Temp. Feels Like (f): {response_json['current']['feelslike_f']}"))
    menu.append(gopher.menu.info(f"Temp. Feels Like (c): {response_json['current']['feelslike_c']}"))
    menu.append(gopher.menu.info(f"Humidity (%): {response_json['current']['humidity']}"))
    menu.append(gopher.menu.info(f"Cloud Cover (%): {response_json['current']['cloud']}"))
    menu.append(gopher.menu.info(f"Precipitation (in): {response_json['current']['precip_in']}"))
    menu.append(gopher.menu.info(f"Precipitation (mm): {response_json['current']['precip_mm']}"))
    menu.append(gopher.menu.info(f"Wind Direction: {response_json['current']['wind_dir']}"))
    menu.append(gopher.menu.info(f"Wind (MPH): {response_json['current']['wind_mph']}"))
    menu.append(gopher.menu.info(f"Wind (KPH): {response_json['current']['wind_kph']}"))
    menu.append(gopher.menu.info(f"Wind Gusts (MPH): {response_json['current']['gust_mph']}"))
    menu.append(gopher.menu.info(f"Wind Gusts (KPH): {response_json['current']['gust_kph']}"))
    menu.append(gopher.menu.info(f"Air Pressure (in): {response_json['current']['pressure_in']}"))
    menu.append(gopher.menu.info(f"Air Pressure (mb): {response_json['current']['pressure_mb']}"))
    menu.append(gopher.menu.info(f"Visibility (mi): {response_json['current']['vis_miles']}"))
    menu.append(gopher.menu.info(f"Visibility (km): {response_json['current']['vis_km']}"))
    menu.append(gopher.menu.info(f"UV Index: {response_json['current']['uv']}"))
    menu.append(gopher.menu.info(f"Last Updated: {response_json['current']['last_updated']}"))
    menu.append(gopher.menu.info(" "))
    menu.append(gopher.menu.info("CURRENT AIR QUALITY"))
    menu.append(gopher.menu.info(" "))
    menu.append(gopher.menu.info(f"Carbon Monoxide (μg/m3): {response_json['current']['air_quality']['co']}"))
    menu.append(gopher.menu.info(f"Ozone (μg/m3): {response_json['current']['air_quality']['o3']}"))
    menu.append(gopher.menu.info(f"Nitrogen dioxide (μg/m3): {response_json['current']['air_quality']['no2']}"))
    menu.append(gopher.menu.info(f"Sulphur dioxide (μg/m3): {response_json['current']['air_quality']['so2']}"))
    menu.append(gopher.menu.info(f"PM2.5 (μg/m3): {response_json['current']['air_quality']['pm2_5']}"))
    menu.append(gopher.menu.info(f"PM10 (μg/m3): {response_json['current']['air_quality']['pm10']}"))
    menu.append(gopher.menu.info(f"EPA Index: {epa_index[response_json['current']['air_quality']['us-epa-index']]}"))
    menu.append(gopher.menu.info("UK Defra Index"))
    menu.append(gopher.menu.info(f"Band: {uk_defra_index[response_json['current']['air_quality']['gb-defra-index']][0]}"))
    menu.append(gopher.menu.info(f"µgm-3: {uk_defra_index[response_json['current']['air_quality']['gb-defra-index']][1]}"))
    menu.append(gopher.menu.info(f"Last Updated: {response_json['current']['last_updated']}"))
    menu.append(gopher.menu.info(" "))
    menu.append(gopher.menu.info("FORECAST"))
    menu.append(gopher.menu.info(" "))
    for day in response_json['forecast']['forecastday']:
        menu.append(gopher.menu.info(f"Date: {day['date']}"))
        menu.append(gopher.menu.info(f"Condition: {day['day']['condition']['text']}"))
        menu.append(gopher.menu.info(f"Chance of Rain (%): {day['day']['daily_chance_of_rain']}"))
        menu.append(gopher.menu.info(f"Chance of Snow (%): {day['day']['daily_chance_of_snow']}"))
        menu.append(gopher.menu.info(f"Avg. Temp. (f): {day['day']['avgtemp_f']}"))
        menu.append(gopher.menu.info(f"Avg. Temp. (c): {day['day']['avgtemp_c']}"))
        menu.append(gopher.menu.info(f"Max. Temp. (f): {day['day']['maxtemp_f']}"))
        menu.append(gopher.menu.info(f"Max. Temp. (c): {day['day']['maxtemp_c']}"))
        menu.append(gopher.menu.info(f"Min. Temp. (f): {day['day']['mintemp_f']}"))
        menu.append(gopher.menu.info(f"Min. Temp. (c): {day['day']['mintemp_c']}"))
        menu.append(gopher.menu.info(f"Max. Wind (MPH): {day['day']['maxwind_mph']}"))
        menu.append(gopher.menu.info(f"Max. Wind (KPH): {day['day']['maxwind_kph']}"))
        menu.append(gopher.menu.info(f"Total Precipitation (in): {day['day']['totalprecip_in']}"))
        menu.append(gopher.menu.info(f"Total Precipitation (mm): {day['day']['totalprecip_mm']}"))
        menu.append(gopher.menu.info(f"Avg. Visibility (mi): {day['day']['avgvis_miles']}"))
        menu.append(gopher.menu.info(f"Avg. Visibility (km): {day['day']['avgvis_km']}"))
        menu.append(gopher.menu.info(f"Avg. Humidity: {day['day']['avghumidity']}"))
        menu.append(gopher.menu.info(f"UV Index: {day['day']['uv']}"))
        menu.append(gopher.menu.info(f"Sunrise: {day['astro']['sunrise']}"))
        menu.append(gopher.menu.info(f"Sunset: {day['astro']['sunset']}"))
        menu.append(gopher.menu.info(f"Moonrise: {day['astro']['moonrise']}"))
        menu.append(gopher.menu.info(f"Moonset: {day['astro']['moonset']}"))
        menu.append(gopher.menu.info(f"Moon Phase: {day['astro']['moon_phase']}"))
        menu.append(gopher.menu.info(f"Moon Illumination (%): {day['astro']['moon_illumination']}"))
        menu.append(gopher.menu.info(" "))
    return gopher.render_menu(*menu)

@app.errorhandler(500)
@app.errorhandler(404)
def error(e):
    menu = [
        gopher.menu.info('Oops, it appears this gopher hole has collapsed!'),
        ]
    return gopher.render_menu(*menu)

if __name__ == '__main__':
   app.run(LOCAL_IP, LOCAL_PORT, request_handler=GopherRequestHandler, debug=False)
