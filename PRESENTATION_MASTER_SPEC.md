# Presentation Master Specification & Slide Content

## Project Overview
- **Course**: UE24CS352A - Machine Learning Mini-Project
- **Project Title**: Training a Playlist Curator Based on Track Features
- **Team Members**: Mohammed Adaan Hamad & Lakshya Jeet Singh
- **Section**: E
- **Institution**: PES University
- **Repository**: git@github.com:Adaan-Ai/ml-playlist-classifier.git

---

## Slide-by-Slide Exact Content

### Slide 1: Title Slide (Dark Theme / Executive Cover)
- **Top Badge**: `UE24CS352A — MACHINE LEARNING MINI-PROJECT`
- **Main Title**: Training a Playlist Curator Based on Track Features
- **Subtitle**: A Leakage-Free, Multi-Label Adaptation of the Stanford CS229 Recommender
- **Divider**: Teal Accent Line
- **Team Information**:
  - Mohammed Adaan Hamad (SRN / Member)
  - Lakshya Jeet Singh (SRN / Member)
  - Section: E | Evaluation Date: October 2026
- **Speaker Notes**:
  > "Good morning faculty and evaluation panel. Today we present our machine learning mini-project: 'Training a Playlist Curator Based on Track Features'. We adapted the Stanford CS229 recommender formulation to build a leakage-free, multi-label classifier on 32,800+ Spotify songs, evaluating three distinct model families to rank playlist categories purely from acoustic signals."

---

### Slide 2: Problem Statement & Practical Framing
- **Header**: Problem Formulation & Project Scope
- **Category Badge**: `02 / METHODOLOGY`
- **Key Cards / Columns**:
  - **Card 1: Original Problem & Gap**
    - Stanford CS229 project framed playlist curation around individual user listening histories.
    - Real-world constraint: The archival dataset lacks private user IDs and personalized interaction logs.
  - **Card 2: Our Content-Based Adaptation**
    - Formulated a content-based proxy: Given a track's intrinsic audio attributes, predict and rank the playlist genres it naturally belongs to.
    - Multi-label classification across 6 top-level genres (`edm`, `latin`, `pop`, `r&b`, `rap`, `rock`).
  - **Card 3: Defense & Honest Scope**
    - Playlist genres represent editorial/curator placement, not subjective listener taste.
    - Explicitly bounds our claim: We provide a reproducible acoustic classification baseline, not an ungrounded taste predictor.
- **Speaker Notes**:
  > "We must be methodologically honest: the supplied dataset does not contain individual user listening logs. Therefore, we adapted the playlist curation problem into a rigorous content-based proxy. We predict which broad playlist genres a song fits into based strictly on its acoustic properties. This allows us to benchmark machine learning models without making unprovable claims about personal taste."

---

### Slide 3: Dataset Architecture & Multi-Label Ground Truth
- **Header**: Dataset Architecture & Multi-Label Setup
- **Category Badge**: `03 / DATA ENGINEERING`
- **Metric Highlight Cards**:
  - **32,833**: Source Playlist-Track Rows
  - **28,356**: Unique Track IDs (Deduplicated)
  - **12**: Continuous Audio Features
  - **6**: Target Playlist Genres
- **Two-Column Comparative Analysis**:
  - **Column 1: 12 Acoustic Features (Content-Only)**
    - Danceability, Energy, Loudness, Speechiness, Acousticness, Instrumentalness, Liveness, Valence, Tempo, Key, Mode, Duration (ms).
    - *Zero Target Leakage*: Excluded playlist titles, playlist IDs, and popularity scores (which reflect external marketing rather than acoustic content).
  - **Column 2: Multi-Label Representation**
    - 1,687 tracks appear in multiple genres (e.g., Pop + R&B, EDM + Latin).
    - Forcing single-class labels discards valid crossover ground truth.
    - Multi-hot encoding across 6 classes: `edm` (5,537), `rap` (5,486), `r&b` (5,138), `pop` (5,132), `latin` (4,641), `rock` (4,451).
