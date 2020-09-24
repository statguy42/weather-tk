import tkinter as tk
from fnc import btn_pressed


class MainWindow(tk.Tk):
    def __init__(self, threadworker):
        super().__init__()
        self.geometry('400x200')
        self.title('Weather')

        self.lab1 = tk.Label(self)
        self.lab1.configure(text="Enter city:")
        self.lab1.pack()

        self.input = InputFrame(self)
        self.input.pack()

        self.status_label = tk.Label(self)
        self.status_label.pack()

        self.current_weather = CurrentWeatherFrame(self)
        # self.CurrentWeather gets packed after the button is pressed

        # the following dict is used to cache icons in memory
        self.icon_cache = dict()

        self.threadworker = threadworker

        try:
            with open("api_key.txt") as keyfile:
                self.WEATHER_SERVICE_URL = "http://api.openweathermap.org/data/2.5/weather?"
                self.API_KEY = keyfile.read().rstrip("\n")
                self.UNIT = "metric"

        except:
            self.status_label.configure(text = "error openning api_key.txt")
            self.input.get_btn.configure(state=tk.DISABLED)


class InputFrame(tk.Frame):
    def __init__(self,parent):
        super().__init__()
        self.inp_text = tk.StringVar()
        self.inp_text.set("London")

        self.inp = tk.Entry(self, textvariable=self.inp_text)
        self.inp.grid(row=0,column=1)

        #self.get_btn = tk.Button(self, text="Submit", command=lambda: btn_pressed(parent, self.inp.get()))
        self.get_btn = tk.Button(self, text="Submit", command=lambda: parent.threadworker.submit(btn_pressed, parent, self.inp.get()))
        self.get_btn.grid(row=0,column=2)


class CurrentWeatherFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__()

        self['bg'] = '#CCCCCC'

        self.city_lab = tk.Label(self)
        self.city_lab.grid(row=0, column=0, sticky='W')

        self.temp_lab = tk.Label(self)
        self.temp_lab.grid(row=1,column=0, sticky='W')

        self.feels_lab = tk.Label(self)
        self.feels_lab.grid(row=2, column=0, sticky='W')

        self.humid_lab = tk.Label(self)
        self.humid_lab.grid(row=3, column=0, sticky='W')

        self.icon_code = None

        self.icon_label = tk.Label(self)
        self.icon_label.grid(row=0, column=1, rowspan=3)

        self.desc_lab = tk.Label(self)
        self.desc_lab.grid(row=2,column=1, rowspan=2)

        self.wind_speed_lab = tk.Label(self)
        self.wind_speed_lab.grid(row=0, column=2, sticky='E')

        self.clouds_lab = tk.Label(self)
        self.clouds_lab.grid(row=1, column=2, sticky='E')

        self.sunrise_lab = tk.Label(self)
        self.sunrise_lab.grid(row=2, column=2, sticky='E')

        self.sunset_lab = tk.Label(self)
        self.sunset_lab.grid(row=3, column=2, sticky='E')

        # change background color of all child widgets
        for widget in self.children.values():
            widget['bg'] = "#CCCCCC"


class ForecastDailyFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__()

        self.forecast_day_list = list()

        for i in range(7):
            self.forecast_day_list.append(ForecastDayFrame(self))
            self.forecast_day_list[i].grid(row=0, column=i)


class ForecastDayFrame(tk.Frame):
    def __init(self, parent):
        super().__init__()

        self.day_label = tk.Label(self)
        self.day_label.grid(row=0, column=0)

        self.icon_code = None

        self.icon_label = tk.Label(self)
        self.icon_label.grid(row=1, column=0)

        self.weather_desc_label = tk.Label(self)
        self.weather_desc_label.grid(row=2, column=0)

        self.temp_max_label = tk.Label(self)
        self.temp_max_label.grid(row=3, column=0)

        self.temp_min_label = tk.Label(self)
        self.temp_min_label.grid(row=4, column=0)
