# Review and live demo guide

## Before the review

1. Install dependencies and place `spotify_songs.csv` at `data/raw/spotify_songs.csv` using `scripts/prepare_dataset.py`.
2. Run `python -m src.playlist_curator` and confirm `results/metrics.json` exists.
3. Run `streamlit run app.py` and keep the app open for the demonstration.
4. Open `output/project_presentation_cv_final.pptx` and `output/project_report.pdf`.
5. Confirm section E is shown on the slides and PDF.

## Two-minute demo sequence

1. Explain the input: 12 acoustic features for a track.
2. Explain why the source rows are grouped by track ID and why the target is multi-label.
3. Show the model comparison slide and name the best model using macro F1.
4. In the app, upload a CSV containing the required feature columns and show the three ranked playlist genres.
5. Close with the main limitation: playlist placement is only a proxy for listener taste.

## Likely questions

**Why group by `track_id` before splitting?**  
The same track appears in multiple playlist rows. Splitting rows directly could put that track in both training and test sets and make the evaluation look better than it is.

**Why use a multi-label target?**  
Some tracks appear under more than one playlist genre. Keeping all labels matches the data instead of forcing one arbitrary genre per track.

**Why exclude playlist name and track popularity from the features?**  
Playlist metadata directly reveals the label, while popularity is not an acoustic property. Excluding them focuses the model on audio features.

**What does macro F1 tell us?**  
It averages the F1 score across genre labels, so common genres do not overwhelm the score for less common ones.

**Can this predict a user's personal playlist choice?**  
No. It ranks broad playlist genres from this dataset. Personal curation needs user-specific playlist examples and a listener-level evaluation.

**Why not query the current Spotify API?**  
The reference API audio-features endpoint is restricted for new use cases. This project uses only the supplied CSV and makes no API calls.

## Individual contribution record

| Team member | Contribution |
|---|---|
| Mohammed Adaan Hamad | Worked on dataset preparation and modeling, including CSV validation, track-level grouping, multi-label target setup, model comparison, metric generation, and prediction-output review. |
| Lakshya Jeet Singh | Worked on model evaluation and project delivery, including feature-selection review, validation of the train/test methodology, Streamlit demo readiness, report and presentation workflow, and final submission QA. |
