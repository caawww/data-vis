from collections import Counter

import pandas as pd
import streamlit as st

from data_loader import load_data, get_all_tags, filter_data, filter_low_data
from visualizations import create_review_ratio_over_time, create_games_per_year_bar, create_upset_plot


def render_cooccurrence_table(tag_df, selected_tag, column_name, title_label):
    """
    Render a co-occurrence analysis table for a tag/category column.

    Args:
        tag_df       : Filtered DataFrame containing only rows with the selected_tag
        selected_tag : The tag currently being analyzed
        column_name  : Name of the column ("Tags" or "Categories")
        title_label  : Label shown in the UI ("Tags", "Categories")
    """
    # Count co-occurring tags
    co_tags = Counter()

    for tags in tag_df[column_name]:
        for t in tags.split(','):
            if t != selected_tag:
                co_tags[t] += 1

    # No results
    if len(co_tags) == 0:
        st.info(f"No co-occurring {title_label.lower()} found.")
        return

    # Build DataFrame
    co_tag_df = (
        pd.DataFrame({
            title_label: list(co_tags.keys()),
            "Games": list(co_tags.values())
        })
        .sort_values("Games", ascending=False)
        .reset_index(drop=True)
    )

    # Compute aggregated stats
    avg_ratios = []
    avg_prices = []
    avg_ccu = []

    for tag in co_tag_df[title_label]:
        sub = tag_df[tag_df[column_name].apply(lambda t: tag in t)]
        avg_ccu.append(sub["Peak CCU"].mean())
        avg_prices.append(sub["Price"].mean())
        avg_ratios.append(sub["Review_ratio"].mean())

    co_tag_df["Avg Review Ratio"] = avg_ratios
    # ✔ Format Avg Price as $XX.XX
    co_tag_df["Avg Price"] = [
        f"${p:.2f}" if pd.notnull(p) else "$0.00"
        for p in avg_prices
    ]
    co_tag_df["Avg Peak CCU"] = avg_ccu

    # Render UI
    st.subheader(f"Top 10 {title_label} Commonly Found With '{selected_tag}'")
    st.dataframe(co_tag_df.head(10), hide_index=True)


def genre_details_page():
    # Set up page and theme
    st.set_page_config(
        page_title="Steam Tags Analysis",
        page_icon="🎮",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    title_placeholder = st.title(f"📊 Tag Details for ")
    st.markdown("""""")

    df = load_data()
    df = filter_data(df)
    all_tags = get_all_tags(df)

    # Year range slider
    valid_years = df['Release_year'].dropna()
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
        value=0,
        step=1
    )

    number_of_min_ccu = st.sidebar.slider(
        "Minimum Amount of Peak CCU per Game",
        min_value=0,
        max_value=100,
        value=0,
        step=1
    )

    df = filter_low_data(df, year_range, number_of_min_reviews, number_of_min_ccu)

    preselected_tag = st.session_state.get("tag", None)
    selected_tag = st.selectbox(
        "Analysis for Tag:",
        options=all_tags,
        index=all_tags.index(preselected_tag) if preselected_tag in all_tags else 0,
        key="genre_selector"
    )
    st.session_state["tag"] = selected_tag
    tag_df = df[df["Tags"].apply(lambda t: selected_tag in t)]
    title_placeholder.title(f"📊 Tag Details for {selected_tag}")

    # Stats about the Tag
    cols = st.columns(3)

    with cols[0]:
        st.metric("Games With Tag", f"{len(tag_df):,}")

    with cols[1]:
        st.metric("Free to Play", f"{(tag_df["Price"] == 0).sum()}")

    with cols[2]:
        st.metric("Release Period", f"{int(tag_df["Release_year"].min())}–{int(tag_df["Release_year"].max())}")

    # with cols[1]:
    #     ...
    #     # st.metric("Average Review Ratio", f"{tag_df["Review_ratio"].mean():.2f}")
    #     # st.metric("Median Review Ratio", f"{tag_df["Review_ratio"].median():.2f}")
    #
    # with cols[2]:
    #     st.info('make plot of distributions')
    #     st.metric("Average Price", f"${tag_df["Price"].mean():.2f}")
    #     st.metric("Median Price", f"${tag_df["Price"].median():.2f}")
    #
    # with cols[3]:
    #     st.info('make plot of distributions')
    #     st.metric("Average Achievements", f"{tag_df["Achievements"].mean():.2f}")
    #     st.metric("Median Achievements", f"{tag_df["Achievements"].median():.0f}")
    #
    # with cols[4]:
    #     ...
    #     # st.metric("Average Age Requirement", f"{tag_df["Required age"].mean():.2f}")
    #     # st.metric("Median Age Requirement", f"{tag_df["Required age"].median():.0f}")
    #
    # with cols[5]:
    #     st.info('make plot of distributions')
    #     avg_playtime = tag_df["Average playtime forever"].mean()
    #     median_playtime = tag_df["Median playtime forever"].mean()
    #     st.metric(f"Mean of Average Playtime", f"{avg_playtime // 60:.0f}h{avg_playtime % 60:02.0f}m")
    #     st.metric(f"Mean of Median Playtime", f"{median_playtime // 60:.0f}h{median_playtime % 60:02.0f}m")
    #
    # with cols[6]:
    #     ...
    #     # st.metric("Average DLC Count", f"{tag_df["DLC count"].mean():.2f}")
    #     # st.metric("Median DLC Count", f"{tag_df["DLC count"].median():.0f}")

    st.subheader(f"Average Positive Review Ratio Over Time for Tag '{selected_tag}'")
    fig = create_review_ratio_over_time(tag_df, selected_tag)
    st.plotly_chart(fig, config={"responsive": True})

    st.subheader(f"Number of Games Released Over Time")
    fig = create_games_per_year_bar(tag_df, selected_tag)
    st.plotly_chart(fig, config={"responsive": True})

    col1, col2 = st.columns(2)

    with col1:
        render_cooccurrence_table(
            tag_df=tag_df,
            selected_tag=selected_tag,
            column_name="Categories",
            title_label="Categories"
        )

    with col2:
        render_cooccurrence_table(
            tag_df=tag_df,
            selected_tag=selected_tag,
            column_name="Tags",
            title_label="Tags"
        )

    st.divider()

    st.subheader(f"Tag Intersection {selected_tag}")

    # Allow user to select additional tags to compare with the main tag
    other_tags = [t for t in all_tags if t != selected_tag]

    selected_tags_for_upset = st.multiselect(
        "Select additional tags to compare:",
        options=other_tags,
        max_selections=5,
    )

    selected_tags_for_upset = [selected_tag] + selected_tags_for_upset

    tag_counts = {
        tag: df["Tags"].apply(lambda t: tag in t).sum()
        for tag in selected_tags_for_upset
    }

    selected_tags_for_upset = sorted(
        selected_tags_for_upset,
        key=lambda t: tag_counts[t],
        reverse=True
    )

    # Generate UpSet only when user picks 2+ tags
    if len(selected_tags_for_upset) >= 2:
        fig = create_upset_plot(df, selected_tags_for_upset)
        if fig:
            st.pyplot(fig)
        else:
            st.info("Not enough data for an UpSet plot.")
    else:
        st.info("Select at least 1 extra tag to generate an UpSet plot.")

    st.divider()

    st.subheader(f"Games:")
    st.dataframe(
        tag_df[
            ["Name", "Release_year", "Peak CCU", "Price", "Total_reviews", "Estimated owners"]
        ].sort_values(by="Peak CCU", ascending=False), hide_index=True, height=700
    )


if __name__ == "__main__":
    genre_details_page()
