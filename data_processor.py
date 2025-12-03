import streamlit as st


@st.cache_data
def prepare_analysis_type_scatter_data(df, raw_df, all_categories):
    # Explode the analysis_type column (split comma-separated values)
    df_exploded = df.copy()
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
    grouped['Avg_peak_ccu'] = grouped['Avg_peak_ccu'].replace(0, 0.1)

    # --- explode raw_df for global counts ---
    raw_exploded = raw_df.copy()
    raw_exploded['Tags'] = raw_exploded['Tags'].str.split(',')
    raw_exploded = raw_exploded.explode('Tags')
    raw_exploded['Tags'] = raw_exploded['Tags'].str.strip()
    raw_exploded = raw_exploded[raw_exploded['Tags'] != '']

    # Global total number of games per tag (unfiltered)
    global_tag_counts = (
        raw_exploded.groupby("Tags")["AppID"]
        .count()
        .reset_index(name="Total_Game_Count")
    )

    grouped = grouped.merge(global_tag_counts, on="Tags", how="left")

    grouped['Total_Game_Count'] = grouped['Total_Game_Count'].fillna(0).astype(int)

    return grouped.sort_values('Game_count', ascending=False)
