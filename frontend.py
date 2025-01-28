import streamlit as st
import requests

# Flask API URL
API_BASE = "http://127.0.0.1:5000"

# Streamlit App
st.title("Twitter Sentiment Analysis")
st.markdown("Analyze sentiments from custom text or live tweets!")

# Analyze Custom Text
st.header("Analyze Custom Text")
user_input = st.text_area("Enter text to analyze sentiment:")

if st.button("Analyze Sentiment"):
    if user_input.strip():
        response = requests.post(f"{API_BASE}/analyze", json={"text": user_input})
        if response.status_code == 200:
            result = response.json()
            st.success(f"Sentiment: {result['sentiment']}")
        else:
            st.error("Error analyzing text. Please try again.")
    else:
        st.error("Please enter some text to analyze.")

# Fetch and Analyze Tweets
st.header("Search and Analyze Tweets")
topic = st.text_input("Enter a topic to search for tweets:")

if st.button("Search Tweets"):
    if topic.strip():
        response = requests.post(f"{API_BASE}/fetch_tweets", json={"topic": topic})
        if response.status_code == 200:
            result = response.json()
            tweets = result["results"]
            st.subheader(f"Results for topic: {topic}")
            for tweet in tweets:
                st.write(f"**Tweet:** {tweet['tweet']}")
                st.write(f"**Sentiment:** {tweet['sentiment']}")
                st.write("---")
        else:
            st.error("Error fetching tweets. Please try again.")
    else:
        st.error("Please enter a topic to search.")

