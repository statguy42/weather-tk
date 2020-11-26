import datetime as DT
import urllib.request, urllib.parse, urllib.error
import json
import io
import tkinter as tk
from PIL import Image, ImageTk
import concurrent.futures


def btn_pressed(parent, inp):
    # disable the submit button till the function completes or errors in other function
    # error probably will only occur in the httpreq() function
    # so there is a line of code to enable the button again in case of error
    # tk.after(0, some_func, args) schedules some_func(args) to be run in tkinter's main thread after 0 ms
    parent.after(0, parent.input.get_btn.configure, {'state':tk.DISABLED})

    current_weather = get_current_weather(parent, inp)
    parent.after(0, write_current_output, parent.current_weather_frame, current_weather)

    parent.after(0, parent.space_label.pack)

    coords = get_city_coords(current_weather)
    forecast_weather = get_forecast_weather(parent, coords)
    parent.after(0, write_forecast_daily_output, parent.forecast_daily_frame, forecast_weather['daily'], forecast_weather['timezone_offset'])

    process_icons(parent, current_weather, forecast_weather['daily'])

    parent.after(0, parent.input.get_btn.configure, {'state':tk.NORMAL})
    parent.status_label.configure(text=f"Updated at {DT.datetime.now().strftime('%I:%M:%S %p')}")


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


def process_icons(parent, current_weather, daily_weather):
    host_list = [parent.current_weather_frame] + parent.forecast_daily_frame.forecast_day_list
    icon_list = get_icon_codes(current_weather, daily_weather)
    draw_all_icons(parent, icon_list, host_list)


def get_icon_codes(current_weather, daily_weather):
    icon_list = [current_weather['weather'][0]['icon'] + '@2x']

    for i in range(1,8):
        icon_code = daily_weather[i]['weather'][0]['icon']
        if icon_code not in icon_list:
            icon_list.append(icon_code)
    return icon_list


def download_icon(parent, icon_code):
    # parent is the main window
    # if the icon does not exist in the cache, then it is downloaded

    # this function returns the icon code itself, because we will run this function in a threadpool
    # and we want to know for which icon the function has completed

    if icon_code in parent.icon_cache:
        return icon_code
    else:
        url = f"http://openweathermap.org/img/wn/{icon_code}.png"
        photoimg = ImageTk.PhotoImage(Image.open(io.BytesIO(httpreq(parent, url))))
        parent.icon_cache[icon_code] = photoimg
        return icon_code


def draw_all_icons(parent, icon_list, host_list):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_list = [executor.submit(download_icon, parent, icon_code) for icon_code in icon_list]
        
        for res in concurrent.futures.as_completed(future_list):
            for frame in host_list:
                if frame.icon_code == res.result():
                    frame.after(0, frame.icon_label.configure, {'image' : parent.icon_cache[frame.icon_code]})


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


def write_current_output(current_weather_frame, weather):
    current_weather_frame.pack()

    current_weather_frame.city_lab.configure(text=f"City: {weather['name']}, {weather['sys']['country']}")
    current_weather_frame.temp_lab.configure(text=f"Temp: {weather['main']['temp']}°C")
    current_weather_frame.feels_lab.configure(text=f"Feels like: {weather['main']['feels_like']}°C")
    current_weather_frame.wind_speed_lab.configure(text=f"Wind speed: {weather['wind']['speed']} m/s")
    current_weather_frame.desc_lab.configure(text=weather['weather'][0]['description'].capitalize())
    current_weather_frame.humid_lab.configure(text=f"Humidty: {weather['main']['humidity']}%")
    current_weather_frame.clouds_lab.configure(text=f"Cloudiness: {weather['clouds']['all']}%")
    current_weather_frame.sunrise_lab.configure(text=f"Sunrise: {DT.datetime.utcfromtimestamp(weather['sys']['sunrise']+weather['timezone']).strftime('%I:%M %p')}")
    current_weather_frame.sunset_lab.configure(text=f"Sunset: {DT.datetime.utcfromtimestamp(weather['sys']['sunset']+weather['timezone']).strftime('%I:%M %p')}")
    current_weather_frame.icon_code = weather['weather'][0]['icon'] + "@2x"
    # the "@2x" is appended to the icon code because bigger icons from openweathermap has it in the filename


def write_forecast_daily_output(forecast_daily_frame, daily_weather, timezone_offset):
    forecast_daily_frame.pack()
    i = 1
    for frame in forecast_daily_frame.forecast_day_list:
        frame.day_label.configure(text = DT.datetime.utcfromtimestamp(daily_weather[i]['dt'] + timezone_offset).strftime('%a'))
        frame.icon_code = daily_weather[i]['weather'][0]['icon']
        frame.weather_desc_label.configure(text = daily_weather[i]['weather'][0]['description'].capitalize())
        frame.temp_max_label.configure(text = f"{daily_weather[i]['temp']['max']}°C")
        frame.temp_min_label.configure(text = f"{daily_weather[i]['temp']['min']}°C")
        i += 1
