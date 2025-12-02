from collections import Counter

import pandas as pd
import streamlit as st

from data_loader import load_data, get_all_tags, filter_data
from visualizations import create_review_ratio_over_time, create_games_per_year_bar


def genre_details_page():
    # Set up page and theme
    st.set_page_config(
        page_title="Steam Tags Analysis",
        page_icon="🎮",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("📊 Tag Analysis")
    st.markdown("""""")

    df = load_data()
    df = filter_data(df)
    all_tags = get_all_tags(df)

    preselected_tag = st.session_state.get("tag", None)
    selected_tag = st.selectbox(
        "Analysis for Tag:",
        options=all_tags,
        index=all_tags.index(preselected_tag) if preselected_tag in all_tags else 0,
        key="genre_selector"
    )
    st.session_state["tag"] = selected_tag
    tag_df = df[df["Tags"].apply(lambda t: selected_tag in t)]

    # Stats about the Tag
    cols = st.columns(7)

    with cols[0]:
        st.metric("Games With Tag", f"{len(tag_df):,}")
        st.metric("Free to Play", f"{(tag_df["Price"] == 0).sum()}")
        st.metric("Active Years", f"{int(tag_df["Release_year"].min())}–{int(tag_df["Release_year"].max())}")

    with cols[1]:
        st.metric("Average Review Ratio", f"{tag_df["Review_ratio"].mean():.2f}")
        st.metric("Median Review Ratio", f"{tag_df["Review_ratio"].median():.2f}")

    with cols[2]:
        st.metric("Average Price", f"${tag_df["Price"].mean():.2f}")
        st.metric("Median Price", f"${tag_df["Price"].median():.2f}")

    with cols[3]:
        st.metric("Average Achievements", f"{tag_df["Achievements"].mean():.2f}")
        st.metric("Median Achievements", f"{tag_df["Achievements"].median():.0f}")

    with cols[4]:
        st.metric("Average Age Requirement", f"{tag_df["Required age"].mean():.2f}")
        st.metric("Median Age Requirement", f"{tag_df["Required age"].median():.0f}")

    with cols[5]:
        avg_playtime = tag_df["Average playtime forever"].mean()
        median_playtime = tag_df["Median playtime forever"].mean()
        st.metric(f"Average Playtime", f"{avg_playtime / 60:.0f}h{avg_playtime % 60:02.0f}m")
        st.metric(f"Median Playtime", f"{median_playtime / 60:.0f}h{median_playtime % 60:02.0f}m")

    with cols[6]:
        st.metric("Average DLC Count", f"{tag_df["DLC count"].mean():.2f}")
        st.metric("Median DLC Count", f"{tag_df["DLC count"].median():.0f}")

    st.subheader(f"Average Positive Review Ratio Over Time for Tag '{selected_tag}'")
    fig = create_review_ratio_over_time(tag_df, selected_tag)
    st.plotly_chart(fig, config={"responsive": True})

    st.subheader(f"Number of Games Released Over Time")
    fig = create_games_per_year_bar(tag_df, selected_tag)
    st.plotly_chart(fig, config={"responsive": True})

    # Count co-occurring tags
    co_tags = Counter()

    for tags in tag_df["Tags"]:
        for t in tags.split(','):
            if t != selected_tag:
                co_tags[t] += 1

    # Build the DataFrame if there are any co-tags
    if len(co_tags) > 0:
        co_tag_df = (
            pd.DataFrame({
                "Tags": list(co_tags.keys()),
                "Games": list(co_tags.values())
            })
            .sort_values("Games", ascending=False)
            .reset_index(drop=True)
        )

        # Compute aggregated stats inside tag_df
        avg_ratios = []
        avg_prices = []
        avg_ccu = []

        for tags in co_tag_df["Tags"]:
            # Correct membership test — as you required
            sub = tag_df[tag_df["Tags"].apply(lambda t: tags in t)]

            avg_ratios.append(sub["Review_ratio"].mean())
            avg_prices.append(sub["Price"].mean())
            avg_ccu.append(sub["Peak CCU"].mean())

        co_tag_df["Avg Review Ratio"] = avg_ratios
        co_tag_df["Avg Price"] = avg_prices
        co_tag_df["Avg Peak CCU"] = avg_ccu

        st.subheader(f"Most Common Tags Found With '{selected_tag}'")
        st.dataframe(co_tag_df.head(10), hide_index=True)
    else:
        st.info("No co-occurring tags found.")

    st.divider()

    st.subheader(f"Games:")
    st.dataframe(
        tag_df[
            ["Name", "Release_year", "Peak CCU", "Price", "Total_reviews", "Estimated owners"]
        ].sort_values(by="Peak CCU", ascending=False), hide_index=True, height=700
    )


if __name__ == "__main__":
    genre_details_page()
