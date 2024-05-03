import streamlit as st
import googleapiclient.discovery
import pandas as pd
import matplotlib.pyplot as plt
from config import DEVELOPER_KEY
import os

# Function to fetch comments from YouTube
def getcomments(video):
    try:
        api_service_name = "youtube"
        api_version = "v3"
        youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=DEVELOPER_KEY)

        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video,
            maxResults=100
        )
        comments = []

        # Execute the request.
        response = request.execute()

        # Get the comments from the response.
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']
            comments.append([
                comment['authorDisplayName'],
                comment['textOriginal'],
                comment['videoId'],
            ])

            while True:
                try:
                    nextPageToken = response['nextPageToken']
                except KeyError:
                    break

                # Create a new object with the next page token.
                nextRequest = youtube.commentThreads().list(part="snippet", videoId=video, maxResults=100, pageToken=nextPageToken)

                # Execute the next request.
                response = nextRequest.execute()

                # Get the comments from the next response.
                for item in response['items']:
                    comment = item['snippet']['topLevelComment']['snippet']
                    comments.append([
                        comment['authorDisplayName'],
                        comment['textOriginal'],
                        comment['videoId'],
                    ])

        df = pd.DataFrame(comments, columns=['author', 'text', 'video_id'])
        return df
    except Exception as e:
        st.error("Please enter the video ID.")
        st.stop()

# Change the overall theme of the app
st.set_page_config(page_title="YouTube Sentiment Analysis", page_icon=":movie_camera:")

# Change the color of the title using HTML
st.markdown("<h1 style='color:red;'>YouTube Sentiment Analysis</h1>", unsafe_allow_html=True)

# Define instructions text
instructions_text = """
1. Enter the YouTube Video ID in the text box provided.
2. Click the "Enter" button to retrieve comments from the specified video.
3. Once the comments are fetched, sentiment analysis and insights will be displayed.
4. Use the visualizations and insights to understand the sentiment distribution and most frequent words in the comments.
5. You can also refresh the data by clicking the "Refresh Data" button.
6. If you encounter any issues, please reach out for assistance.
"""

# Add a sidebar button for instructions
if st.sidebar.button("How to use"):
    # Display instructions in a modal
    st.sidebar.markdown(instructions_text)

# Allow user to input video ID
video_id = st.sidebar.text_input("Enter YouTube Video ID (e.g., xQqsvRHjas4):")
df = getcomments(video_id)
# Fetch comments based on input video ID
comments_df = getcomments(video_id)

# Button for refreshing data
if st.sidebar.button("Refresh Data"):
    # Reload the page
    st.experimental_rerun()

st.write("### Top comments from the video")

# Display the DataFrame
st.dataframe(comments_df)

import re
from wordcloud import WordCloud

# Function to preprocess text
def preprocess_text(text):
    # Convert to lowercase
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r'http\S+', '', text)
    
    # Remove special characters, punctuations, unwanted letters, and unwanted numbers
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    
    # Remove extra whitespaces and newlines
    text = re.sub('\s+', ' ', text).strip()
    
    return text

# Create a Streamlit app
st.markdown("<h1 style='color:green;'>Sentiment Analysis and Insights</h1>", unsafe_allow_html=True)

# Preprocess text data
# Apply preprocessing to the text data
comments_df['clean_text'] = comments_df['text'].apply(preprocess_text)

from textblob import TextBlob

# Function to calculate polarity and subjectivity scores
def get_sentiment_scores(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity
    return polarity, subjectivity

# Apply the function to each comment
comments_df['polarity'], comments_df['subjectivity'] = zip(*comments_df['clean_text'].apply(get_sentiment_scores))

# Filter out rows with polarity and subjectivity both equal to 0
filtered_comments_df = comments_df[(comments_df['polarity'] != 0) | (comments_df['subjectivity'] != 0)]

# Define thresholds for classifying comments
positive_threshold = 0.2
negative_threshold = -0.2

# Function to classify comments into sentiment categories
def classify_sentiment(polarity):
    if polarity > positive_threshold:
        return 'Positive'
    elif polarity < negative_threshold:
        return 'Negative'
    else:
        return 'Neutral'

# Apply the function to classify sentiments
filtered_comments_df['sentiment_label'] = filtered_comments_df['polarity'].apply(classify_sentiment)

# Display the DataFrame with sentiment labels
st.write("### Polarity of comments")
st.dataframe(filtered_comments_df[['clean_text', 'polarity', 'sentiment_label']])

# Plot 1: Pie Chart of Sentiment Distribution
sentiment_distribution = filtered_comments_df['sentiment_label'].value_counts(normalize=True)
fig1, ax1 = plt.subplots(figsize=(8, 6))
ax1.pie(sentiment_distribution, labels=sentiment_distribution.index, autopct='%1.1f%%', startangle=140)
ax1.set_title('Categories')
ax1.axis('equal')

# Display the pie chart using Streamlit
st.write("## Category-wise distribution: <span style='color:blue;'>Positive😀</span>, <span style='color:orange;'>Neutral😐</span> & <span style='color:green;'>Negative😡</span>.", unsafe_allow_html=True)
st.pyplot(fig1)

# Preprocess text data
df['clean_text'] = df['text'].apply(preprocess_text)

# Select top 30 most frequent words
top_words = pd.Series(' '.join(df['clean_text']).split()).value_counts()[:30]

# Generate WordCloud for top 30 words
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(' '.join(top_words.index))

# Display WordCloud
st.write("### <span style='color:orange;'>Most Frequent Words</span> phrases", unsafe_allow_html=True)
fig, ax = plt.subplots(figsize=(10, 6))
ax.imshow(wordcloud, interpolation='bilinear')
ax.axis('off')
st.pyplot(fig)

# Sort comments by polarity scores (positive comments will have higher polarity scores)
top_positive_comments = filtered_comments_df[filtered_comments_df['polarity'] > 0].sort_values(by='polarity', ascending=False).head(20)
top_negative_comments = filtered_comments_df[filtered_comments_df['polarity'] < 0].sort_values(by='polarity').head(20)

# Concatenate positive and negative comments
top_comments = pd.concat([top_positive_comments, top_negative_comments])

# Truncate long comments
top_comments['truncated_text'] = top_comments['clean_text'].apply(lambda x: x[:100] + '...' if len(x) > 100 else x)

# Plot horizontal bar chart
fig3, ax3 = plt.subplots(figsize=(10, 8))
ax3.barh(top_comments['truncated_text'], top_comments['polarity'], color=['green' if x > 0 else 'red' for x in top_comments['polarity']])
ax3.set_xlabel('Polarity')
ax3.set_ylabel('Comment')
ax3.set_title('Top 20 Positive and Negative Comments')
ax3.grid(axis='x')

# Display the horizontal bar chart using Streamlit
st.write("## Top <span style='color:green;'>Positive</span> and <span style='color:red;'>Negative</span> comments with highest polarity", unsafe_allow_html=True)
st.pyplot(fig3)

st.markdown("<br><br> Powered by <a href='https://github.com/SAMFUSEDBITS' style='font-size: 20px;'>SamFusedBits</a>⚡", unsafe_allow_html=True)