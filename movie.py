import pandas as pd
import numpy as np
import streamlit as st
import requests
import pickle
from fuzzywuzzy import fuzz, process  # For fuzzy matching

# Load data (assuming the Kaggle dataset)
movies = pd.read_csv('movies.csv')
cosine_sim = np.load('cosine_sim.npy')

# Extract all tags and genres
all_tags = movies['tags'].str.split().explode()
all_genres = sorted(set(all_tags).intersection(set([
    'action', 'adventure', 'animation', 'comedy', 'crime', 'documentary', 'drama', 'family', 'fantasy',
    'history', 'horror', 'music', 'mystery', 'romance', 'science', 'fiction', 'tv', 'thriller', 'war', 'western'
])))

unique_years = sorted(movies['release_year'].dropna().unique(), reverse=True)

# Get recommendations based on cosine similarity
def get_recommendations(title, cosine_sim=cosine_sim):
    idx = movies[movies['title'] == title].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:21]  # Get top 10 similar movies
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
selected_genre = st.selectbox("Filter by Genre (optional):", ["All"] + all_genres)
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
        #     st.write(f"### {movie_title} ({movie_release_year})")
        #     st.write(movie_overview)


            st.markdown(f"## {matching_movie['title']} ({matching_movie['release_year']})")
            
            st.markdown("### Overview")
            st.write(
                matching_movie['overview']
                if pd.notna(matching_movie['overview']) and matching_movie['overview'].strip()
                else "No overview available."
            )

            st.markdown("### Tags")
            tag_list = matching_movie['tags'].split() if pd.notna(matching_movie['tags']) else []
            if tag_list:
                tag_html = " ".join([
                    f"<span style='display:inline-block;background-color:#d0e8ff;border-radius:20px;padding:6px 12px;margin:4px;font-size:13px;'>{tag}</span>"
                    for tag in tag_list
                ])
                st.markdown(tag_html, unsafe_allow_html=True)
            else:
                st.write("No tags available.")
            

        # Get recommendations based on cosine similarity
        recommendations = get_recommendations(movie_title)

        # Apply genre filter if selected
        if selected_genre != "All":
            recommendations = recommendations[
                recommendations['tags'].apply(lambda x: selected_genre in x.split())
            ]

        # Apply year filter if selected
        if selected_year != "All":
            recommendations = recommendations[
                recommendations['release_year'].astype(str) == selected_year
            ]

        # Display recommendations in a grid layout
        if not recommendations.empty:
            num_recs = len(recommendations)
            max_columns = 5  # Set maximum columns per row
            for i in range(0, num_recs, max_columns):
                cols = st.columns(min(max_columns, num_recs - i))
                for j, col in enumerate(cols):
                    if i + j < num_recs:
                        rec_movie = recommendations.iloc[i + j]
                        rec_movie_title = rec_movie['title']
                        rec_movie_id = rec_movie['movie_id']
                        with col:
                            st.image(fetch_poster(rec_movie_id), width=150)
                            st.write(f"**{rec_movie_title}**")
        else:
            st.warning("No recommendations match the selected filters.")
    else:
        st.write("No movie found with that title.")







# if selected_movie:
#     # Find the movie from the dataset by checking for partial matches (case-insensitive)
#     matching_movies = movies[movies['title'].str.contains(selected_movie, case=False, na=False)]

#     if not matching_movies.empty:
#         # Grab the first matching movie (if there are multiple matches)
#         matching_movie = matching_movies.iloc[0]

#         # Extract movie details
#         movie_title = matching_movie['title']
#         movie_overview = matching_movie['overview']
#         # movie_release_year = matching_movie['release_year'][:4]  # Extracting year from the release_date string
#         movie_release_year = str(matching_movie['release_year'])[:4] if pd.notna(matching_movie['release_year']) else "N/A"

        
#         # Display the selected movie's information
#         col1, col2 = st.columns([1, 2])  # Create two columns, with the second column wider
#         with col1:
#             st.image(fetch_poster(matching_movie['movie_id']), width=200)  # Display poster
#         with col2:
#             st.write(f"### {movie_title} ({movie_release_year})")
#             st.write(movie_overview)


#         # Get the top 10 recommended movies
#         recommendations = get_recommendations(movie_title)

#         num_recs = len(recommendations)

#         if num_recs > 0:
#             max_columns = 5  # Maximum posters per row
#             for i in range(0, num_recs, max_columns):
#                 cols = st.columns(min(max_columns, num_recs - i))  # Adjust column count dynamically
#                 for j, col in enumerate(cols):
#                     if i + j < num_recs:
#                         rec_movie = recommendations.iloc[i + j]
#                         rec_movie_title = rec_movie['title']
#                         rec_movie_id = rec_movie['movie_id']
#                         with col:
#                             st.image(fetch_poster(rec_movie_id), width=150)  # Fixed poster size
#                             st.write(f"**{rec_movie_title}**")
                        
#     else:
#         st.write("No movie found with that title.")

