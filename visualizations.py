import plotly.express as px
import plotly.graph_objects as go
from config import CUSTOM_COLOURS


def create_analysis_type_scatter_plot(scatter_data, analysis_type):
    """
    Create a scatter plot showing analysis_type categories vs review ratio
    """
    if scatter_data.empty:
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

    # Create scatter plot with only two hover values
    fig = px.scatter(
        scatter_data,
        x='Game_count',
        y='Avg_review_ratio_pct',
        hover_name=analysis_type,
        custom_data=[
            scatter_data['Total_reviews'],
            scatter_data['Avg_playtime'],
            scatter_data['Avg_peak_ccu']
        ],
        size_max=15,
        color_discrete_sequence=[CUSTOM_COLOURS['accent_blue']]
    )

    # 50% reference line
    fig.add_hline(
        y=50,
        line_dash="dash",
        line_color=CUSTOM_COLOURS['accent_green'],
        line_width=1,
        opacity=0.7,
        annotation_text="50% Review Ratio",
        annotation_position="right",
        annotation_font_size=12,
        annotation_font_color=CUSTOM_COLOURS['accent_green']
    )

    # Update layout styling
    fig.update_layout(
        title=f'{analysis_type} Analysis: Popularity vs Quality',
        xaxis_title='Number of Games',
        yaxis_title='Average Review Ratio (%)',
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
        # range=[0, scatter_data['Game_count'].max() * 1.05]
    )

    fig.update_yaxes(
        gridcolor=CUSTOM_COLOURS['text'],
        zerolinecolor=CUSTOM_COLOURS['text'],
        ticksuffix='%',
        range=[-2, 102]
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
            "Average Review Ratio: %{y:.1f}%<br>"
            "Total Reviews: %{customdata[0]:,}<br>"
            "Avg Playtime: %{customdata[1]:.1f} hours<br>"
            "Avg Peak CCU: %{customdata[2]:.0f}<extra></extra>"
        )
    )

    return fig
