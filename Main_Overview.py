import streamlit as st

from data_loader import load_data, get_all_tags, filter_data, filter_low_data
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

    st.title("Steam Tag Explorer")
    st.markdown("""
This is a data visualization course project, which aims to support exploration of different Steam tags (a term for video game genres on the platform).
The goal is to make exploring Steam market and its users' behaviour easier.
It might be interesting for you, if you are a game developer, who wants to make decisions about your projects; or if you are a part of the general public, which is curious about data and loves numbers.
You can use the sliders in the left menu for minimum number of reviews and players per game to filter out very small, unknown games. We have pre-selected a value of 10, which leaves less than 8% of games!
At the bottom you can click a drop-down button to see all the Steam tags written out.

Additional information:
The data comes from this Kaggle [dataset](https://www.kaggle.com/datasets/fronkongames/steam-games-dataset/). At the time we have accessed it, it was last modified in May 2025.\\
The numbers of peak concurrent players are not newer than May 2025.\\
In some visualisation we are displaying a ratio of positive reviews. We have calculated this as a percentage of positive reviews out of the total number of reviews.
""")

    # Load data
    raw_df = load_data()
    total_number_of_games = len(raw_df)
    raw_df = filter_data(raw_df)

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
        "Year Range",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
        step=1
    )

    number_of_min_reviews = st.sidebar.slider(
        "Minimum Amount of Reviews per Game",
        min_value=0,
        max_value=100,
        value=10,
        step=1
    )

    number_of_min_ccu = st.sidebar.slider(
        "Minimum Amount of Peak CCU per Game",
        min_value=0,
        max_value=100,
        value=10,
        step=1
    )

    df = filter_low_data(raw_df, year_range, number_of_min_reviews, number_of_min_ccu)
    all_tags = get_all_tags(df)

    scatter_data = prepare_analysis_type_scatter_data(df, raw_df, all_tags)
    filtered_tags = scatter_data["Tags"].unique().tolist()

    # Data summary
    st.subheader(f"📁 Dataset Summary")
    col1, col2 = st.columns(2)
    filtered_number_of_games = len(df)
    with col1:
        st.metric("Total Games", f"{total_number_of_games:,} (100.00%)")
        st.metric("Filtered Games",
                  f"{filtered_number_of_games:,} ({100 * filtered_number_of_games / total_number_of_games:.2f}%)")

    with col2:
        st.metric(f"Total Tags", f"{len(get_all_tags(raw_df)):,}")
        st.metric(f"Filtered Tags", f"{len(filtered_tags):,}")

    # Add the scatter plot visualization above data summary
    st.subheader(f"Peak Concurrent Number of Users vs Number of Released Games per Tag")
    st.markdown("""
    This visualisation enables you to explore which tags are getting a higher attention (measured by the peak number of concurrent players, which is the recorder maximum number of players playing simultaneously) and how many games within the tags are offered on the Steam platform.
    You can also click on a specific tag to explore it in more detail.
    """)
    selected_tags = st.multiselect(
        f"Tags to highlight:",
        options=filtered_tags,
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

    with st.container():
        st.markdown("---")
        st.write("© 2025 Steam Tag Explorer. Created by Michal Kubirita, Marina Baños Ramírez, and Matej Zelenák.")


if __name__ == "__main__":
    main()
