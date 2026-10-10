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

## Lakshya's Individual Defense & Viva Cheat Sheet

When evaluated on your individual contributions, use this section to confidently explain your technical ownership and the specific codebase files you worked on.

### Codebase Ownership & File Walkthrough

| File | What You Owned & How to Explain It |
|---|---|
| [`src/playlist_curator.py`](file:///Users/lakshya/Builds/University/ml-playlist-classifier/src/playlist_curator.py) | **Evaluation Methodology & Feature Engineering Validation**: Designed the leakage-free evaluation scheme. Ensured grouping occurs by unique `track_id` *before* the 80/20 train/test split. Formulated the multi-label target aggregation. Verified that preprocessing (median imputation + standard scaling) is encapsulated inside scikit-learn `Pipeline` objects to prevent cross-validation data leakage. Implemented metric computation: Macro F1, Micro F1, Exact Subset Accuracy, Top-1 Hit Rate, and Recall@3. |
| [`app.py`](file:///Users/lakshya/Builds/University/ml-playlist-classifier/app.py) | **Live Demo Flow & Error Handling**: Built demo upload validation for user-supplied audio feature CSVs. Handled missing model bundle states gracefully, structured probability output ranking (Top 3 genres), and provided a formatted CSV download for recommendations. |
| [`scripts/build_report.py`](file:///Users/lakshya/Builds/University/ml-playlist-classifier/scripts/build_report.py) | **Automated Report Generation**: Developed the ReportLab script that ingests `results/metrics.json` and automatically compiles a clean, publication-ready 2-page project PDF report without manual copying of metrics. |
| [`scripts/build_presentation.py`](scripts/build_presentation.py) | **Automated Slide Presentation Workflow**: Created the portable Python slide generator using `python-pptx` that turns verified experimental metrics into a structured 6-slide executive deck (`output/project_presentation_cv_final.pptx`). |
| [`DEMO_GUIDE.md`](file:///Users/lakshya/Builds/University/ml-playlist-classifier/DEMO_GUIDE.md) & [`README.md`](file:///Users/lakshya/Builds/University/ml-playlist-classifier/README.md) | **Submission QA, Reproducibility & Checklist**: Structured the reproducibility documentation, seed anchoring (seed 42), the 2-minute live demo script, and the pre-submission verification checklist. |

---

### Five Core Methodology Decisions to Defend

1. **Why group by `track_id` before train/test splitting?**
   - *Defense*: The raw dataset contains 32,833 playlist-track occurrences for only 28,356 unique tracks. If we split at the row level, identical tracks would exist simultaneously in both training and test sets. This creates severe optimistic data leakage (evaluating on memorized songs). Grouping first and averaging numeric audio attributes guarantees an honest out-of-sample evaluation.

2. **Why formulate as Multi-Label Classification rather than Multi-Class?**
   - *Defense*: Tracks frequently straddle genre boundaries (e.g., Pop and R&B, or EDM and Latin). Forcing each song into a single genre label discards ground-truth playlist associations. Multi-label classification models each genre independently via binary relevance while allowing joint ranking.

3. **Why use Macro F1 as the primary model selection criterion?**
   - *Defense*: Accuracy and Micro F1 can be misleadingly high if dominated by dominant genres or true negatives. Macro F1 computes the unweighted mean F1 across all six genre classes, ensuring the selected model performs well across every genre rather than over-indexing on majority classes.

4. **Why restrict to 12 acoustic features and exclude metadata/popularity?**
   - *Defense*: Playlist name, playlist ID, and subgenre directly leak the target labels. Popularity reflects external commercial trends and temporal virality rather than inherent musical content. Using only intrinsic audio attributes (tempo, energy, acousticness, etc.) keeps the system purely content-based.

5. **How does this address the "User Taste" objective?**
   - *Defense*: The provided course dataset lacks user interaction logs or personalized listening histories. We explicitly adapted the task to a content-based proxy: mapping track audio properties to broad playlist genres. For true user taste curation, collaborative filtering or user-specific playlist histories would be required.

