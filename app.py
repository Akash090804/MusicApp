import requests
import base64
import pickle
import os
import pandas as pd
from flask import Flask, request, jsonify
from dotenv import load_dotenv,find_dotenv
 
dotenv =find_dotenv()
load_dotenv(dotenv)
# Initialize Flask app
app = Flask(__name__)

CLIENT_ID= os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# Function to get Spotify access token
def get_spotify_token():
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode(),
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print("Error getting token:", response.json())
        return None

# Function to fetch song details from Spotify
def fetch_song_details(song_title, token):
    url = f"https://api.spotify.com/v1/search?q={song_title}&type=track&limit=1"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        try:
            track = data['tracks']['items'][0]
            return {
                "title": track['name'],
                "album": track['album']['name'],
                "cover": track['album']['images'][0]['url']
            }
        except IndexError:
            return {"error": "No results found"}
    else:
        print("Error fetching song details:", response.json())
        return None

# Function to generate recommendations
def recommend_music(song_title):
    # Load pre-trained data and similarity matrix
    music_dict = pickle.load(open('musicrecco.pkl', 'rb'))
    music = pd.DataFrame(music_dict)
    similarity = pickle.load(open('similarities.pkl', 'rb'))

    # Check if the song exists in the dataset
    if song_title not in music['title'].values:
        return {"error": "Song not found in the dataset"}

    # Find similar songs
    music_index = music[music['title'] == song_title].index[0]
    distances = similarity[music_index]
    recommended_indexes = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    # Fetch song details from Spotify
    token = get_spotify_token()
    recommendations = []
    for i in recommended_indexes:
        track_title = music.iloc[i[0]].title
        song_details = fetch_song_details(track_title, token)
        recommendations.append(song_details)
    
    return recommendations

# API endpoint for recommendations
@app.route('/recommend', methods=['GET'])
def recommend():
    song_title = request.args.get('song')  # Song title from query parameter
    if not song_title:
        return jsonify({"error": "Song title is required"}), 400
    
    recommendations = recommend_music(song_title)
    return jsonify(recommendations)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
