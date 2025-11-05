import pandas as pd
import numpy as np
import streamlit as st
from config import OWNER_SCORES, USER_METRIC_MAP


def safe_aggregate(group, column, method):
    """Safely aggregate numeric columns"""
    if column not in group.columns:
        return 0

    # Convert to numeric, coercing errors to NaN
    numeric_series = pd.to_numeric(group[column], errors='coerce')

    if method == 'mean':
        result = numeric_series.mean()
    elif method == 'median':
        result = numeric_series.median()
    elif method == 'sum':
        result = numeric_series.sum()
    else:
        result = numeric_series.mean()

    return result if not pd.isna(result) else 0


def get_category_column(analysis_type):
    """Get the appropriate column name based on analysis type"""
    return 'Genres' if analysis_type == 'Genres' else 'Tags'


def filter_categories(df, selected_categories, category_filter_type, analysis_type):
    """Filter dataframe based on category selection and filter type"""
    if not selected_categories:
        return df

    category_column = get_category_column(analysis_type)

    if category_filter_type == "Include only selected categories":
        # Keep only games that have at least one of the selected categories
        def has_selected_category(category_string):
            if pd.isna(category_string):
                return False
            categories = [c.strip() for c in str(category_string).split(',')]
            return any(category in categories for category in selected_categories)

        category_mask = df[category_column].apply(has_selected_category)
        filtered_df = df[category_mask]

    else:  # "Exclude selected categories"
        # Remove games that have any of the selected categories
        def has_excluded_category(category_string):
            if pd.isna(category_string):
                return False
            categories = [c.strip() for c in str(category_string).split(',')]
            return any(category in categories for category in selected_categories)

        category_mask = df[category_column].apply(has_excluded_category)
        filtered_df = df[~category_mask]

    return filtered_df


def prepare_category_data(df, year_range, selected_categories, category_filter_type, analysis_type, user_metric,
                          aggregation_method):
    """Prepare category-level aggregated data for visualization"""

    # Filter by year range
    year_mask = (df['Release_year'] >= year_range[0]) & (df['Release_year'] <= year_range[1])
    filtered_df = df[year_mask].copy()

    if len(filtered_df) == 0:
        st.warning("❌ No data available for the selected year range. Please adjust the filters.")
        return pd.DataFrame(), pd.DataFrame()

    # Apply category filtering
    filtered_df = filter_categories(filtered_df, selected_categories, category_filter_type, analysis_type)

    if len(filtered_df) == 0:
        st.warning("❌ No data available after category filtering. Please adjust the filters.")
        return pd.DataFrame(), pd.DataFrame()

    # Get the appropriate column name
    category_column = get_category_column(analysis_type)

    # Explode categories (one row per category per game)
    filtered_df['Categories_split'] = filtered_df[category_column].fillna('').str.split(',')
    exploded_df = filtered_df.explode('Categories_split')
    exploded_df['Categories_split'] = exploded_df['Categories_split'].str.strip()
    exploded_df = exploded_df[exploded_df['Categories_split'] != '']

    if len(exploded_df) == 0:
        st.warning("❌ No category data available after processing. Please check your filters.")
        return pd.DataFrame(), pd.DataFrame()

    metric_col = USER_METRIC_MAP[user_metric]

    # For categorical owners, convert to numerical score for visualization
    if user_metric == 'Estimated owners (categorical)':
        # Aggregate by category using manual aggregation
        category_stats = exploded_df.groupby('Categories_split').agg({
            'AppID': 'count'
        }).rename(columns={'AppID': 'Game_count'})

        # Add other metrics using safe aggregation
        category_stats['Positive'] = exploded_df.groupby('Categories_split').apply(
            lambda x: safe_aggregate(x, 'Positive', 'sum')
        )
        category_stats['Peak CCU'] = exploded_df.groupby('Categories_split').apply(
            lambda x: safe_aggregate(x, 'Peak CCU', aggregation_method)
        )
        category_stats['Total_reviews'] = exploded_df.groupby('Categories_split').apply(
            lambda x: safe_aggregate(x, 'Total_reviews', 'sum')
        )

        # Calculate owner scores
        def calculate_owner_score(category_group):
            valid_owners = category_group['Estimated owners'].dropna()
            if len(valid_owners) == 0:
                return 0

            total_games = len(valid_owners)
            score = sum(OWNER_SCORES.get(str(owner_cat), 0) for owner_cat in valid_owners) / total_games
            return score

        owner_scores_by_category = exploded_df.groupby('Categories_split').apply(calculate_owner_score)
        category_stats['User_metric_value'] = owner_scores_by_category

    else:
        # For numeric metrics
        category_stats = exploded_df.groupby('Categories_split').agg({
            'AppID': 'count'
        }).rename(columns={'AppID': 'Game_count'})

        # Add the user metric using safe aggregation
        if metric_col == 'Positive':
            category_stats['User_metric_value'] = exploded_df.groupby('Categories_split').apply(
                lambda x: safe_aggregate(x, 'Positive', aggregation_method)
            )
        elif metric_col == 'Peak CCU':
            category_stats['User_metric_value'] = exploded_df.groupby('Categories_split').apply(
                lambda x: safe_aggregate(x, 'Peak CCU', aggregation_method)
            )
        elif metric_col == 'Total_reviews':
            category_stats['User_metric_value'] = exploded_df.groupby('Categories_split').apply(
                lambda x: safe_aggregate(x, 'Total_reviews', aggregation_method)
            )

        # Add other metrics for completeness
        category_stats['Positive'] = exploded_df.groupby('Categories_split').apply(
            lambda x: safe_aggregate(x, 'Positive', 'sum')
        )
        category_stats['Peak CCU'] = exploded_df.groupby('Categories_split').apply(
            lambda x: safe_aggregate(x, 'Peak CCU', aggregation_method)
        )
        category_stats['Total_reviews'] = exploded_df.groupby('Categories_split').apply(
            lambda x: safe_aggregate(x, 'Total_reviews', 'sum')
        )

    # Filter out categories with too few games for meaningful analysis
    category_stats = category_stats[category_stats['Game_count'] >= 3]

    if len(category_stats) == 0:
        st.warning("❌ No categories with sufficient data (minimum 3 games per category). Please adjust filters.")
        return pd.DataFrame(), exploded_df

    category_stats = category_stats.sort_values('Game_count', ascending=False)

    return category_stats, exploded_df
