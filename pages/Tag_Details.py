import streamlit as st
from collections import Counter
import pandas as pd
from data_loader import load_data, set_theme, get_all_tags, filter_data
from visualizations import create_review_ratio_over_time


def genre_details_page():
    # Set up page and theme
    set_theme()
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
    col1, col2, col3, col4 = st.columns(4)

    tag_count = len(tag_df)
    median_ratio = tag_df["Review_ratio"].median()
    median_price = tag_df["Price"].median()
    min_year = int(tag_df["Release_year"].min())
    max_year = int(tag_df["Release_year"].max())

    with col1:
        st.metric("Games With Tag", f"{tag_count:,}")

    with col2:
        st.metric("Median Review Ratio", f"{median_ratio:.2f}")

    with col3:
        st.metric("Median Price", f"${median_price:.2f}")

    with col4:
        st.metric("Active Years", f"{min_year}–{max_year}")

    st.subheader(f"Positive Reviews Over Time")
    fig = create_review_ratio_over_time(tag_df, selected_tag)
    st.plotly_chart(fig, use_container_width=True)

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

        st.subheader(f"Tags Often Found With '{selected_tag}'")
        st.dataframe(co_tag_df.style.hide(axis="index"), use_container_width=True)
    else:
        st.info("No co-occurring tags found.")

    st.divider()

    st.markdown(f"Games with tag **{selected_tag}**: {len(tag_df)}")
    st.dataframe(
        tag_df[
            ["Name", "Release_year", "Peak CCU", "Price", "Total_reviews", "Estimated owners"]
        ].sort_values(by="Peak CCU", ascending=False)
    )


if __name__ == "__main__":
    genre_details_page()
