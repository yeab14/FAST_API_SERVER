import logging
import re
import os
from youtube_transcript_api import YouTubeTranscriptApi, CouldNotRetrieveTranscript, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

# Configure COR
app = FastAPI()

# Origin of chrome extension or other allowed origins
origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)

# Function to extract video ID from URL
def extract_video_id(url: str):
    video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return video_id_match.group(1) if video_id_match else None

# Function to extract transcript data
def extract_transcript_data(youtube_video_id: str):
    language_codes = ["en", "de", "es", "fr", "ru"]  # English, German, Spanish, French, Russian
    transcript_text = ""
    
    for code in language_codes:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(youtube_video_id, languages=[code])
            transcript_text = " ".join([i["text"] for i in transcript])
            return {"transcript": transcript_text, "language": code}
        except (NoTranscriptFound, CouldNotRetrieveTranscript):
            continue  # Try the next language
        except VideoUnavailable:
            raise HTTPException(status_code=404, detail="Video is unavailable")
        except TranscriptsDisabled:
            raise HTTPException(status_code=403, detail="Transcripts are disabled for this video")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

    raise HTTPException(status_code=404, detail="No transcript found for this video in the supported languages")

@app.get("/transcribe")
def transcribe(video_url: str = Query(..., description="The YouTube video URL")):
    video_id = extract_video_id(video_url)
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    return extract_transcript_data(video_id)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)


