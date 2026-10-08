"""Train and evaluate playlist genre recommendations from the supplied CSV."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.base import clone
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, precision_score, recall_score
from sklearn.model_selection import KFold, train_test_split
from sklearn.multiclass import OneVsRestClassifier
from sklearn.multioutput import MultiOutputClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MultiLabelBinarizer, StandardScaler
from sklearn.svm import SVC

SEED = 42
TARGET = "playlist_genre"
TRACK_ID = "track_id"
FEATURES = [
    "danceability", "energy", "key", "loudness", "mode", "speechiness",
    "acousticness", "instrumentalness", "liveness", "valence", "tempo", "duration_ms",
]
METADATA = ["track_name", "track_artist", "playlist_name", "playlist_subgenre"]


def load_dataset(csv_path: str | Path) -> tuple[pd.DataFrame, np.ndarray, list[str]]:
    """Create one feature row per track and a multi-label genre target.

    The source CSV repeats tracks across playlists. We aggregate those rows by
    track ID and retain every genre associated with a track, avoiding leakage
    between train and test and preserving tracks that appear in several genres.
    """
    frame = pd.read_csv(csv_path)
    source_row_count = len(frame)
    required = {TRACK_ID, TARGET, *FEATURES}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"CSV is missing required columns: {', '.join(missing)}")
    frame = frame.dropna(subset=[TRACK_ID, TARGET]).copy()
    for column in FEATURES:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame = frame.dropna(subset=FEATURES)
    frame[TARGET] = frame[TARGET].astype(str).str.strip().str.lower()
    frame = frame[frame[TARGET] != ""]

    track_features = frame.groupby(TRACK_ID, sort=True)[FEATURES].mean()
    track_labels = frame.groupby(TRACK_ID, sort=True)[TARGET].apply(lambda values: sorted(set(values)))
    track_metadata = frame.groupby(TRACK_ID, sort=True)[[c for c in METADATA if c in frame.columns]].first()
    labels = sorted(frame[TARGET].unique())
    binarizer = MultiLabelBinarizer(classes=labels)
    y = binarizer.fit_transform(track_labels.reindex(track_features.index))
    data = track_features.join(track_metadata, how="left").reset_index()
    data["true_genres"] = track_labels.reindex(data[TRACK_ID]).map(lambda xs: ", ".join(xs)).to_numpy()
    data.attrs["n_source_rows"] = source_row_count
    return data, y, labels


def build_models() -> dict[str, Any]:
    """Return three comparable multi-label baselines."""
    return {
        "Logistic Regression": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
            ("model", OneVsRestClassifier(LogisticRegression(max_iter=2000, class_weight="balanced",
                                                               random_state=SEED))),
        ]),
        "RBF SVM": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
            # Omit `probability`: sklearn 1.9 deprecates setting it even to False.
            # Its default keeps probability estimation disabled, so predictions
            # are ranked from the SVM decision margins in probability_matrix().
            ("model", OneVsRestClassifier(SVC(kernel="rbf", C=2.0, gamma="scale",
                                                class_weight="balanced", random_state=SEED))),
        ]),
        "Random Forest": Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("model", MultiOutputClassifier(RandomForestClassifier(n_estimators=220, min_samples_leaf=2,
                                                                    class_weight="balanced_subsample",
                                                                    random_state=SEED, n_jobs=-1))),
        ]),
    }


def probability_matrix(model: Any, X: pd.DataFrame) -> np.ndarray:
    """Normalize model outputs to N x C ranking scores in [0, 1]."""
    if not hasattr(model, "predict_proba"):
        # SVM margins provide a fast ranking score; sigmoid maps margins to [0, 1].
        margins = np.asarray(model.decision_function(X))
        return 1.0 / (1.0 + np.exp(-np.clip(margins, -40, 40)))
    probabilities = model.predict_proba(X)
    if isinstance(probabilities, list):
        columns = []
        fitted_model = model.named_steps["model"] if isinstance(model, Pipeline) else model
        estimators = fitted_model.estimators_
        for result, estimator in zip(probabilities, estimators):
            class_values = list(estimator.classes_)
            positive_index = class_values.index(1) if 1 in class_values else 0
            columns.append(result[:, positive_index])
        return np.column_stack(columns)
    return np.asarray(probabilities)


def _scores(y_true: np.ndarray, probs: np.ndarray) -> tuple[np.ndarray, dict[str, float]]:
    y_pred = (probs >= 0.5).astype(int)
    empty = y_pred.sum(axis=1) == 0
    if empty.any():
        y_pred[empty, probs[empty].argmax(axis=1)] = 1
    ranked = np.argsort(probs, axis=1)[:, ::-1]
    hit_at_1 = float(np.mean([y_true[row, order[0]] == 1 for row, order in enumerate(ranked)]))
    recall_at_3 = float(np.mean([
        y_true[row, order[:3]].sum() / max(1, y_true[row].sum())
        for row, order in enumerate(ranked)
    ]))
    metrics = {
        "micro_f1": float(f1_score(y_true, y_pred, average="micro", zero_division=0)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "subset_accuracy": float(np.mean(np.all(y_true == y_pred, axis=1))),
        "precision_at_1": hit_at_1,
        "recall_at_3": recall_at_3,
        "micro_precision": float(precision_score(y_true, y_pred, average="micro", zero_division=0)),
        "micro_recall": float(recall_score(y_true, y_pred, average="micro", zero_division=0)),
    }
    return y_pred, metrics


def evaluate(data: pd.DataFrame, y: np.ndarray, labels: list[str], output_dir: str | Path) -> dict[str, Any]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    X = data[FEATURES]
    indices = np.arange(len(data))
    train_idx, test_idx = train_test_split(indices, test_size=0.20, random_state=SEED, shuffle=True)
    X_development, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_development, y_test = y[train_idx], y[test_idx]

    summary: dict[str, Any] = {
        "dataset": "User-supplied Spotify Songs CSV",
        "target": "multi-label playlist_genre memberships per unique track_id",
        "seed": SEED,
        "n_source_rows": int(data.attrs.get("n_source_rows", len(data))),
        "n_unique_tracks": int(len(data)),
        "n_features": len(FEATURES),
        "n_classes": len(labels),
        "classes": labels,
        "class_track_counts": {label: int(y[:, labels.index(label)].sum()) for label in labels},
        "tracks_with_multiple_genres": int(np.sum(y.sum(axis=1) > 1)),
        "split": {"train": int(len(train_idx)), "test": int(len(test_idx)), "test_fraction": 0.20,
                  "unit": "unique track_id"},
        "cross_validation": {"folds": 5, "selection_metric": "mean macro F1",
                             "unit": "unique track_id within development set"},
        "models": {},
    }
    fold_splitter = KFold(n_splits=5, shuffle=True, random_state=SEED)
    candidate_models = build_models()
    best_name, best_score = None, -1.0
    for name, model_template in candidate_models.items():
        print(f"Cross-validating {name}...", flush=True)
        fold_metrics: list[dict[str, Any]] = []
        fold_genre_f1: list[list[float]] = []
        for fold_train_idx, fold_valid_idx in fold_splitter.split(X_development):
            model = clone(model_template)
            X_fold_train = X_development.iloc[fold_train_idx]
            X_fold_valid = X_development.iloc[fold_valid_idx]
            y_fold_train = y_development[fold_train_idx]
            y_fold_valid = y_development[fold_valid_idx]
            model.fit(X_fold_train, y_fold_train)
            fold_probs = probability_matrix(model, X_fold_valid)
            fold_pred, metrics = _scores(y_fold_valid, fold_probs)
            fold_metrics.append(metrics)
            fold_genre_f1.append([
                float(f1_score(y_fold_valid[:, col], fold_pred[:, col], zero_division=0))
                for col in range(len(labels))
            ])

        cv_metrics = {
            metric: float(np.mean([fold[metric] for fold in fold_metrics]))
            for metric in fold_metrics[0]
        }
        cv_metrics["per_genre"] = {
            label: {
                "f1": float(np.mean([fold[col] for fold in fold_genre_f1])),
                "support": int(y_development[:, col].sum()),
            }
            for col, label in enumerate(labels)
        }
        summary["models"][name] = cv_metrics
        if cv_metrics["macro_f1"] > best_score:
            best_name, best_score = name, cv_metrics["macro_f1"]

    # The held-out test set is first used here, after model selection is complete.
    print(f"Fitting selected model ({best_name}) on the full development set...", flush=True)
    best_model = candidate_models[best_name]
    best_model.fit(X_development, y_development)
    best_probabilities = probability_matrix(best_model, X_test)
    test_pred, test_metrics = _scores(y_test, best_probabilities)
    test_metrics["per_genre"] = {
        label: {
            "f1": float(f1_score(y_test[:, col], test_pred[:, col], zero_division=0)),
            "support": int(y_test[:, col].sum()),
        }
        for col, label in enumerate(labels)
    }
    summary["selected_model"] = best_name
    summary["selection_metric"] = "mean macro F1 across 5-fold CV on development set"
    summary["test_evaluation"] = test_metrics
    summary["note"] = "Scores are for the supplied CSV and must not be generalized to all Spotify tracks or listeners."
    (output_dir / "metrics.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    joblib.dump({"model": best_model, "features": FEATURES, "classes": labels,
                 "selected_model": best_name}, output_dir / "playlist_model.joblib")

    ranked = np.argsort(best_probabilities, axis=1)[:, ::-1]
    predictions = []
    for row, source_index in enumerate(test_idx):
        pred_mask = (best_probabilities[row] >= 0.5)
        if not pred_mask.any():
            pred_mask[ranked[row, 0]] = True
        predictions.append({
            "track_id": data.iloc[source_index][TRACK_ID],
            "track_name": data.iloc[source_index].get("track_name", ""),
            "track_artist": data.iloc[source_index].get("track_artist", ""),
            "actual_genres": data.iloc[source_index]["true_genres"],
            "predicted_genres": ", ".join(labels[j] for j in np.where(pred_mask)[0]),
            "top_3": ", ".join(f"{labels[j]} ({best_probabilities[row, j]:.2f})" for j in ranked[row, :3]),
        })
    pd.DataFrame(predictions).to_csv(output_dir / "test_predictions.csv", index=False)
    return summary


def recommend(model_bundle: dict[str, Any], tracks: pd.DataFrame, top_k: int = 3) -> pd.DataFrame:
    missing = [column for column in model_bundle["features"] if column not in tracks.columns]
    if missing:
        raise ValueError(f"CSV is missing required feature columns: {', '.join(missing)}")
    probs = probability_matrix(model_bundle["model"], tracks[model_bundle["features"]])
    labels = model_bundle["classes"]
    ranked = np.argsort(probs, axis=1)[:, ::-1]
    output = tracks[[c for c in (TRACK_ID, "track_name", "track_artist") if c in tracks]].copy()
    output["recommended_genres"] = [", ".join(labels[j] for j in order[:top_k]) for order in ranked]
    output["top_genre_confidence"] = [float(prob[row, order[0]]) for row, (prob, order) in enumerate(zip(probs, ranked))]
    output["ranked_genres"] = [", ".join(f"{labels[j]} ({prob[j]:.2f})" for j in order[:top_k])
                               for prob, order in zip(probs, ranked)]
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", default="data/raw/spotify_songs.csv")
    parser.add_argument("--output", default="results")
    args = parser.parse_args()
    data, y, labels = load_dataset(args.csv)
    result = evaluate(data, y, labels, args.output)
    print(json.dumps({"tracks": result["n_unique_tracks"], "classes": result["classes"],
                      "selected_model": result["selected_model"],
                      "metrics": result["models"]}, indent=2))


if __name__ == "__main__":
    main()
