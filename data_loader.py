import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime


def set_steam_theme():
    """Apply Steam-like dark theme to the Streamlit app"""
    st.markdown(f"""
        <style>
        .main {{
            background-color: #1b2838;
            color: #c7d5e0;
        }}
        .stSidebar {{
            background-color: #171a21 !important;
        }}
        .css-1d391kg, .css-1lcbmhc {{
            background-color: #1b2838;
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: #ffffff;
        }}
        .stSelectbox label, .stSlider label, .stRadio label {{
            color: #c7d5e0 !important;
        }}
        .stDataFrame {{
            background-color: #2a475e;
        }}
        </style>
    """, unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Load and preprocess the Steam games dataset"""
    try:
        columns = [
            'AppID', 'Name', 'Release date', 'Estimated owners', 'Peak CCU', 'Required age', 'Price',
            'Discount', 'DLC count', 'About the game', 'Supported languages', 'Full audio languages', 'Reviews',
            'Header image', 'Website', 'Support url', 'Support email', 'Windows', 'Mac', 'Linux', 'Metacritic score',
            'Metacritic url', 'User score', 'Positive', 'Negative', 'Score rank', 'Achievements', 'Recommendations',
            'Notes', 'Average playtime forever', 'Average playtime two weeks', 'Median playtime forever',
            'Median playtime two weeks', 'Developers', 'Publishers', 'Categories', 'Genres', 'Tags', 'Screenshots',
            'Movies'
        ]
        df = pd.read_csv(
            'data/games.csv',
            sep=',',  # columns are comma-separated
            quotechar='"',  # respect quotes around text
            names=columns,
            skiprows=1,
        )

    except FileNotFoundError:
        st.error("❌ File 'games.csv' not found. Please ensure it's in the same directory as this script.")
        st.stop()

    # Data cleaning and preprocessing
    st.info("🔄 Loading and cleaning data...")

    # Convert release date to datetime and handle errors
    df['Release date'] = pd.to_datetime(df['Release date'], errors='coerce')

    # Remove rows with invalid dates
    initial_count = len(df)
    df = df.dropna(subset=['Release date'])
    filtered_count = len(df)

    if initial_count > filtered_count:
        st.sidebar.warning(f"⚠️ Removed {initial_count - filtered_count} rows with invalid dates")

    # Extract release year safely
    df['Release_year'] = df['Release date'].dt.year

    # Clean and categorize estimated owners
    from config import OWNER_CATEGORIES
    df['Estimated owners'] = df['Estimated owners'].astype(str).str.strip()
    valid_owners = df['Estimated owners'].isin(OWNER_CATEGORIES)
    df.loc[~valid_owners, 'Estimated owners'] = '0 - 20000'  # Default for invalid values

    df['Estimated owners'] = pd.Categorical(
        df['Estimated owners'],
        categories=OWNER_CATEGORIES,
        ordered=True
    )

    # Convert numeric columns with error handling
    numeric_columns = {
        'Price': 0,
        'Positive': 0,
        'Negative': 0,
        'Peak CCU': 0,
        'Achievements': 0
    }

    for col, default_value in numeric_columns.items():
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(default_value)

    # Calculate derived metrics
    df['Total_reviews'] = df['Positive'] + df['Negative']
    df['Review_ratio'] = np.where(
        df['Total_reviews'] > 0,
        df['Positive'] / df['Total_reviews'],
        0
    )

    # Clean Genres and Tags columns
    df['Genres'] = df['Genres'].fillna('')
    df['Tags'] = df['Tags'].fillna('')

    st.success(f"✅ Data loaded successfully: {len(df)} games")
    return df


def get_all_categories(df, analysis_type):
    """Extract all unique categories (genres or tags) from the dataset"""
    if analysis_type == 'Genres':
        column = 'Genres'
    else:  # Tags
        column = 'Tags'

    all_categories = sorted(set([
        category.strip()
        for category_list in df[column].dropna().str.split(',')
        for category in category_list
        if category.strip()
    ]))
    return all_categories
