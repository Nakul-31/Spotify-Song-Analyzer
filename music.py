# music.py
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import logging
import requests
from urllib.parse import quote

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Spotify API credentials
CLIENT_ID = "349d45f233a44f31b4aa41a8a9d5e92e"
CLIENT_SECRET = "b42401046af9496292e08e70e4ccf75a"

# Initialize Spotify client
def initialize_spotify_client():
    """
    Initialize and return Spotify client with credentials
    """
    try:
        auth_manager = SpotifyClientCredentials(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET
        )
        sp = spotipy.Spotify(auth_manager=auth_manager)
        logger.info("Spotify client initialized successfully")
        return sp
    except Exception as e:
        logger.error(f"Error initializing Spotify client: {e}")
        return None

def search_track_with_preview(sp, track_name, artist_name):
    """
    Search for a track on Spotify with multiple attempts to find preview
    """
    try:
        # Try different search strategies
        search_queries = [
            f'track:"{track_name}" artist:"{artist_name}"',
            f'{track_name} {artist_name}',
            f'{track_name}',
        ]
        
        for query in search_queries:
            logger.info(f"Searching with query: {query}")
            results = sp.search(q=query, type='track', limit=10, market='US')
            
            if results['tracks']['items']:
                # First, try to find exact match with preview
                for track in results['tracks']['items']:
                    artist_match = any(artist_name.lower() in artist['name'].lower() 
                                     for artist in track['artists'])
                    track_match = track_name.lower() in track['name'].lower()
                    
                    if artist_match and track_match and track['preview_url']:
                        logger.info(f"Found exact match with preview: {track['name']}")
                        return create_track_info(track)
                
                # Then try any track with preview from results
                for track in results['tracks']['items']:
                    if track['preview_url']:
                        logger.info(f"Found track with preview: {track['name']}")
                        return create_track_info(track)
                
                # If no preview found, return first result
                track = results['tracks']['items'][0]
                logger.warning(f"No preview available, returning: {track['name']}")
                return create_track_info(track)
        
        return None
    except Exception as e:
        logger.error(f"Error in search_track_with_preview: {e}")
        return None

def create_track_info(track):
    """
    Create standardized track info dictionary
    """
    return {
        'id': track['id'],
        'name': track['name'],
        'artist': track['artists'][0]['name'],
        'album': track['album']['name'],
        'album_image': track['album']['images'][0]['url'] if track['album']['images'] else None,
        'preview_url': track['preview_url'],
        'popularity': track['popularity'],
        'release_date': track['album']['release_date'],
        'duration_ms': track['duration_ms'],
        'external_url': track['external_urls']['spotify'],
        'uri': track['uri']
    }

def get_alternative_preview_url(track_name, artist_name):
    """
    Generate alternative preview sources
    """
    alternatives = {
        'youtube_search': f"https://www.youtube.com/results?search_query={quote(track_name + ' ' + artist_name + ' audio')}",
        'youtube_music': f"https://music.youtube.com/search?q={quote(track_name + ' ' + artist_name)}",
        'soundcloud': f"https://soundcloud.com/search?q={quote(track_name + ' ' + artist_name)}",
    }
    return alternatives

def get_audio_features(sp, track_id):
    """
    Get audio features for a track
    Returns features like danceability, energy, tempo, etc.
    """
    try:
        logger.info(f"Fetching audio features for track ID: {track_id}")
        features = sp.audio_features(track_id)
        
        if features and features[0]:
            audio_data = features[0]
            logger.info("Audio features retrieved successfully")
            return {
                'danceability': audio_data.get('danceability', 0) * 100,
                'energy': audio_data.get('energy', 0) * 100,
                'speechiness': audio_data.get('speechiness', 0) * 100,
                'acousticness': audio_data.get('acousticness', 0) * 100,
                'instrumentalness': audio_data.get('instrumentalness', 0) * 100,
                'liveness': audio_data.get('liveness', 0) * 100,
                'valence': audio_data.get('valence', 0) * 100,
                'tempo': audio_data.get('tempo', 120),
                'loudness': audio_data.get('loudness', -5),
                'key': audio_data.get('key', 0),
                'mode': audio_data.get('mode', 1),
                'time_signature': audio_data.get('time_signature', 4)
            }
        
        # Return default values if no features available
        logger.warning("No audio features found, using defaults")
        return {
            'danceability': 50,
            'energy': 50,
            'speechiness': 10,
            'acousticness': 30,
            'instrumentalness': 20,
            'liveness': 15,
            'valence': 50,
            'tempo': 120,
            'loudness': -5,
            'key': 0,
            'mode': 1,
            'time_signature': 4
        }
    except Exception as e:
        logger.error(f"Error getting audio features: {e}")
        # Return default values
        return {
            'danceability': 50,
            'energy': 50,
            'speechiness': 10,
            'acousticness': 30,
            'instrumentalness': 20,
            'liveness': 15,
            'valence': 50,
            'tempo': 120,
            'loudness': -5,
            'key': 0,
            'mode': 1,
            'time_signature': 4
        }

def get_track_preview(track_name, artist_name):
    """
    Main function to get track preview URL and all information
    Returns complete track data including preview_url for playback
    """
    try:
        sp = initialize_spotify_client()
        if not sp:
            return None, "Failed to initialize Spotify client. Please check your credentials."
        
        track_info = search_track_with_preview(sp, track_name, artist_name)
        if not track_info:
            return None, f"Track '{track_name}' by '{artist_name}' not found on Spotify."
        
        # Get audio features (always, even if preview not available)
        audio_features = get_audio_features(sp, track_info['id'])
        track_info['audio_features'] = audio_features
        logger.info("Complete track data retrieved")
        
        # Get alternative preview sources
        track_info['alternatives'] = get_alternative_preview_url(track_name, artist_name)
        
        if not track_info['preview_url']:
            return track_info, "Spotify preview not available. Alternative listening options provided below."
        
        return track_info, None
        
    except Exception as e:
        logger.error(f"Error in get_track_preview: {e}")
        return None, f"An error occurred: {str(e)}"

def create_spotify_embed(track_id):
    """Create Spotify embed HTML for a given track ID"""
    embed_html = f"""
    <iframe src="https://open.spotify.com/embed/track/{track_id}" 
            width="100%" 
            height="152" 
            frameborder="0" 
            allowfullscreen="" 
            allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" 
            loading="lazy"
            style="border-radius: 12px;">
    </iframe>
    """
    return embed_html