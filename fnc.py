import datetime as DT
import urllib.request, urllib.parse, urllib.error
import json
import io
import tkinter as tk
from PIL import Image, ImageTk


def btn_pressed(parent, inp):
    parent.after(0, parent.input.get_btn.configure, {'state':tk.DISABLED})
    current_weather = get_current_weather(parent, inp)
    coords = get_city_coords(current_weather)
    forecast_weather = get_forecast_weather(parent, coords)
    write_current_output(parent, current_weather)
    write_forecast_daily_output(parent, forecast_weather['daily'], forecast_weather['timezone_offset'])
    #parent.after(0, write_output, parent, response)
    icon = get_icon(parent, parent.current_weather)
    draw_icon(parent.current_weather, icon)
    parent.after(0, parent.input.get_btn.configure, {'state':tk.NORMAL})


def get_current_weather(parent, inp):
    params = {
        'q':inp,
        'appid': parent.API_KEY,
        'units': parent.UNIT
    }

    return httpreq(parent, parent.WEATHER_CURRENT_URL, params)

def get_city_coords(current_weather):
    return {
        "lon" : current_weather["coord"]["lon"],
        "lat" : current_weather["coord"]["lat"]
    }


def get_forecast_weather(parent, coords):
    params = {
        'lon' : coords['lon'],
        'lat' : coords['lat'],
        'appid' : parent.API_KEY,
        'exclude' : 'current,minutely,hourly',
        'units': parent.UNIT
    }
    return httpreq(parent, parent.WEATHER_FORECAST_URL, params)


def get_icon(parent, host):
    # parent is the main window, host is the frame that holds the icon
    
    # if the icon exists in the cache, then return it. otherwise, download it
    if host.icon_code in parent.icon_cache:
        return parent.icon_cache[host.icon_code]

    else:
        url = f"http://openweathermap.org/img/wn/{host.icon_code}.png"
        photoimg = ImageTk.PhotoImage(Image.open(io.BytesIO(httpreq(parent, url))))
        parent.icon_cache[host.icon_code] = photoimg
        return photoimg


def httpreq(parent, url, params=None):
    if params is not None:
        url = url + urllib.parse.urlencode(params)

    try:
        with urllib.request.urlopen(url) as req:
            if req.info().get_content_subtype() == "json":
                return json.loads(req.read().decode())
            elif req.info().get_content_subtype() == "png":
                return req.read()

    except urllib.error.HTTPError as err:
        parent.status_label.configure(text=err)
        print(err)
        parent.after(0, parent.input.get_btn.configure, {'state':tk.NORMAL})
        raise


def draw_icon(host, icon):
    host.icon_label.configure(image=icon)


def write_current_output(parent,response):
    parent.current_weather.pack()
    parent.space_label.pack()
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
    parent.current_weather.icon_code = response['weather'][0]['icon'] + "@2x"
    # the "@2x" is appended to the icon code because bigger icons from openweathermap has it in the filename


def write_forecast_daily_output(parent, daily_weather, timezone_offset):
    parent.forecast_daily.pack()
    i = 1
    for frame in parent.forecast_daily.forecast_day_list:
        frame.day_label.configure(text = DT.datetime.utcfromtimestamp(daily_weather[i]['dt'] + timezone_offset).strftime('%a'))
        frame.icon_code = daily_weather[i]['weather'][0]['icon']
        frame.weather_desc_label.configure(text = daily_weather[i]['weather'][0]['description'])
        frame.temp_max_label.configure(text = f"{daily_weather[i]['temp']['max']}°C")
        frame.temp_min_label.configure(text = f"{daily_weather[i]['temp']['min']}°C")
        i += 1
