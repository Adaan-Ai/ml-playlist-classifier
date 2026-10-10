# Playlist Curator: Predicting Playlist Genres

**UE24CS352A - Machine Learning mini-project**  
Team members: **Mohammed Adaan Hamad** and **Lakshya Jeet Singh**  
Section: **E**

## What it does

The model uses acoustic features to recommend playlist genres for a track. The supplied CSV has playlist associations, so tracks that occur in more than one genre retain multiple labels. We compare three multi-label classifiers and rank the likely genres in a small Streamlit demo.

This project uses the dataset you supplied in `archive (1).zip`. It does not connect to Spotify or request Spotify API data.

## Dataset and target

The archive contains `spotify_songs.csv` and a data dictionary. The CSV has 32,833 playlist-track rows, 23 columns, 471 playlist IDs, six top-level playlist genres, and 24 subgenres. It includes 28,356 unique track IDs. Repeated tracks can have different playlist genres, so the pipeline groups rows by track ID, averages repeated acoustic feature values, and preserves every associated genre as a multi-label target. Train and test splitting happens after this grouping, so one track cannot appear on both sides of the split.

The project uses 12 numeric audio attributes: danceability, energy, key, loudness, mode, speechiness, acousticness, instrumentalness, liveness, valence, tempo, and duration. It does not use track IDs, playlist labels, or popularity as model features.

## Setup

Use Python 3.10 or newer.

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/prepare_dataset.py "C:\path\to\archive (1).zip"
```

The last command extracts and validates `spotify_songs.csv` into `data/raw/spotify_songs.csv`. The dataset is ignored by Git and should not be uploaded unless your instructor confirms its redistribution terms.

## Train and evaluate

```powershell
python -m src.playlist_curator
```

The pipeline creates one row per unique track and a six-column multi-hot genre label. It makes an 80/20 random split at the unique-track level with seed 42. The 20% test set stays untouched during model selection. On the 80% development set, it compares logistic regression, an RBF SVM, and a random forest with 5-fold cross-validation, selecting the model with the highest mean macro F1. Median imputation and scaling are fitted inside each model pipeline in every fold. The selected model is then trained on the full development set and evaluated once on the test set. We report micro F1, macro F1, exact subset accuracy, top-1 genre hit rate, and recall at three.

Generated files under `results/`:

- `metrics.json`: data dimensions, split counts, per-model cross-validation metrics, and the selected model's final test metrics. Commit this for review.
- `test_predictions.csv`: held-out actual genres and predictions. Commit this for review.
- `playlist_model.joblib`: selected model and feature schema. This file is intentionally ignored by Git because it is a generated binary.

## Run the demo

```powershell
streamlit run app.py
```

Upload a CSV with the same 12 audio feature columns. The app returns the three highest ranked playlist genres and their estimated probabilities. A small upload example is available at `samples/demo_tracks.csv`.

## Build review deliverables

After training, generate the PDF write-up from the measured metrics:

```powershell
python scripts/build_report.py
```

The presentation deck is generated from `results/metrics.json` by `scripts/build_presentation.mjs` when the presentation artifact tooling is available. If that tooling is unavailable on a review machine, submit the already generated `output/project_presentation_cv_final.pptx` and keep the script as the source used to create it.

For final submission, make sure these files are present:

- `README.md`: setup and run instructions.
- `DEMO_GUIDE.md`: live-review sequence and individual contribution record.
- `REVIEW_NOTES.md`: technical Q&A preparation notes.
- `REFERENCES.md`: source and data notes.
- `results/metrics.json`: measured model results.
- `results/test_predictions.csv`: held-out prediction examples.
- `output/project_report.pdf`: two-page project write-up.
- `output/project_presentation_cv_final.pptx`: review slide deck.

## Files

```text
app.py                            Streamlit demo
src/playlist_curator.py           data preparation, model comparison, evaluation
scripts/prepare_dataset.py        archive extraction and schema validation
scripts/build_report.py           two-page PDF write-up from measured metrics
scripts/build_presentation.mjs    editable six-slide deck from measured metrics
samples/demo_tracks.csv           small CSV for Streamlit upload testing
REVIEW_NOTES.md                   technical Q&A preparation notes
output/project_report.pdf         assignment write-up
output/project_presentation_cv_final.pptx  final review slides
```

## Limitations

- The supplied CSV describes playlist genres in a historical sample, not an individual user's personal taste.
- Genre membership is multi-label and comes from playlist placement. It does not prove that listeners would make the same assignment.
- The track-level random split avoids duplicate-track leakage, but the test data comes from the same dataset collection process.
- A single split can vary. Repeated or time-based evaluation would give a stronger estimate.
- Probabilities are model scores and are not guaranteed to be calibrated.
- The dataset readme attributes its source to Spotify via the `spotifyr` package. Spotify's current developer policy restricts training ML models on Spotify content. Confirm with your instructor that using this supplied historical dataset for the course assignment is acceptable. If not, use the FMA alternative described in `REFERENCES.md`.

## Reproducibility

The seed is fixed at 42. Keep the dataset, `results/metrics.json`, PDF, and slide deck consistent. Do not commit the dataset, virtual environment, or model binary to the private repository by default. If results are regenerated, rebuild the PDF and slide deck before submission so the numbers match.
