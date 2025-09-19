import os
import requests

from dotenv import load_dotenv
load_dotenv()



# Retrieve the API key from the environment variable
tmdb_api_key = os.getenv("TMDb_API_KEY").strip('"')
# print(f"API key raw: {repr(tmdb_api_key)}")

if tmdb_api_key is None:
    raise ValueError("TMDb_API_KEY environment variable is not set. Please set it before running the script.")

# Now you can use the variable in your requests
url = f"https://api.themoviedb.org/3/movie/27205?api_key={tmdb_api_key}"

if not tmdb_api_key:
    raise ValueError("TMDb_API_KEY environment variable not set.")

def fetch_movie_and_credits(movie_id):
    """Fetches movie details and its credits (cast, crew) from TMDb API."""
    base_url = "https://api.themoviedb.org/3"
    
    print(f"details for movie url : base url : {base_url} and movie id ${movie_id} , api key = ${tmdb_api_key}")
    # Endpoint for movie details
    movie_url = f"{base_url}/movie/{movie_id}?api_key={tmdb_api_key}"
    movie_response = requests.get(movie_url)              
    movie_response.raise_for_status() # Raise an exception for bad status codes
    movie_data = movie_response.json()

    # Endpoint for movie credits
    credits_url = f"{base_url}/movie/{movie_id}/credits?api_key={tmdb_api_key}"
    credits_response = requests.get(credits_url)
    credits_response.raise_for_status()
    credits_data = credits_response.json()

    return movie_data, credits_data

if __name__ == "__main__":
    # Example: Inception (ID: 27205)
    movie_details, movie_credits = fetch_movie_and_credits(27205)

    # print("--- Movie Details ---")
    # print(f"Title: {movie_details.get('title')}")
    # print(f"Overview: {movie_details.get('overview')[:100]}...") # Print a snippet
    
    # print("\n--- Cast ---")
    # # Get the top 5 cast members
    # for cast_member in movie_credits.get('cast', [])[:5]:
    #     print(f"Name: {cast_member.get('name')}, Character: {cast_member.get('character')}")

    # You now have the raw data! You'll use this in the next steps.