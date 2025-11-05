import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
import streamlit as st
from data_processor import safe_aggregate
from config import OWNER_SCORES, USER_METRIC_MAP, STEAM_COLORS


def create_gap_analysis_chart(category_stats, user_metric, analysis_type):
    """Create bubble chart showing developer vs user attention gap"""

    if len(category_stats) == 0:
        return None, category_stats

    # Calculate ranks
    category_stats['Dev_rank'] = category_stats['Game_count'].rank(ascending=False, method='min')
    category_stats['User_rank'] = category_stats['User_metric_value'].rank(ascending=False, method='min')
    category_stats['Gap'] = category_stats['Dev_rank'] - category_stats['User_rank']

    # Size based on geometric mean of both metrics (avoiding extreme values)
    category_stats['Bubble_size'] = np.sqrt(category_stats['Game_count'] * category_stats['User_metric_value'])

    # Create the scatter plot
    fig = px.scatter(
        category_stats,
        x='Game_count',
        y='User_metric_value',
        size='Bubble_size',
        hover_name=category_stats.index,
        color='Gap',
        color_continuous_scale='RdYlBu_r',  # Red (oversaturated) to Blue (underserved)
        title=f"{analysis_type} Gap Analysis: Developer Releases vs {user_metric}",
        labels={
            'Game_count': 'Number of Game Releases (Developer Attention)',
            'User_metric_value': f'{user_metric} (User Attention)',
            'Gap': 'Dev Rank - User Rank'
        }
    )

    # Add quadrant annotations
    max_x = category_stats['Game_count'].max()
    max_y = category_stats['User_metric_value'].max()

    fig.add_annotation(
        x=max_x * 0.75, y=max_y * 0.25,
        text="Over-saturated<br>(High Dev, Low User)",
        showarrow=False,
        bgcolor="rgba(255,100,100,0.3)",
        bordercolor="red",
        font=dict(color="white")
    )

    fig.add_annotation(
        x=max_x * 0.25, y=max_y * 0.75,
        text="Under-served<br>(Low Dev, High User)",
        showarrow=False,
        bgcolor="rgba(100,100,255,0.3)",
        bordercolor="blue",
        font=dict(color="white")
    )

    fig.update_layout(
        plot_bgcolor=STEAM_COLORS['card'],
        paper_bgcolor=STEAM_COLORS['background'],
        font_color=STEAM_COLORS['text'],
        title_font_color='#ffffff',
        showlegend=False,
        height=600
    )

    fig.update_traces(
        marker=dict(line=dict(width=1, color='DarkSlateGrey')),
        hovertemplate=(
                "<b>%{hovertext}</b><br><br>" +
                "Game Releases: %{x}<br>" +
                f"{user_metric}: %{{y:.2f}}<br>" +
                "Gap (Dev Rank - User Rank): %{marker.color:.1f}<extra></extra>"
        )
    )

    return fig, category_stats


def create_trend_chart(exploded_df, selected_trend_category, user_metric, aggregation_method, analysis_type):
    """Create time series trend for a specific category"""

    if not selected_trend_category or len(exploded_df) == 0:
        return None

    # Filter for selected category
    trend_df = exploded_df[exploded_df['Categories_split'] == selected_trend_category].copy()

    if len(trend_df) == 0:
        return None

    metric_col = USER_METRIC_MAP[user_metric]

    # Prepare yearly data using safe aggregation
    yearly_data = []

    for year, year_group in trend_df.groupby('Release_year'):
        game_releases = len(year_group)

        if user_metric == 'Estimated owners (categorical)':
            # Handle categorical owners
            valid_owners = year_group['Estimated owners'].dropna()
            if len(valid_owners) == 0:
                user_metric_value = 0
            else:
                total_games = len(valid_owners)
                user_metric_value = sum(OWNER_SCORES.get(str(owner_cat), 0) for owner_cat in valid_owners) / total_games
        else:
            # Handle numeric metrics
            user_metric_value = safe_aggregate(year_group, metric_col, aggregation_method)

        yearly_data.append({
            'Release_year': year,
            'Game_releases': game_releases,
            'User_metric': user_metric_value if not pd.isna(user_metric_value) else 0
        })

    yearly_data = pd.DataFrame(yearly_data).set_index('Release_year')

    if len(yearly_data) < 2:
        st.info(
            f"📊 Not enough yearly data for trend analysis of '{selected_trend_category}'. Need at least 2 years of data.")
        return None

    # Create subplot with two y-axes
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Developer attention (left axis)
    fig.add_trace(
        go.Scatter(
            x=yearly_data.index,
            y=yearly_data['Game_releases'],
            name="Game Releases (Dev)",
            line=dict(color=STEAM_COLORS['accent_blue'], width=3),
            mode='lines+markers'
        ),
        secondary_y=False,
    )

    # User attention (right axis)
    fig.add_trace(
        go.Scatter(
            x=yearly_data.index,
            y=yearly_data['User_metric'],
            name=f"{user_metric} (User)",
            line=dict(color=STEAM_COLORS['accent_green'], width=3),
            mode='lines+markers'
        ),
        secondary_y=True,
    )

    fig.update_layout(
        title=f"Trend Analysis: {selected_trend_category} ({analysis_type})",
        plot_bgcolor=STEAM_COLORS['card'],
        paper_bgcolor=STEAM_COLORS['background'],
        font_color=STEAM_COLORS['text'],
        title_font_color='#ffffff',
        height=400,
        showlegend=True
    )

    fig.update_xaxes(title_text="Release Year", showgrid=True, gridwidth=1, gridcolor='#3c5a78')
    fig.update_yaxes(title_text="Number of Game Releases", secondary_y=False, showgrid=False)
    fig.update_yaxes(title_text=user_metric, secondary_y=True, showgrid=False)

    return fig


def create_rankings_tables(ranked_categories, user_metric, analysis_type):
    """Create ranking tables for display in the sidebar"""
    if len(ranked_categories) == 0:
        return None, None, None, None

    # Top categories by developer interest
    dev_top = ranked_categories.nlargest(8, 'Game_count')[['Game_count']]
    dev_top['Game_count'] = dev_top['Game_count'].astype(int)

    # Top categories by user interest
    user_top = ranked_categories.nlargest(8, 'User_metric_value')
    display_col = 'User_metric_value'
    if user_metric == 'Estimated owners (categorical)':
        user_top[display_col] = user_top[display_col].round(2)
    else:
        user_top[display_col] = user_top[display_col].round(1)

    # Gap analysis table
    gap_analysis = ranked_categories[['Game_count', 'User_metric_value', 'Gap']].copy()
    gap_analysis['Gap'] = gap_analysis['Gap'].round(1)

    # Show biggest positive and negative gaps
    oversaturated = gap_analysis.nlargest(3, 'Gap')
    underserved = gap_analysis.nsmallest(3, 'Gap')

    return dev_top, user_top, oversaturated, underserved
