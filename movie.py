import pandas as pd
import numpy as np
import streamlit as st
import requests
import pickle

# import gzip
# with gzip.open('movie_data.pkl.gz', 'rb') as f:
#     movies, cosine_sim = pickle.load(f)

movies = pd.read_csv('movies.csv')
cosine_sim = np.load('cosine_sim.npy')

def get_recommendations(title, cosine_sim=cosine_sim):
    idx = movies[movies['title'] == title].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:21]  # Get top 10 similar movies
    movie_indices = [i[0] for i in sim_scores]
    return movies[['title', 'movie_id']].iloc[movie_indices]

def fetch_poster(movie_id):
    api_key = '70333490c45cf5705e44cb3d3dbf8ff3'  # Replace with your TMDB API key
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}'
    response = requests.get(url)
    data = response.json()
    poster_path = data['poster_path']
    full_path = f"https://image.tmdb.org/t/p/w500{poster_path}"
    return full_path
    


st.title("Movie Recommendation System")

selected_movie = st.text_input("Select a movie:")




if selected_movie:
    # Find the movie from the dataset by checking for partial matches (case-insensitive)
    matching_movies = movies[movies['title'].str.contains(selected_movie, case=False, na=False)]

    if not matching_movies.empty:
        # Grab the first matching movie (if there are multiple matches)
        matching_movie = matching_movies.iloc[0]

        # Extract movie details
        movie_title = matching_movie['title']
        movie_overview = matching_movie['overview']
        # movie_release_year = matching_movie['release_year'][:4]  # Extracting year from the release_date string
        movie_release_year = str(matching_movie['release_year'])[:4] if pd.notna(matching_movie['release_year']) else "N/A"

        
        # Display the selected movie's information
        col1, col2 = st.columns([1, 2])  # Create two columns, with the second column wider
        with col1:
            st.image(fetch_poster(matching_movie['movie_id']), width=200)  # Display poster
        with col2:
            st.write(f"### {movie_title} ({movie_release_year})")
            st.write(movie_overview)


        # Get the top 10 recommended movies
        recommendations = get_recommendations(movie_title)

        num_recs = len(recommendations)

        if num_recs > 0:
            max_columns = 5  # Maximum posters per row
            for i in range(0, num_recs, max_columns):
                cols = st.columns(min(max_columns, num_recs - i))  # Adjust column count dynamically
                for j, col in enumerate(cols):
                    if i + j < num_recs:
                        rec_movie = recommendations.iloc[i + j]
                        rec_movie_title = rec_movie['title']
                        rec_movie_id = rec_movie['movie_id']
                        with col:
                            st.image(fetch_poster(rec_movie_id), width=150)  # Fixed poster size
                            st.write(f"**{rec_movie_title}**")
                        
    else:
        st.write("No movie found with that title.")