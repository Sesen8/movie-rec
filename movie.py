

import pandas as pd
import numpy as np
import streamlit as st
import requests
import pickle
from fuzzywuzzy import fuzz, process  # For fuzzy matching

# Load data (assuming the Kaggle dataset)
movies = pd.read_csv('movies.csv')
cosine_sim = np.load('cosine_sim.npy')

import ast

def safe_eval_list(x):
    if pd.isna(x):
        return []
    if isinstance(x, list):
        return x
    if isinstance(x, str) and x.strip().startswith('[') and x.strip().endswith(']'):
        try:
            return ast.literal_eval(x)
        except:
            return []
    return x.split()  # fallback for space-separated strings

list_columns = ['genres', 'keywords', 'cast', 'crew']
for col in list_columns:
    movies[col] = movies[col].apply(safe_eval_list)

# Extract all tags and genres
all_tags = movies['tags'].str.split().explode()
all_genres = sorted(set(all_tags).intersection(set([
    'action', 'adventure', 'animation', 'comedy', 'crime', 'documentary', 'drama', 'family', 'fantasy',
    'history', 'horror', 'music', 'mystery', 'romance', 'science', 'fiction', 'tv', 'thriller', 'war', 'western'
])))

unique_years = sorted(movies['release_year'].dropna().unique(), reverse=True)

# Get recommendations based on cosine similarity
def get_recommendations(title, cosine_sim=cosine_sim, num_recs=20):
    idx = movies[movies['title'] == title].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    # sim_scores = sim_scores[1:num_recs+1]  # Get top 20 similar movies
    sim_scores = sim_scores[1:51] 
    movie_indices = [i[0] for i in sim_scores]
    return movies[['title', 'movie_id', 'tags', 'release_year']].iloc[movie_indices]

# Fetch poster from TMDB API
def fetch_poster(movie_id):
    api_key = '70333490c45cf5705e44cb3d3dbf8ff3'  # Replace with your TMDB API key
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}'
    response = requests.get(url)
    data = response.json()
    poster_path = data['poster_path']
    full_path = f"https://image.tmdb.org/t/p/w500{poster_path}"
    return full_path

# Streamlit layout
st.title("Movie Recommendation System")

# Filters (moved to main layout)
st.header("Filter Recommendations")

selected_genre = st.multiselect("Filter by Genre(s) (optional):", all_genres)
selected_year = st.selectbox("Filter by Year (optional):", ["All"] + unique_years)
selected_movie = st.text_input("Search for a movie:")

if selected_movie:
    # Use fuzzy matching to allow partial matches
    selected_movie_cleaned = selected_movie.strip().lower()
    matching_movies = movies[movies['title'].str.contains(selected_movie_cleaned, case=False, na=False)]

    if not matching_movies.empty:
        matching_movie = matching_movies.iloc[0]
        movie_title = matching_movie['title']
        movie_overview = matching_movie['overview']
        movie_release_year = str(matching_movie['release_year'])[:4] if pd.notna(matching_movie['release_year']) else "N/A"

        # Display selected movie details
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(fetch_poster(matching_movie['movie_id']), width=200)
        with col2:
            # Display title and release year
            st.markdown(f"## {matching_movie['title']} ({matching_movie['release_year']})")
            
            # Display Overview
            st.markdown("### Overview")
            st.write(
                matching_movie['overview']
                if pd.notna(matching_movie['overview']) and matching_movie['overview'].strip()
                else "No overview available."
            )

            # Genres
            st.markdown("### Genre")
            if isinstance(matching_movie['genres'], list) and len(matching_movie['genres']) > 0:
                st.write(", ".join(matching_movie['genres']))
            else:
                st.write("No genres available.")

            # Cast
            st.markdown("### Cast")
            if isinstance(matching_movie['cast'], list) and len(matching_movie['cast']) > 0:
                st.write(", ".join(matching_movie['cast'][:10]))  # Show top 10 cast members
            else:
                st.write("No cast available.")

            # Crew
            st.markdown("### Crew")
            if isinstance(matching_movie['crew'], list) and len(matching_movie['crew']) > 0:
                st.write(", ".join(matching_movie['crew'][:10]))  # Show top 10 crew members
            else:
                st.write("No crew available.")

            # Keywords
            st.markdown("### Keywords")
            if isinstance(matching_movie['keywords'], list) and len(matching_movie['keywords']) > 0:
                st.write(", ".join(matching_movie['keywords']))
            else:
                st.write("No keywords available.")
    
        # Get recommendations based on cosine similarity
        recommendations = get_recommendations(movie_title)

        # Apply genre filter if selected
        if selected_genre:
            recommendations = recommendations[
                recommendations['tags'].apply(lambda x: any(genre in x.split() for genre in selected_genre))
            ]

        # Apply year filter if selected
        if selected_year != "All":
            recommendations = recommendations[
                recommendations['release_year'].astype(str) == selected_year
            ]

        # Display recommendations in a grid layout
        num_recs = len(recommendations)
        max_columns = 5  # Set maximum columns per row
        num_rows = (num_recs // max_columns) + (num_recs % max_columns > 0)

        for i in range(num_rows):
            cols = st.columns(min(max_columns, num_recs - i * max_columns))
            for j, col in enumerate(cols):
                if i * max_columns + j < num_recs:
                    rec_movie = recommendations.iloc[i * max_columns + j]
                    rec_movie_title = rec_movie['title']
                    rec_movie_id = rec_movie['movie_id']
                    with col:
                        st.image(fetch_poster(rec_movie_id), width=150)
                        st.write(f"**{rec_movie_title}**")

        # If there are still empty spots, continue fetching more similar movies
        if num_recs < num_rows * max_columns:
            additional_recs = get_recommendations(movie_title, num_recs=(num_rows * max_columns - num_recs))
            additional_recs = additional_recs[~additional_recs['title'].isin(recommendations['title'])]

            # Display the additional recommendations
            if not additional_recs.empty:
                for i in range(0, len(additional_recs), max_columns):
                    cols = st.columns(min(max_columns, len(additional_recs) - i))
                    for j, col in enumerate(cols):
                        if i + j < len(additional_recs):
                            rec_movie = additional_recs.iloc[i + j]
                            rec_movie_title = rec_movie['title']
                            rec_movie_id = rec_movie['movie_id']
                            with col:
                                st.image(fetch_poster(rec_movie_id), width=150)
                                st.write(f"**{rec_movie_title}**")
    else:
        st.write("No movie found with that title.")