# YouTube Videos & Shorts Sentiment Analysis

YoutubeSenti, a tool designed to help users analyze the sentiment of comments on both YouTube videos and shorts. By fetching comments from a specified video and performing sentiment analysis, users can gain insights into the overall sentiment distribution and identify popular words used by viewers.

## Live

    youtubesenti.streamlit.app

## Features

- Fetch comments from YouTube video based on the video ID.
- Perform sentiment analysis on the fetched comments.
- Visualize sentiment distribution using pie charts.
- Generate word clouds to visualize popular words in the comments.
- Display top positive and negative comments.

## Installation

1. Clone the repository:

   git clone https://github.com/SamFusedBits/YoutubeSenti.git

2. Install the required Python packages:
   
   pip install -r requirements.txt

## Usage

1. Run the Streamlit app:
   
        streamlit run app.py

2. Enter the YouTube Video ID in the provided text box.

3. Click the "Enter" button to retrieve comments and analyze sentiment.

## Contributing

Contributions are welcome! If you find any bugs or have suggestions for improvements, please open an issue or submit a pull request.

## License

[MIT License](LICENSE)