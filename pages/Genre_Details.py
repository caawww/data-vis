import streamlit as st

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

    st.title("📊 Genre / Tag Analysis")
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

    st.divider()

    st.markdown(f"Games with tag **{selected_tag}**: {len(tag_df)}")
    st.dataframe(
        tag_df[
            ["Name", "Release_year", "Peak CCU", "Price", "Total_reviews", "Estimated owners"]
        ].sort_values(by="Peak CCU", ascending=False)
    )


if __name__ == "__main__":
    genre_details_page()
