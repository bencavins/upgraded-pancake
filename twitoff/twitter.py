import os
import tweepy
import spacy
from .models import DB, Tweet, User


# Get API keys from environment vars
key = os.getenv('TWITTER_API_KEY')
secret = os.getenv('TWITTER_API_KEY_SECRET')


# Connect to the Twitter API
twitter_auth = tweepy.OAuthHandler(key, secret)
twitter = tweepy.API(twitter_auth)

# Load our pretrained spacy model
nlp = spacy.load('my_model/')


def vectorize_tweet(tweet_text):
    return nlp(tweet_text).vector


def add_or_update_user(username):
    twitter_user = twitter.get_user(screen_name=username)

    db_user = User.query.get(twitter_user.id)
    if not db_user:
        # Add new user to DB
        db_user = User(id=twitter_user.id, username=username)
        
    DB.session.add(db_user)

    tweets = twitter_user.timeline(
        count=200,
        exclude_replies=True,
        include_rts=False,
        tweet_mode='extended',
    )
    for tweet in tweets:
        db_tweet = Tweet(
            id=tweet.id, 
            text=tweet.full_text,
            vector=vectorize_tweet(tweet.text),
        )
        db_user.tweets.append(db_tweet)
        DB.session.add(db_tweet)
    
    DB.session.commit()