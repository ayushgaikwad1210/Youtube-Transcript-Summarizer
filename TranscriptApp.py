# Import all the necessary dependencies
from flask import Flask, request
from youtube_transcript_api import YouTubeTranscriptApi
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from collections import defaultdict

application = Flask(__name__)

@application.get('/summary')
def summary_api():
    """
    Summarizes the transcript of a YouTube video.

    This function takes a YouTube video URL and an optional max_length parameter.
    It first retrieves the transcript of the YouTube video using subtitles.
    Then, it generates a summary of the transcript using TextRank algorithm.

    Parameters:
    - url (str): The URL of the YouTube video.
    - max_length (int, optional): The maximum length of the summary. Defaults to 150.

    Returns:
    - str: The summarized transcript.
    - int: HTTP status code (200 for success, 404 for failure).
    """
    url = request.args.get('url', '')
    max_length = int(request.args.get('max_length', 150))
    language = request.args.get('language', 'en')
    video_id = get_video_id(url)

    try:
        transcript = get_transcript(video_id, language)
    except Exception as e:
        return "Error: {}".format(str(e)), 404

    summary = generate_summary(transcript, max_length)

    return summary, 200

def get_video_id(url):
    """
    Extracts the video ID from a YouTube video URL.

    Parameters:
    - url (str): The URL of the YouTube video.

    Returns:
    - str: The video ID.
    """
    video_id = url.split('=')[-1]
    return video_id

def get_transcript(video_id, language='en'):
    """
    Retrieves the transcript of a YouTube video using subtitles.

    Parameters:
    - video_id (str): The ID of the YouTube video.
    - language (str, optional): The language of the transcript. Defaults to 'en'.

    Returns:
    - str: The transcript text.
    """
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
        transcript = ' '.join([d['text'] for d in transcript_list])
        return transcript
    except Exception as e:
        raise e

def generate_summary(transcript, max_length_words):
    """
    Generates a summary of the transcript based on word count.

    Parameters:
    - transcript (str): The transcript text.
    - max_length_words (int): The maximum length of the summary (in words).

    Returns:
    - str: The summarized transcript.
    """
    # Tokenize the transcript into sentences
    sentences = sent_tokenize(transcript)

    # Tokenize the sentences into words and remove stopwords
    stop_words = set(stopwords.words('english'))
    words = [word for sentence in sentences for word in word_tokenize(sentence.lower()) if word.isalpha() and word not in stop_words]

    # Calculate word frequencies
    word_freq = defaultdict(int)
    for word in words:
        word_freq[word] += 1

    # Calculate sentence scores based on word frequencies
    sentence_scores = defaultdict(int)
    for i, sentence in enumerate(sentences):
        for word in word_tokenize(sentence.lower()):
            if word in word_freq:
                sentence_scores[i] += word_freq[word]

    # Select top sentences based on scores until the maximum word limit is reached
    total_words = 0
    summary_sentences = []
    for i in sorted(sentence_scores, key=sentence_scores.get, reverse=True):
        summary_sentences.append(sentences[i])
        total_words += len(word_tokenize(sentences[i]))
        if total_words >= max_length_words:
            break

    # Combine summary sentences into a summary
    summary = ' '.join(summary_sentences)

    return summary

if __name__ == '__main__':
    application.run(debug=True)
