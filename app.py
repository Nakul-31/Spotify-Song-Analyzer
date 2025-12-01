# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from music import get_track_preview, initialize_spotify_client, create_spotify_embed
import base64
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Spotify Song Analyzer",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load custom CSS
def load_css():
    """Load custom CSS styling"""
    css_file = Path("style.css")
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning("style.css not found")

load_css()

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = None
if 'selected_track' not in st.session_state:
    st.session_state.selected_track = None

# Header section
st.markdown("""
    <div class="header-container">
        <div class="spotify-logo">🎵</div>
        <h1 class="main-title">Spotify Song Analyzer</h1>
        <p class="subtitle">Discover the audio characteristics of your favorite tracks</p>
    </div>
""", unsafe_allow_html=True)

# File upload section
st.markdown('<div class="section-divider"><span>📁 Upload Dataset</span></div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    uploaded_file = st.file_uploader(
        "Upload your Spotify dataset (CSV)",
        type=['csv'],
        help="Upload a CSV file containing track information"
    )

if uploaded_file is not None:
    try:
        st.session_state.df = pd.read_csv(uploaded_file)
        st.success(f"✅ Dataset loaded successfully! ({len(st.session_state.df)} tracks)")
    except Exception as e:
        st.error(f"❌ Error loading file: {e}")

# Load default dataset if no file uploaded
if st.session_state.df is None:
    try:
        st.session_state.df = pd.read_csv('songs.csv')
        st.info("ℹ️ Using default dataset (songs.csv)")
    except:
        st.warning("⚠️ No dataset available. Please upload a CSV file.")

