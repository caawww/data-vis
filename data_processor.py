def prepare_analysis_type_scatter_data(df, analysis_type, year_range):
    """
    Prepare data for scatter plot showing analysis_type categories vs review ratio

    Args:
        df: DataFrame with game data
        analysis_type: 'Genres', 'Tags', or 'Categories'
        year_range: tuple of (min_year, max_year)

    Returns:
        DataFrame with aggregated metrics per analysis_type
    """
    # Filter by year range
    min_year, max_year = year_range
    df_filtered = df[(df['Release_year'] >= min_year) & (df['Release_year'] <= max_year)]

    # Explode the analysis_type column (split comma-separated values)
    df_exploded = df_filtered.copy()
    df_exploded[analysis_type] = df_exploded[analysis_type].str.split(',')
    df_exploded = df_exploded.explode(analysis_type)

    # Clean up - remove whitespace and filter out empty strings
    df_exploded[analysis_type] = df_exploded[analysis_type].str.strip()
    df_exploded = df_exploded[df_exploded[analysis_type] != '']

    # Group by analysis_type and calculate aggregated metrics
    grouped = df_exploded.groupby(analysis_type).agg({
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
    grouped['Avg_review_ratio_pct'] = grouped['Avg_review_ratio'] * 100
    grouped['Total_reviews'] = grouped['Positive'] + grouped['Negative']

    # Fill NaN values for playtime and CCU with 0
    grouped['Avg_playtime'] = grouped['Avg_playtime'].fillna(0)
    grouped['Avg_peak_ccu'] = grouped['Avg_peak_ccu'].fillna(0)

    # Filter out categories with very few games (optional - adjust threshold as needed)
    grouped = grouped[grouped['Game_count'] >= 3]

    return grouped.sort_values('Game_count', ascending=False)
