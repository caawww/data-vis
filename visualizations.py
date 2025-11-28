import plotly.express as px
import plotly.graph_objects as go


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


def create_main_scatter_plot(scatter_data, selected_categories):
    """
    Create a scatter plot showing Tags categories vs review ratio
    """
    if scatter_data.empty:
        return empty_figure()

    scatter_data['highlight'] = scatter_data['Tags'].isin(selected_categories)

    # Create scatter plot
    fig = px.scatter(
        scatter_data,
        x='Game_count',
        y='Avg_peak_ccu',
        hover_name='Tags',
        custom_data=[
            scatter_data['Avg_total_review_ratio_pct'],
            scatter_data['Total_reviews'],
            scatter_data['Avg_playtime'],
            scatter_data['Avg_peak_ccu'],
            scatter_data['Avg_review_ratio_pct']
        ],
        size_max=15,
        color="highlight",
        color_discrete_map={True: '#ff0000'}  # TODO - Specify what colour to highlight with
    )

    # Update layout styling
    fig.update_layout(
        # title=f'Tags Analysis: Popularity vs Quality',
        xaxis_title='Number of Released Games (log)',
        yaxis_title='Average Peak CCU (log)',
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
    )

    fig.update_yaxes(
        tickformat=',',
        type='log',
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
            "Number of Games: %{x}<br>"
            "Average Review Ratio: %{customdata[4]:.1f}%<br>"
            "Total Average Review ratio: %{customdata[0]:.1f}%<br>"
            "Total Reviews: %{customdata[1]:,}<br>"
            "Avg Playtime: %{customdata[2]:.1f} hours<br>"
            "Avg Peak CCU: %{customdata[3]:.0f}<extra></extra>"
        )
    )

    return fig


def create_review_ratio_over_time(tag_df, selected_tag):
    """Plot average Review_ratio per year for a given tag, including count of games in hover."""
    if tag_df.empty:
        return empty_figure()

    # Compute average ratio per year
    yearly_avg = (
        tag_df.groupby("Release_year")["Review_ratio"]
        .mean()
        .reset_index()
    )

    # Compute number of games per year
    yearly_count = (
        tag_df.groupby("Release_year")["Name"]
        .count()
        .reset_index(name="Game_count")
    )

    # Merge the two
    yearly_stats = yearly_avg.merge(yearly_count, on="Release_year").sort_values("Release_year")

    fig = px.line(
        yearly_stats,
        x="Release_year",
        y="Review_ratio",
        markers=True,
        labels={
            "Release_year": "Release Year",
            "Review_ratio": "Average Positive Review Ratio",
            "Game_count": "Number of Games"
        },
        # title=f"Average Review Ratio Over Time for Tag '{selected_tag}'",
        hover_data={
            "Game_count": True,
            "Review_ratio": ":.3f"  # cleaner formatting
        }
    )

    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=8, opacity=0.9),
    )

    fig.update_yaxes(
        range=[-0.02, 1.02],
    )

    fig.update_xaxes(
        dtick=1,
    )

    return fig
