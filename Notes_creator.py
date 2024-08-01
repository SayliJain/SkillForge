import streamlit as st
from googleapiclient.discovery import build
from IPython.display import YouTubeVideo, display
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import google.generativeai as genai
from urllib.parse import urlparse, parse_qs

YOUTUBE_DATA_API_KEY = "AIzaSyDWSmR2qRaTviw739lZObCIKUM9FREHN2U"
GEMINI_API_KEY = "AIzaSyCeG-08H7jsgXlkRHdggXgPQe4Ujlgg7UE"

# Configure the YouTube and Gemini API clients
youtube = build(serviceName='youtube', version='v3', developerKey=YOUTUBE_DATA_API_KEY)
genai.configure(api_key=GEMINI_API_KEY)
genai_model = genai.GenerativeModel('gemini-pro')

class Search_Response:
    def __init__(self, search_response):
        self.prev_page_token = search_response.get('prevPageToken')
        self.next_page_token = search_response.get('nextPageToken')
        items = search_response.get('items', [])
        self.search_results = [Search_Result(item) for item in items]

class Search_Result:
    def __init__(self, search_result):
        self.video_id = search_result['id']['videoId']
        self.title = search_result['snippet']['title']
        self.description = search_result['snippet']['description']
        self.thumbnails = search_result['snippet']['thumbnails']['default']['url']

def search_yt(query, max_results=5, page_token=None):
    request = youtube.search().list(
        part="snippet",
        maxResults=max_results,
        pageToken=page_token,
        q=query,
        videoCaption='closedCaption',
        type='video',
    )
    response = request.execute()
    return Search_Response(response)

def display_yt_results(search_response, extract_prompt=None):
    for search_result in search_response.search_results:
        st.write(f'### {search_result.title}')
        st.video(f'https://www.youtube.com/watch?v={search_result.video_id}')
        if extract_prompt is not None:
            transcript = get_transcript(search_result.video_id)
            extracted_text, _, _ = get_ai_extract(extract_prompt, transcript)
            st.write("#### Extracted Notes:")
            st.write(extracted_text)

def get_transcript(video_id, languages=['en', 'en-US', 'en-GB']):
    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
    transcript = TextFormatter().format_transcript(transcript)
    return transcript

def get_ai_extract(prompt, text):
    response = genai_model.generate_content(prompt + text, stream=False)
    return response.text, response.prompt_feedback, response.candidates

def extract_video_id(youtube_link):
    parsed_url = urlparse(youtube_link)
    video_id = parse_qs(parsed_url.query).get('v')
    return video_id[0] if video_id else None

def get_summary_from_youtube_link(youtube_link, extract_prompt="Summarize video content and give Notes: "):
    video_id = extract_video_id(youtube_link)
    if video_id:
        transcript = get_transcript(video_id)
        summary, _, _ = get_ai_extract(extract_prompt, transcript)
        return summary
    else:
        return "Invalid YouTube link. Please provide a valid link."

# Streamlit application
st.title("YouTube Video Summarizer and Note Extractor")

choice = st.radio("Do you want to provide a YouTube video link or search for a term?", ('link', 'search'))

if choice == 'link':
    youtube_link = st.text_input("Enter the YouTube video link:")
    if st.button("Get Summary and Notes"):
        summary = get_summary_from_youtube_link(youtube_link)
        st.write("### Video Summary and Notes:")
        st.write(summary)
elif choice == 'search':
    search_term = st.text_input("Enter the search term:")
    if st.button("Search and Extract Notes"):
        search_response = search_yt(search_term, max_results=2)
        display_yt_results(search_response, 'Extract notes from this video: ')
