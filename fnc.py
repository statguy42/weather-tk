import datetime as DT
import urllib.request, urllib.parse, urllib.error
import json
import io
import tkinter as tk
from PIL import Image, ImageTk


def btn_pressed(parent, inp):
    parent.after(0, parent.input.get_btn.configure, {'state':tk.DISABLED})
    response = get_weather(parent, inp)
    write_output(parent, response)
    #parent.after(0, write_output, parent, response)
    icon = get_icon(parent, parent.current_weather)
    draw_icon(parent.current_weather, icon)
    parent.after(0, parent.input.get_btn.configure, {'state':tk.NORMAL})



def get_weather(parent, inp):
    params = {
        'q':inp,
        'appid': parent.API_KEY,
        'units': parent.UNIT
    }
    return httpreq(parent, parent.WEATHER_SERVICE_URL, params)


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
        raise


def draw_icon(host, icon):
    host.icon_label.configure(image=icon)


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
    parent.current_weather.icon_code = response['weather'][0]['icon'] + "@2x"
    # the "@2x" is appended to the icon code because bigger icon's from openweathermap has it in the filename

