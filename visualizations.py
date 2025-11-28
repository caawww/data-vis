import plotly.express as px
import plotly.graph_objects as go

from config import CUSTOM_COLOURS


def empty_figure():
    fig = go.Figure()
    fig.add_annotation(
        text="No data available for the selected filters",
        xref="paper", yref="paper",
        x=0.5, y=0.5, xanchor='center', yanchor='middle',
        showarrow=False,
        font=dict(size=16, color=CUSTOM_COLOURS['text'])
    )
    fig.update_layout(
        paper_bgcolor=CUSTOM_COLOURS['background'],
        plot_bgcolor=CUSTOM_COLOURS['background'],
        font=dict(color=CUSTOM_COLOURS['text']),
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
        color_discrete_map={
            True: CUSTOM_COLOURS['red'],
            False: CUSTOM_COLOURS['accent_blue']
        }
    )

    # Update layout styling
    fig.update_layout(
        # title=f'Tags Analysis: Popularity vs Quality',
        xaxis_title='Number of Released Games (log)',
        yaxis_title='Average Peak CCU (log)',
        paper_bgcolor=CUSTOM_COLOURS['background'],
        plot_bgcolor=CUSTOM_COLOURS['card'],
        font=dict(color=CUSTOM_COLOURS['text']),
        height=600,
        showlegend=False,
        hoverlabel=dict(
            bgcolor=CUSTOM_COLOURS['sidebar'],
            font_size=12,
            font_family="Arial"
        )
    )

    fig.update_xaxes(
        gridcolor=CUSTOM_COLOURS['text'],
        zerolinecolor=CUSTOM_COLOURS['text'],
        tickformat=',',
        type='log',
    )

    fig.update_yaxes(
        gridcolor=CUSTOM_COLOURS['text'],
        zerolinecolor=CUSTOM_COLOURS['text'],
        tickformat=',',
        type='log',
    )

    # Update dot styling
    fig.update_traces(
        marker=dict(
            size=8,
            opacity=0.7,
            line=dict(width=1, color=CUSTOM_COLOURS['text'])
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
