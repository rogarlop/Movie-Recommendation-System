from fastapi import FastAPI, HTTPException
from typing import Optional, List
from pydantic import BaseModel

from sqlmodel import Field, Session, SQLModel, create_engine, select
import os
from dotenv import load_dotenv

from scipy.sparse import save_npz, load_npz
import faiss
import numpy as np

from sqlalchemy import case

load_dotenv()

# Instance of FastAPI
app = FastAPI()

#Load sparse matrix for calculating ANN with faiss
X_sparse = load_npz("X_sparse.npz")
dim_sparse = X_sparse.shape[1]

tag1 = ["Movies Management"]
tag2 = ["Recommendation System"]
tag3 = ["Search"]

# Path (or endpoint) for the root URL
@app.get("/")
# Path operation function
def root():
    return {"message": "Movie Recommendation System API"}

# Pydantic model for movie data
class Movies(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    original_title: str | None = Field(default=None, index=True)
    release_date: int | None = Field(default=None, index=True)
    production_companies: str | None = Field(default=None, index=True)
    vote_average: float | None = Field(default=None, index=True)
    vote_count: int | None = Field(default=None, index=True)
    runtime : int | None = Field(default=None, index=True)
    revenue: int | None = Field(default=None, index=True)
    budget: int | None = Field(default=None, index=True)
    genres: str | None = Field(default=None, index=True)
    original_language: str | None = Field(default=None, index=True)
    popularity: float | None = Field(default=None, index=True)
    production_countries: str | None = Field(default=None, index=True)
    spoken_languages: str | None = Field(default=None, index=True)
    keywords: str | None = Field(default=None, index=True)

# Model for put operations
class MoviesCreate(SQLModel):
    original_title: str 
    release_date: int | None = Field(default=None, index=True)
    production_companies: str | None = Field(default=None, index=True)
    vote_average: float | None = Field(default=None, index=True)
    vote_count: int | None = Field(default=None, index=True)
    runtime : int | None = Field(default=None, index=True)
    revenue: int | None = Field(default=None, index=True)
    budget: int | None = Field(default=None, index=True)
    genres: str | None = Field(default=None, index=True)
    original_language: str | None = Field(default=None, index=True)
    popularity: float | None = Field(default=None, index=True)
    production_countries: str | None = Field(default=None, index=True)
    spoken_languages: str | None = Field(default=None, index=True)
    keywords: str | None = Field(default=None, index=True)

# Model for retrieving partial details of a movie (including id)
class MoviesRead(SQLModel):
    id: int = Field(default=None, primary_key=True)
    original_title: str = Field(default=None, index=True)
    release_date: int | None = Field(default=None, index=True)
    production_companies: str | None = Field(default=None, index=True)

    class Config:
        orm_mode = True

# Model for response message
class MoviesMsj(SQLModel):
    message: str
    data: MoviesRead

class Reccomendations(SQLModel):
    message: str
    data: List[MoviesRead]

# Model for patch and put operations 
class Movies_Update(SQLModel):
    original_title: str 
    release_date: int | None = None
    production_companies: str | None = None
    vote_average: float | None = None
    vote_count: int | None = None
    runtime : int | None = None
    revenue: int | None = None
    budget: int | None = None
    genres: str |None = None
    original_language: str | None = None
    popularity: float | None = None
    production_countries: str | None = None
    spoken_languages: str | None = None
    keywords: str | None = None

user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")

database_name = "movies_db"
my_sql_url = f'mysql+pymysql://{user}:{password}@{host}/movies_db'
engine = create_engine(my_sql_url, echo=True)

@app.get("/movies/sql", tags = tag1, summary="Get movies from the database inside the specified range", response_model=list[MoviesRead])
def view_movies(limit: Optional[int] = 50, offset: Optional[int] = 0):

    if limit > 50:
        limit = 50

    with Session(engine) as session:
        statement = select(Movies).order_by(Movies.id).offset(offset).limit(limit)
        results = session.exec(statement).all()
        return results
    
# Add a new movie into the database
@app.post("/movies/sql", tags = tag1, summary="Add a new movie into the database", response_model=MoviesMsj)
def add_movie(movie_info: MoviesCreate):
    
    with Session(engine) as session:
        movie = Movies.from_orm(movie_info)
        session.add(movie)
        session.commit()
        session.refresh(movie)
    
        movie_read = MoviesRead.from_orm(movie)

        return MoviesMsj(
            message="Movie added successfully",
            data=movie_read)

# Delete a movie by ID from the database
@app.delete("/movies/sql{movie_id}", tags = tag1, summary=" Delete movie register", response_model=MoviesMsj)
def delete_movie(movie_id: int):

    with Session(engine) as session:
        statement = select(Movies).where(Movies.id == movie_id)
        try:
            register = session.exec(statement).one()
        except:
            raise HTTPException(status_code=404, detail="Movie id not found. Not existing movie in our registers")
        
        title_erased = MoviesRead.from_orm(register)
        session.delete(register)
        session.commit()
 
    return MoviesMsj(
            message="Movie deleted successfully",
            data=title_erased)
    
# Partially update an existing movie by ID
@app.patch("/movies/sql{movie_id}", tags = tag1, summary=" Update a movie register (selective fields)", response_model=MoviesMsj)
def modify_movie(movie_id: int, movie_info: Movies_Update):

    with Session(engine) as session:
        db_movie = session.get(Movies, movie_id)

        if not db_movie:
            raise HTTPException(status_code=404, detail="Movie id not found. Not existing movie in our registers")
        
        update_data = movie_info.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_movie, key, value)

        session.add(db_movie)
        session.commit()
        session.refresh(db_movie)

        movie_read = MoviesRead.from_orm(db_movie)

    return MoviesMsj(
            message="Movie updated successfully",
            data=movie_read)

