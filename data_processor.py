import pandas as pd


def filter_year(df, year_range):
    return df[(df['Release_year'] >= year_range[0]) & (df['Release_year'] <= year_range[1])]


def prepare_analysis_type_scatter_data(df, analysis_type, year_range, all_categories):
    """
    Prepare data for scatter plot showing analysis_type categories vs review ratio

    Args:
        df: DataFrame with game data
        analysis_type: 'Genres', 'Tags', or 'Categories'
        year_range: tuple of (min_year, max_year)
        all_categories: dict with lists of categories/genres/tags to include for each analysis type

    Returns:
        DataFrame with aggregated metrics per analysis_type
    """
    df_filtered = filter_year(df, year_range)

    # Explode the analysis_type column (split comma-separated values)
    df_exploded = df_filtered.copy()
    df_exploded[analysis_type] = df_exploded[analysis_type].str.split(',')
    df_exploded = df_exploded.explode(analysis_type)

    # Clean up - remove whitespace and filter out empty strings
    df_exploded[analysis_type] = df_exploded[analysis_type].str.strip()
    df_exploded = df_exploded[df_exploded[analysis_type] != '']

    # keep only selected categories/genres/tags
    df_exploded = df_exploded[df_exploded[analysis_type].isin(all_categories[analysis_type])]

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
    # TODO - which review ratio to use
    grouped['Avg_review_ratio_pct'] = grouped['Avg_review_ratio'] * 100
    grouped['Total_reviews'] = grouped['Positive'] + grouped['Negative']
    grouped['Avg_total_review_ratio_pct'] = grouped['Positive'] / grouped['Total_reviews'] * 100

    # Fill NaN values for playtime and CCU with 0
    grouped['Avg_playtime'] = grouped['Avg_playtime'].fillna(0)
    grouped['Avg_peak_ccu'] = grouped['Avg_peak_ccu'].fillna(0)

    # Filter out categories with very few games (optional - adjust threshold as needed)
    grouped = grouped[grouped['Game_count'] >= 3]

    return grouped.sort_values('Game_count', ascending=False)


def prepare_ccu_histogram_data(df, year_range):
    """
    Prepare histogram data for Peak CCU ranges.

    Args:
        df: DataFrame with game data
        year_range: tuple of (min_year, max_year)

    Returns:
        DataFrame with 'CCU_bin' as index and counts as values
    """
    df_filtered = filter_year(df, year_range)

    # Define bins
    bins = [0, 1, 20, 200, 2000, 20000, float('inf')]
    labels = ['0-1', '2-20', '21-200', '201-2000', '2001-20000', '20001+']

    df_filtered['CCU_bin'] = pd.cut(df_filtered['Peak CCU'], bins=bins, labels=labels, right=True)

    # Count number of games per bin
    ccu_counts = df_filtered['CCU_bin'].value_counts().sort_index()

    return ccu_counts


def prepare_category_metric_data(df, analysis_type, year_range, metric, top_n=None):
    """
    Prepare data for bar chart showing a selected metric per category.

    Args:
        df: DataFrame with game data
        analysis_type: 'Genres', 'Tags', or 'Categories'
        year_range: tuple of (min_year, max_year)
        metric: 'Total_reviews', 'Game_count', 'Avg_peak_ccu'
        top_n: int, optional, limit to top N categories by the metric

    Returns:
        DataFrame with columns: [analysis_type, metric]
    """
    # Filter by year
    min_year, max_year = year_range
    df_filtered = df[(df['Release_year'] >= min_year) & (df['Release_year'] <= max_year)]

    # Explode categories/tags/genres
    df_exploded = df_filtered.copy()
    df_exploded[analysis_type] = df_exploded[analysis_type].str.split(',')
    df_exploded = df_exploded.explode(analysis_type)
    df_exploded[analysis_type] = df_exploded[analysis_type].str.strip()
    df_exploded = df_exploded[df_exploded[analysis_type] != '']

    # Aggregate metrics
    grouped = df_exploded.groupby(analysis_type).agg({
        'AppID': 'count',  # number of games
        'Positive': 'sum',
        'Negative': 'sum',
        'Peak CCU': 'mean'
    }).reset_index()

    # Add derived metrics
    grouped['Game_count'] = grouped['AppID']
    grouped['Total_reviews'] = grouped['Positive'] + grouped['Negative']
    grouped['Avg_peak_ccu'] = grouped['Peak CCU']

    # Select desired metric
    grouped_metric = grouped[[analysis_type, metric]]

    # Sort by metric descending
    grouped_metric = grouped_metric.sort_values(metric, ascending=False)

    # Limit top N if requested
    if top_n:
        grouped_metric = grouped_metric.head(top_n)

    return grouped_metric