- **Speaker Notes**:
  > "The source dataset contains 32,833 rows representing playlist placements. Crucially, 1,687 tracks appear in multiple playlists under different genres. Instead of arbitrarily picking one genre, we formulated this as a multi-label classification problem. Furthermore, we strictly excluded playlist names, IDs, and popularity scores to avoid target leakage, training purely on 12 continuous acoustic features."

---

### Slide 4: Leakage-Free Workflow & Pipeline Design
- **Header**: Leakage Prevention & Model Selection Workflow
- **Category Badge**: `04 / PIPELINE DESIGN`
- **4-Stage Flowchart / Step Blocks**:
  - **Step 1: Track-Level Aggregation**
    - Group by `track_id` *before* train/test splitting.
    - Average repeated acoustic measurements to obtain 1 clean vector per track.
    - Union playlist genres into a binary multi-label vector.
  - **Step 2: Strict 80/20 Out-of-Sample Split**
    - Split at the unique `track_id` level (Seed 42).
    - Train: 22,684 tracks | Held-out Test: 5,672 tracks.
    - Prevents duplicate tracks from leaking across split boundaries.
  - **Step 3: Encapsulated 5-Fold Cross-Validation**
    - 5-fold CV executed strictly on the 80% development set.
    - `SimpleImputer` (median) and `StandardScaler` wrapped inside scikit-learn `Pipeline` objects to guarantee validation fold isolation.
  - **Step 4: Macro F1 Selection Criterion**
    - Select winning model by highest mean cross-validation **Macro F1** to balance majority and minority genres equally.
- **Speaker Notes**:
  > "The single most important methodological safeguard in our project is leakage prevention. In naive pipelines, splitting rows directly causes duplicate tracks to appear in both training and test sets. We group by unique track ID first, average repeated values, and split 80/20 at the song level. Furthermore, all imputations and scalers are encapsulated inside scikit-learn Pipelines, preventing test-fold statistics from leaking into training."

---

### Slide 5: Model Benchmarking & 5-Fold Cross-Validation
- **Header**: 5-Fold Cross-Validation Comparison
- **Category Badge**: `05 / BENCHMARKS`
- **Benchmark Table (Development Set Results)**:
  | Model Architecture | Mean Micro F1 | Mean Macro F1 | Top-1 Hit Rate | Recall@3 | Subset Accuracy |
  |---|---|---|---|---|---|
  | **Logistic Regression (L2)** | 0.463 | 0.473 | 48.5% | 82.6% | 9.7% |
  | **RBF Support Vector Machine** | 0.540 | 0.528 | 56.2% | 86.4% | 48.2% |
  | **Random Forest (100 Trees)** ★ | **0.570** | **0.556** | **59.0%** | **87.9%** | **54.1%** |
- **Takeaway Callout Cards**:
  - **Winning Model**: Random Forest achieved the highest Macro F1 (0.556) and Micro F1 (0.570).
  - **Model Dynamics**: Logistic Regression suffered on exact subset match (9.7%) due to non-linear feature boundaries. Random Forest captured feature interactions (e.g., high Energy + low Acousticness = EDM/Rock) effectively.
- **Speaker Notes**:
  > "We benchmarked three distinct model families across 5-fold cross-validation on our development set. Logistic regression provides a calibrated linear baseline, RBF SVM models non-linear boundaries in Hilbert space, and Random Forest models complex threshold interactions. Random Forest clearly dominated with a 0.556 Macro F1, 59.0% Top-1 hit rate, and 54.1% exact subset match, leading to its selection as our final deployment model."

---

### Slide 6: Final Held-Out Test Evaluation
- **Header**: Final Evaluation on Held-Out Test Set
- **Category Badge**: `06 / EVALUATION`
- **Primary Metric Summary Badges (5,672 Test Tracks)**:
  - **Macro F1**: `0.563` (Unweighted across 6 genres)
  - **Micro F1**: `0.576` (Global harmonic mean)
  - **Subset Accuracy**: `54.87%` (Exact 6-label vector match)
  - **Top-1 Hit Rate**: `59.36%` (Primary genre prediction accuracy)
  - **Recall@3**: `88.15%` (True genre present in Top-3 recommendations)
