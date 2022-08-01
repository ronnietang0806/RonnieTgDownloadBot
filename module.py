import configparser
from tweepy.auth import OAuth1UserHandler
from tweepy.api import API
import json

config = configparser.ConfigParser()
config.read('config.ini')
consumer_key = config['Twitter']['api_key']
consumer_secret = config['Twitter']['api_key_secret']
bearer_token = "AAAAAAAAAAAAAAAAAAAAAHp4fQEAAAAAU%2FLhBYeUeqr97SAVUEHgosxz8K4%3DYJtWOZsr9FENhrWVRNts7VjzgCy2ur8xQh9uD4xNLWFwohhPsB"
access_token = config['Twitter']['access_token']
access_token_secret = config['Twitter']['access_token_secret']
 
def get_tweet(tweet_id):
        auth = OAuth1UserHandler(
                consumer_key, consumer_secret, access_token, access_token_secret
                
        )
        api = API(auth)
        api.retry_count = 2
        api.retry_delay = 0 if use_replay else 5