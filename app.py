import streamlit as st
from googleapiclient.discovery import build
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
import pandas as pd
import re
import emoji

# Replace with your API Key
API_KEY = 'AIzaSyANR3XTVAuRHpkmkEuUxCP5JXpLtXtEA8U'
youtube = build('youtube', 'v3', developerKey=API_KEY)
analyzer = SentimentIntensityAnalyzer()

# Function to clean comment
def clean_comment(comment):
    comment = re.sub(r'http\S+', '', comment)
    comment = emoji.replace_emoji(comment, replace='')
    return comment

# Function to fetch comments
def get_comments(video_id, max_comments=100):
    comments = []
    next_page_token = None

    while len(comments) < max_comments:
        response = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            maxResults=100,
            pageToken=next_page_token,
            textFormat='plainText'
        ).execute()

        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comments.append(clean_comment(comment))
            if len(comments) >= max_comments:
                break

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    return comments

# Function to analyze sentiment
def analyze_sentiment(comments):
    sentiments = {'Positive': 0, 'Neutral': 0, 'Negative': 0}
    for comment in comments:
        score = analyzer.polarity_scores(comment)['compound']
        if score >= 0.05:
            sentiments['Positive'] += 1
        elif score <= -0.05:
            sentiments['Negative'] += 1
        else:
            sentiments['Neutral'] += 1
    return sentiments

# Streamlit UI
st.title("🎥 YouTube Comment Sentiment Analyzer")

video_url = st.text_input("Enter YouTube Video URL")

if st.button("Analyze"):
    if video_url:
        video_id = video_url.strip()[-11:]
        st.info(f"Extracted Video ID: `{video_id}`")

        with st.spinner("Fetching comments and analyzing..."):
            comments = get_comments(video_id)
            sentiments = analyze_sentiment(comments)

        total = sum(sentiments.values())
        st.subheader("Sentiment Distribution")
        st.write(sentiments)

        # Pie chart
        fig, ax = plt.subplots()
        ax.pie(sentiments.values(), labels=sentiments.keys(), autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        st.pyplot(fig)

        st.success(f"✅ Analyzed {total} comments successfully!")
    else:
        st.warning("Please enter a valid YouTube video URL.")