- **Per-Genre Test Breakdown (F1 Score & Support)**:
  - **Rock**: `0.703` F1 (896 tracks) — Distinct acoustic signature (high loudness, low acousticness).
  - **EDM**: `0.683` F1 (1,158 tracks) — High energy, high tempo, synthetic profile.
  - **Rap**: `0.653` F1 (1,151 tracks) — High speechiness, distinct rhythmic profile.
  - **R&B**: `0.491` F1 (1,023 tracks) — Overlaps with Pop and Rap tempos.
  - **Latin**: `0.457` F1 (879 tracks) — Diverse acoustic spectrum, frequent crossover.
  - **Pop**: `0.391` F1 (948 tracks) — Broadest umbrella category with high variance.
- **Speaker Notes**:
  > "Evaluating our selected Random Forest on the 5,672 untouched test tracks confirmed strong generalization with virtually zero overfitting: Test Macro F1 was 0.563 versus 0.556 in CV. Notice our recommendation metrics: the Top-1 Hit Rate is 59.4%, and Recall@3 reaches 88.2%, meaning 9 out of 10 times, the true playlist genre is inside our top three recommendations. Per-genre analysis reveals acoustic-heavy genres like Rock and EDM are easiest to classify, while broad umbrella genres like Pop present higher ambiguity."

---

### Slide 7: Live Demonstration & Recommender Architecture
- **Header**: Deployment Architecture & Live Streamlit Demo
- **Category Badge**: `07 / LIVE DEMO`
- **Demo Architecture Workflow**:
  - **1. Serialized Bundle (`results/playlist_model.joblib`)**: Pretrained Random Forest pipeline + label encoder + schema metadata (419 MB).
  - **2. Audio Feature Ingestion (`samples/demo_tracks.csv`)**: Validates 12 numeric attributes and rejects missing/corrupted columns.
  - **3. Probabilistic Ranking**: Computes `predict_proba` for all 6 genres, sorts descending, and returns Top 3 candidate playlist genres.
  - **4. Output Presentation**: Streamlit interactive dataframe + downloadable recommendation CSV.
- **Demo Verification Checklist**:
  - [x] Streamlit app runs locally with `streamlit run app.py`.
  - [x] Fallback error handling when model bundle is absent.
  - [x] Offline execution: Zero external API calls, compliant with Spotify terms.
- **Speaker Notes**:
  > "Our live demonstration is powered by Streamlit. The application loads our serialized pipeline and accepts user-supplied CSV files matching the 12 audio feature columns. It outputs the top three candidate playlist genres along with calibrated model confidence scores, and enables one-click CSV export for downstream playlist creation."

---

### Slide 8: Limitations & Individual Contribution Record
- **Header**: Limitations & Team Contributions
- **Category Badge**: `08 / CONCLUSION & QA`
- **Two-Column Split**:
  - **Column 1: Technical Limitations & Future Work**
    - *Proxy Limitation*: Playlist genre categorization is an editorial proxy, not personal user taste.
    - *Data Policy*: Historical dataset utilized; no Spotify API scraping performed.
    - *Future Scope*: Integrating collaborative filtering or sequence-based RNN/Transformer playlist continuation.
  - **Column 2: Individual Contribution Record**
    - **Mohammed Adaan Hamad**:
      - Dataset extraction and schema validation (`scripts/prepare_dataset.py`).
      - Track-level grouping and multi-label target setup.
      - Model comparison implementation and CV scoring.
    - **Lakshya Jeet Singh**:
      - Evaluation methodology and data leakage prevention design.
      - Feature selection validation (excluding metadata & popularity).
      - Streamlit demo development and error handling (`app.py`).
      - Automated report and presentation generation pipeline.
      - Final QA, sanity testing (`scripts/sanity_check.py`), and documentation.
- **Speaker Notes**:
  > "To conclude, this project demonstrates that intrinsic audio features can serve as a dependable baseline for multi-label playlist genre assignment. Our contribution table clearly documents our division of labor between modeling and evaluation methodology. We welcome any questions from the panel."
