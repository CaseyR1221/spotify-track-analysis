import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import os
from datetime import datetime
import json

# Spotify API credentials
SPOTIPY_CLIENT_ID = os.environ.get('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.environ.get('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = 'http://localhost:5000'

# Set Spotify scopes
scope = "user-read-recently-played"

# Spotify API client
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope=scope
))

# Path to store CSV file
csv_file_path = './play_history.csv'

# Function to fetch recently played tracks
def get_recently_played_tracks():
    data = sp.current_user_recently_played(limit=10)
    return data['items']

def get_audio_features(id):
    audio_features = sp.audio_features(id) 
    return audio_features

# Function to load CSV into a DataFrame or create a new one if file doesn't exist
def load_csv_data():
    if os.path.exists(csv_file_path):
        print('File exists')
        return pd.read_csv(csv_file_path)
    else:
        # Create a new empty DataFrame if the file does not exist
        print('File does not exist')
        return pd.DataFrame(columns=['track_name', 'artist_name', 'danceability', 'energy', 'valence', 'played_at', 'track_id', 'play_count'])

# Function to append new data or update existing data in the DataFrame
def append_or_update_data(df, new_tracks):
    for track_id, track_info in new_tracks.items():
        if track_id in df['track_id'].values:
            # Update play_count and played_at for existing tracks
            df.loc[df['track_id'] == track_id, 'play_count'] += 1
            df.loc[df['track_id'] == track_id, 'played_at'] = track_info['played_at']
        else:
            # Append new tracks
            new_row = pd.Series({
                'track_name': track_info['track_name'],
                'artist_name': track_info['artist_name'],
                'danceability': track_info['danceability'],
                "energy": track_info['energy'],
                'valence': track_info['valence'],
                'played_at': track_info['played_at'],
                'track_id': track_id,
                'play_count': 1
            })
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    return df

# Main script
if __name__ == "__main__":
    # Fetch recently played tracks
    tracks = get_recently_played_tracks()
    
    # x = json.dumps(tracks, indent=4)
    # print(x)

    # Load existing CSV data into a DataFrame
    df = load_csv_data()

    # Prepare new tracks data
    new_tracks = {}
    for track in tracks:
        # Get audio features for the track
        af = get_audio_features(track['track']['id'])
        
        track_name = track['track']['name']
        artist_name = ', '.join([artist['name'] for artist in track['track']['artists']])
        danceability = af[0]['danceability']
        energy = af[0]['energy']
        valence = af[0]['valence']
        played_at = datetime.strptime(track['played_at'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S')
        track_id = track['track']['id']

        new_tracks[track_id] = {
            'track_name': track_name,
            'artist_name': artist_name,
            'danceability': danceability,
            'energy': energy,
            'valence': valence,
            'played_at': played_at,
            'track_id': track_id
        }
    
    # Append or update DataFrame with new data
    df = append_or_update_data(df, new_tracks)

    # Write updated DataFrame back to the CSV
    df.to_csv(csv_file_path, index=False)
    
    print(df)