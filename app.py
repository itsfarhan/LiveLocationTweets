import re
import traceback
import os
import geocoder
import tweepy
import folium
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from textblob import TextBlob

app = Flask(__name__)

# ─── Twitter API Credentials ─────────────────────────────────────────────────
CONSUMER_KEY        = ''
CONSUMER_SECRET     = ''
ACCESS_TOKEN        = ''
ACCESS_TOKEN_SECRET = ''

# ─── Twitter Auth ─────────────────────────────────────────────────────────────
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api  = tweepy.API(auth, wait_on_rate_limit=True)

# ─── Map Initialisation ───────────────────────────────────────────────────────
tweet_map = folium.Map(
    location=[20.0, 0.0],
    tiles="CartoDB dark_matter",
    zoom_start=2,
)

# ─── Helpers ──────────────────────────────────────────────────────────────────
def clean_tweet(text: str) -> str:
    """Strip mentions, special chars, and URLs from a tweet."""
    return ' '.join(
        re.sub(r"(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", text).split()
    )


def get_sentiment(text: str):
    """Return a TextBlob sentiment namedtuple for the cleaned tweet text."""
    return TextBlob(clean_tweet(text)).sentiment


def polygon_center(coords: list) -> list:
    """Return the centroid of a bounding-box polygon (4-point list)."""
    return [
        sum(p[0] for p in coords) / len(coords),
        sum(p[1] for p in coords) / len(coords),
    ]


def add_marker(lat: float, lon: float, popup: str, polarity: float) -> None:
    """Add a colour-coded marker to the global map."""
    if polarity > 0:
        colour = 'green'
    elif polarity < 0:
        colour = 'red'
    else:
        colour = 'gray'
    try:
        folium.Marker(
            [lat, lon],
            popup=folium.Popup(popup, max_width=300),
            icon=folium.Icon(color=colour, icon='twitter', prefix='fa'),
        ).add_to(tweet_map)
    except Exception:
        traceback.print_exc()


def save_map() -> None:
    """Persist the Folium map to the static directory."""
    tweet_map.save(os.path.join(app.root_path, 'static', 'sentiment_map.html'))


def fetch_and_plot(query: str, from_date: str, to_date: str) -> dict:
    """Fetch up to 50 geolocated tweets and plot them; return sentiment stats."""
    stats = {'positive': 0, 'neutral': 0, 'negative': 0, 'total': 0}

    try:
        cursor = tweepy.Cursor(
            api.search,
            q=query,
            since=from_date,
            until=to_date,
            lang='en',
        ).items(50)

        for tweet in cursor:
            try:
                data      = tweet._json
                text      = clean_tweet(data.get('text', ''))
                sentiment = get_sentiment(text)

                # Prefer precise place bounding box
                if data.get('place'):
                    coords = data['place']['bounding_box']['coordinates'][0]
                    center = polygon_center(coords)
                    add_marker(center[0], center[1], text, sentiment.polarity)

                # Fall back to user-profile location
                elif data.get('user', {}).get('location'):
                    geo = geocoder.arcgis(data['user']['location'])
                    if geo.lat and geo.lng:
                        add_marker(geo.lat, geo.lng, text, sentiment.polarity)
                    else:
                        continue
                else:
                    continue

                # Update stats
                stats['total'] += 1
                if sentiment.polarity > 0:
                    stats['positive'] += 1
                elif sentiment.polarity < 0:
                    stats['negative'] += 1
                else:
                    stats['neutral'] += 1

            except Exception:
                traceback.print_exc()

    except Exception:
        traceback.print_exc()

    return stats


# ─── Routes ───────────────────────────────────────────────────────────────────
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    query     = request.form.get('tweet', '').strip()
    from_date = request.form.get('fromdate', '')
    to_date   = request.form.get('todate', '')

    stats = fetch_and_plot(query, from_date, to_date)
    save_map()

    return render_template(
        'map_result.html',
        query=query,
        from_date=from_date,
        to_date=to_date,
        stats=stats,
    )


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon',
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
