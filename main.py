import warnings

import streamlit as st

from config import ANALYSIS_TYPES
from data_loader import load_data, set_theme, get_all_categories
from data_processor import prepare_analysis_type_scatter_data, prepare_ccu_histogram_data
from visualizations import create_analysis_type_scatter_plot, create_ccu_histogram

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
        index=0,
        help="Choose whether to analyze by Genres or Tags"
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

    # TODO - replace with custom categories instead of all categories
    all_categories = get_all_categories(df)

    # Add the scatter plot visualization above data summary
    st.subheader(f"Popularity vs Quality")

    # Prepare data for scatter plot
    scatter_data = prepare_analysis_type_scatter_data(df, analysis_type, year_range, all_categories)

    # Create and display the scatter plot
    scatter_fig = create_analysis_type_scatter_plot(scatter_data, analysis_type)
    st.plotly_chart(scatter_fig, use_container_width=True)

    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("Popularity Distribution (Peak CCU)")
        ccu_counts = prepare_ccu_histogram_data(df, year_range)
        fig_hist = create_ccu_histogram(ccu_counts)
        st.plotly_chart(fig_hist, use_container_width=True)

    # Data summary
    with st.expander("📁 Dataset Summary"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Games", f"{len(df):,}")
        with col2:
            st.metric("Time Period", f"{min_year} - {max_year}")
        with col3:
            st.metric(f"Unique {analysis_type}", f"{len(all_categories[analysis_type]):,}")

        st.info(
            "\n\n".join(
                f"**{key}**  \n{values}"
                for key, values in all_categories.items()
            )
        )


if __name__ == "__main__":
    main()
