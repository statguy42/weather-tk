# Weather-tk, a very basic weather app

Weather-tk is an app written in Python that shows the current weather. Weather data is fetched using the Openweathermap API.

This project is a learning experience for me. Everything in this repo is licensed under the MIT license.

## Dependencies
- Python 3 (duh)
- Python modules:
  - tkinter, used for GUI
  - urllib.{request, parse, error}, to process http requests
  - json, to parse weather data
  - io, to pass downloaded icons to pillow
  - pillow, used for icon support (the only one that needs to be manually installed using `pip`)
  - datetime, to show times
- An openweathermap API key, used to get weather data

More dependencies may be required as the proeject goes on.

## How to run
- You will need an API key from openweathermap, you can get one for free in their website by creating an account.
- Copy and paste your API key in a file named `api_key.txt` and place it in the same directory as `weather-tk.py`.
- Then simply run `python weather-tk.py`.

## Roadmap
- Add multithreading so that the UI doesn't freeze when getting data from the API
- ~~Add weather icons~~ (done, but the implementation might be changed)
- Add daily forecast for 7 days
- Add hourly forecast for 24 hours

## Contribution
This project is open to suggestions and pull requests.