import streamlit as st
import requests

# Streamlit app title
st.title("YouTube Video Transcriber")

# Input field for the YouTube URL
video_url = st.text_input("Enter YouTube URL")

# Button to transcribe the video
if st.button("Transcribe"):
    if video_url:
        # Define the FastAPI endpoint
        api_url = "https://fast-api-server-aoxg.onrender.com/transcribe"
        
        try:
            # Send GET request to the FastAPI endpoint
            response = requests.get(api_url, params={"video_url": video_url})
            
            if response.status_code == 200:
                data = response.json()
                if "transcript" in data:
                    # Display the transcript
                    st.subheader("Transcript")
                    st.write(data["transcript"])
                else:
                    st.error(data["error"])
            else:
                st.error("Failed to retrieve transcript")
        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred: {e}")
    else:
        st.error("Please enter a valid YouTube URL")




