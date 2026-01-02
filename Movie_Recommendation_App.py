from streamlit_extras.stylable_container import stylable_container
from PIL import Image
import streamlit_antd_components as sac
import streamlit as st
import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()
omdb_key = os.getenv("OMDB_API_KEY")

# predetermined_img = Image.open("not-available.jpg")
predetermined_img = Image.open("No_image.png")


st.set_page_config(layout="wide")

limit = 50

if "titles" not in st.session_state:
    st.session_state.titles = []
if "selected_movie" not in st.session_state:
    st.session_state.selected_movie = None
if "offset" not in st.session_state:
    st.session_state.offset = 0 
if "recommended" not in st.session_state:
    st.session_state.recommended = []

def list_of_movies(lim, off = 0):
    response = requests.get('http://127.0.0.1:8000/movies/sql', params={"limit":lim, "offset":off})
    data = response.json()
    titles = [movie["original_title"] for movie in data]
    
    return titles

def recommendation(movie_title):
    cols = st.columns(3)
    with cols[2]:
        with st.spinner('Please wait...'):
            response = requests.get('http://127.0.0.1:8000/movies/recommend/', params={"movie_title":movie_title})
            data = response.json()

    return data['data']

#Modify to get the correct poster. It can be returned specifying an "i" parameter which is the IMDB id that needs to be valid.
def posters(movie_title):
    response = requests.get('http://www.omdbapi.com/', params={'apikey': omdb_key, 't':movie_title})
    poster = response.json()

    # if 'Search' in poster:
    #     for posters in poster['Search']:
    #         print(posters.get("Title"))
    #     poster = poster['Search'][0]
    #     poster_url = poster.get("Poster")
    # else:
    poster_url = poster.get("Poster")
 
    return poster_url

def movie_details(movie_id, details = {'runtime', 'genres', 'production_countries', 'production_companies'}):
    response = requests.get(f'http://127.0.0.1:8000/movies/search/{movie_id}')
    data = response.json()

    filtered = [{k: v for k, v in d.items() if k in details} for d in data]
    
    return filtered

def details_graphic(movie_details):
    expander = st.expander("See details")
    text = "\n\n".join( f"**{' '.join(word.capitalize() for word in k.split('_'))}**: {v}" for k, v in movie_details.items() )
    expander.write(text)

def show_recommendations(data):
    cols = st.columns([1,1,1,1,1])
    
    keys = data[0].keys() 
    lists = {k: [record[k] for record in data] for k in keys}
    for i, col in enumerate(cols):
        image = posters(lists['original_title'][i]) #Must be changed by ImDB Id to get the correct poster
        
        with col:
            if not image or image == 'N/A':
                image = predetermined_img
            
            st.image(image)
            st.markdown(f"""
                <div style="
                    text-align:left;
                    font-size:20px;
                    padding:40px;
                    border-radius:8px;
                ">
                    <h3>{lists['original_title'][i]} ({lists['release_date'][i]})</h3>
                </div>
            """, unsafe_allow_html=True)

            current_id = lists['id'][i]
            details = movie_details(current_id)
            details_graphic(details[0])


def button_clicked(btn_name):
    st.session_state.clicked = btn_name

st.session_state.titles = list_of_movies(limit, st.session_state.offset)

st.markdown(' <h2 style="text-align: center;">  Movie Recommendation System </h2> ', unsafe_allow_html=True)
st.markdown("""<h3 style="text-align: center;">Type or select a movie</h3>""", unsafe_allow_html=True)

st.markdown("""
    <style>
    div[data-baseweb="select"] > div {
        margin: 0 auto;
        width: 650px;
        font-size: 25px;
        height: 55px;
    }     

    div.stButton {
    margin-bottom: 10px;
}
            
    </style>
""", unsafe_allow_html=True)

st.session_state.selected_movie = st.selectbox('movie_select_box' , st.session_state.titles, key="movie_selectbox", label_visibility="collapsed", index = 0)

css_controls = """
button { background-color: #5A5E63; color: white; width: 100px; }
"""

css_select = """
button { background-color: #024d02; color: white; width: 150px; }
"""

col1, col2, col3 = st.columns([1,1,1])

with col1:
    with stylable_container(key = "first", css_styles=css_controls):
        prev_button = st.button("Prev")

with col2:
    with stylable_container(key = "second", css_styles=css_controls):
        next_button = st.button("Next")

with col3:
    with stylable_container(key = "third", css_styles=css_select):
        select_clicked = st.button('Select Movie')


if prev_button and st.session_state.offset > 0:
    st.session_state.offset -= limit
    st.rerun()

if next_button:
    st.session_state.offset += limit
    st.rerun()

if select_clicked:
        st.session_state.recommended = recommendation(st.session_state.selected_movie)
        st.session_state.clicked = None
        show_recommendations(st.session_state.recommended)
