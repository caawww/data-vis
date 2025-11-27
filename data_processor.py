def filter_year(df, year_range):
    return df[(df['Release_year'] >= year_range[0]) & (df['Release_year'] <= year_range[1])]


def prepare_analysis_type_scatter_data(df, year_range, all_categories, number_of_games_range):
    """
    Prepare data for scatter plot showing analysis_type categories vs review ratio

    Args:
        df: DataFrame with game data
        year_range: tuple of (min_year, max_year)
        all_categories: dict with lists of categories/genres/tags to include for each analysis type

    Returns:
        DataFrame with aggregated metrics per analysis_type
    """
    df_filtered = filter_year(df, year_range)

    # Explode the analysis_type column (split comma-separated values)
    df_exploded = df_filtered.copy()
    df_exploded['Tags'] = df_exploded['Tags'].str.split(',')
    df_exploded = df_exploded.explode('Tags')

    # Clean up - remove whitespace and filter out empty strings
    df_exploded['Tags'] = df_exploded['Tags'].str.strip()
    df_exploded = df_exploded[df_exploded['Tags'] != '']

    # keep only selected categories/genres/tags
    df_exploded = df_exploded[df_exploded['Tags'].isin(all_categories)]

    # Group by Tags and calculate aggregated metrics
    grouped = df_exploded.groupby('Tags').agg({
        'AppID': 'count',  # Number of games
        'Review_ratio': 'mean',  # Average review ratio
        'Positive': 'sum',  # Total positive reviews
        'Negative': 'sum',  # Total negative reviews
        'Average playtime forever': 'mean',  # Avg playtime
        'Peak CCU': 'mean'  # Avg peak CCU
    }).reset_index()

    # Rename columns for clarity
    grouped = grouped.rename(columns={
        'AppID': 'Game_count',
        'Review_ratio': 'Avg_review_ratio',
        'Average playtime forever': 'Avg_playtime',
        'Peak CCU': 'Avg_peak_ccu'
    })

    # Calculate percentage values for display
    # TODO - which review ratio to use
    grouped['Avg_review_ratio_pct'] = grouped['Avg_review_ratio'] * 100
    grouped['Total_reviews'] = grouped['Positive'] + grouped['Negative']
    grouped['Avg_total_review_ratio_pct'] = grouped['Positive'] / grouped['Total_reviews'] * 100

    # Fill NaN values for playtime and CCU with 0
    grouped['Avg_playtime'] = grouped['Avg_playtime'].fillna(0)
    grouped['Avg_peak_ccu'] = grouped['Avg_peak_ccu'].fillna(0)

    # Filter out categories with very few games (optional - adjust threshold as needed)
    grouped = grouped[grouped['Game_count'] >= number_of_games_range]

    return grouped.sort_values('Game_count', ascending=False)
