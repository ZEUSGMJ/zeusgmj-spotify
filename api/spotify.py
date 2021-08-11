import os
import json
import random
import requests
import re

from base64 import b64encode
from dotenv import load_dotenv, find_dotenv
from flask import Flask, Response, jsonify, render_template, templating

load_dotenv(find_dotenv())

# Spotify scopes:
#   user-read-currently-playing
#   user-read-recently-played
PLACEHOLDER_IMAGE = "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"
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_SECRET_ID = os.getenv("SPOTIFY_SECRET_ID")
SPOTIFY_REFRESH_TOKEN = os.getenv("SPOTIFY_REFRESH_TOKEN")

FALLBACK_THEME = "spotify.html.j2"

REFRESH_TOKEN_URL = "https://accounts.spotify.com/api/token"
NOW_PLAYING_URL = "https://api.spotify.com/v1/me/player/currently-playing"
RECENTLY_PLAYING_URL = (
    "https://api.spotify.com/v1/me/player/recently-played?limit=10"
)

app = Flask(__name__)


def getAuth():
    return b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_SECRET_ID}".encode()).decode(
        "ascii"
    )


def refreshToken():
    data = {
        "grant_type": "refresh_token",
        "refresh_token": SPOTIFY_REFRESH_TOKEN,
    }

    headers = {"Authorization": "Basic {}".format(getAuth())}
    response = requests.post(REFRESH_TOKEN_URL, data=data, headers=headers)

    try:
        return response.json()["access_token"]
    except KeyError:
        print(json.dumps(response.json()))
        print("\n---\n")
        raise KeyError(str(response.json()))


def recentlyPlayed():
    token = refreshToken()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(RECENTLY_PLAYING_URL, headers=headers)

    if response.status_code == 204:
        return {}
    return response.json()


def nowPlaying():
    token = refreshToken()
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(NOW_PLAYING_URL, headers=headers)

    if response.status_code == 204:
        return {}
    return response.json()

def barGen(barCount):
    barCSS = ""
    left = 1
    for i in range(1, barCount + 1):
        anim = random.randint(1000, 1350)
        barCSS += (
            ".bar:nth-child({})  {{ left: {}px; animation-duration: {}ms; }}".format(
                i, left, anim
            )
        )
        left += 4
    return barCSS

def getTemplate():
    try:
        file = open("api/templates.json","r")
        templates = json.loads(file.read())
        return templates["templates"][templates["current-theme"]]
    except Exception as e:
        print(f"Failed to load templates.")
        return FALLBACK_THEME


def loadImageB64(url):
    resposne = requests.get(url)
    return b64encode(resposne.content).decode("ascii")

def makeSVG(data):
    barCount = 105
    contentBar = "".join(["<div class='bar'></div>" for i in range(barCount)])
    barCSS = barGen(barCount)

    if data == {} or data["item"] == "None" or data["item"] is None and data["item"]["is_local"] == 'false':
        contentBar = ""
        currentStatus = "Was listening to:"
        recentPlays = recentlyPlayed()
        recentPlaysLength = len(recentPlays["items"])
        itemIndex = random.randint(0, recentPlaysLength - 1)
        item = recentPlays["items"][itemIndex]["track"]
    else:
        item = data["item"]
        currentStatus = "Listening to:" if item["is_local"] == False else 'Listening to a Local File:'
    if item["album"]["images"] == [] or item["is_local"] == True:
        image = PLACEHOLDER_IMAGE
    else :
        image = loadImageB64(item["album"]["images"][0]["url"])

    artists = []

    for i in item["artists"]:
        artists.append(i["name"])
    
    if len(artists) >= 2:
        artists.insert(-1, '&amp;')

    artistName = ', '.join(artists[:-2]) + ' ' + ' '.join(artists[-2:])
    songName = item["name"].replace("&", "&amp;")
    albumName = item["album"]["name"].replace("&", "&amp;")
    songUrl = ''
    
    if (item["is_local"] == False):
        songUrl = item["external_urls"]["spotify"]

    artistName = re.sub("&", "&amp;", artistName)

    dataDict = {
        "contentBar": contentBar,
        "barCSS": barCSS,
        "artistName": artistName,
        "songName": songName,
        "image": image,
        "status": currentStatus,
        "albumName": albumName,
        "songURL": songUrl,
    }

    return render_template(getTemplate(), **dataDict)


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def catch_all(path):
    data = nowPlaying()
    svg = makeSVG(data)

    resp = Response(svg, mimetype="image/svg+xml")
    resp.headers["Cache-Control"] = "s-maxage=1"

    return resp

if __name__ == "__main__":
    app.run(debug=True)
