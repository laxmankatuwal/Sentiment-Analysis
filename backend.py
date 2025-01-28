from flask import Flask, request, jsonify
import joblib
import tweepy
import os

# Load the ML model and vectorizer
try:
    model = joblib.load("trained_model.pkl")
    vectorizer = joblib.load("vectorizer.pkl")
except FileNotFoundError:
    model = None
    vectorizer = None

# Twitter API setup
def authenticate_twitter():
    api_key = os.environ.get('TWITTER_API_KEY')
    api_secret = os.environ.get('TWITTER_API_SECRET')
    access_token = os.environ.get('TWITTER_ACCESS_TOKEN')
    access_token_secret = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')

    if not api_key or not api_secret or not access_token or not access_token_secret:
        raise ValueError("Missing Twitter API credentials")
    
    auth = tweepy.OAuthHandler(api_key, api_secret)
    auth.set_access_token(access_token, access_token_secret)
    return tweepy.API(auth)

# Ensure Twitter API credentials are loaded correctly
try:
    api = authenticate_twitter()
except ValueError as e:
    api = None
    twitter_error = str(e)

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the Sentiment Analysis API!"

@app.route('/analyze', methods=['POST'])
def analyze_text():
    if model is None or vectorizer is None:
        return jsonify({"error": "Model or vectorizer not loaded. Please check server setup."}), 500
    
    data = request.json
    if not data or 'text' not in data:
        return jsonify({"error": "Invalid input. Provide 'text'."}), 400

    try:
        text = data['text']
        vectorized_input = vectorizer.transform([text])
        prediction = model.predict(vectorized_input)
        sentiment_map = {0: "Negative 😟", 1: "Neutral 😐", 2: "Positive 😊"}
        sentiment = sentiment_map[prediction[0]]

        return jsonify({"text": text, "sentiment": sentiment})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/fetch_tweets', methods=['POST'])
def fetch_tweets():
    if api is None:
        return jsonify({"error": "Twitter API authentication failed. " + twitter_error}), 500

    data = request.json
    if not data or 'topic' not in data:
        return jsonify({"error": "Invalid input. Provide 'topic'."}), 400

    topic = data['topic']
    tweets = []
    try:
        # Adjust the number of tweets you fetch as necessary
        for tweet in tweepy.Cursor(api.search_tweets, q=topic, lang="en").items(5):
            vectorized_tweet = vectorizer.transform([tweet.text])
            prediction = model.predict(vectorized_tweet)
            sentiment_map = {0: "Negative 😟", 1: "Neutral 😐", 2: "Positive 😊"}
            sentiment = sentiment_map[prediction[0]]
            
            tweets.append({"tweet": tweet.text, "sentiment": sentiment})
        
        return jsonify({"topic": topic, "results": tweets})
    except tweepy.TweepError as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)
