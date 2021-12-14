import urllib.request, urllib.error, urllib.parse, json, webbrowser, requests
from flask import Flask, render_template, request

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

from spotifysecrets import CLIENT_ID, CLIENT_SECRET

app = Flask(__name__)

def one_emoji(emoji_name):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    param_key = {"access_key": "d9dad43868a372189f68abfb1902595f971b52b0"}
    # emoji_name = "grinning-squinting-face"
    baseurl = "https://emoji-api.com/emojis/" + emoji_name
    mypage = requests.get(baseurl, headers=headers, params=param_key)
    emojis = json.loads(mypage.text)
    # print(emojis)
    return emojis

emojiStrings = ['grinning-squinting-face', 'star-struck', 'sleepy-face', 'worried-face', 'angry-face', 'crying-face','face-vomiting', 'sparkling-heart', 'relieved-face']

emojiDict = {}
for emoji in emojiStrings:
    emojiDict[emoji] = one_emoji(emoji)[0]['character']
    emoji_output = one_emoji(emoji)[0]['character']
    #print(emoji_output)


@app.route("/")
def main_handler():
    app.logger.info("In MainHandler")
    return render_template("weathertemplate.html", page_title="Weather Form")


"""Method to actually handle authorization"""


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


def get_weather_data(baseurl='http://api.weatherapi.com/v1', k="cdcdc165a33343d9810205011211711", city=None):
    paramstr = {"key": k, "q": city}
    wrequest = baseurl + "/current.json" + "?" + urllib.parse.urlencode(paramstr)
    result = urllib.request.urlopen(wrequest).read()
    dict = json.loads(result)
    return (dict)


print(pretty(get_weather_data(city="Seattle")))

forecastdict = {"forecasts": {}}


# cities = {"Seattle", "Taipei", "New York City"}
# print_weather(cities)
#
# for loc in cities:
#     llstring = "%s" % loc
#     forecast = get_weather_data(city=llstring)
#
#     if forecast is not None:
#         forecastdict["forecasts"][loc] = forecast["current"]["temp_f"]

def print_weather(cities={}):
    for c in cities:
        dict = get_weather_data(city=c)
        return (dict["location"]["name"] + " temperature on %s: " % str(dict["location"]["localtime"]) + str(
            dict["current"]["temp_f"]))

def print_emoji(emojiStrings = {}):
    for emoji_face in emojiStrings:
        emoji_output = one_emoji(emoji_face)[0]['character']
        return (emoji_output)

class spotiClient():
    # I'm going to create a client class to handle requests to spotify
    # including managing authorization.
    # This is different from Flickr where we just wrote one function

    def __init__(self):
        self.accessToken = None
        self.spotifyAuth()

    def spotifyAuth(self):
        """Method to actually handle authorization"""

        # Note: I put my client id and client secret in secrets.py
        # and told git to ignore that file. You should too.
        import base64

        # Following documentation in
        # https://developer.spotify.com/web-api/authorization-guide/#client_credentials_flow
        #
        # To get a bearer token, Spotify expects:
        # the Authorization in the *header*, as a Base 64-encoded
        # string that contains the client ID and client secret key.
        # The field must have the format:
        # Authorization: Basic <base64 encoded client_id:client_secret>
        #
        # To get a bearer token to work as a "client," it also needs:
        # grant_type = "client_credentials" as a parameter

        # build the header
        authorization = base64.standard_b64encode((CLIENT_ID +
                                                   ':' + CLIENT_SECRET).encode())
        headers = {"Authorization": "Basic " + authorization.decode()}

        # encode the params dictionary, note it needs to be byte encoded
        params = {"grant_type": "client_credentials"}
        encodedparams = urllib.parse.urlencode(params).encode()

        # request goes to POST https://accounts.spotify.com/api/token
        request = urllib.request.Request(
            'https://accounts.spotify.com/api/token',
            data=encodedparams, headers=headers)
        resp = urllib.request.urlopen(request)

        # I should do some error handling, but this is a quick example
        respdata = json.load(resp)
        self.accessToken = respdata['access_token']
        # Note that by default this token will expire in 60 minutes.
        # If your application will run longer, you will need to manage
        # that - for example, you could detect an expired token and call
        # spotifyAuth again.

    def apiRequest(self,
                   version="v1",
                   endpoint="search",
                   item=None,
                   params=None):
        """Method for API calls once authorized.
        By default, it will execute a search.

        See
        https://developer.spotify.com/web-api/endpoint-reference/
        for endpoints

        Items, e.g., a track ID, are passed in via the item parameter.
        Parameters, e.g., search parameters, are passed in via the
        params dictionary."""

        if self.accessToken is None:
            print(
                "Sorry, you must have an access token for this to work.")
            return {}

        baseurl = "https://api.spotify.com/"
        endpointurl = "%s%s/%s" % (baseurl, version, endpoint)

        # are there any params we need to pass in?
        if item is not None:
            endpointurl = endpointurl + "/" + item
        if params is not None:
            fullurl = endpointurl + "?" + urllib.parse.urlencode(params)

        headers = {"Authorization": "Bearer " + self.accessToken}
        request = urllib.request.Request(fullurl, headers=headers)
        resp = urllib.request.urlopen(request)

        # again, I should some error handling
        return json.load(resp)


