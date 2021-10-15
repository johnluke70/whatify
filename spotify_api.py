
import webbrowser

import requests
import json
from requests.auth import HTTPBasicAuth
import logging
import re
import os.path

log = logging.getLogger("spotify_api")

API_URL = "https://api.spotify.com/v1"

CACHE_PATH = ".spotify/token.json"

#TODO: Add this to argparse?
redirect_url = "http://localhost/callback" # this needs to match what is in the Spotify developer console 


# Full guide to authenticate against Spotify API is here: 
# https://developer.spotify.com/documentation/general/guides/authorization-guide/


class Spotify:

    def __init__(self, client_id, client_secret):
        # self._token = self.authenticate(client_id, client_secret)
        token = self._load_token()
        if token is None:
            self.authenticate_client(client_id, client_secret)
            token = self._load_token()
        self.retrieve_ephemeral_token(token, redirect_url, client_secret, client_secret)

    # Returns Bearer token to be used in all subsequent requests
    # This request grants a token that cannot be used to access individual user account info.
    def authenticate(self, client_id, client_secret):
        params = {
            'grant_type': 'client_credentials'
        }
        headers = {
            # "accept": "application/json"
        }
        r = requests.post("https://accounts.spotify.com/api/token", data=params, headers=headers, auth=HTTPBasicAuth(client_id, client_secret))
        if r.status_code == 200:
            response = r.json()
            log.info(f"Authentication succeeded, expiring in {response['expires_in']}s")
            return response['access_token']
        else:
            log.error(f"Unable to authenticate against spotify API. code={r.status_code}. [{r.content}]")


    def _load_token(self):
        if os.path.isfile(CACHE_PATH):
            with open(CACHE_PATH, 'r') as f:
                j = json.load(f)
                return j['token']
        return None


    def authenticate_client(self, client_id, client_secret):
        
        params = {
            'client_id': client_id,
            'response_type': 'code',
            'redirect_uri': redirect_url,
            'scope': 'user-read-private'
        }
        # Build url, and open in a browser
        param_str = []
        for key, value in params.items():
            param_str.append(key + "=" + value)
        url = "https://accounts.spotify.com/authorize?" + "&".join(param_str)
        
        log.info(f"About to open [{url}] in a browser")
        webbrowser.open(url)
        redirected_url = input("Once you've granted permission, paste the url here: \n")
        token = re.findall("code=[^&]+", redirected_url)
        with open(CACHE_PATH, 'w') as f:
            json.dump(f, {'token': token[0]})
        log.info("Successfully written the token")


    def retrieve_ephemeral_token(self, token, redirect_uri, client_id, client_secret):
        payload = {
            'grant_type': 'authorization_code',
            'code': token,
            'redirect_uri': redirect_uri
        }
        log.info("requesting ephemeral token")
        r = requests.post("https://accounts.spotify.com/api/token", auth=(client_id, client_secret), data=payload)
        print(r.status_code)
        print(r.content)


    def auth_header(self):
        return {"Authorization": "Bearer " + self._token}

    def get_my_profile(self):
        r = requests.get(f"{API_URL}/me", headers=self.auth_header())
        log.info(f"Get my profile: [{r.status_code}]")

    # def get_playlists(self):
    #     r = requests.get("https://api.spotify.com/v1/users")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    with open(".spotify/credentials.json", 'r') as f:
        creds = json.load(f)
        sp = Spotify(creds['client_id'], creds['client_secret'])
