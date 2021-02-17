import datetime as DT
import urllib.request, urllib.parse, urllib.error
import json
import io
import tkinter as tk
from PIL import Image, ImageTk
import concurrent.futures


def btn_pressed(mainwindow, inp):
    # disable the submit button till the function completes or errors in other function
    # error probably will only occur in httpreq()
    # so there is a line of code to enable the button again in case of error

    # tk.after(0, some_func, args) schedules some_func(args) to be run in tkinter's main thread after 0 ms
    # writing it this way, because someguy said I should only do stuff to tkinter from its own thread
    mainwindow.after(0, mainwindow.input.get_btn.configure, {'state':tk.DISABLED})

    current_weather = get_current_weather(mainwindow, inp)    # fetches current weather, displays it in the next line
    mainwindow.after(0, write_current_output, mainwindow.current_weather_frame, current_weather)

    mainwindow.after(0, mainwindow.space_label.pack)

    # city coordinates, this is required because the next api request does not support calling by city name
    coords = get_city_coords(current_weather)

    forecast_weather = get_forecast_weather(mainwindow, coords)    # fetches forecast weather, displays it in the next line
    mainwindow.after(0, write_forecast_daily_output, mainwindow.forecast_daily_frame, forecast_weather['daily'], forecast_weather['timezone_offset'])

    # we shall now download icons and display them
    process_icons(mainwindow, current_weather, forecast_weather['daily'])

    # since we are done fetching and displaying everything, we can now enable the button so that it can be pressed again
    mainwindow.after(0, mainwindow.input.get_btn.configure, {'state':tk.NORMAL})
    mainwindow.status_label.configure(text=f"Updated at {DT.datetime.now().strftime('%I:%M:%S %p')}")


def get_current_weather(mainwindow, inp):
    params = {
        'q':inp,
        'units': mainwindow.UNIT,
        'appid': mainwindow.API_KEY
    }
    return httpreq(mainwindow, mainwindow.WEATHER_CURRENT_URL, params)


def get_city_coords(current_weather):
    return {
        "lon" : current_weather["coord"]["lon"],
        "lat" : current_weather["coord"]["lat"]
    }


def get_forecast_weather(mainwindow, coords):
    params = {
        'lon' : coords['lon'],
        'lat' : coords['lat'],
        'exclude' : 'current,minutely,hourly',
        'units': mainwindow.UNIT,
        'appid' : mainwindow.API_KEY
    }
    return httpreq(mainwindow, mainwindow.WEATHER_FORECAST_URL, params)


def process_icons(mainwindow, current_weather, daily_weather):
    frames_list = [mainwindow.current_weather_frame] + mainwindow.forecast_daily_frame.forecast_day_list
    icon_list = get_icon_codes(current_weather, daily_weather)
    draw_all_icons(mainwindow, icon_list, frames_list)


def get_icon_codes(current_weather, daily_weather):
    # initializing the icon list with the icon code of the current weather
    # "@2x" is added because that's how openweathermap names bigger icons
    icon_list = [current_weather['weather'][0]['icon'] + '@2x']

    # range(1.8) because the api returns weather for 8 days
    # the first day being the current day
    # and we don't want the current day
    for i in range(1,8):
        icon_code = daily_weather[i]['weather'][0]['icon']
        if icon_code not in icon_list:
            icon_list.append(icon_code)
    return icon_list


def download_icon(mainwindow, icon_code):
    # mainwindow is the main window
    # if the icon does not exist in the cache, then it is downloaded
    # this function returns the icon code itself, because we will run this function in a threadpool
    # and we want to know for which icon the function has completed
    # then display the icon in the frames which contains this icon code
    
    if icon_code in mainwindow.icon_cache:
        return icon_code
    else:
        url = f"http://openweathermap.org/img/wn/{icon_code}.png"
        photoimg = ImageTk.PhotoImage(Image.open(io.BytesIO(httpreq(mainwindow, url))))    # copied from SO, I think
        mainwindow.icon_cache[icon_code] = photoimg
        return icon_code


def draw_all_icons(mainwindow, icon_list, frame_list):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_list = [executor.submit(download_icon, mainwindow, icon_code) for icon_code in icon_list]
        
        # each "future" is a future object
        # the result attribute is the return value of the function in that future
        # the function being run is returning the icon codes
        # if the icon code matches with any of the frames' icon code, we shall display it there
        for future in concurrent.futures.as_completed(future_list):
            for frame in frame_list:
                if frame.icon_code == future.result():
                    frame.after(0, frame.icon_label.configure, {'image' : mainwindow.icon_cache[frame.icon_code]})


def httpreq(mainwindow, url, params=None):
    if params is not None:
        url = url + urllib.parse.urlencode(params)

    try:
        with urllib.request.urlopen(url) as req:
            if req.info().get_content_subtype() == "json":
                return json.loads(req.read().decode())
            elif req.info().get_content_subtype() == "png":
                return req.read()

    except urllib.error.HTTPError as err:
        mainwindow.status_label.configure(text=err)

        # setting the submit button to normal state because it was set to disabled when it was pressed
        mainwindow.after(0, mainwindow.input.get_btn.configure, {'state':tk.NORMAL})

        print(err)    # printing this if anyone wants to know where the error occured
        print(url.split("&appid")[0])    # we don't want the api key to be printed in the console
        # raising the exception again
        # because we don't want to run any code that follows this function call because of the error
        # probably should have done it in a cleaner way
        # TODO: may "fix" it later
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
    # starting from 1 because the 0th day is the current day
    i = 1
    for frame in forecast_daily_frame.forecast_day_list:
        frame.day_label.configure(text = DT.datetime.utcfromtimestamp(daily_weather[i]['dt'] + timezone_offset).strftime('%a'))
        frame.icon_code = daily_weather[i]['weather'][0]['icon']
        frame.weather_desc_label.configure(text = daily_weather[i]['weather'][0]['description'].capitalize())
        frame.temp_max_label.configure(text = f"{daily_weather[i]['temp']['max']}°C")
        frame.temp_min_label.configure(text = f"{daily_weather[i]['temp']['min']}°C")
        i += 1
