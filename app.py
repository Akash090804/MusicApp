import requests
import base64
import pickle
import os
import pandas as pd
from flask import Flask, request, jsonify
from dotenv import load_dotenv, find_dotenv
from flask_cors import CORS

dotenv = find_dotenv()
load_dotenv(dotenv)

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# Spotify token retrieval
def get_spotify_token():
    if not CLIENT_ID or not CLIENT_SECRET:
        raise RuntimeError("Spotify CLIENT_ID or CLIENT_SECRET is missing in .env file.")
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
        raise RuntimeError(f"Error getting Spotify token: {response.json()}")

# Song details fetch
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
        raise RuntimeError(f"Error fetching song details: {response.json()}")

# Music recommendation
def recommend_music(song_title):
    try:
        music_dict = pickle.load(open('musicrecco.pkl', 'rb'))
        similarity = pickle.load(open('similarities.pkl', 'rb'))
    except FileNotFoundError:
        raise RuntimeError("Model files not found. Ensure 'musicrecco.pkl' and 'similarities.pkl' are in the directory.")
    
    music = pd.DataFrame(music_dict)
    if song_title not in music['title'].values:
        return {"error": "Song not found in the dataset"}
    
    music_index = music[music['title'] == song_title].index[0]
    distances = similarity[music_index]
    recommended_indexes = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    token = get_spotify_token()
    recommendations = []
    for i in recommended_indexes:
        track_title = music.iloc[i[0]].title
        song_details = fetch_song_details(track_title, token)
        recommendations.append(song_details)
    return recommendations

@app.route('/recommend', methods=['GET'])
def recommend():
    song_title = request.args.get('song')
    if not song_title:
        return jsonify({"error": "Song title is required"}), 400
    try:
        recommendations = recommend_music(song_title)
        return jsonify(recommendations)
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
