from django.shortcuts import render
from textblob import TextBlob

from . import forms, models
from tweepy import API, Cursor, OAuthHandler
import numpy as np
import pandas as pd
import datetime
import csv
import os
import re


# Create your views here.


def index(request):
    return render(request, 'TwiSenApp/index.html')


def search_by_uname(request):
    form = forms.SearchFormUsername()
    tweets = []
    if request.method == 'POST':
        form = forms.SearchFormUsername(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            number_of_tweets = form.cleaned_data['number_of_tweets']
            fetcher = TweetsFetcher()
            fetched_tweets = fetcher.fetch_tweets_by_username(username, number_of_tweets)
            new_post = models.Post(usernameorhashtag=username, since=datetime.date.today())
            new_post.save()
            for tweet in fetched_tweets:
                data = fetcher.extract_data(tweet)
                new_tweet = models.Tweet(post_id=new_post, tweet_text=data[0], tweet_id=data[1], tweet_length=data[2],
                                         tweet_created_at=data[3], tweet_source=data[4], tweet_favorite_count=data[5],
                                         tweet_retweet_count=data[6], tweet_location=data[7])
                new_tweet.save()
                tweets.append(data)

    return render(request, 'TwiSenApp/searchbyuname.html', {'form':form, 'tweets':tweets})

def search_by_htag(request):
    form = forms.SearchFormHashtag()
    tweets = []
    if request.method == 'POST':
        form = forms.SearchFormHashtag(request.POST)
        if form.is_valid():
            hashtag = form.cleaned_data['search_hashtag']
            number_of_tweets = form.cleaned_data['number_of_tweets']
            date = str(form.cleaned_data['date'])

            fetcher = TweetsFetcher()
            fetched_tweets = fetcher.fetch_tweets_by_hashtag(hashtag, date, number_of_tweets)
            new_post = models.Post(usernameorhashtag=hashtag, since=date)
            new_post.save()
            for tweet in fetched_tweets:
                data = fetcher.extract_data(tweet)
                new_tweet = models.Tweet(post_id=new_post, tweet_text=data[0], tweet_id=data[1], tweet_length=data[2],
                                         tweet_created_at=data[3], tweet_source=data[4], tweet_favorite_count=data[5],
                                         tweet_retweet_count=data[6], tweet_location=data[7])


                new_tweet.save()
                tweets.append(data)

    return render(request, 'TwiSenApp/searchbyhtag.html', {'form':form, 'tweets':tweets})


def sentiment_analysis_of_tweets(request):
    tweet_id = models.Post.objects.all().order_by('-id')[0]
    tweets = models.Tweet.objects.filter(post_id=tweet_id)

    tweet_analyzer = SentimentAnalysis()

    df = tweet_analyzer.tweet_to_dataframe(tweets)
    df['sentiment'] = np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in df['tweets']])

    positive = 0
    negative = 0
    neutral = 0
    sentiments = [x for x in df['sentiment']]
    tweets = [x for x in df['tweets']]
    tweets_with_sentiments = []
    for x in range(len(sentiments)):
        tweets_with_sentiments.append([tweets[x], sentiments[x]])

    for i in sentiments:
        if i == 1:
            positive += 1
        elif i == -1:
            negative += 1
        else:
            neutral += 1
    return render(request, 'TwiSenApp/sentimentanalysisreport.html', {'positive':positive, 'negative':negative, 'neutral':neutral,
                                                                      'tweetswithsentiments':tweets_with_sentiments})

def save_to_csv(request):
    form = forms.CSVFileForm()
    error = ""
    if request.method == 'POST':
        form = forms.CSVFileForm(request.POST)

        if form.is_valid():
            filename = form.cleaned_data['filename']
            if '.' in filename:
                error = "Only enter the filename without extension"
            else:
                recent_data = models.Post.objects.all().order_by('-id')[0]
                data = [["text", "id", "length", "date", "source", "likes", "retweet", "location"]]
                rows = models.Tweet.objects.filter(post_id=recent_data.id)
                for row in rows:
                    text = row.tweet_text
                    id = row.tweet_id
                    length = row.tweet_length
                    date = row.tweet_created_at
                    source = row.tweet_source
                    likes = row.tweet_favorite_count
                    retweet = row.tweet_retweet_count
                    location = row.tweet_location
                    data.append([text, id, length, date, source, likes, retweet, location])

                desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
                print(desktop+"\\"+filename+".csv")
                with open(desktop+"\\"+filename+".csv", "w", encoding="utf-8") as csvFile:
                    writer = csv.writer(csvFile)
                    writer.writerows(data)
                    csvFile.close()


    return render(request, 'TwiSenApp/savetocsv.html', {'form':form, 'error':error})

class TwitterCredentials():
    ACCESS_TOKEN = ""
    ACCESS_TOKEN_SECRET = ""
    CONSUMER_KEY = ""
    CONSUMER_SECRET = ""


class TwitterAuthenticator():
    def authenticate(self):
        auth = OAuthHandler(TwitterCredentials.CONSUMER_KEY, TwitterCredentials.CONSUMER_SECRET)
        auth.set_access_token(TwitterCredentials.ACCESS_TOKEN, TwitterCredentials.ACCESS_TOKEN_SECRET)
        return auth


class TweetsFetcher():
    def __init__(self):
        self.auth = TwitterAuthenticator().authenticate()
        self.twitter_client = API(self.auth)

    def fetch_tweets_by_username(self, username, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=username).items(num_tweets):
            tweets.append(tweet)
        return tweets

    def fetch_tweets_by_hashtag(self, hashtag, date, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.search, q=hashtag, lang="en", since=date).items(num_tweets):
            tweets.append(tweet)
        return tweets

    def extract_data(self, tweet):
        extracted_data = []
        extracted_data.append(tweet.text)
        extracted_data.append(tweet.id)
        extracted_data.append(len(tweet.text))
        extracted_data.append(tweet.created_at)
        extracted_data.append(tweet.source)
        extracted_data.append(tweet.favorite_count)
        extracted_data.append(tweet.retweet_count)
        if tweet.place != None:
            extracted_data.append(str(tweet.place.country + ", " + tweet.place.full_name))
        else:
            extracted_data.append("None")

        return extracted_data

class SentimentAnalysis():
    def tweet_to_dataframe(self, tweets):
        df = pd.DataFrame(data=[tweet.tweet_text for tweet in tweets], columns=['tweets'])
        df['id'] = np.array([tweet.tweet_id for tweet in tweets])
        df['len'] = np.array([tweet.tweet_length for tweet in tweets])
        df['date'] = np.array([tweet.tweet_created_at for tweet in tweets])
        df['source'] = np.array([tweet.tweet_source for tweet in tweets])
        df['likes'] = np.array([tweet.tweet_favorite_count for tweet in tweets])
        df['retweets'] = np.array([tweet.tweet_retweet_count for tweet in tweets])
        return df

    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def analyze_sentiment(self, tweet):
        analysis = TextBlob(self.clean_tweet(tweet))

        if analysis.sentiment.polarity > 0:
            return 1
        elif analysis.sentiment.polarity == 0:
            return 0
        else:
            return -1