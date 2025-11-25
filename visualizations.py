import plotly.express as px
import plotly.graph_objects as go

from config import CUSTOM_COLOURS


def create_analysis_type_scatter_plot(scatter_data, analysis_type, selected_categories):
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

    scatter_data['highlight'] = scatter_data[analysis_type].isin(selected_categories)
    # Create scatter plot with only two hover values
    fig = px.scatter(
        scatter_data,
        x='Game_count',
        y='Avg_review_ratio_pct',
        hover_name=analysis_type,
        custom_data=[
            scatter_data['Avg_total_review_ratio_pct'],
            scatter_data['Total_reviews'],
            scatter_data['Avg_playtime'],
            scatter_data['Avg_peak_ccu']
        ],
        size_max=15,
        color="highlight",
        color_discrete_map={
            True: CUSTOM_COLOURS['red'],   # color for items in your list
            False: CUSTOM_COLOURS['accent_blue']    # default color
        }
    )

    # Update layout styling
    fig.update_layout(
        # title=f'{analysis_type} Analysis: Popularity vs Quality',
        xaxis_title='Number of Released Games (log)',
        yaxis_title='Average Ratio of Positive Reviews (%)',
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
        # range=[-2, 102]
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
            "Total Average Review ratio: %{customdata[0]:.1f}%<br>"
            "Total Reviews: %{customdata[1]:,}<br>"
            "Avg Playtime: %{customdata[2]:.1f} hours<br>"
            "Avg Peak CCU: %{customdata[3]:.0f}<extra></extra>"
        )
    )

    return fig


def create_analysis_type_scatter_plot_peak(scatter_data, analysis_type, selected_categories):
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

    scatter_data['highlight'] = scatter_data[analysis_type].isin(selected_categories)
    # Create scatter plot with only two hover values
    fig = px.scatter(
        scatter_data,
        x='Game_count',
        y='Avg_peak_ccu',
        hover_name=analysis_type,
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
            True: CUSTOM_COLOURS['red'],   # color for items in your list
            False: CUSTOM_COLOURS['accent_blue']    # default color
        }
    )

    # Update layout styling
    fig.update_layout(
        # title=f'{analysis_type} Analysis: Popularity vs Quality',
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


def create_ccu_histogram(ccu_counts):
    """
    Create a histogram for Peak CCU ranges.

    Args:
        ccu_counts: Series with CCU_bin as index and counts as values

    Returns:
        Plotly figure
    """
    fig = px.bar(
        x=ccu_counts.index,
        y=ccu_counts.values,
        labels={'x': 'Peak CCU Range', 'y': 'Number of Games'},
        title='Games by Peak Concurrent Users',
        color_discrete_sequence=[CUSTOM_COLOURS['accent_blue']]
    )

    fig.update_layout(
        paper_bgcolor=CUSTOM_COLOURS['background'],
        plot_bgcolor=CUSTOM_COLOURS['card'],
        font=dict(color=CUSTOM_COLOURS['text']),
        title_font_size=16
    )

    fig.update_xaxes(gridcolor=CUSTOM_COLOURS['text'], zerolinecolor=CUSTOM_COLOURS['text'])
    fig.update_yaxes(gridcolor=CUSTOM_COLOURS['text'], zerolinecolor=CUSTOM_COLOURS['text'])

    return fig


def create_category_metric_bar(df_metric, analysis_type, metric):
    """
    Create a bar chart for a specific metric per category.
    """
    if df_metric.empty:
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

    fig = px.bar(
        df_metric,
        x=analysis_type,
        y=metric,
        text=metric,
        color_discrete_sequence=[CUSTOM_COLOURS['accent_blue']]
    )

    fig.update_layout(
        paper_bgcolor=CUSTOM_COLOURS['background'],
        plot_bgcolor=CUSTOM_COLOURS['card'],
        font=dict(color=CUSTOM_COLOURS['text']),
        xaxis_title=analysis_type,
        yaxis_title=metric.replace('_', ' '),
        height=500
    )

    # TODO - add number of games
    fig.update_traces(
        texttemplate='%{text:.2f}' if df_metric[metric].dtype != int else '%{text}',
        textposition='outside',
        marker=dict(line=dict(width=1, color=CUSTOM_COLOURS['text']))
    )

    return fig
