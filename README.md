# Spotify-Song-Analyzer
A Spotify-powered Streamlit app that analyzes songs with audio features, charts, track insights, and a built-in 30-second music preview. Upload datasets, explore artists, and visualize music like never before.



🚀 Features
🔍 Track Search & Insights
-Search any track by song name + artist
-Displays:
-Album cover
-Artist & album
-Release date
-Popularity score
-Track duration
-Spotify external link

🎧 Music Preview Player
-Built-in 30-second audio preview
-If unavailable, auto-fallback to:
--Spotify Embed
--YouTube Music
--YouTube Search

📊 Audio Feature Analysis
Fully interactive charts generated using Plotly:
-Bar Chart – audio feature comparison
-Radar Chart – overall sound profile
-Tempo Gauge – BPM indicator

Audio features include:
-Danceability
-Energy
-Speechiness
-Acousticness
-Instrumentalness
-Liveness
-Valence
-Tempo

📁 Dataset Upload & Exploration
-Upload your own CSV dataset
-View the dataset in a scrollable table
-Includes basic dataset statistics:
--Total tracks
--Unique artists
--Unique albums
--Average popularity

🎨 Modern Spotify-Styled UI
Built using custom CSS (style.css):
-Glassmorphism cards
-Gradient animations
-Custom buttons & input fields
-Responsive layout

📂 Project Structure
📦 Spotify Song Analyzer
├── app.py                # Main Streamlit application
├── music.py              # Spotify API + preview + audio features
├── display_dataset.py    # Dataset viewer module
├── style.css             # Modern Spotify-themed UI styling
├── cleaned_dataset.csv   # Sample dataset
└── README.md

🛠️ Tech Stack
-Python
-Streamlit
-Spotipy (Spotify API)
-Plotly
-Pandas / NumPy
-Custom CSS

#main
Add Spotify API Credentials
In music.py, update:

CLIENT_ID = "your_spotify_client_id"
CLIENT_SECRET = "your_spotify_client_secret"
Create credentials here:
👉 https://developer.spotify.com/dashboard/
