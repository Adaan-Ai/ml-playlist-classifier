"""Create the assignment slide deck from measured project results."""

from __future__ import annotations

import json
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu, Pt

NAVY = RGBColor(0x15, 0x23, 0x3B)
INK = RGBColor(0x1F, 0x29, 0x37)
TEAL = RGBColor(0x17, 0x6B, 0x67)
MINT = RGBColor(0xDD, 0xF3, 0xED)
SLATE = RGBColor(0x52, 0x60, 0x78)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LINE = RGBColor(0xD8, 0xDE, 0xE8)
AMBER = RGBColor(0xD9, 0x77, 0x06)
PALE = RGBColor(0xF5, 0xF7, 0xFA)

SLIDE_W = Emu(12192000)  # 12.8 in
SLIDE_H = Emu(6858000)   # 7.2 in


def _set_fill(shape, rgb: RGBColor) -> None:
    shape.fill.solid()
    shape.fill.fore_color.rgb = rgb
    shape.line.fill.background()


def _textbox(slide, text, left, top, width, height, size, color=INK, bold=False, align=PP_ALIGN.LEFT):
    box = slide.shapes.add_textbox(left, top, width, height)
    frame = box.text_frame
    frame.word_wrap = True
    paragraph = frame.paragraphs[0]
    paragraph.alignment = align
    run = paragraph.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = "Arial"
    return box


def _rect(slide, left, top, width, height, fill: RGBColor):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    _set_fill(shape, fill)
    return shape


def _ellipse(slide, left, top, width, height, fill: RGBColor):
    shape = slide.shapes.add_shape(MSO_SHAPE.OVAL, left, top, width, height)
    _set_fill(shape, fill)
    return shape


def _notes(slide, text: str) -> None:
    slide.notes_slide.notes_text_frame.text = text


def _heading(slide, label: str, num: int) -> None:
    _textbox(slide, label, Emu(724000), Emu(476000), Emu(10287000), Emu(514000), 34, NAVY, True)
    _rect(slide, Emu(724000), Emu(1105000), Emu(10744200), Emu(28600), TEAL)
    _textbox(
        slide,
        f"{num:02d}  /  UE24CS352A",
        Emu(9334000),
        Emu(6381000),
        Emu(2134000),
        Emu(191000),
        12,
        SLATE,
        False,
        PP_ALIGN.RIGHT,
    )


def _bullets(slide, items: list[str], left, top, width, gap, size=23) -> None:
    for index, item in enumerate(items):
        y = top + index * gap
        _ellipse(slide, left, y + Emu(86000), Emu(133000), Emu(133000), TEAL)
        _textbox(slide, item, left + Emu(324000), y, width - Emu(324000), gap - Emu(95000), size, INK)


