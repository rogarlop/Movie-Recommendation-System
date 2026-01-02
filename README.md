# Movie-Recommendation-System
Repository that contains the programs for developing a simple movie recommendation system. Uses MySQL as database, Python for data transformation, FastAPI for endpoints creation and Streamlit for visualization purposes.

<p align="center"> <img width="1268" height="557" alt="Movie_Recommendation_Image" src="https://github.com/user-attachments/assets/d7dbac12-154c-48d9-9d53-0607d01a6798" /> </p>

## Project description

This is a project that was intended as a first approximation to build an integration between SQL + FastAPI + Python. It consist of a database stored in MySQL, a FastAPI development (without Auth and AutZ) with just the neccesary endpoints to serve the model and a Streamlit UI for visualizing the results. The recommendation system is built using faiss library. Details are extended below.

### Process for project development

#### Database

The database used is from The Movie Data Base (TMDB) available [here](https://www.kaggle.com/datasets/asaniczka/tmdb-movies-dataset-2023-930k-movies). It consists of more than 1M movie registers. The fields that the database contains are:

1) Movie id (unique identifier for movie)
2) Title
3) Vote Average (average rating given by viewers)
4) Vote Count (number of votes for a specific movie)
5) Status (Released, In production, Rumored, etc)
6) Release date
7) Revenue
8) Runtime (in mins)
9) Adult ( True = for adults )
10) Backdrop path (URL for the backdrop image of the movie. Not used in our case)
11) Homepage (official movie URL in case it exists)
12) imdb_id (unique IMDB identifier in case it exists)
13) original language (i.e. en for english, fr for french, sp for spanish)
14) original title
15) overview
16) popularity (score for measure popularity)
17) poster path (URL for the poster image. Not used in our case)
18) tagline (catchphrase or line associated with movie)
19) genres
20) production companies
21) production countries
22) spoken languages (languages spoken in the movie)
23) keywords

The notebook named "ETL" loads the original file, and perform cleaning processes on it, removing undesired columns, duplicates, incorrect or incomplete registers, movies that have not been released, and string cleaned with regex. It also performs the vectorization of some fields, in particular, over the text columns defined (i.e. title, language, genres, companies) using TF-IDF technique. This was done because mixing of numerical and string columns was performed for take both in consideration during the recommendation of similar movies, and the domination of one numerical column or a text feature, was intended to be avoided.

#### Database connection

After the original database was cleaned, it was stored locally on MySQL. There, it was accessed by Python using sql alchemy. The script was used for creating the database from Python, ensuring the correct update of information in case it was needed and the writing of SQL queries in Python using SQL Alchemy. This process can be seen in the notebook "Database_creation_managment".

#### Fast API 

In the file named "main.py" the development of the API was performed. This file connects with the SQL database stored. It also defines different Pydantic schemas for retrieving information in different levels, depending on the endpoint, and simple CRUD operations were developed. Finally, in the endpoint /movies/recommend/ the movie is searched based on the title, and the more similar occurence is retrieved as the movie desired. Once that process is finished, the faiss library was loaded for perform the prediction. Our system works as follows: 

A recommendation system needs to compare distances to decide whether two movies are similar enough to be recommended. This comparison is costly if the data is multidimensional and also if there exists too many registers (in our case 1M), because the comparison is performed between all pairs of registers. It is extremely slow because the dimensionality and the number of comparison to be performed. Faiss, in basic terms, performs a search in the data represented as numeric vectors. It performs the comparison then from one query vector (the particular register) against approximate candidates (not all registers) and retrieve the top 5 similar results. In our case, we preloaded the sparse matrix (named X_sparse) that we precalculated in the ETL step. This means the recommendation system will always retrieve the same recommendations from the same question (movie) until you recalculate the sparse matrix with newer information. The sparse matrix consists in the combination of numerical features or columns, scaled with the MinMaxScaler, combined with the TF-IDF transformed string columns (appended to form 1 vector).

#### Streamlit 

Finally, in streamlit we developed a simple user interface where it can be consulted the entire movie catalog (presented in pages) and when the buttons are pressed, internally the system communicates with the API for retrieving the recommendations along with additional information of the recommended movies. Here the posters are also shown by consulting the [OMDB API](https://www.omdbapi.com/) which needs the movie identifier to retrieve a poster. To run the system, you must download the file "X_sparse.npz", the main.py and the Movie_Recommendation_App.py, store the database cleaned in SQL, start the Fast API local server with uvicorn and run the streamlit app (streamlit run Movie_Recommendation_App) for see the results. Additional efforts needs to be done to store the database in a cloud environment to avoid connecting to it locally, but the systems works as a proof of concept. Below is provided an example on the system performance.


![Movie Recommendation System - Trim (4)](https://github.com/user-attachments/assets/3a40a900-2976-4ed3-b501-c0664842c385)



