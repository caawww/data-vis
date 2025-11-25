import numpy as np
import pandas as pd
import streamlit as st

from config import CUSTOM_COLOURS, ANALYSIS_TYPES


def set_theme():
    st.markdown(f"""
        <style>
        .main {{
            background-color: {CUSTOM_COLOURS['background']};
            color: {CUSTOM_COLOURS['text']};
        }}
        .stSidebar {{
            background-color: {CUSTOM_COLOURS['sidebar']} !important;
        }}
        .css-1d391kg, .css-1lcbmhc {{
            background-color: {CUSTOM_COLOURS['background']};
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: {CUSTOM_COLOURS['white']};
        }}
        .stSelectbox label, .stSlider label, .stRadio label {{
            color: {CUSTOM_COLOURS['text']} !important;
        }}
        .stDataFrame {{
            background-color: {CUSTOM_COLOURS['card']};
        }}
        </style>
    """, unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Load and preprocess the Steam games dataset"""
    columns = [
        'AppID', 'Name', 'Release date', 'Estimated owners', 'Peak CCU', 'Required age', 'Price',
        'Discount', 'DLC count', 'About the game', 'Supported languages', 'Full audio languages', 'Reviews',
        'Header image', 'Website', 'Support url', 'Support email', 'Windows', 'Mac', 'Linux', 'Metacritic score',
        'Metacritic url', 'User score', 'Positive', 'Negative', 'Score rank', 'Achievements', 'Recommendations',
        'Notes', 'Average playtime forever', 'Average playtime two weeks', 'Median playtime forever',
        'Median playtime two weeks', 'Developers', 'Publishers', 'Categories', 'Genres', 'Tags', 'Screenshots',
        'Movies'
    ]

    needed_cols = [
        'AppID', 'Name', 'Release date', 'Estimated owners', 'Peak CCU', 'Required age', 'Positive', 'Negative',
        'Recommendations', 'Average playtime forever', 'Median playtime forever', 'Categories', 'Genres', 'Tags'
    ]

    try:
        df = pd.read_csv(
            'data/games.csv',
            sep=',',  # columns are comma-separated
            quotechar='"',  # respect quotes around text
            names=columns,
            skiprows=1,
        )

        # df = df[needed_cols]

    except FileNotFoundError:
        st.error("❌ File 'data/games.csv' not found.")
        st.stop()

    return df

def filter_data(df):
    # Convert release date to datetime and handle errors
    df['Release date'] = pd.to_datetime(df['Release date'], errors='coerce')

    # Remove rows with invalid dates
    initial_count = len(df)
    df = df.dropna(subset=['Release date'])
    filtered_count = len(df)

    print(f"⚠️ Removed {initial_count - filtered_count} rows with invalid dates")

    # Extract release year
    df['Release_year'] = df['Release date'].dt.year

    # Convert numeric columns with error handling
    numeric_columns = {
        'Peak CCU': 0,
        'Positive': 0,
        'Negative': 0,
        'Average playtime forever': 0,
        'Median playtime forever': 0,

        'Price': 0,
        'Achievements': 0,
    }

    for col, default_value in numeric_columns.items():
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(default_value)

    # Calculate derived metrics
    df['Total_reviews'] = df['Positive'] + df['Negative']

    review_count_filter = 10
    df = df[df['Total_reviews'] >= review_count_filter]
    print(f"⚠️ Removed {filtered_count - len(df)} rows with less than {review_count_filter} reviews")

    df['Review_ratio'] = np.where(
        df['Total_reviews'] > 0,
        df['Positive'] / df['Total_reviews'],
        0
    )

    # Clean Genres and Tags columns
    df['Categories'] = df['Categories'].fillna('')
    df['Genres'] = df['Genres'].fillna('')
    df['Tags'] = df['Tags'].fillna('')

    # Normalize Categories / Genres / Tags capitalization
    def normalize_list_string(s):
        if not isinstance(s, str) or s.strip() == "":
            return s

        items = [item.strip().title() for item in s.split(',')]
        return ",".join(items)

    for col in ['Categories', 'Genres', 'Tags']:
        df[col] = df[col].apply(normalize_list_string)

    print(f"✅ Data loaded successfully: {len(df)} games")
    return df


def get_all_categories(df):
    return {
        at: sorted(set([
            category.strip()
            for category_list in df[at].dropna().str.split(',')
            for category in category_list
            if category.strip()
        ]))
        for at in ANALYSIS_TYPES
    }
