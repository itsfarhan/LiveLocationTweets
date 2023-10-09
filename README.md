# Sentiment Analysis Twitter Map

This Python application allows you to perform sentiment analysis on tweets and visualize the results on a map. The application uses the Twitter API to search for tweets based on a specific keyword or phrase and analyzes the sentiment of these tweets using TextBlob. The sentiment analysis results are then displayed on a map using the Folium library.

## Prerequisites

Before running the application, make sure you have the following libraries installed:

- `re`
- `traceback`
- `folium`
- `geocoder`
- `tweepy`
- `flask`
- `textblob`
- `datetime`

You can install these libraries using the following command:

```
pip install re traceback folium geocoder tweepy flask textblob datetime
```

## Configuration

Before using the application, you need to configure your Twitter API credentials. Replace the following variables in the code with your Twitter API credentials:

- `CONSUMER_KEY`: Your Twitter API consumer key
- `CONSUMER_SECRET`: Your Twitter API consumer secret
- `ACCESS_TOKEN`: Your Twitter API access token
- `ACCESS_TOKEN_SECRET`: Your Twitter API access token secret

## Running the Application

To run the application, execute the `app.py` file. The application will start a Flask server and you can access it in your web browser at `http://localhost:5000`.

## How to Use

1. Access the application in your web browser.
2. Enter a keyword or phrase in the search box.
3. Select the start and end dates for the tweets you want to analyze.
4. Click the "Search" button to initiate the search and sentiment analysis process.
5. The application will plot the tweets on the map based on their sentiment. Green markers represent positive sentiment, red markers represent negative sentiment, and black markers represent neutral sentiment.

## Notes

- Tweets with geolocation information will be plotted based on their coordinates.
- Tweets without geolocation information will be plotted based on the location mentioned in the user's profile. If no location is found, these tweets will be skipped.