class Track:

    def __init__(self, track_dict):
        self.id = track_dict['id']
        self.name = track_dict['name']
        self.url = track_dict['external_urls']['spotify']
        self.album_id = track_dict['album']['id']
        artists = track_dict['artists']
        self.artist_ids = [artist['id'] for artist in artists]
        self.accessToken = None
        self.spotifyAuth()

    def spotifyAuth(self):
        """Method to actually handle authorization"""

        # Note: I put my client id and client secret in secrets.py
        # and told git to ignore that file. You should too.
        import base64

        # Following documentation in
        # https://developer.spotify.com/web-api/authorization-guide/#client_credentials_flow
        #
        # To get a bearer token, Spotify expects:
        # the Authorization in the *header*, as a Base 64-encoded
        # string that contains the client ID and client secret key.
        # The field must have the format:
        # Authorization: Basic <base64 encoded client_id:client_secret>
        #
        # To get a bearer token to work as a "client," it also needs:
        # grant_type = "client_credentials" as a parameter

        # build the header
        authorization = base64.standard_b64encode((CLIENT_ID +
                                                   ':' + CLIENT_SECRET).encode())
        headers = {"Authorization": "Basic " + authorization.decode()}

        # encode the params dictionary, note it needs to be byte encoded
        params = {"grant_type": "client_credentials"}
        encodedparams = urllib.parse.urlencode(params).encode()

        # request goes to POST https://accounts.spotify.com/api/token
        request = urllib.request.Request(
            'https://accounts.spotify.com/api/token',
            data=encodedparams, headers=headers)
        resp = urllib.request.urlopen(request)

        # I should do some error handling, but this is a quick example
        respdata = json.load(resp)
        self.accessToken = respdata['access_token']
        # Note that by default this token will expire in 60 minutes.
        # If your application will run longer, you will need to manage
        # that - for example, you could detect an expired token and call
        # spotifyAuth again.

    def get_track_tempo(self):
        baseurl = 'https://api.spotify.com/v1/audio-analysis/'

        fullurl = baseurl + self.id
        headers = {"Authorization": "Bearer " + self.accessToken}
        request = urllib.request.Request(fullurl, headers=headers)
        resp = urllib.request.urlopen(request)

        resp_dict = json.load(resp)

        return resp_dict['track']['tempo']


def search_by_genre(genre):
    sclient = spotiClient()
    searchresult = sclient.apiRequest(params={'q': 'genre:' + genre, 'type': 'track', 'limit': 17})
    return searchresult['tracks']['items']

# converts input temperature to an index to match to song in list
@app.route("/wresponse")
def weather_response_handler():
    input_city = request.args.get("weather")
    app.logger.info(input_city)
    if input_city:
        dict = get_weather_data(city=input_city)
        temp = dict["current"]["temp_f"]
        song_index = 0

        if temp >= -40 and temp < -30:
            song_index = 1
        elif temp >= -30 and temp < -20:
            song_index = 2
        elif temp >= -20 and temp < -10:
            song_index = 3
        elif temp >= -10 and temp < 0:
            song_index = 4
        elif temp >= 0 and temp < 10:
            song_index = 5
        elif temp >= 10 and temp < 20:
            song_index = 6
        elif temp >= 20 and temp < 30:
            song_index = 7
        elif temp >= 30 and temp < 40:
            song_index = 8
        elif temp >= 40 and temp < 50:
            song_index = 9
        elif temp >= 50 and temp < 60:
            song_index = 10
        elif temp >= 60 and temp < 70:
            song_index = 11
        elif temp >= 70 and temp < 80:
            song_index = 12
        elif temp >= 80 and temp < 90:
            song_index = 13
        elif temp >= 90 and temp < 100:
            song_index = 14
        elif temp >= 100 and temp < 110:
            song_index = 15
        elif temp >= 110 and temp < 120:
            song_index = 16

        # get emoji input
        select_emoji = request.args.getlist("emoji_type")
        app.logger.info(select_emoji)

            # Use emoji faces to return genres
        print(select_emoji)
        if select_emoji:
            genre = ""
            if select_emoji[0] == "crying-face":
                genre = "blues"
            elif select_emoji[0] == "relieved-face":
                genre = "indie"
            elif select_emoji[0] == "grinning-squinting-face":
                genre = "alternative"
            elif select_emoji[0] == "angry-face":
                genre = "rap"
            elif select_emoji[0] == "star-struck":
                genre = 'pop'
            elif select_emoji[0] == "worried-face":
                genre = "grunge"
            elif select_emoji[0] == "sleepy-face":
                genre = "classical"
            elif select_emoji[0] == "sparkling-heart":
                genre = "r&b"


        print('GENREEEEEEE:' + genre)
        tracks = search_by_genre(genre)
        # print(pretty(rnb_tracks))

        track_list = [Track(curr_track) for curr_track in tracks]

        track_tempo = []

        for track in track_list:
            track_tempo_dict = {}
            track_tempo_dict['track'] = track
            track_tempo_dict['tempo'] = track.get_track_tempo()
            track_tempo.append(track_tempo_dict)

        #    photos_tags_dict_sorted = sorted(photos_tags_dict_keys, key=lambda k: photos_tags_dict[k], reverse=True)

        track_tempo_sorted = sorted(track_tempo, key=lambda k: k['tempo'])

        song = track_tempo_sorted[song_index]['track']
        print("SONG NAME" + song.name)

        print(track_tempo_sorted)
        return render_template("weathertemplate.html",
                               answer=str(song.name),
                               url = str(song.url),
                               page_title="Your Song")
    else:
        return render_template("weathertemplate.html", page_title="Weather Form - Error", prompt="No city or emoji entered")


# temp = weather_response_handler()

# Note: I put my client id and client secret in secrets.py
# and told git to ignore that file. You should too.


if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)

# import jinja2, os

# JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
#                                       extensions = ["jinja2.ext.autoescape"],
#                                       autoescape = True)

# template = JINJA_ENVIRONMENT.get_template("weathertemplate.html")
# with open("forecast.html", "w") as forecastfile:
#    forecastfile.write(template.render(forecastdict))
