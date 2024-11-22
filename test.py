import requests

# Deployed API URL
API_URL = "http://127.0.0.1:5000"

# Test songs
test_songs = [
    "Aankh Marey",
    "Coca Cola",
    "Apna Time Aayega",
    "Mungda",
    "Tere Bin",
    "Gali Gali"
]

def test_recommend_api(song_title):
    # Set up the query parameters
    params = {"song": song_title}
    
    # Send the GET request to the API
    response = requests.get(API_URL, params=params)
    
    # Check the response status and print results
    if response.status_code == 200:
        print(f"Recommendations for '{song_title}':")
        recommendations = response.json()
        for i, recommendation in enumerate(recommendations, 1):
            if recommendation:  # Check if recommendation is not None
                print(f"{i}. Title: {recommendation.get('title', 'N/A')}, "
                      f"Album: {recommendation.get('album', 'N/A')}, "
                      f"Cover: {recommendation.get('cover', 'N/A')}")
            else:
                print(f"{i}. Recommendation data is unavailable.")
    else:
        print(f"Error for '{song_title}': {response.status_code}")
        print("Message:", response.json())
    print("\n")  # Add spacing between outputs for clarity

if __name__ == "__main__":
    # Test each song
    for song in test_songs:
        test_recommend_api(song)
