from database import Database
from twitter_utils import get_tweety_api, remove_tweet_link, tweet_time_difference, save_image
import json
import requests
import time
import sys

class User:
    
    sql_create_published_tweets_table = """CREATE TABLE IF NOT EXISTS published_tweets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username text,
        tweet_id text NOT NULL,
        FOREIGN KEY (username)
            REFERENCES users(username)
    );"""
                                    
    sql_create_user_table = """CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username text,
        oauth_token text NOT NULL,
        oauth_token_secret text NOT NULL
    );"""
    
    def __init__(self, username, oauth_token, oauth_token_secret, id=None):
        self.username = username
        self.oauth_token = oauth_token
        self.oauth_token_secret = oauth_token_secret
        self.id = id
        
    @staticmethod
    def create_table():
        with Database() as cursor:
            cursor.execute(User.sql_create_user_table)
            cursor.execute(User.sql_create_published_tweets_table)

    def __repr__(self):
        return f'{self.username}'

    def save_user_to_db(self):
        with Database() as cursor:
            cursor.execute('INSERT INTO users (username, oauth_token, oauth_token_secret) VALUES (?, ?, ?)',
                           (self.username, self.oauth_token, self.oauth_token_secret))
        print('Saved user to database')

    def save_published_tweet(self, tweet_id):
        with Database() as cursor:
            cursor.execute('INSERT INTO published_tweets (username, tweet_id) VALUES (?, ?)',
                           (self.username, tweet_id))

    def load_published_tweets_id(self):
        with Database() as cursor:
            cursor.execute(
                'SELECT * FROM published_tweets WHERE username = ?', (self.username,))
            user_data = cursor.fetchall()
            if user_data:
                return [tweet[2] for tweet in user_data]
            return []

    @classmethod
    def load_data_by_username(cls, username):
        with Database() as cursor:
            cursor.execute(
                'SELECT * FROM users WHERE username=?', (username, ))
            user_data = cursor.fetchone()
            if user_data:
                return cls(
                    username=user_data[1],
                    oauth_token=user_data[2],
                    oauth_token_secret=user_data[3],
                    id=user_data[0]
                )

    def user_timeline(self, screen_name, count=20):
        api = get_tweety_api(self.oauth_token, self.oauth_token_secret)
        
        try:
            return api.user_timeline(screen_name=screen_name, count=count, tweet_mode="extended")
        except tweepy.TweepError as e:
            print("The handle you entered was invalid, please try again: ")
            sys.exit(1)

    def publish_tweet(self, img_name, tweet_txt):
        """Tweet the image and text to Twitter. Parameter name of the image and the text"""

        api = get_tweety_api(self.oauth_token, self.oauth_token_secret)
        status = api.update_with_media(f'images/{img_name}.jpg', tweet_txt)

    def get_tweets(self, screen_name, hrs=2, time_delay=100):
        
        tweets = self.user_timeline(screen_name, 5)
        tweets.reverse()
        published_tweets = self.load_published_tweets_id()
        print(published_tweets)
        for tweet in tweets:
            try:
                if hasattr(tweet, 'extended_entities'):
                    media = tweet.extended_entities['media'][0]
                    hours = tweet_time_difference(tweet.created_at)
                    tweet_id = tweet.id_str
                    if hours < hrs and media['type'] == 'photo' and tweet_id not in published_tweets:
                        try:
                            img_url = media['media_url']
                            tweet_text = remove_tweet_link(tweet.full_text)
                            img_name = save_image(tweet_id, img_url)
                            if img_name:
                                # self.publish_tweet(img_name, tweet_text)
                                self.save_published_tweet(tweet_id)
                                print('Tweet published')
                                print('Tweet id saved in database')
                                time.sleep(time_delay)

                        except KeyError:
                            print('Cannot find media')
                            pass
            except KeyError:
                pass
