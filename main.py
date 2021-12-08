import urllib.request, urllib.error, urllib.parse, json, webbrowser

### Utility functions you may want to use
def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)

def safe_get(url):
    try:
        return urllib.request.urlopen(url)
    except urllib.error.HTTPError as e:
        print("The server couldn't fulfill the request.")
        print("Error code: ", e.code)
    except urllib.error.URLError as e:
        print("We failed to reach a server")
        print("Reason: ", e.reason)
    return None

def get_weather_data(baseurl = 'http://api.weatherapi.com/v1', k = "cdcdc165a33343d9810205011211711",city=None):
    paramstr = {"key":k, "q":city}
    wrequest = baseurl + "/current.json" + "?" + urllib.parse.urlencode(paramstr)
    result = urllib.request.urlopen(wrequest).read()
    dict = json.loads(result)
    return(dict)

print(pretty(get_weather_data(city="Seattle")))

def print_weather(cities = {}):
    for c in cities:
        dict = get_weather_data(city = c)
        print(dict["location"]["name"] + " temperature on %s: "%str(dict["location"]["localtime"]) + str(dict["current"]["temp_f"]))

cities = {"Seattle", "Taipei", "New York City"}
print_weather(cities)

#locinfo = json.load(open("locinfo.json", "r"))
#for loc in cities:
#    llstring = "%s"%loc
#    if llstring not in locinfo:
#        locinfo[llstring] = get_weather_data(city=loc)

#json.dump(locinfo, open("locinfo.json", "w"))

forecastdict = {"forecasts":{}}
for loc in cities:
    llstring="%s"%loc
    forecast = get_weather_data(city=llstring)

    if forecast is not None:
        forecastdict["forecasts"][loc] = forecast["current"]["temp_f"]

from flask import Flask, render_template, request
import logging
app = Flask(__name__)

@app.route("/")
def main_handler():
    app.logger.info("In MainHandler")
    return render_template("weathertemplate.html", page_title ="Weather Form")

def print_weather(cities = {}):
    for c in cities:
        dict = get_weather_data(city = c)
        return(dict["location"]["name"] + " temperature on %s: "%str(dict["location"]["localtime"]) + str(dict["current"]["temp_f"]))

@app.route("/wresponse")
def weather_response_handler():
    city = request.args.get("weather")
    app.logger.info(city)
    if city:
        return render_template("weathertemplate.html",
            answer = print_weather(cities = {city}),
            page_title = "Your Current Weather"
        )
    else:
        return render_template("weathertemplate.html", page_title = "Weather Form - Error", prompt = "No city entered")

if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug = True)

#import jinja2, os

#JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
#                                       extensions = ["jinja2.ext.autoescape"],
#                                       autoescape = True)

#template = JINJA_ENVIRONMENT.get_template("weathertemplate.html")
#with open("forecast.html", "w") as forecastfile:
#    forecastfile.write(template.render(forecastdict))