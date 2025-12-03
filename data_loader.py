import numpy as np
import pandas as pd
import streamlit as st


@st.cache_data
def load_data():
    """Load and preprocess the Steam games dataset"""
    try:
        df = pd.read_csv(
            'data/games.csv',
            sep=',',  # columns are comma-separated
            quotechar='"',  # respect quotes around text
        )

    except FileNotFoundError:
        st.error("❌ File 'data/games.csv' not found.")
        st.stop()

    return df


@st.cache_data
def filter_data(input_df):
    df = input_df.copy()

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


@st.cache_data
def filter_year(df, year_range):
    return df[(df['Release_year'] >= year_range[0]) & (df['Release_year'] <= year_range[1])]


@st.cache_data
def filter_low_data(input_df, year_range, number_of_min_reviews, number_of_min_ccu):
    df = input_df.copy()
    df = filter_year(df, year_range)
    df = df[df['Total_reviews'] >= number_of_min_reviews]
    df = df[df['Peak CCU'] >= number_of_min_ccu]
    print(
        f"⚠️ Removed {len(input_df) - len(df)} rows with less than {number_of_min_reviews} reviews"
        f" and less than {number_of_min_ccu} CCU per game and are withing year range {year_range}"
    )
    return df


@st.cache_data
def get_all_tags(df):
    return sorted(set([
        category.strip()
        for category_list in df['Tags'].dropna().str.split(',')
        for category in category_list
        if category.strip()
    ]))
