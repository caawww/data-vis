import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots
from upsetplot import UpSet, from_indicators


@st.cache_data
def empty_figure():
    fig = go.Figure()
    fig.add_annotation(
        text="No data available for the selected filters",
        xref="paper", yref="paper",
        x=0.5, y=0.5, xanchor='center', yanchor='middle',
        showarrow=False,
        font=dict(size=16)
    )
    fig.update_layout(
        height=500
    )
    return fig


@st.cache_data
def create_main_scatter_plot(scatter_data, selected_categories):
    if scatter_data.empty:
        return empty_figure()

    scatter_data['highlight'] = scatter_data['Tags'].isin(selected_categories)
    scatter_data['x_jitter'] = scatter_data['Game_count'] + np.random.uniform(-0.05, 0.05, len(scatter_data))
    scatter_data['y_jitter'] = scatter_data['Avg_peak_ccu'] + np.random.uniform(-0.05, 0.05, len(scatter_data))

    scatter_data['play_hours'] = (scatter_data['Avg_playtime'] // 60).astype(int)
    scatter_data['play_minutes'] = (scatter_data['Avg_playtime'] % 60).astype(int)

    # Create scatter plot
    fig = px.scatter(
        scatter_data,
        x='x_jitter',
        y='y_jitter',
        hover_name='Tags',
        custom_data=[
            scatter_data['Avg_total_review_ratio_pct'],
            scatter_data['Total_reviews'],
            scatter_data['Avg_peak_ccu'],
            scatter_data['Avg_review_ratio_pct'],
            scatter_data['Total_Game_Count'],
            scatter_data['Game_count'],
            scatter_data['play_hours'],
            scatter_data['play_minutes']
        ],
        size_max=15,
        color="highlight",
        color_discrete_map={True: '#ff0000'}
    )

    # Update layout styling
    fig.update_layout(
        # title=f'Tags Analysis: Popularity vs Quality',
        xaxis_title='Number of Released Games (log scale)',
        yaxis_title='Average Peak CCU (log scale)',
        height=600,
        showlegend=False,
        hoverlabel=dict(
            font_size=12,
            font_family="Arial"
        )
    )

    fig.update_xaxes(
        tickformat=',',
        type='log',
        # dtick=1,
        showgrid=True,
    )

    fig.update_yaxes(
        tickformat=',',
        type='log',
        # dtick=1,
        showgrid=True,
    )

    # Update dot styling
    fig.update_traces(
        marker=dict(
            size=8,
            opacity=0.7,
            line=dict(width=1)
        ),
        hovertemplate=(
            "<b>%{hovertext}</b><br><br>"
            "Filtered Number of Games: %{customdata[5]} (out of %{customdata[4]:,})<br>"
            "Average Review Ratio: %{customdata[3]:.1f}%<br>"
            "Total Average Review ratio: %{customdata[0]:.1f}%<br>"
            "Total Reviews: %{customdata[1]:,}<br>"
            "Avg Playtime: %{customdata[6]}h %{customdata[7]:02d}m<br>"
            "Avg Peak CCU: %{customdata[2]:.0f}<extra></extra>"
        )
    )

    return fig


def create_violin_summary(tag_df, year_range):
    min_year, max_year = year_range
    all_years = list(range(min_year, max_year + 1))

    fig = make_subplots(
        rows=2, cols=2,
        shared_xaxes="all",
        horizontal_spacing=0.1,
        vertical_spacing=0.15,
        subplot_titles=("Peak CCU", "Average Playtime Forever", "Review Ratio", "Price")
    )

    cols_info = [
        ("Peak CCU", 1, 1, "blue", "log"),
        ("Average playtime forever", 1, 2, "purple", "log"),
        ("Review_ratio", 2, 1, "orange", "linear"),
        ("Price", 2, 2, "green", "linear"),
    ]

    for col_name, row, col, color, scale in cols_info:
        for year in all_years:
            year_values = tag_df[tag_df["Release_year"] == year][col_name].tolist()
            if len(year_values) == 0:
                year_values = [0]
            fig.add_trace(
                go.Violin(
                    y=year_values,
                    x=[year] * len(year_values),
                    name=str(year),
                    box_visible=True,
                    line_color=color,
                    marker=dict(size=3),
                    meanline_visible=True,
                    showlegend=False,
                    hovertemplate="Year: %{x}<br>" + col_name + ": %{y}<extra></extra>"
                ),
                row=row,
                col=col
            )
        fig.update_yaxes(title_text=col_name, type=scale, row=row, col=col)

    fig.update_layout(
        height=800,
        width=1000,
        hovermode="closest",
        title_text="Tag Metrics Over Years"
    )

    fig.update_xaxes(title_text="Release Year", tickmode="linear", row=1, col=1, showticklabels=True)
    fig.update_xaxes(title_text="Release Year", tickmode="linear", row=1, col=2, showticklabels=True)
    fig.update_xaxes(title_text="Release Year", tickmode="linear", row=2, col=1, showticklabels=True)
    fig.update_xaxes(title_text="Release Year", tickmode="linear", row=2, col=2, showticklabels=True)

    return fig


@st.cache_data
def create_games_per_year_bar(tag_df, selected_tag):
    """Plot number of games released per year for a given tag as a bar chart."""
    if tag_df.empty:
        return empty_figure()  # Define empty_figure() to return a blank figure

    # Count number of games per year
    yearly_count = (
        tag_df.groupby("Release_year")["Name"]
        .count()
        .reset_index(name="Game_count")
        .sort_values("Release_year")
    )

    fig = px.bar(
        yearly_count,
        x="Release_year",
        y="Game_count",
        labels={
            "Release_year": "Release Year",
            "Game_count": "Number of Games"
        },
        # title=f"Number of Games Released Over Time for Tag '{selected_tag}'",
        hover_data={
            "Game_count": True
        },
        text="Game_count"
    )

    fig.update_traces(marker_color='skyblue', textposition='outside')
    fig.update_xaxes(dtick=1)
    fig.update_yaxes(rangemode='tozero')

    return fig


def create_upset_plot(df, selected_tags, width=12, height=6):
    if len(df) < 50 or len(selected_tags) < 2:
        fig = plt.figure(figsize=(width, height))
        fig.add_subplot(111).text(
            0.5, 0.5, "Not enough data available for the selected filters",
            ha='center', va='center', fontsize=16
        )
        return fig

    data = df.copy()
    for tag in selected_tags:
        data[tag] = data["Tags"].apply(lambda t: tag in t)

    indicators = from_indicators(selected_tags, data[selected_tags])

    fig = plt.figure(figsize=(width, height))

    upset = UpSet(
        indicators,
        subset_size="count",
        sort_by="cardinality",
        sort_categories_by=None,
    )
    upset.plot(fig=fig)

    return fig
