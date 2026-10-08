"""Create the assignment's two-page summary from measured project results."""

from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def build() -> Path:
    metrics_path = Path("results/metrics.json")
    if not metrics_path.exists():
        raise SystemExit("Run `python -m src.playlist_curator` first. The report must use measured results.")
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    out = Path("output/project_report.pdf")
    out.parent.mkdir(parents=True, exist_ok=True)
    base = getSampleStyleSheet()
    base.add(ParagraphStyle(name="TitleCustom", parent=base["Title"], fontName="Helvetica-Bold",
                            fontSize=18, leading=21, textColor=colors.HexColor("#15233B"),
                            alignment=TA_LEFT, spaceAfter=5))
    base.add(ParagraphStyle(name="SubtitleCustom", parent=base["Normal"], fontSize=8.5,
                            leading=11, textColor=colors.HexColor("#526078"), spaceAfter=7))
    base.add(ParagraphStyle(name="SectionCustom", parent=base["Heading2"], fontSize=11.5,
                            leading=14, textColor=colors.HexColor("#176B67"), spaceBefore=4, spaceAfter=3))
    base.add(ParagraphStyle(name="BodyCustom", parent=base["BodyText"], fontSize=8.7,
                            leading=11.4, spaceAfter=4))
    base.add(ParagraphStyle(name="SmallCustom", parent=base["BodyText"], fontSize=7.1,
                            leading=8.5, textColor=colors.HexColor("#526078"), spaceAfter=2))

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#D8DEE8"))
        canvas.line(18*mm, 14*mm, 192*mm, 14*mm)
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(colors.HexColor("#64748B"))
        canvas.drawString(18*mm, 9*mm, "UE24CS352A | Machine Learning Mini-Project")
        canvas.drawRightString(192*mm, 9*mm, f"{doc.page}")
        canvas.restoreState()

    story = [
        Paragraph("Training a Playlist Curator Based on Track Features", base["TitleCustom"]),
        Paragraph("UE24CS352A - Machine Learning Mini-Project | Team: __________________________ | Section: __________", base["SubtitleCustom"]),
        Paragraph("Problem statement", base["SectionCustom"]),
        Paragraph("Given the audio features of a track, recommend the playlist genres that best fit it. A track can appear in multiple playlists, so we model genre assignment as a multi-label problem. The project adapts the supplied CS229 playlist-curation idea to the provided Spotify Songs dataset.", base["BodyCustom"]),
        Paragraph("Dataset", base["SectionCustom"]),
        Paragraph(f"The supplied archive contains {metrics['n_source_rows']:,} playlist-track rows and 23 columns. After grouping repeated rows by track ID, the project uses {metrics['n_unique_tracks']:,} unique tracks, {metrics['n_features']} audio features, and six playlist genres: {', '.join(metrics['classes'])}. We found {metrics['tracks_with_multiple_genres']:,} tracks with more than one genre label. The features are danceability, energy, key, loudness, mode, speechiness, acousticness, instrumentalness, liveness, valence, tempo, and duration. We exclude track popularity and playlist metadata from the model inputs.", base["BodyCustom"]),
        Paragraph("Approach", base["SectionCustom"]),
        Paragraph(f"We average repeated audio feature values by track ID and retain every associated playlist genre. We split unique-track rows into {metrics['split']['train']:,} development and {metrics['split']['test']:,} test tracks (80/20, seed {metrics['seed']}). The test set remains untouched during model selection. We compare one-versus-rest logistic regression, one-versus-rest RBF SVM, and a multi-output random forest using 5-fold cross-validation on the development set. Median imputation and scaling are fit inside each fold's training pipeline. We compare micro F1, macro F1, exact subset accuracy, top-1 hit rate, and recall at three; mean macro F1 selects the model.", base["BodyCustom"]),
        PageBreak(),
        Paragraph("Implementation and measured results", base["SectionCustom"]),
        Paragraph("The Python pipeline validates and reads the CSV, aggregates playlist rows at track level, builds multi-hot genre labels, trains and compares models, and saves metrics, held-out predictions, and the selected model. The Streamlit demo accepts a CSV with the same 12 features and ranks the three most likely playlist genres.", base["BodyCustom"]),
    ]
    rows = [["Model", "Micro F1", "Macro F1", "Top-1 hit", "Recall@3"]]
    for name, values in metrics["models"].items():
        rows.append([name, f"{values['micro_f1']:.3f}", f"{values['macro_f1']:.3f}",
                     f"{values['precision_at_1']:.3f}", f"{values['recall_at_3']:.3f}"])
    table = Table(rows, colWidths=[51*mm, 28*mm, 28*mm, 28*mm, 28*mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#15233B")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTNAME", (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("ALIGN", (1,1), (-1,-1), "CENTER"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F1F5F9")]),
        ("LINEBELOW", (0,0), (-1,0), 0.7, colors.HexColor("#176B67")),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("TOPPADDING", (0,0), (-1,-1), 5),
    ]))
    story += [table, Spacer(1, 2*mm), Paragraph(f"Selected model: <b>{metrics['selected_model']}</b> by mean cross-validation macro F1. On the untouched test set, it achieved macro F1 {metrics['test_evaluation']['macro_f1']:.3f} and micro F1 {metrics['test_evaluation']['micro_f1']:.3f}. Exact subset accuracy requires all genre labels for a track to match.", base["BodyCustom"])]
    story += [
        Paragraph("Conclusion", base["SectionCustom"]),
        Paragraph(f"The selected model ({metrics['selected_model']}) provides the strongest macro-F1 result on this fixed track-level test split. The project demonstrates how acoustic features can rank broad playlist genres, including multiple plausible genres for a track. The task does not measure personal taste or reproduce a specific listener's playlist decisions. Evaluation on listener-curated playlists and repeated splits would provide stronger evidence.", base["BodyCustom"]),
        Paragraph("Limitations and data note", base["SectionCustom"]),
        Paragraph("The archive README says the dataset was obtained from Spotify via the spotifyr package and does not specify a redistribution license. Spotify's current Developer Policy restricts using Spotify content to train ML models. We did not call the Spotify API. Confirm with the instructor that use of this supplied archival dataset is permitted for the course, and do not redistribute it without permission.", base["SmallCustom"]),
        Paragraph("References", base["SectionCustom"]),
        Paragraph("Awadelkarim and Coelho (2018), Training a Playlist Curator Based on User Taste, CS229 report and poster. Defferrard et al. (2017), FMA: A Dataset For Music Analysis, ISMIR, https://arxiv.org/abs/1612.01840 (alternative open music dataset). Spotify for Developers, Spotify Developer Policy, effective 15 May 2025, https://developer.spotify.com/policy.", base["SmallCustom"]),
    ]
    doc = SimpleDocTemplate(str(out), pagesize=A4, rightMargin=18*mm, leftMargin=18*mm,
                            topMargin=15*mm, bottomMargin=19*mm, title="Playlist Curator Mini-Project")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return out


if __name__ == "__main__":
    print(build())
