import warnings

import streamlit as st

from data_loader import load_data, set_theme, get_all_tags, filter_data
from data_processor import prepare_analysis_type_scatter_data
from visualizations import create_main_scatter_plot

warnings.simplefilter(action='ignore', category=FutureWarning)


def main():
    # Set up page and theme
    set_theme()
    st.set_page_config(
        page_title="Steam Tags Analysis",
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

    all_tags = get_all_tags(df)

    # Check data
    if len(df) == 0:
        st.error("❌ No valid data available after preprocessing.")
        return

    # Sidebar controls
    st.sidebar.header("Control Panel")

    # Year range slider
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

    # Add the scatter plot visualization above data summary
    selected_tags = st.multiselect(
        f"Tags to highlight:",
        options=all_tags,
        default=None,
    )

    # Main scatter plot
    st.subheader(f"Peak CCU vs Number of Released Games by Tags")
    scatter_data = prepare_analysis_type_scatter_data(df, year_range, all_tags, number_of_games_range)
    scatter_fig = create_main_scatter_plot(scatter_data, selected_tags)
    event = st.plotly_chart(scatter_fig, use_container_width=True, key="iris", on_select="rerun")
    if event and event['selection']['points']:
        clicked_tag = event['selection']['points'][0]['hovertext']
        st.session_state['tag'] = clicked_tag
        st.switch_page("pages/Genre_Details.py")

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
            st.metric(f"Unique Tags", f"{len(all_tags):,}")

        st.info(f"**Tags**  \n{all_tags}")


if __name__ == "__main__":
    main()