# Main analysis section
if st.session_state.df is not None:
    df = st.session_state.df
    
    # Selection section
    st.markdown('<div class="section-divider"><span>🎧 Select Track</span></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        artists = sorted(df['artist'].unique())
        selected_artist = st.selectbox(
            "Choose Artist",
            options=artists,
            key="artist_select"
        )
    
    with col2:
        artist_songs = df[df['artist'] == selected_artist]['track_name'].unique()
        selected_song = st.selectbox(
            "Choose Song",
            options=sorted(artist_songs),
            key="song_select"
        )
    
    # Fetch track data button
    if st.button("🔍 Analyze Track", use_container_width=True):
        with st.spinner("🎵 Fetching track data from Spotify..."):
            track_data, error = get_track_preview(selected_song, selected_artist)
            
            if track_data:
                st.session_state.selected_track = track_data
                if error:
                    st.warning(f"⚠️ {error}")
                else:
                    st.success("✅ Track data loaded successfully!")
            else:
                st.error(f"❌ {error if error else 'Unable to fetch track data'}")
                st.session_state.selected_track = None
    
    # Display track information
    if st.session_state.selected_track:
        track = st.session_state.selected_track
        
        st.markdown('<div class="section-divider"><span>🎵 Track Information</span></div>', unsafe_allow_html=True)
        
        # Track card
        col1, col2 = st.columns([1, 2])
        
        with col1:
            if track.get('album_image'):
                st.markdown(f"""
                    <div class="album-card">
                        <img src="{track['album_image']}" class="album-image">
                    </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="info-card">
                    <h2 class="track-title">{track['name']}</h2>
                    <p class="track-artist">by {track['artist']}</p>
                    <div class="track-details">
                        <div class="detail-item">
                            <span class="detail-label">Album:</span>
                            <span class="detail-value">{track['album']}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Release Date:</span>
                            <span class="detail-value">{track['release_date']}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Popularity:</span>
                            <span class="detail-value">{track['popularity']}/100</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Duration:</span>
                            <span class="detail-value">{track['duration_ms'] // 60000}:{(track['duration_ms'] // 1000) % 60:02d}</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        # Audio player - 30 second preview with styled player
        st.markdown('<div class="section-divider"><span>▶️ Music Player</span></div>', unsafe_allow_html=True)
        
        if track.get('preview_url'):
            # Custom styled 30-second preview player
            player_html = f"""
            <div style="background: linear-gradient(135deg, rgba(29, 185, 84, 0.15) 0%, rgba(30, 215, 96, 0.1) 100%); 
                        padding: 25px; 
                        border-radius: 20px; 
                        backdrop-filter: blur(10px); 
                        border: 2px solid rgba(29, 185, 84, 0.4); 
                        box-shadow: 0 8px 32px rgba(29, 185, 84, 0.3);
                        margin-bottom: 2rem;">
                <div style="display: flex; align-items: center; gap: 20px; margin-bottom: 15px;">
                    <img src="{track['album_image']}" 
                         alt="Album Art" 
                         style="width: 80px; 
                                height: 80px; 
                                border-radius: 12px; 
                                box-shadow: 0 4px 15px rgba(0,0,0,0.5);">
                    <div>
                        <h3 style="color: #1DB954; margin: 0; font-size: 1.3rem; font-weight: 700;">{track['name']}</h3>
                        <p style="color: rgba(255, 255, 255, 0.8); margin: 5px 0 0 0; font-size: 1rem;">{track['artist']}</p>
                    </div>
                </div>
                <audio controls 
                       style="width: 100%; 
                              margin-top: 10px;
                              border-radius: 25px;
                              filter: brightness(0.9) contrast(1.1);">
                    <source src="{track['preview_url']}" type="audio/mpeg">
                    Your browser does not support the audio element.
                </audio>
                <p style="color: #1DB954; 
                          font-size: 0.85rem; 
                          margin-top: 10px; 
                          text-align: center;
                          font-weight: 600;">
                    🎧 30-Second Preview Available
                </p>
            </div>
            """
            st.components.v1.html(player_html, height=200)
            
        else:
            # Show Spotify embed when preview not available
            st.markdown("""
                <div style="background: linear-gradient(135deg, rgba(255, 193, 7, 0.1) 0%, rgba(255, 152, 0, 0.05) 100%); 
                            border-radius: 15px; 
                            padding: 1.5rem; 
                            backdrop-filter: blur(10px); 
                            border: 2px solid rgba(255, 193, 7, 0.4); 
                            box-shadow: 0 8px 32px rgba(255, 193, 7, 0.2);
                            margin-bottom: 1.5rem;
                            text-align: center;">
                    <p style="color: #FFC107; margin-bottom: 0.5rem; font-weight: 600; font-size: 1.1rem;">
                        ⚠️ 30-Second Preview Not Available For All Songs
                    </p>
                    <p style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem; margin-bottom: 1rem;">
                        Due to licensing restrictions, this track doesn't have a 30-second preview
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            # Show Spotify embed player
            st.markdown("### 🎵 Listen on Spotify")
            embed_html = create_spotify_embed(track['id'])
            st.components.v1.html(embed_html, height=180)
        
        # Always show listening options
        st.markdown("""
            <div style="background: rgba(255, 255, 255, 0.03); 
                        border-radius: 15px; 
                        padding: 1.5rem; 
                        backdrop-filter: blur(10px); 
                        border: 1px solid rgba(29, 185, 84, 0.2);
                        margin-top: 1.5rem;">
                <h4 style="color: #1DB954; text-align: center; margin-bottom: 1rem;">🎵 Listen to Full Track</h4>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
                <a href="{track['external_url']}" target="_blank" 
                   style="display: block; 
                          background: linear-gradient(135deg, #1DB954 0%, #1ed760 100%); 
                          color: white; 
                          text-decoration: none; 
                          padding: 1rem; 
                          border-radius: 12px; 
                          text-align: center; 
                          font-weight: 600;
                          transition: transform 0.2s;
                          box-shadow: 0 4px 15px rgba(29, 185, 84, 0.3);"
                   onmouseover="this.style.transform='translateY(-3px)'"
                   onmouseout="this.style.transform='translateY(0)'">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">🎵</div>
                    <div>Spotify</div>
                </a>
            """, unsafe_allow_html=True)
        
        with col2:
            if track.get('alternatives'):
                st.markdown(f"""
                    <a href="{track['alternatives']['youtube_music']}" target="_blank" 
                       style="display: block; 
                              background: linear-gradient(135deg, #FF0000 0%, #CC0000 100%); 
                              color: white; 
                              text-decoration: none; 
                              padding: 1rem; 
                              border-radius: 12px; 
                              text-align: center; 
                              font-weight: 600;
                              transition: transform 0.2s;
                              box-shadow: 0 4px 15px rgba(255, 0, 0, 0.3);"
                       onmouseover="this.style.transform='translateY(-3px)'"
                       onmouseout="this.style.transform='translateY(0)'">
                        <div style="font-size: 2rem; margin-bottom: 0.5rem;">🎥</div>
                        <div>YouTube Music</div>
                    </a>
                """, unsafe_allow_html=True)
        
        with col3:
            if track.get('alternatives'):
                st.markdown(f"""
                    <a href="{track['alternatives']['youtube_search']}" target="_blank" 
                       style="display: block; 
                              background: linear-gradient(135deg, #FF6B6B 0%, #FF5252 100%); 
                              color: white; 
                              text-decoration: none; 
                              padding: 1rem; 
                              border-radius: 12px; 
                              text-align: center; 
                              font-weight: 600;
                              transition: transform 0.2s;
                              box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);"
                       onmouseover="this.style.transform='translateY(-3px)'"
                       onmouseout="this.style.transform='translateY(0)'">
                        <div style="font-size: 2rem; margin-bottom: 0.5rem;">▶️</div>
                        <div>YouTube</div>
                    </a>
                """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Audio features visualization
        if track.get('audio_features'):
            features = track['audio_features']
            
            st.markdown('<div class="section-divider"><span>📊 Audio Features Analysis</span></div>', unsafe_allow_html=True)
            
            # Feature cards grid
            col1, col2, col3, col4 = st.columns(4)
            
            feature_items = [
                ('Danceability', features['danceability'], '💃'),
                ('Energy', features['energy'], '⚡'),
                ('Speechiness', features['speechiness'], '🗣️'),
                ('Acousticness', features['acousticness'], '🎸'),
                ('Instrumentalness', features['instrumentalness'], '🎹'),
                ('Liveness', features['liveness'], '🎤'),
                ('Valence', features['valence'], '😊'),
                ('Tempo', features['tempo'], '🥁')
            ]
            
            cols = [col1, col2, col3, col4]
            for idx, (name, value, icon) in enumerate(feature_items):
                with cols[idx % 4]:
                    if name == 'Tempo':
                        st.markdown(f"""
                            <div class="feature-card">
                                <div class="feature-icon">{icon}</div>
                                <div class="feature-name">{name}</div>
                                <div class="feature-value">{value:.0f} BPM</div>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                            <div class="feature-card">
                                <div class="feature-icon">{icon}</div>
                                <div class="feature-name">{name}</div>
                                <div class="feature-value">{value:.1f}%</div>
                            </div>
                        """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Bar chart for audio features
            st.markdown("### 📊 Feature Distribution")
            feature_names = ['Danceability', 'Energy', 'Speechiness', 'Acousticness', 
                           'Instrumentalness', 'Liveness', 'Valence']
            feature_values = [features['danceability'], features['energy'], features['speechiness'],
                            features['acousticness'], features['instrumentalness'], 
                            features['liveness'], features['valence']]
            
            fig_bar = go.Figure(data=[
                go.Bar(
                    x=feature_names,
                    y=feature_values,
                    marker=dict(
                        color=feature_values,
                        colorscale=[[0, '#0a4d2e'], [0.5, '#1DB954'], [1, '#1ed760']],
                        line=dict(color='#1DB954', width=2)
                    ),
                    text=[f'{v:.1f}%' for v in feature_values],
                    textposition='outside',
                    textfont=dict(color='white', size=14, family='Poppins')
                )
            ])
            
            fig_bar.update_layout(
                plot_bgcolor='rgba(10, 14, 39, 0.5)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', family='Poppins'),
                yaxis=dict(
                    range=[0, 110], 
                    title=dict(text='Percentage (%)', font=dict(size=14)),
                    gridcolor='rgba(255,255,255,0.1)',
                    tickfont=dict(size=12)
                ),
                xaxis=dict(
                    title=dict(text='', font=dict(size=14)),
                    tickfont=dict(size=12)
                ),
                height=450,
                margin=dict(t=40, b=60, l=60, r=40),
                showlegend=False
            )
            
            st.plotly_chart(fig_bar, use_container_width=True, key="bar_chart")
            
            # Radar chart and Tempo Gauge
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🎯 Audio Profile Radar")
                fig_radar = go.Figure()
                
                fig_radar.add_trace(go.Scatterpolar(
                    r=feature_values,
                    theta=feature_names,
                    fill='toself',
                    fillcolor='rgba(29, 185, 84, 0.4)',
                    line=dict(color='#1DB954', width=3),
                    name='Audio Features',
                    marker=dict(size=8, color='#1ed760')
                ))
                
                fig_radar.update_layout(
                    polar=dict(
                        bgcolor='rgba(10, 14, 39, 0.5)',
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100],
                            gridcolor='rgba(255,255,255,0.2)',
                            tickfont=dict(color='white', size=11, family='Poppins'),
                            ticksuffix='%'
                        ),
                        angularaxis=dict(
                            gridcolor='rgba(255,255,255,0.2)',
                            tickfont=dict(color='white', size=12, family='Poppins', weight='bold')
                        )
                    ),
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white', family='Poppins'),
                    height=450,
                    margin=dict(t=60, b=60, l=60, r=60),
                    showlegend=False
                )
                
                st.plotly_chart(fig_radar, use_container_width=True, key="radar_chart")
            
            with col2:
                st.markdown("### 🎼 Tempo Gauge")
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=features['tempo'],
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Beats Per Minute", 'font': {'color': 'white', 'size': 20, 'family': 'Poppins'}},
                    number={'font': {'color': '#1DB954', 'size': 56, 'family': 'Poppins', 'weight': 'bold'}, 'suffix': ' BPM'},
                    delta={'reference': 120, 'increasing': {'color': "#1ed760"}, 'decreasing': {'color': "#1DB954"}},
                    gauge={
                        'axis': {'range': [0, 200], 'tickcolor': 'white', 'tickfont': {'size': 12, 'family': 'Poppins'}},
                        'bar': {'color': '#1DB954', 'thickness': 0.7},
                        'bgcolor': 'rgba(10, 14, 39, 0.5)',
                        'borderwidth': 3,
                        'bordercolor': '#1DB954',
                        'steps': [
                            {'range': [0, 60], 'color': 'rgba(29, 185, 84, 0.15)'},
                            {'range': [60, 120], 'color': 'rgba(29, 185, 84, 0.25)'},
                            {'range': [120, 180], 'color': 'rgba(29, 185, 84, 0.35)'},
                            {'range': [180, 200], 'color': 'rgba(29, 185, 84, 0.45)'}
                        ],
                        'threshold': {
                            'line': {'color': "#1ed760", 'width': 5},
                            'thickness': 0.8,
                            'value': features['tempo']
                        }
                    }
                ))
                
                fig_gauge.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white', family='Poppins'),
                    height=450,
                    margin=dict(t=80, b=60, l=40, r=40)
                )
                
                st.plotly_chart(fig_gauge, use_container_width=True, key="tempo_gauge")
        else:
            st.warning("⚠️ Audio features not available for this track.")
    
    # Dataset preview
    st.markdown('<div class="section-divider"><span>📋 Dataset Preview</span></div>', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="table-container">
    """, unsafe_allow_html=True)
    
    st.dataframe(
        df.head(20),
        use_container_width=True,
        height=400
    )
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Dataset statistics
    st.markdown('<div class="section-divider"><span>📈 Dataset Statistics</span></div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-icon">🎵</div>
                <div class="stat-label">Total Tracks</div>
                <div class="stat-value">{len(df)}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-icon">🎤</div>
                <div class="stat-label">Unique Artists</div>
                <div class="stat-value">{df['artist'].nunique()}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if 'popularity' in df.columns:
            avg_popularity = df['popularity'].mean()
            st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-icon">⭐</div>
                    <div class="stat-label">Avg Popularity</div>
                    <div class="stat-value">{avg_popularity:.1f}</div>
                </div>
            """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class="stat-card">
                <div class="stat-icon">💿</div>
                <div class="stat-label">Unique Albums</div>
                <div class="stat-value">{df['album'].nunique() if 'album' in df.columns else 'N/A'}</div>
            </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("""
    <div class="footer">
        <p>Designed By Nakul Dhiman</p>
        <p style="font-size: 0.8rem; opacity: 0.7;">🎵 Discover, Analyze, Enjoy Music</p>
    </div>
""", unsafe_allow_html=True)