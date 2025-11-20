import streamlit as st
from data_loader import load_data, set_theme, get_all_categories
from data_processor import prepare_category_data
from visualizations import create_gap_analysis_chart, create_trend_chart, create_rankings_tables
from config import ANALYSIS_TYPES
import warnings

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

    st.title("🎮 Steam Category Analysis: Developer vs User Attention")
    st.markdown("""
    **Analyze the gap between what developers are creating and what users are engaging with on Steam.**
    Identify over-saturated categories (high developer interest, low user engagement) and under-served categories (low developer interest, high user engagement).
    """)

    # Load data
    df = load_data()

    # Check if we have valid data
    if len(df) == 0:
        st.error("❌ No valid data available after preprocessing. Please check your dataset.")
        return

    # Sidebar controls
    st.sidebar.header("🔧 Control Panel")

    # Analysis type selection
    st.sidebar.subheader("📈 Analysis Type")
    analysis_type = st.sidebar.radio(
        "Analyze by:",
        options=list(ANALYSIS_TYPES.keys()),
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
        value=(max(min_year, 2015), max_year),
        step=1
    )

    # Category selection with include/exclude option
    all_categories = get_all_categories(df, analysis_type)

    st.sidebar.subheader("🎯 Category Filtering")
    category_filter_type = st.sidebar.radio(
        f"{analysis_type} Filter Type:",
        options=["Include only selected categories", "Exclude selected categories"],
        index=0,
        help=f"Choose whether to include only the selected {analysis_type.lower()} or exclude them"
    )

    selected_categories = st.sidebar.multiselect(
        f"{analysis_type} to {category_filter_type.split()[-1].lower()}:",
        options=all_categories,
        default=None,
        help=f"Select {analysis_type.lower()} to {category_filter_type.lower()}"
    )

    st.sidebar.subheader("📊 Analysis Settings")

    # User metric selection
    user_metric = st.sidebar.selectbox(
        "User Attention Metric:",
        options=[
            'Estimated owners (categorical)',
            'Positive reviews',
            'Peak CCU',
            'Total reviews'
        ],
        index=0,
        help="Choose how to measure user engagement and attention"
    )

    # Aggregation method
    aggregation_method = st.sidebar.radio(
        "Aggregation Method:",
        options=['mean', 'median'],
        index=1,
        help="Mean for total impact, Median for typical game performance"
    )

    # Prepare data
    category_stats, exploded_df = prepare_category_data(
        df, year_range, selected_categories, category_filter_type, analysis_type, user_metric, aggregation_method
    )

    # Main content
    if len(category_stats) == 0:
        st.warning("🚫 No data available for the current filters. Please adjust your selection.")
        return

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader(f"📊 {analysis_type} Gap Analysis")
        gap_fig, ranked_categories = create_gap_analysis_chart(category_stats, user_metric, analysis_type)

        if gap_fig:
            st.plotly_chart(gap_fig, use_container_width=True)
        else:
            st.warning("Unable to generate gap analysis chart with current data.")

        # Interpretation guide
        with st.expander("💡 How to interpret this chart"):
            st.markdown(f"""
            - **Over-saturated {analysis_type}** (Bottom-right, Red): Many games being released but relatively low user engagement
            - **Under-served {analysis_type}** (Top-left, Blue): High user engagement but relatively few games being released  
            - **Bubble Size**: Overall market presence (combination of releases and user engagement)
            - **Gap Score**: Positive = Developer interest > User interest | Negative = User interest > Developer interest
            """)

    with col2:
        st.subheader(f"🏆 {analysis_type} Rankings")

        if len(ranked_categories) > 0:
            dev_top, user_top, oversaturated, underserved = create_rankings_tables(ranked_categories, user_metric,
                                                                                   analysis_type)

            # Top categories by developer interest
            st.markdown(f"**Top {analysis_type} by Developer Releases:**")
            st.dataframe(dev_top, width='stretch')

            # Top categories by user interest
            st.markdown(f"**Top {analysis_type} by {user_metric}:**")
            st.dataframe(user_top[['User_metric_value']], width='stretch')

            # Gap analysis table
            st.markdown("**Largest Attention Gaps:**")

            st.markdown("Over-saturated (Dev > User):")
            st.dataframe(oversaturated[['Gap']], width='stretch')

            st.markdown("Under-served (User > Dev):")
            st.dataframe(underserved[['Gap']], width='stretch')

    # Trend analysis section
    st.subheader("📈 Trend Analysis")

    if len(exploded_df) > 0 and len(category_stats) > 0:
        trend_col1, trend_col2 = st.columns([1, 3])

        with trend_col1:
            available_trend_categories = sorted(category_stats.index.tolist())
            selected_trend_category = st.selectbox(
                f"Select {analysis_type[:-1]} for Trend Analysis:",
                options=available_trend_categories,
                index=0 if available_trend_categories else None
            )

        with trend_col2:
            if selected_trend_category:
                trend_fig = create_trend_chart(exploded_df, selected_trend_category, user_metric, aggregation_method,
                                               analysis_type)
                if trend_fig:
                    st.plotly_chart(trend_fig, use_container_width=True)
                else:
                    st.info(f"Not enough data for trend analysis of '{selected_trend_category}'.")
            else:
                st.info(f"Please select a {analysis_type.lower()[:-1]} to view its trend analysis.")
    else:
        st.info("No data available for trend analysis with current filters.")

    # Data summary
    with st.expander("📁 Dataset Summary"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Games", f"{len(df):,}")
        with col2:
            st.metric("Time Period", f"{min_year} - {max_year}")
        with col3:
            st.metric(f"Unique {analysis_type}", f"{len(all_categories):,}")
        with col4:
            filtered_count = len(exploded_df['AppID'].unique()) if len(exploded_df) > 0 else 0
            st.metric("Filtered Games", f"{filtered_count:,}")


if __name__ == "__main__":
    main()
