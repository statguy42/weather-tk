import datetime as DT
import tkinter as tk
import urllib.request, urllib.parse, urllib.error
import json


def get_weather(parent, inp):
    params = {
        'q':inp,
        'appid': parent.API_KEY,
        'units': parent.UNIT
    }
    response = httpreq(parent, parent.WEATHER_SERVICE_URL, params)
    write_output(parent, response)


def httpreq(parent, url, params=None):
    if params is not None:
        url = url + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url) as req:
            return json.loads(req.read().decode())
            
    except urllib.error.HTTPError as err:
        parent.status_label.configure(text=err)


def write_output(parent,response):
    parent.current_weather.pack()
    parent.status_label.configure(text=f"Updated at {DT.datetime.now().strftime('%I:%M:%S %p')}")
    parent.current_weather.city_lab.configure(text=f"City: {response['name']}, {response['sys']['country']}")
    parent.current_weather.temp_lab.configure(text=f"Temp: {response['main']['temp']}°C")
    parent.current_weather.feels_lab.configure(text=f"Feels like: {response['main']['feels_like']}°C")
    parent.current_weather.wind_speed_lab.configure(text=f"Wind speed: {response['wind']['speed']} m/s")
    parent.current_weather.desc_lab.configure(text=response['weather'][0]['description'].capitalize())
    parent.current_weather.humid_lab.configure(text=f"Humidty: {response['main']['humidity']}%")
    parent.current_weather.clouds_lab.configure(text=f"Cloudiness: {response['clouds']['all']}%")
    parent.current_weather.sunrise_lab.configure(text=f"Sunrise: {DT.datetime.utcfromtimestamp(response['sys']['sunrise']+response['timezone']).strftime('%I:%M %p')}")
    parent.current_weather.sunset_lab.configure(text=f"Sunset: {DT.datetime.utcfromtimestamp(response['sys']['sunset']+response['timezone']).strftime('%I:%M %p')}")

