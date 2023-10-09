import re
import traceback
import os
import datetime
import geocoder
import tweepy
import folium
from flask import Flask, render_template, request, redirect, send_from_directory
from textblob import TextBlob

app = Flask(__name__)

# Twitter API credentials
CONSUMER_KEY = ''
CONSUMER_SECRET = ''
ACCESS_TOKEN = ''
ACCESS_TOKEN_SECRET = ''

# Twitter API authentication
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)

# Initialize map object
map = folium.Map(location=[17.3850, 78.4867], tiles="OpenStreetMap", zoom_start=10)

# Function to perform sentiment analysis using TextBlob
def sentimentAnalysis(tweet):
    tweet = TextBlob(cleanTweets(tweet))
    return tweet.sentiment

# Function to clean tweets
def cleanTweets(tweet):
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

# Function to calculate the center of a polygon
def calcCenterOfPolygon(coordinates):
    return [sum([x[0] for x in coordinates]) / 4, sum([x[1] for x in coordinates]) / 4]

# Function to plot coordinates on the map based on sentiment
def plotCoordinates(coordinates, tweet, sentiment):
    point = coordinates
    try:
        if sentiment.polarity > 0:
            folium.Marker(point, popup=tweet, icon=folium.Icon(color='green')).add_to(map)
        elif sentiment.polarity == 0:
            folium.Marker(point, popup=tweet, icon=folium.Icon(color='black')).add_to(map)
        else:
            folium.Marker(point, popup=tweet, icon=folium.Icon(color='red')).add_to(map)
    except Exception as e:
        print(traceback.print_exc())
        pass

# Function to get tweets and plot them on the map
def getTweets(search_query, from_date, to_date):
    try:
        for tweet in tweepy.Cursor(api.search, q=search_query, since=from_date, until=to_date, lang="en").items(50):
            try:
                data = tweet._json
                if data.get('place') is not None:
                    coordinates = calcCenterOfPolygon(data['place']['bounding_box']['coordinates'][0])
                    tweet_text = cleanTweets(data['text'])
                    sentiment = sentimentAnalysis(tweet_text)
                    plotCoordinates(coordinates, tweet_text, sentiment)
                elif data.get('user').get('location'):
                    location = data['user']['location']
                    result = geocoder.arcgis(location)
                    coordinates = [result.x, result.y]
                    if coordinates[0] is not None and coordinates[1] is not None:
                        tweet_text = cleanTweets(data['text'])
                        sentiment = sentimentAnalysis(tweet_text)
                        plotCoordinates(coordinates, tweet_text, sentiment)
            except Exception as e:
                print(traceback.print_exc())
                pass
    except Exception as e:
        print(traceback.print_exc())
        pass

# Flask routes
@app.route('/home')
@app.route('/home/tweet_input', methods=['GET'])
def tweet_input():
    return render_template('index.html')

@app.route('/home/get_tweets', methods=['POST'])
def gather_tweets():
    if request.method == 'POST':
        tweet = request.form['tweet']
        from_date = request.form['fromdate']
        to_date = request.form['todate']
        getTweets(tweet, from_date, to_date)
        save_map()
        return redirect("http://localhost:5000/static/sentimental_chart.html", code=302)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
