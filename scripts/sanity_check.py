"""Lightweight sanity-check script to verify model bundle, metrics, and demo inference."""

import json
import sys
from pathlib import Path

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.playlist_curator import recommend


def main() -> int:
    print("Running lightweight repository sanity check...\n")
    errors = []

    # 1. Verify metrics.json
    metrics_path = Path("results/metrics.json")
    if not metrics_path.exists():
        errors.append("results/metrics.json not found.")
    else:
        try:
            with metrics_path.open("r", encoding="utf-8") as f:
                metrics = json.load(f)
            assert "selected_model" in metrics, "Missing 'selected_model' in metrics.json"
            assert "classes" in metrics and len(metrics["classes"]) == 6, "Expected 6 classes in metrics.json"
            assert "test_evaluation" in metrics, "Missing 'test_evaluation' in metrics.json"
            print(f"[OK] metrics.json validated (Selected Model: {metrics['selected_model']}, Test Macro F1: {metrics['test_evaluation']['macro_f1']:.4f})")
        except Exception as exc:
            errors.append(f"Failed to validate metrics.json: {exc}")

    # 2. Verify test_predictions.csv
    preds_path = Path("results/test_predictions.csv")
    if not preds_path.exists():
        errors.append("results/test_predictions.csv not found.")
    else:
        try:
            preds_df = pd.read_csv(preds_path)
            assert len(preds_df) > 0, "test_predictions.csv is empty."
            print(f"[OK] test_predictions.csv validated ({len(preds_df)} rows)")
        except Exception as exc:
            errors.append(f"Failed to validate test_predictions.csv: {exc}")

    # 3. Verify deliverables
    pdf_path = Path("output/project_report.pdf")
    pptx_path = Path("output/project_presentation_cv_final.pptx")
    if not pdf_path.exists():
        errors.append("output/project_report.pdf not found.")
    else:
        print(f"[OK] output/project_report.pdf exists ({pdf_path.stat().st_size} bytes)")

    if not pptx_path.exists():
        errors.append("output/project_presentation_cv_final.pptx not found.")
    else:
        print(f"[OK] output/project_presentation_cv_final.pptx exists ({pptx_path.stat().st_size} bytes)")

    # 4. Verify model bundle & inference on sample tracks
    model_path = Path("results/playlist_model.joblib")
    sample_path = Path("samples/demo_tracks.csv")

    if not model_path.exists():
        errors.append("results/playlist_model.joblib not found. Train the model using python -m src.playlist_curator")
    elif not sample_path.exists():
        errors.append("samples/demo_tracks.csv not found.")
    else:
        try:
            bundle = joblib.load(model_path)
            sample_df = pd.read_csv(sample_path)
            results = recommend(bundle, sample_df)
            assert not results.empty, "Recommendation returned empty dataframe."
            assert "recommended_genres" in results.columns, "Missing recommended_genres in output columns."
            assert "ranked_genres" in results.columns, "Missing ranked_genres in output columns."
            print(f"[OK] Demo recommendation inference succeeded on {len(sample_df)} sample tracks:")
            for _, row in results.iterrows():
                print(f"     * {row['track_name']} ({row['track_artist']}): {row['ranked_genres']}")
        except Exception as exc:
            errors.append(f"Failed inference test with model bundle: {exc}")

    print()
    if errors:
        print(f"FAILED: {len(errors)} sanity check error(s) found:")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("ALL SANITY CHECKS PASSED SUCCESSFULLY.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
