import streamlit as st

from data_loader import load_data, set_theme, get_all_tags, filter_data


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

    st.info("# TODO - PLOTS")

    st.divider()

    st.markdown(f"Games with tag **{selected_tag}**: {len(tag_df)}")
    st.dataframe(
        tag_df[
            ["Name", "Release_year", "Peak CCU", "Price", "Total_reviews", "Estimated owners"]
        ].sort_values(by="Peak CCU", ascending=False)
    )


if __name__ == "__main__":
    genre_details_page()
