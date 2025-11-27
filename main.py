import warnings

import streamlit as st

from config import ANALYSIS_TYPES
from data_loader import load_data, set_theme, get_all_categories, filter_data
from data_processor import prepare_analysis_type_scatter_data, prepare_ccu_histogram_data, prepare_category_metric_data
from visualizations import create_main_scatter_plot, create_ccu_histogram, create_category_metric_bar

warnings.simplefilter(action='ignore', category=FutureWarning)


def main():
    # Set up page and theme
    set_theme()
    st.set_page_config(
        page_title="Steam Genre Analysis",
        page_icon="🎮",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("🎮 Steam Visualisation")
    st.markdown("""""")

    # Load data
    df = load_data()
    total_number_of_games = len(df)
    df = filter_data(df)

    # TODO - replace with custom categories instead of all categories
    all_categories = get_all_categories(df)

    # Check data
    if len(df) == 0:
        st.error("❌ No valid data available after preprocessing.")
        return

    # Sidebar controls
    st.sidebar.header("Control Panel")
    # Analysis type selection
    st.sidebar.subheader("Analysis Type")
    analysis_type = st.sidebar.radio(
        "Analyze by:",
        options=ANALYSIS_TYPES,
        index=1,
        help="Choose whether to analyze by Categories or Tags"
    )

    # Year range slider - safely get min and max years
    valid_years = df['Release_year'].dropna()
    if len(valid_years) == 0:
        st.error("❌ No valid release years found in the dataset.")
        return

    min_year = int(valid_years.min())
    max_year = int(valid_years.max())

    year_range = st.sidebar.slider(
        "Select Year Range:",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
        step=1
    )

    number_of_games_range = st.sidebar.slider(
        "Select Number of Min Games:",
        min_value=1,
        max_value=50,
        value=1,
        step=1
    )

    # # Right column controls
    # st.sidebar.subheader("Analysis Type")
    # right_metric = st.sidebar.selectbox(
    #     "Select Metric for Bar Chart (Right Side):",
    #     options=['Total_reviews', 'Game_count', 'Avg_peak_ccu'],
    #     index=0
    # )
    # upper_buffer = len(all_categories[analysis_type])
    # top_n = st.sidebar.slider("Top N categories to show", min_value=5, max_value=min(100, upper_buffer),
    #                           value=min(40, upper_buffer), step=1)

    # Add the scatter plot visualization above data summary
    selected_categories = st.multiselect(
        f"{analysis_type} to highlight:",
        options=all_categories[analysis_type],
        default=None,
    )

    st.subheader(f"Peak CCU vs Number of Released Games by {analysis_type}")
    scatter_data = prepare_analysis_type_scatter_data(df, analysis_type, year_range, all_categories,
                                                      number_of_games_range)
    scatter_fig = create_main_scatter_plot(scatter_data, analysis_type, selected_categories)
    st.plotly_chart(scatter_fig, use_container_width=True)

    # # Visualise multiple data
    # st.subheader(f"{right_metric.replace('_', ' ')} per {analysis_type} [TODO RENAME]")
    # df_right = prepare_category_metric_data(df, analysis_type, year_range, right_metric, top_n=top_n)
    # fig_right = create_category_metric_bar(df_right, analysis_type, right_metric)
    # st.plotly_chart(fig_right, use_container_width=True)
    #
    # col_left, col_right = st.columns(2)
    # with col_left:
    #     st.subheader("Popularity Distribution (Peak CCU)")
    #     ccu_counts = prepare_ccu_histogram_data(df, year_range)
    #     fig_hist = create_ccu_histogram(ccu_counts)
    #     st.plotly_chart(fig_hist, use_container_width=True)

    # Data summary
    with st.expander("📁 Dataset Summary"):
        col1, col2, col3, col4 = st.columns(4)
        filtered_number_of_games = len(df)
        with col1:
            st.metric("Total Games", f"{total_number_of_games:,}")
        with col2:
            st.metric("Filtered Games",
                      f"{filtered_number_of_games:,} ({100 * filtered_number_of_games / total_number_of_games:.2f}%)")
        with col3:
            st.metric("Time Period", f"{min_year} - {max_year}")
        with col4:
            st.metric(f"Unique {analysis_type}", f"{len(all_categories[analysis_type]):,}")

        st.info(
            "\n\n".join(
                f"**{key}**  \n{values}"
                for key, values in all_categories.items()
            )
        )


if __name__ == "__main__":
    main()
