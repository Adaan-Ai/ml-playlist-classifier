"""Streamlit demo for the learned playlist-genre recommender."""

from pathlib import Path

import joblib
import pandas as pd
import streamlit as st

from src.playlist_curator import recommend

st.set_page_config(page_title="Playlist Curator", page_icon="🎵", layout="wide")
st.title("Playlist Curator")
st.write("Upload tracks with Spotify-style audio features to rank likely playlist genres.")
st.caption("This is a course demonstration on the provided historical CSV, not a Spotify-connected application.")

model_path = Path("results/playlist_model.joblib")
if not model_path.exists():
    st.info("Train the model first: `python -m src.playlist_curator`. See README for dataset setup.")
    st.stop()

bundle = joblib.load(model_path)
st.write(f"Model: **{bundle['selected_model']}** | Categories: {', '.join(bundle['classes'])}")
uploaded = st.file_uploader("Upload a CSV with audio features", type=["csv"])
if uploaded:
    frame = pd.read_csv(uploaded)
    try:
        results = recommend(bundle, frame)
        st.dataframe(results, use_container_width=True)
        st.download_button("Download genre recommendations", results.to_csv(index=False),
                           file_name="playlist_recommendations.csv", mime="text/csv")
    except ValueError as error:
        st.error(str(error))
