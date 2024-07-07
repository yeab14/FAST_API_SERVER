import logging
import re
import asyncio
import concurrent.futures
from youtube_transcript_api import YouTubeTranscriptApi, CouldNotRetrieveTranscript, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from cachetools import TTLCache


# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize FastAPI
app = FastAPI()

# Initialize YouTubeTranscriptApi instance eagerly for multiple languages
initialization_video_id = "rkB4g7XdyfM"
languages_to_initialize = ["en", "de", "es", "fr", "ru", "ja", "ko", "zh-Hans", "zh-Hant", "it", "pt", "nl", "ar"]

def initialize_languages():
    for lang in languages_to_initialize:
        try:
            YouTubeTranscriptApi.get_transcript(initialization_video_id, languages=[lang])
            logging.info(f"Successfully initialized YouTubeTranscriptApi for language {lang}")
        except Exception as e:
            logging.error(f"Failed to initialize YouTubeTranscriptApi for language {lang}: {e}")

initialize_languages()

# Configure CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Function to extract video ID from URL
def extract_video_id(url: str):
    video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return video_id_match.group(1) if video_id_match else None

# Asynchronous function to fetch transcript data
async def fetch_transcript(youtube_video_id: str, language: str):
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        return await loop.run_in_executor(
            pool, YouTubeTranscriptApi.get_transcript, youtube_video_id, [language]
        )

# Asynchronous function to extract transcript data
async def extract_transcript_data(youtube_video_id: str):
    language_codes = ["en", "de", "es", "fr", "ru", "ja", "ko", "zh-Hans", "zh-Hant", "it", "pt", "nl", "ar"]
    transcript_text = ""

    for code in language_codes:
        try:
            transcript = await fetch_transcript(youtube_video_id, code)
            transcript_text = " ".join([i["text"] for i in transcript])
            return {"transcript": transcript_text, "language": code}
        except (NoTranscriptFound, CouldNotRetrieveTranscript):
            continue  # Try the next language
        except VideoUnavailable:
            raise HTTPException(status_code=404, detail="Video is unavailable")
        except TranscriptsDisabled:
            raise HTTPException(status_code=403, detail="Transcripts are disabled for this video")
        except Exception as e:
            logging.error(f"Error fetching transcript for language {code}: {e}")
            continue

    raise HTTPException(status_code=404, detail="No transcript found for this video in the supported languages")

# Initialize cache
cache = TTLCache(maxsize=100, ttl=86400)  # Cache up to 100 transcripts for 1 day

# Function to cache transcript data
async def get_cached_transcript_data(youtube_video_id: str):
    if youtube_video_id in cache:
        return cache[youtube_video_id]
    transcript_data = await extract_transcript_data(youtube_video_id)
    cache[youtube_video_id] = transcript_data
    return transcript_data

# Endpoint to transcribe YouTube video
@app.get("/transcribe")
async def transcribe(video_url: str = Query(..., description="The YouTube video URL")):
    video_id = extract_video_id(video_url)
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    try:
        transcript_data = await get_cached_transcript_data(video_id)
        return transcript_data
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Unexpected error during transcription: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    port = 9001
    
    uvicorn.run(app, host="0.0.0.0", port=port)




