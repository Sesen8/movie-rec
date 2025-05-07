# Movie Recommendation System

## Overview
This is a Movie Recommendation System built using Python and Streamlit. The system allows users to search for movies, view their details, and get movie recommendations based on their search. It uses cosine similarity to recommend movies that are similar to the user's query, with the added ability to filter recommendations by genre and release year.

The system fetches movie details from a local dataset and uses the TMDB API to fetch posters for movies. The recommendations are based on a content-based filtering approach using TF-IDF and cosine similarity.

## Features

- **Search Movies**: Users can search for movies by title. The system uses fuzzy string matching to provide results even if there are typos or partial matches.
- **Movie Details**: For each movie, the system displays details such as the title, release year, genres, cast, crew, and keywords.
- **Movie Recommendations**: Once a movie is selected, the system recommends similar movies based on the cosine similarity of the movie's tags and metadata.
- **Filters**:
  - **Genre Filter**: Users can filter recommendations based on one or more genres.
  - **Year Filter**: Users can filter recommendations by release year.

## Technologies Used

- **Python**: The main programming language.
- **Streamlit**: Used for creating the interactive web interface.
- **Pandas**: For data manipulation and analysis.
- **NumPy**: For numerical operations, especially working with arrays and matrices.
- **Fuzzywuzzy**: For fuzzy string matching when searching for movie titles.
- **TMDB API**: Used to fetch movie posters and additional information.
- **Cosine Similarity & TF-IDF**: Used to calculate movie similarity for recommendations.

## Setup

### Prerequisites

- **Python 3.x**: Ensure you have Python 3.x installed.
- **Streamlit**: Install Streamlit to run the web app.
- **TMDB API Key**: You need an API key from TMDB to fetch movie posters.

### Installation Steps

1. Clone the repository (or download the code).
2. Install the required dependencies:

    ```bash
    pip install streamlit pandas numpy requests fuzzywuzzy scikit-learn
    ```

3. Set up TMDB API key:
   - Go to TMDB, sign up (if you don't have an account), and get your API key.
   - Replace the placeholder API key in the script with your actual API key.

4. **Dataset**:
   - The code assumes you have a `movies.csv` file containing movie data. You should have columns like `title`, `movie_id`, `tags`, `genres`, `keywords`, `cast`, `crew`, and `release_year`. You can use your own dataset or modify the code to fetch live data.
   - Ensure you also have the `cosine_sim.npy` file containing the precomputed cosine similarity matrix, which you can generate using your data.


5. Run the Streamlit app:

    ```bash
    streamlit run app.py
    ```

    Replace `app.py` with the name of your Python file if it's different.


## File Structure

- `project/`
  - `tmdb_5000_credits.csv`
  - `tmdb_5000_movies.csv`
  - `movies.csv`
  - `cosine_sim.npy`
  - `movie.py`
  - `movie-recs.ipynb`

## Usage

### Search for a movie:
Enter the movie title in the search bar. The system will display movies matching your search using fuzzy matching.

### View movie details:
Once a movie is selected, its details (title, overview, genres, cast, crew, keywords) will be displayed. Additionally, a movie poster will be shown fetched from the TMDB API.

### Get recommendations:
After viewing a movie, the system will recommend similar movies based on cosine similarity. You can further filter these recommendations by genre and release year.

### Apply filters:
You can filter the recommendations by genre(s) and release year to refine the results.



## Future Enhancements

- **Collaborative Filtering**: Implement collaborative filtering for personalized recommendations based on user ratings and preferences.
- **User Authentication**: Add user profiles to save favorite movies or recommendations.
- **Rating System**: Allow users to rate movies and incorporate those ratings into the recommendation engine.
- **Real-Time Data**: Instead of using a static dataset, fetch the latest movie data directly from the TMDB API.recommendations.