# Modify an existing movie by ID (entire update)
@app.put("/movies/sql{movie_id}", tags = tag1, summary="Modify the entire register of a movie", response_model=MoviesMsj)
def modify_movie(movie_id: int, movie_info: Movies_Update):
    
    with Session(engine) as session:
        db_movie = session.get(Movies, movie_id)

        if not db_movie:
            raise HTTPException(status_code=404, detail="Movie id not found. Not existing movie in our registers")
        
        update_data = movie_info.dict()
        for key, value in update_data.items():
            setattr(db_movie, key, value)

        session.add(db_movie)
        session.commit()
        session.refresh(db_movie)

        movie_read = MoviesRead.from_orm(db_movie)

    return MoviesMsj(
            message="Movie register updated successfully",
            data=movie_read)

# Logic for similarity search (based on the precalculated sparse Matrix)
def faiss_recommendation(movie_index: int):

    index = faiss.IndexFlatL2(dim_sparse)
    index.add(X_sparse.astype(np.float32).toarray())
    xq = X_sparse[movie_index-1].reshape(1, -1).toarray().astype('float32')
    _ , Indexes = index.search(xq, k=6) 

    return Indexes

# Get a movie recommendation by ID 
@app.get("/movies/recommend/{movie_id}", tags = tag2,  summary="Recommend similar movies by specified ID from the database", response_model=Reccomendations)
def recommend_movie(movie_id: int):

    with Session(engine) as session:
        db_movie = session.get(Movies, movie_id)

        if not db_movie:
            raise HTTPException(status_code=404, detail="Movie id not found. Not existing movie in our registers")
        
        ind = faiss_recommendation(movie_id)
        ind = ind + 1 # Discrepancy between the index in python (0) and SQL (1)
        ind = ind[0][1:].tolist() # Exclude the first index as it is the movie itself
        
        order_similarity = case({id_: i for i, id_ in enumerate(ind)}, value=Movies.id)

        statement = select(Movies).where(Movies.id.in_(ind)).order_by(order_similarity)
        results = session.exec(statement).all()

    return Reccomendations(
                            message=f"As you've searched '{db_movie.original_title}', you may also like",
                            data=results
                            )

# Recommendation based on movie title (searches for the closest match)
@app.get("/movies/recommend/", tags = tag2, summary="Recommend similar movies by approximate title found from the database", response_model=Reccomendations)
def recommend_movie(movie_title: str):

    with Session(engine) as session:
        db_movie = select(Movies).where(Movies.original_title.like(f"%{movie_title}%"))
        db_movie = session.exec(db_movie).first()

        if not db_movie:
            raise HTTPException(status_code=404, detail="Movie id not found. Not existing movie in our registers")

        ind = faiss_recommendation(db_movie.id)
        ind = ind + 1 # Discrepancy between the index in python (0) and SQL (1)
        ind = ind[0][1:].tolist() # Exclude the first index as it is the movie itself

        order_similarity = case({id_: i for i, id_ in enumerate(ind)}, value=Movies.id)

        statement = select(Movies).where(Movies.id.in_(ind)).order_by(order_similarity) 
        results = session.exec(statement).all()

    return Reccomendations(
                            message=f"As you've searched '{db_movie.original_title}', you may also like",
                            data=results
                            )


# # Write Authentication logic here, including user registration and login

# # Search movies by title, genre or year.
# @app.get("/movies/search", tags = tag3, summary="Search movies by title, genre or year")
# def search_movies(title: Optional[str] = None, genre: Optional[str] = None, year: Optional[int] = None):
#     return {"message": "Functionality in development"}

# Scale for storing movies in a MySQL database.
# Also, store MinHash of recommendation system developed, in the database.