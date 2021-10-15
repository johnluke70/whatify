
import argparse
import logging
from argparse import ArgumentParser
import re
import json
import requests
from requests.auth import HTTPBasicAuth

log = logging.getLogger("whatify")

def parse_args(argparse: ArgumentParser):
    argparse.add_argument("--chat_txt", required=True, action="store", dest="chat_txt", help="Path to txt file with full whatsapp chat history.")
    argparse.add_argument("--spotify_creds", required=False, action="store", dest="cred_file", 
    default=".spotify/credentials.json", 
    help="Path to JSON file with full spotify API credentials")
    argparse.add_argument("--playlist_name", required=True, action="store", dest="playlist_name", help="Name of the playlist to add to")
    

def load_spotify_links(chat_txt):
    links = []
    with open(chat_txt, 'r', errors="ignore") as f: # ignoring unicode errors, as we don't care about emojis etc.
        for l in f.readlines():
            if "spotify" in l:
                link = extract_song_link(l)    
                if link is not None:
                    links.append(link)  
    return links


def extract_song_link(raw_line):
    exc = re.findall("(https:\/\/open\.spotify\.com\/track\/[^?\s]+)", raw_line)
    if len(exc) > 1:
        log.warn(f"Found multiple links here: {raw_line}")
    elif len(exc) == 0:
        log.warn(f"didn't find a spotify link here: {raw_line}")
    else:
        return exc[0]
    return None


def load_spotify_creds(cred_file):
    with open(cred_file, 'r') as f:
        return json.load(f)


def spotify_auth(cred_file):
    creds = load_spotify_creds(cred_file)
    r = requests.post("https://accounts.spotify.com/api/token", auth=(HTTPBasicAuth(creds['client_id'], creds['client_secret'])))
    print(r)
    print(r.content)

# def fetch_track_details( track_id):



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    argparser = ArgumentParser()
    parse_args(argparser)
    args = argparser.parse_args()
    log.info(f"Looking up links in {args.chat_txt}")
    links = load_spotify_links(args.chat_txt)    
    log.info(f"Found {len(links)} link(s). here is an eg. {links[0]}")

    # spotify_auth(args.cred_file)


