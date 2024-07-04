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
        api_url = "http://185.124.109.231:9000/transcribe"
        
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
                    st.error(f"Error: {data.get('error', 'Unknown error')}")
            else:
                st.error(f"Error: Failed to retrieve transcript. Status code {response.status_code}")
        
        except requests.exceptions.RequestException as e:
            st.error(f"Error: An exception occurred: {str(e)}")
    else:
        st.error("Error: Please enter a valid YouTube URL")




