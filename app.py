import streamlit as st
import pickle
import numpy as np
import base64
import pandas as pd

# --- 1. Helper function to encode the local image for the background ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- 2. Custom CSS for Full-Page Background and Popping UI ---
try:
    img_base64 = get_base64_of_bin_file('BG_app.jpeg')
    
    # We use linear-gradient(rgba, rgba) to apply a dark dimming layer OVER the image
    css_style = f"""
    <style>
    /* Target the entire Streamlit app background */
    .stApp {{
        background: linear-gradient(rgba(15, 15, 20, 0.6), rgba(15, 15, 20, 0.6)), url("data:image/jpeg;base64,{img_base64}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    
    /* Force main text elements to be white for readability */
    h1, h2, h3, p {{
        color: white !important;
    }}

    /* Target the Search Bar Label specifically to make it larger and softer */
    .stSelectbox label, .stSelectbox label p {{
        color: white !important;
        font-size: 1.6rem !important; /* Increases the size */
        font-family: 'Trebuchet MS', 'Nunito', 'Segoe UI', sans-serif !important; /* Softer, rounder font stack */
        font-weight: 500 !important; /* Makes it crisp but not overly bold */
        letter-spacing: 0.5px;
        margin-bottom: 10px;
    }}

    /* Container for the recommendations */
    .recommendation-box {{
        padding: 2rem;
        border-radius: 15px;
        background-color: rgba(0, 0, 0, 0.3);
        margin-top: 2rem;
        backdrop-filter: blur(10px); /* Creates a frosted glass effect */
    }}
    
    .recommendation-box h2 {{
        margin-top: 0;
        margin-bottom: 1.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
    }}

    /* The "Popping" Recommendation Items */
    .rec-item {{
        font-size: 1.3rem;
        margin-bottom: 1.2rem;
        padding: 15px 20px;
        /* Sleek dark gradient background for the item */
        background: linear-gradient(135deg, rgba(45, 20, 70, 0.9) 0%, rgba(20, 15, 35, 0.9) 100%);
        /* Neon Cyan highlight border on the left */
        border-left: 6px solid #00f3ff;
        border-radius: 10px;
        color: white !important;
        /* Subtle neon glow shadow */
        box-shadow: 0 4px 15px rgba(0, 243, 255, 0.15);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        transition: transform 0.2s ease-in-out;
    }}
    
    /* Subtle animation when mouse hovers over a game */
    .rec-item:hover {{
        transform: translateX(10px);
    }}

    /* Make the numbers (1, 2, 3) pop with the same Neon Cyan */
    .rec-item b {{
        color: #00f3ff !important;
        font-size: 1.5rem;
        margin-right: 10px;
    }}
    </style>
    """
    st.markdown(css_style, unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("Could not find 'BG_app.jpeg'. The app will still work, but without the custom background.")

# --- 3. Load the Machine Learning Data (BULLETPROOF VERSION) ---
try:
    games_dict = pickle.load(open('games_dict.pkl', 'rb'))
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    
    if isinstance(games_dict, pd.DataFrame):
        games_df = games_dict
    else:
        games_df = pd.DataFrame(games_dict)
    
    lower_cols = [str(c).lower() for c in games_df.columns]
    
    if 'title' in lower_cols:
        col_name = games_df.columns[lower_cols.index('title')]
    elif 'name' in lower_cols:
        col_name = games_df.columns[lower_cols.index('name')]
    elif 'app_name' in lower_cols:
        col_name = games_df.columns[lower_cols.index('app_name')]
    else:
        col_name = games_df.columns[0]
    
    games_list = games_df[col_name].values
    
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# --- 4. The Recommendation Logic ---
def recommend(game):
    try:
        game_index = games_df[games_df[col_name] == game].index[0]
        distances = similarity[game_index]
        
        games_and_scores = list(enumerate(distances))
        sorted_games = sorted(games_and_scores, key=lambda x: x[1], reverse=True)[1:6]
        
        recommended_games = []
        for i in sorted_games:
            recommended_games.append(games_df.iloc[i[0]][col_name])
            
        return recommended_games
    except Exception as e:
        return []

# --- 5. The Streamlit User Interface ---

st.title("The Nugget Engine")
st.write("Select a game you love, and the algorithm will find 5 similar titles based on genres and tags.")

# The Search Bar
selected_game_name = st.selectbox(
    'Search for a game:',
    games_list
)

if st.button('Recommend'):
    with st.spinner('Scanning database...'):
        recommendations = recommend(selected_game_name)
        
    if recommendations:
      
        html_content = f"""
        <div class="recommendation-box">
            <h2>If you liked <i>{selected_game_name}</i>, you might like:</h2>
        """
        
     
        for i, game in enumerate(recommendations):
            html_content += f'<div class="rec-item"><b>{i+1}.</b> {game}</div>'
            
        
        html_content += "</div>"
        
        # 4. Tell Streamlit to render the whole thing at exactly the same time
        st.markdown(html_content, unsafe_allow_html=True)
    else:
        st.error("We couldn't generate recommendations for that title. Please try another one.")