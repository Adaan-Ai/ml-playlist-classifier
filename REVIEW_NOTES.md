# Technical review notes

Use these notes to prepare for individual Q&A. The goal is to explain the project decisions clearly, not to memorize exact wording.

## Problem framing

The assigned problem is "Training a Playlist Curator Based on User Taste." The available dataset does not contain individual user playlists or listener feedback, so this project implements a content-based proxy: given a track's audio features, rank the broad playlist genres where that track is likely to fit.

State the limitation directly during review:

> We adapted the playlist-curation idea to the supplied Spotify Songs dataset. Since the dataset has playlist genre labels instead of personal user playlists, the model learns playlist-genre fit from audio features, not an individual listener's taste.

## Data preparation decisions

**Why group by `track_id` before splitting?**  
The source CSV is playlist-track level, so the same song can appear in multiple rows. If rows were split directly, one track could appear in both training and test sets, causing leakage. Grouping first creates one row per unique track and makes the evaluation more honest.

**Why average repeated audio features?**  
Audio features should describe the track, not the playlist row. When the same track appears multiple times, averaging repeated numeric features gives one stable feature vector per track.

**Why multi-label classification?**  
Some tracks appear under more than one playlist genre. Forcing one label would throw away valid labels. Multi-label targets let a track belong to several genres at once.

## Feature decisions

The model uses 12 numeric audio attributes:

- danceability
- energy
- key
- loudness
- mode
- speechiness
- acousticness
- instrumentalness
- liveness
- valence
- tempo
- duration_ms

**Why exclude playlist names and playlist IDs?**  
They directly reveal the target category and would make the model memorize playlist metadata instead of learning from audio features.

**Why exclude track popularity?**  
Popularity is not an acoustic property. Excluding it keeps the model focused on content-based recommendation.

## Model and evaluation decisions

**Why compare three models?**  
The project compares logistic regression, RBF SVM, and random forest to cover a simple linear baseline, a nonlinear margin-based model, and a tree-based ensemble.

**Why use 5-fold cross-validation on the development set?**  
Cross-validation gives a more stable model-selection estimate than choosing from one validation split. The untouched test set is used only after selecting the best model.

**Why select by macro F1?**  
Macro F1 gives each genre equal weight. This matters because common genres can dominate micro-averaged scores.

**What does exact subset accuracy mean?**  
It is the strictest metric: every predicted genre label for a track must match the true multi-label target exactly.

**Why report top-1 hit rate and recall at three?**  
The demo ranks genres, so ranking metrics are useful. Top-1 hit checks whether the highest-ranked genre is valid. Recall at three checks how much of the true multi-label set appears in the top three recommendations.

## Demo explanation

The Streamlit app loads `results/playlist_model.joblib`, accepts a CSV with the same 12 feature columns, and returns the three highest-ranked playlist genres. Use `samples/demo_tracks.csv` for a quick live test.

If the app says the model is missing, run:

```powershell
python -m src.playlist_curator
```

Then restart:

```powershell
streamlit run app.py
```

## Strong closing answer

If asked what the project proves, say:

> It shows that acoustic features can provide a reproducible baseline for ranking broad playlist genres. It does not prove personal taste prediction, because that would require user-specific playlist histories and listener-level evaluation.