def build() -> Path:
    metrics_path = Path("results/metrics.json")
    if not metrics_path.exists():
        raise SystemExit("Run `python -m src.playlist_curator` first. The deck must use measured results.")
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    out = Path("output/project_presentation_cv_final.pptx")
    out.parent.mkdir(parents=True, exist_ok=True)

    pres = Presentation()
    pres.slide_width = SLIDE_W
    pres.slide_height = SLIDE_H
    blank = pres.slide_layouts[6]

    # 1. Title
    slide = pres.slides.add_slide(blank)
    _rect(slide, Emu(0), Emu(0), SLIDE_W, SLIDE_H, NAVY)
    _rect(slide, Emu(0), Emu(0), Emu(171500), SLIDE_H, TEAL)
    _textbox(slide, "UE24CS352A  /  MACHINE LEARNING", Emu(800000), Emu(838000), Emu(10287000), Emu(286000), 17, RGBColor(0x9F, 0xD8, 0xCA), True)
    _textbox(slide, "Training a Playlist Curator\nBased on Track Features", Emu(800000), Emu(1676000), Emu(9906000), Emu(1676000), 44, WHITE, True)
    _textbox(slide, "A genre-based, reproducible adaptation of the CS229 project", Emu(819000), Emu(3714000), Emu(9334000), Emu(400000), 22, RGBColor(0xD3, 0xDA, 0xE5))
    _rect(slide, Emu(819000), Emu(4590000), Emu(6572000), Emu(19100), RGBColor(0x3B, 0x50, 0x6B))
    _textbox(slide, "Team: Mohammed Adaan Hamad and Lakshya Jeet Singh     Section: E", Emu(819000), Emu(4858000), Emu(10478000), Emu(267000), 18, WHITE)
    _notes(slide, "Opening: this project adapts the supplied 2018 CS229 playlist-curation report. The data source and task proxy are explained on the following slides. References: https://cs229.stanford.edu/proj2018/report/22.pdf and https://cs229.stanford.edu/proj2018/poster/22.pdf")

    # 2. Problem and scope
    slide = pres.slides.add_slide(blank)
    _rect(slide, Emu(0), Emu(0), SLIDE_W, SLIDE_H, WHITE)
    _heading(slide, "Problem and project scope", 2)
    _bullets(slide, [
        "Input: a track represented by numeric acoustic features.",
        "Output: the most likely playlist category, plus ranked alternatives.",
        "Playlist genres act as category labels, so the model does not learn individual taste.",
        "The objective is a reproducible content-based classification baseline.",
    ], Emu(895000), Emu(1505000), Emu(10097000), Emu(971000), 23)
    _notes(slide, "The 2018 report frames playlist continuation as assigning a track to one of a user's playlists. Our supplied dataset has playlist genre labels, not personal playlist membership. We state this proxy clearly.")

    # 3. Dataset
    slide = pres.slides.add_slide(blank)
    _rect(slide, Emu(0), Emu(0), SLIDE_W, SLIDE_H, WHITE)
    _heading(slide, "Dataset and feature representation", 3)
    _textbox(slide, "Supplied Spotify Songs data", Emu(857000), Emu(1543000), Emu(4096000), Emu(381000), 24, TEAL, True)
    _textbox(slide, f"{metrics['n_source_rows']:,} playlist-track rows", Emu(857000), Emu(2095000), Emu(4191000), Emu(438000), 28, NAVY, True)
    _textbox(slide, f"{metrics['n_unique_tracks']:,} unique tracks", Emu(857000), Emu(2590000), Emu(4191000), Emu(400000), 22, NAVY, True)
    _textbox(slide, f"{metrics['n_features']} numeric audio features", Emu(857000), Emu(3105000), Emu(4572000), Emu(400000), 20, INK)
    _textbox(slide, f"{metrics['n_classes']} playlist genres", Emu(857000), Emu(3581000), Emu(4572000), Emu(400000), 20, INK)
    _rect(slide, Emu(5905000), Emu(1524000), Emu(19100), Emu(4000000), LINE)
    _textbox(slide, "Data preparation", Emu(6381000), Emu(1543000), Emu(4191000), Emu(381000), 24, TEAL, True)
    _bullets(slide, [
        "Aggregate repeated rows by track ID.",
        "Keep every genre label for multi-label learning.",
        f"Track-level 80/20 split; seed {metrics['seed']}.",
        f"{metrics['tracks_with_multiple_genres']:,} tracks carry multiple genre labels.",
    ], Emu(6400000), Emu(2114000), Emu(4858000), Emu(705000), 16)
    _notes(slide, "We group by track_id, average repeated acoustic feature values, and preserve every playlist_genre assigned to that track.")

    # 4. Modeling workflow
    slide = pres.slides.add_slide(blank)
    _rect(slide, Emu(0), Emu(0), SLIDE_W, SLIDE_H, WHITE)
    _heading(slide, "Modeling workflow", 4)
    steps = [
        ("01", "Load and group", "playlist rows\nby track ID", TEAL),
        ("02", "Prepare", "average repeated\nacoustic features", TEAL),
        ("03", "Compare", "logistic regression\nRBF SVM\nrandom forest", TEAL),
        ("04", "Evaluate", "micro + macro F1\nranking metrics", AMBER),
    ]
    box_w = Emu(2381000)
    gap = Emu(324000)
    x0 = Emu(800000)
    for index, (number, title, body, accent) in enumerate(steps):
        x = x0 + index * (box_w + gap)
        _textbox(slide, number, x, Emu(1619000), Emu(667000), Emu(343000), 20, TEAL, True)
        _rect(slide, x, Emu(2048000), box_w, Emu(38100), accent)
        _textbox(slide, title, x, Emu(2286000), box_w, Emu(381000), 24, NAVY, True)
        _textbox(slide, body, x, Emu(2876000), box_w, Emu(1162000), 18, INK)
    _textbox(slide, "Preprocessing stays inside each model pipeline, fitted on training data only.", Emu(819000), Emu(4876000), Emu(10097000), Emu(362000), 20, SLATE)
    _notes(slide, "We split unique track IDs at random with seed 42. Imputation and scaling are scikit-learn pipeline steps fit on training data only.")

    # 5. Results
    slide = pres.slides.add_slide(blank)
    _rect(slide, Emu(0), Emu(0), SLIDE_W, SLIDE_H, WHITE)
    _heading(slide, "5-fold cross-validation comparison", 5)
    names = list(metrics["models"].keys())
    rows = [["Model", "Micro F1", "Macro F1", "Top-1 hit", "Recall@3"]]
    for name in names:
        values = metrics["models"][name]
        rows.append([
            name,
            f"{values['micro_f1']:.3f}",
            f"{values['macro_f1']:.3f}",
            f"{values['precision_at_1']:.3f}",
            f"{values['recall_at_3']:.3f}",
        ])
    table_shape = slide.shapes.add_table(len(rows), 5, Emu(724000), Emu(1619000), Emu(7718000), Emu(2858000))
    table = table_shape.table
    widths = [Emu(2286000), Emu(1359000), Emu(1359000), Emu(1359000), Emu(1359000)]
    for col, width in enumerate(widths):
        table.columns[col].width = width
    selected_row = names.index(metrics["selected_model"]) + 1
    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            cell = table.cell(r, c)
            cell.text = value
            paragraph = cell.text_frame.paragraphs[0]
            paragraph.alignment = PP_ALIGN.CENTER if c else PP_ALIGN.LEFT
            run = paragraph.runs[0]
            run.font.name = "Arial"
            run.font.size = Pt(14)
            run.font.bold = r == 0
            if r == 0:
                run.font.color.rgb = WHITE
                cell.fill.solid()
                cell.fill.fore_color.rgb = NAVY
            elif r == selected_row:
                run.font.color.rgb = INK
                cell.fill.solid()
                cell.fill.fore_color.rgb = MINT
            else:
                run.font.color.rgb = INK
                cell.fill.solid()
                cell.fill.fore_color.rgb = WHITE if r % 2 else PALE
    selected = metrics["selected_model"]
    _textbox(slide, "Selected model", Emu(8860000), Emu(1695000), Emu(2381000), Emu(248000), 16, SLATE, True)
    _textbox(slide, selected, Emu(8860000), Emu(2134000), Emu(2477000), Emu(400000), 24, TEAL, True)
    _textbox(slide, f"CV Macro F1: {metrics['models'][selected]['macro_f1']:.3f}", Emu(8860000), Emu(2781000), Emu(2477000), Emu(305000), 16, INK)
    _textbox(slide, f"Test Macro F1: {metrics['test_evaluation']['macro_f1']:.3f}", Emu(8860000), Emu(3181000), Emu(2477000), Emu(305000), 16, INK)
    _textbox(slide, f"Test exact match: {metrics['test_evaluation']['subset_accuracy']:.3f}", Emu(8860000), Emu(3581000), Emu(2477000), Emu(400000), 16, INK)
    _textbox(slide, f"{metrics['split']['test']:,} untouched test tracks", Emu(8860000), Emu(4115000), Emu(2477000), Emu(286000), 14, SLATE)
    _textbox(slide, "Table shows mean 5-fold CV scores on the 80% development set. The test set is evaluated once for the selected model.", Emu(838000), Emu(5201000), Emu(10478000), Emu(457000), 14, SLATE)
    _notes(slide, f"The selected model, {selected}, is refit on all development tracks and evaluated once on the untouched test set.")

    # 6. Demo and conclusions
    slide = pres.slides.add_slide(blank)
    _rect(slide, Emu(0), Emu(0), SLIDE_W, SLIDE_H, WHITE)
    _heading(slide, "Demo and conclusions", 6)
    _textbox(slide, "Live demo", Emu(838000), Emu(1562000), Emu(4191000), Emu(343000), 24, TEAL, True)
    _bullets(slide, [
        "Train the model from the supplied playlist-track CSV.",
        "Upload a CSV with matching acoustic features.",
        "Review the top category, probability, and alternatives.",
    ], Emu(876000), Emu(2076000), Emu(5000000), Emu(800000), 16)
    _rect(slide, Emu(6191000), Emu(1524000), Emu(19100), Emu(3790000), LINE)
    _textbox(slide, "Conclusion", Emu(6667000), Emu(1562000), Emu(4191000), Emu(343000), 24, TEAL, True)
    _textbox(
        slide,
        f"The best measured baseline is {selected}. Acoustic features support broad category ranking, while playlist placement cannot validate personal taste.",
        Emu(6667000), Emu(2076000), Emu(4477000), Emu(1581000), 18, INK,
    )
    _textbox(slide, "Next: evaluate listener-curated playlists and repeated cross-validation.", Emu(6667000), Emu(4019000), Emu(4382000), Emu(686000), 16, SLATE)
    _textbox(slide, "Thank you", Emu(838000), Emu(5524000), Emu(2858000), Emu(429000), 26, NAVY, True)
    _notes(slide, "Demo workflow: run `python -m src.playlist_curator`, then `streamlit run app.py`. Limit the conclusion to this measured playlist-genre task.")

    pres.save(out)
    return out


if __name__ == "__main__":
    print(build())
