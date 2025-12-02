# streamlit_page_title: Custom Name
import streamlit as st

from data_loader import load_data, get_all_tags, filter_data
from data_processor import prepare_analysis_type_scatter_data
from visualizations import create_main_scatter_plot


def main():
    # Set up page and theme
    st.set_page_config(
        page_title="Steam Tags Analysis",
        page_icon="🎮",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("🎮 Steam Visualisation")
    st.markdown("""""")

    # Load data
    raw_df = load_data()
    total_number_of_games = len(raw_df)
    raw_df = filter_data(raw_df)

    all_tags = get_all_tags(raw_df)

    # Check data
    if len(raw_df) == 0:
        st.error("❌ No valid data available after preprocessing.")
        return

    # Sidebar controls
    st.sidebar.header("Filters")

    # Year range slider
    valid_years = raw_df['Release_year'].dropna()
    if len(valid_years) == 0:
        st.error("❌ No valid release years found in the dataset.")
        return

    min_year = int(valid_years.min())
    max_year = int(valid_years.max())

    year_range = st.sidebar.slider(
        "Year Range:",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
        step=1
    )

    number_of_min_reviews = st.sidebar.slider(
        "Minimum Amount of Reviews within a Game:",
        min_value=0,
        max_value=100,
        value=10,
        step=1
    )

    df = raw_df[raw_df['Total_reviews'] >= number_of_min_reviews]
    print(f"⚠️ Removed {len(raw_df) - len(df)} rows with less than {number_of_min_reviews} reviews")

    scatter_data = prepare_analysis_type_scatter_data(df, raw_df, year_range, all_tags)

    # Data summary
    st.subheader(f"📁 Dataset Summary")
    col1, col2, col3 = st.columns(3)
    filtered_number_of_games = len(df)
    with col1:
        st.metric("Total Games", f"{total_number_of_games:,} (100.00%)")
        st.metric("Filtered Games",
                  f"{filtered_number_of_games:,} ({100 * filtered_number_of_games / total_number_of_games:.2f}%)")
    with col2:
        st.metric("Time Period", f"{min_year} - {max_year}")
        # st.metric("Filtered Time Period", f"{int(scatter_data['Release_year'].min())} - {int(scatter_data['Release_year'].max())}")

    with col3:
        st.metric(f"Total Tags", f"{len(get_all_tags(raw_df)):,}")
        st.metric(f"Filtered Tags", f"{len(scatter_data):,}")

    # Add the scatter plot visualization above data summary
    st.subheader(f"Peak Concurrent Number of Users vs Number of Released Games per Tag")
    selected_tags = st.multiselect(
        f"Tags to highlight:",
        options=all_tags,
        default=None,
    )

    # Main scatter plot
    scatter_fig = create_main_scatter_plot(scatter_data, selected_tags)
    event = st.plotly_chart(scatter_fig, config={"responsive": True}, key="iris", on_select="rerun")
    if event and event['selection']['points']:
        clicked_tag = event['selection']['points'][0]['hovertext']
        st.session_state['tag'] = clicked_tag
        st.switch_page("pages/Tag_Details.py")

    # st.info(f"**Tags**  \n{all_tags}")
    with st.expander('All Tags'):
        st.markdown(', '.join(get_all_tags(raw_df)))


if __name__ == "__main__":
    main()
