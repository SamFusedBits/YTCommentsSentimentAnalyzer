import streamlit as st
import googleapiclient.discovery
import pandas as pd
import matplotlib.pyplot as plt
import os
import re
from textblob import TextBlob
from wordcloud import WordCloud

# Page configuration
st.set_page_config(
    page_title="YouTube Sentiment Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Global styles
custom_css = """
    <style>
        /* Global Styling */
        body {
            font-family: 'Roboto', sans-serif;
            background-color: #f9f9f9;
        }

        /* Sidebar */
        .css-1d391kg {
            background-color: #f1f1f1;
            border-right: 1px solid #ddd;
        }

        /* Title and Headers */
        h1, h2, h3 {
            color: #ff0000; /* YouTube Red */
            font-weight: bold;
        }

        /* Buttons */
        .stButton > button {
            background-color: #ff0000;
            color: white;
            border-radius: 5px;
            font-size: 16px;
            padding: 10px;
            border: none;
            cursor: pointer;
        }
        
        .stButton > button:hover {
            background-color: #e60000;
        }

        /* DataFrames */
        .dataframe {
            border: 1px solid #ddd;
            border-radius: 8px;
        }

        /* Footer */
        .footer {
            text-align: center;
            font-size: 14px;
            margin-top: 50px;
            color: #666;
        }
        .footer a {
            text-decoration: none;
            color: #ff0000;
        }
    </style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Header section
st.markdown(
    """
    <div style="text-align: center; margin-bottom: 20px;">
        <h1>YouTube Sentiment Analysis</h1>
        <p style="color: #555;">Analyze viewer sentiments and trends in YouTube comments</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Function to fetch comments from YouTube
def getcomments(video):
    try:
        api_service_name = "youtube"
        api_version = "v3"
        youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=st.secrets["DEVELOPER_KEY"])

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

# Sidebar instructions
st.sidebar.markdown(
    """
    ### Instructions
    - Enter the **YouTube Video ID** below.
    - Click **Fetch Comments** to start analysis.
    - View sentiment distribution, frequent words, and top comments.
    """
)

# Sidebar input
video_id = st.sidebar.text_input(
    "🎥 Enter YouTube Video ID",
    placeholder="e.g., xQqsvRHjas4",
    help="You can find the video ID in the URL after 'v='.",
)

# Sidebar actions
if st.sidebar.button("Fetch Comments"):
    st.experimental_rerun()

# Fetch and analyze comments
if video_id:

    st.write("### Top comments from the video")
    # Fetch comments based on input video ID
    comments_df = getcomments(video_id)
    st.dataframe(comments_df)
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
    st.markdown("<h1 style='color:orange;'>Sentiment Analysis and Insights</h1>", unsafe_allow_html=True)

    # Preprocess text data
    # Apply preprocessing to the text data
    comments_df['clean_text'] = comments_df['text'].apply(preprocess_text)

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
    st.write("### Polarity of Comments")
    st.dataframe(filtered_comments_df[['clean_text', 'polarity', 'sentiment_label']])

    # Plot 1: Pie Chart of Sentiment Distribution
    sentiment_distribution = filtered_comments_df['sentiment_label'].value_counts(normalize=True)
    fig1, ax1 = plt.subplots(figsize=(13, 6))
    ax1.pie(sentiment_distribution, labels=sentiment_distribution.index, autopct='%1.1f%%', startangle=140)
    ax1.set_title('Categories')
    ax1.axis('equal')

    # Display the pie chart using Streamlit
    st.write("## Sentiment Breakdown: <span style='color:orange;'>Positive😀</span>, <span style='color:blue;'>Neutral😐</span> & <span style='color:green;'>Negative😡</span>.", unsafe_allow_html=True)
    st.pyplot(fig1)

    df = getcomments(video_id)
    # Preprocess text data
    df['clean_text'] = df['text'].apply(preprocess_text)

    # Select top 30 most frequent words
    top_words = pd.Series(' '.join(df['clean_text']).split()).value_counts()[:30]

    # Generate WordCloud for top 30 words
    wordcloud = WordCloud(width=800, height=300, background_color='white').generate(' '.join(top_words.index))

    # Display WordCloud
    st.write("### <span style='color:orange;'>Most Frequent</span> Words", unsafe_allow_html=True)
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
    st.write("## <span style='color:orange;'>Top</span> <span style='color:green;'>Positive</span> <span style='color:orange;'>&</span> <span style='color:red;'>Negative</span> <span style='color:orange;'>comments with highest polarity</span>", unsafe_allow_html=True)
    st.pyplot(fig3)

# Footer
st.markdown(
    """
    <div class="footer">
        Built with ❤️ by <a href="https://github.com/SAMFUSEDBITS">SamFusedBits</a> ⚡
    </div>
    """,
    unsafe_allow_html=True,
)