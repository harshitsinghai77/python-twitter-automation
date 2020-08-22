import constants
import urllib.parse
import tweepy
import socket
from datetime import datetime, timezone
import requests
import re
import sys
import os

auth = tweepy.OAuthHandler(constants.CONSUMER_KEY, constants.CONSUMER_SECRET, callback='oob')
 

def get_authorization():
    auth_url = auth.get_authorization_url()
    print('Authorization URL: ' + auth_url)
    verifier = input('PIN: ').strip()
    auth.get_access_token(verifier)
    print('Generated ACCESS_KEY and ACCESS_SECRET')
    return auth.access_token, auth.access_token_secret

def get_tweety_api(access_token, access_token_secret):
    tweepy_auth = tweepy.OAuthHandler(
        constants.CONSUMER_KEY, constants.CONSUMER_SECRET)
    
    tweepy_auth.set_access_token(access_token, access_token_secret)
    return tweepy.API(tweepy_auth)


def remove_tweet_link(text):
    return re.sub(r"http\S+", '', text)


def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)


def tweet_time_difference(tweet_created_at):
    """Calculates the difference in time between now() and tweet time"""

    twitter_date_format = '%a %b %d %H:%M:%S +0000 %Y'

    time_now = datetime.now().replace(tzinfo=None)
    tweet_time = utc_to_local(tweet_created_at).replace(tzinfo=None)

    difference = time_now - tweet_time

    hours = int(difference.seconds // (60 * 60))
    mins = int((difference.seconds // 60) % 60)

    return hours


def save_image(img_name, img_url):
    """Download the image and save it to the disk. Takes name of the image and image url as parameter"""
    img = requests.get(img_url)
    if img.status_code == 200:
        with open(f'images/{img_name}.jpg', 'wb') as f:
            f.write(img.content)
            f.close()
        return img_name


def checkInternetSocket(host="8.8.8.8", port=53, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        print('Not connected to the internet. Try again later')
        sys.exit(1)

def check_dir_exists():   
    if not os.path.exists('images'):
        os.makedirs('images')

