##############
# Your turn! #
##############
# Now you're ready for the next part, where you retrieve data from an API
# of your choice. Note that you may need to provide an authentication key
# for some APIs. For that, work another file, called hw5-application.py.
#
# You will need to copy a few of the import statements from the top of this
# file. You may copy any helpful functions, too, like pretty() or
# safe_get().
#
# See requirements in the README.
#
# Also note that when the sunrise sunset API we used is queried for a
# date that doesn't exist, it gives a 400 error. Some APIs that you may
# use will return JSON-formatted data saying that the requested item
# couldn't be found. You may have to check the contents of the data you 
# get back to see whether a query was successful. You don't have to do
# that with the sunrise sunset API.

import urllib.parse, urllib.request, urllib.error, json

def pretty(obj):
    return json.dumps(obj, sort_keys=True, indent=2)

#
#
# # auth_handler = urllib.request.HTTPBasicAuthHandler()
#
#
# auth_url = 'https://accounts.spotify.com/api/token'
#
# creds = {
#     'grant_type': 'client_credentials',
#     'client_id': client_id,
#     'client_secret': client_secret
# }

# param_str = urllib.parse.urlencode(creds)
#
# request = urllib.request(auth_url, creds)
# auth_response = urllib.urlopen(request)
#
# access_token = auth_response.json().get('access_token')
# print(access_token)

"""Method to actually handle authorization"""

# Note: I put my client id and client secret in secrets.py
# and told git to ignore that file. You should too.

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
        from secrets import CLIENT_ID, CLIENT_SECRET
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

class track():

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
        from secrets import CLIENT_ID, CLIENT_SECRET
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



if __name__ == "__main__":

    def search_by_genre(genre):
        sclient = spotiClient()
        searchresult = sclient.apiRequest(params={'q': 'genre:' + genre, 'type': 'track', 'limit': 17})
        return searchresult['tracks']['items']

    genre = 'r&b'

    tracks = search_by_genre(genre)
    # print(pretty(rnb_tracks))

    track_list = [track(curr_track) for curr_track in tracks]

    track_tempo = []

    for track in track_list:
        track_tempo_dict = {}
        track_tempo_dict['id'] = track.id
        track_tempo_dict['tempo'] = track.get_track_tempo()
        track_tempo.append(track_tempo_dict)

#    photos_tags_dict_sorted = sorted(photos_tags_dict_keys, key=lambda k: photos_tags_dict[k], reverse=True)

    track_tempo_sorted = sorted(track_tempo, key=lambda k: k['tempo'])
    print(track_tempo_sorted)

    # sclient = spotiClient()
    # searchresult = sclient.apiRequest(params={'q': 'genre:r&b', 'type': 'track', 'limit': 17})
    # print(pretty(searchresult))



