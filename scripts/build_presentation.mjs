import fs from "node:fs/promises";
import path from "node:path";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const workspaceDir = process.cwd();
const buildDir = path.join(workspaceDir, ".codex-build");
const outputDir = path.join(workspaceDir, "output");
const finalPath = path.join(outputDir, "project_presentation_cv_final.pptx");
const metricsPath = path.join(workspaceDir, "results/metrics.json");

try {
  await fs.access(metricsPath);
} catch {
  console.error("Missing results/metrics.json. Run `python -m src.playlist_curator` before building the deck.");
  process.exit(1);
}

const metrics = JSON.parse(await fs.readFile(metricsPath, "utf8"));
await fs.mkdir(buildDir, { recursive: true });
await fs.mkdir(outputDir, { recursive: true });

const C = { navy: "#15233B", ink: "#1F2937", teal: "#176B67", mint: "#DDF3ED", pale: "#F5F7FA", slate: "#526078", white: "#FFFFFF", line: "#D8DEE8", amber: "#D97706" };
const pres = Presentation.create({ slideSize: { width: 1280, height: 720 } });

function text(slide, value, x, y, w, h, size, color = C.ink, bold = false, name = "text") {
  const shape = slide.shapes.add({
    geometry: "textbox", name,
    position: { left: x, top: y, width: w, height: h },
    fill: "none", line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = [[{ run: value, style: { typeface: "Arial", fontSize: `${size}px`, color, bold } }]];
  shape.text.insets = 0;
  return shape;
}

function rule(slide, x, y, w, color = C.line, weight = 2) {
  slide.shapes.add({ geometry: "rect", position: { left: x, top: y, width: w, height: weight },
    fill: color, line: { style: "solid", fill: "none", width: 0 } });
}

function heading(slide, label, num) {
  text(slide, label, 76, 50, 1080, 54, 34, C.navy, true, `slide-${num}-title`);
  rule(slide, 76, 116, 1128, C.teal, 3);
  text(slide, `${String(num).padStart(2, "0")}  /  UE24CS352A`, 980, 670, 224, 20, 12, C.slate, false, `slide-${num}-footer`);
}

function bullets(slide, items, x = 90, y = 160, w = 1060, gap = 96, size = 24) {
  items.forEach((item, i) => {
    const yy = y + i * gap;
    slide.shapes.add({ geometry: "ellipse", position: { left: x, top: yy + 9, width: 14, height: 14 },
      fill: C.teal, line: { style: "solid", fill: "none", width: 0 } });
    text(slide, item, x + 34, yy, w - 34, gap - 10, size, C.ink, false, `bullet-${i + 1}`);
  });
}

// 1. Minimal title slide
{
  const slide = pres.slides.add();
  slide.background.fill = C.navy;
  slide.shapes.add({ geometry: "rect", position: { left: 0, top: 0, width: 18, height: 720 }, fill: C.teal,
    line: { style: "solid", fill: "none", width: 0 } });
  text(slide, "UE24CS352A  /  MACHINE LEARNING", 84, 88, 1080, 30, 17, "#9FD8CA", true, "course");
  text(slide, "Training a Playlist Curator\nBased on Track Features", 84, 176, 1040, 176, 48, C.white, true, "title");
  text(slide, "A genre-based, reproducible adaptation of the CS229 project", 86, 390, 980, 42, 23, "#D3DAE5", false, "subtitle");
  rule(slide, 86, 482, 690, "#3B506B", 2);
  text(slide, "Team: Mohammed Adaan Hamad and Lakshya Jeet Singh     Section: E", 86, 510, 1100, 28, 18, C.white, false, "team");
  slide.speakerNotes.text = "Opening: this project adapts the supplied 2018 CS229 playlist-curation report. The data source and task proxy are explained on the following slides. References: https://cs229.stanford.edu/proj2018/report/22.pdf and https://cs229.stanford.edu/proj2018/poster/22.pdf";
}

// 2. Problem and scope
{
  const slide = pres.slides.add(); heading(slide, "Problem and project scope", 2);
  bullets(slide, [
    "Input: a track represented by numeric acoustic features.",
    "Output: the most likely playlist category, plus ranked alternatives.",
    "Playlist genres act as category labels, so the model does not learn individual taste.",
    "The objective is a reproducible content-based classification baseline.",
  ], 94, 158, 1060, 102, 23);
  slide.speakerNotes.text = "The 2018 report frames playlist continuation as assigning a track to one of a user's playlists. Our supplied dataset has playlist genre labels, not personal playlist membership. We state this proxy clearly. Source: https://cs229.stanford.edu/proj2018/report/22.pdf";
}

// 3. Dataset
{
  const slide = pres.slides.add(); heading(slide, "Dataset and feature representation", 3);
  text(slide, "Supplied Spotify Songs data", 90, 162, 430, 40, 26, C.teal, true, "dataset-label");
  text(slide, `${metrics.n_source_rows.toLocaleString()} playlist-track rows`, 90, 220, 440, 46, 31, C.navy, true, "source-count");
  text(slide, `${metrics.n_unique_tracks.toLocaleString()} unique tracks`, 90, 272, 440, 42, 24, C.navy, true, "track-count");
  text(slide, `${metrics.n_features.toLocaleString()} numeric audio features`, 90, 326, 480, 42, 23, C.ink, false, "feature-count");
  text(slide, `${metrics.n_classes} playlist genres`, 90, 376, 480, 42, 23, C.ink, false, "class-count");
  rule(slide, 620, 160, 2, C.line, 420);
  text(slide, "Data preparation", 670, 162, 440, 40, 28, C.teal, true, "prep-title");
  bullets(slide, [
    "Aggregate repeated rows by track ID.",
    "Keep every genre label for multi-label learning.",
    `Track-level 80/20 split; seed ${metrics.seed}.`,
    `${metrics.tracks_with_multiple_genres.toLocaleString()} tracks carry multiple genre labels.`,
  ], 672, 222, 510, 74, 18);
  slide.speakerNotes.text = "The supplied TidyTuesday Spotify Songs data has 32,833 rows and 23 columns. We group by track_id, average repeated acoustic feature values, and preserve every playlist_genre assigned to that track. The dataset readme says it was collected via the spotifyr package. Source: https://github.com/rfordatascience/tidytuesday/tree/master/data/2020/2020-01-21";
}

// 4. Modeling workflow
{
  const slide = pres.slides.add(); heading(slide, "Modeling workflow", 4);
  const steps = [
    ["01", "Load and group", "playlist rows\nby track ID"],
    ["02", "Prepare", "average repeated\nacoustic features"],
    ["03", "Compare", "logistic regression\nRBF SVM\nrandom forest"],
    ["04", "Evaluate", "micro + macro F1\nranking metrics"],
  ];
  const x0 = 84, boxW = 250, gap = 34;
  steps.forEach((s, i) => {
    const x = x0 + i * (boxW + gap);
    text(slide, s[0], x, 170, 70, 36, 20, C.teal, true, `workflow-${i}-number`);
    rule(slide, x, 215, boxW, i === 3 ? C.amber : C.teal, 4);
    text(slide, s[1], x, 240, boxW, 40, 25, C.navy, true, `workflow-${i}-title`);
    text(slide, s[2], x, 302, boxW, 122, 18, C.ink, false, `workflow-${i}-body`);
  });
  text(slide, "Preprocessing stays inside each model pipeline, fitted on training data only.", 86, 512, 1060, 38, 22, C.slate, false, "leakage-note");
  slide.speakerNotes.text = "We split unique track IDs at random with seed 42. Imputation and scaling are scikit-learn pipeline steps fit on training data only, avoiding test-set leakage. Logistic regression, RBF SVM, and random forest provide three standard supervised baselines, consistent with the reference report's model-comparison approach.";
}

// 5. Results in an editable native table
{
  const slide = pres.slides.add(); heading(slide, "5-fold cross-validation comparison", 5);
  const names = Object.keys(metrics.models);
  const rows = [["Model", "Micro F1", "Macro F1", "Top-1 hit", "Recall@3"], ...names.map(name => [
    name,
    metrics.models[name].micro_f1.toFixed(3),
    metrics.models[name].macro_f1.toFixed(3),
    metrics.models[name].precision_at_1.toFixed(3),
    metrics.models[name].recall_at_3.toFixed(3),
  ])];
  const table = slide.tables.add({ rows: rows.length, columns: rows[0].length, left: 76, top: 170, width: 810, height: 300,
    values: rows.map((row, ri) => row.map(value => [{ run: value, style: { typeface: "Arial", fontSize: ri === 0 ? "17px" : "16px", bold: ri === 0, color: ri === 0 ? C.white : C.ink } }])) });
  table.styleOptions = { headerRow: true, bandedRows: true };
  table.borders.assign({ style: "solid", fill: C.line, width: 1 });
  for (let c = 0; c < rows[0].length; c++) table.getCell(0, c).fill = C.navy;
  const selectedRow = names.indexOf(metrics.selected_model) + 1;
  for (let c = 0; c < rows[0].length; c++) table.getCell(selectedRow, c).fill = C.mint;
  text(slide, "Selected model", 930, 178, 250, 26, 16, C.slate, true, "selected-label");
  text(slide, metrics.selected_model, 930, 224, 260, 42, 28, C.teal, true, "selected-model");
  text(slide, `CV Macro F1: ${metrics.models[metrics.selected_model].macro_f1.toFixed(3)}`, 930, 292, 260, 32, 19, C.ink, false, "cv-macro-f1");
  text(slide, `Test Macro F1: ${metrics.test_evaluation.macro_f1.toFixed(3)}`, 930, 334, 260, 32, 19, C.ink, false, "test-macro-f1");
  text(slide, `Test exact match: ${metrics.test_evaluation.subset_accuracy.toFixed(3)}`, 930, 376, 260, 42, 18, C.ink, false, "best-exact-match");
  text(slide, `${metrics.split.test.toLocaleString()} untouched test tracks`, 930, 432, 260, 30, 16, C.slate, false, "test-count");
  text(slide, "Table shows mean 5-fold CV scores on the 80% development set. The test set is evaluated once for the selected model.", 88, 546, 1100, 48, 16, C.slate, false, "results-caveat");
  slide.speakerNotes.text = `The table shows mean 5-fold cross-validation metrics on the 80% development set. Macro F1 gives each genre equal weight and selects the model. The selected model, ${metrics.selected_model}, is then refit on all development tracks and evaluated once on the untouched ${metrics.split.test}-track test set; those final metrics are shown at right. Dataset source noted in the archive: https://github.com/rfordatascience/tidytuesday/tree/master/data/2020/2020-01-21`;
}

// 6. Demonstration and conclusion
{
  const slide = pres.slides.add(); heading(slide, "Demo and conclusions", 6);
  text(slide, "Live demo", 88, 164, 440, 36, 27, C.teal, true, "demo-heading");
  bullets(slide, [
    "Train the model from the supplied playlist-track CSV.",
    "Upload a CSV with matching acoustic features.",
    "Review the top category, probability, and alternatives.",
  ], 92, 218, 525, 84, 19);
  rule(slide, 650, 160, 2, C.line, 398);
  text(slide, "Conclusion", 700, 164, 440, 36, 27, C.teal, true, "conclusion-heading");
  text(slide, `The best measured baseline is ${metrics.selected_model}. Acoustic features support broad category ranking, while playlist placement cannot validate personal taste.`, 700, 218, 470, 166, 22, C.ink, false, "conclusion-copy");
  text(slide, "Next: evaluate listener-curated playlists and repeated cross-validation.", 700, 422, 460, 72, 19, C.slate, false, "next-step");
  text(slide, "Thank you", 88, 580, 300, 45, 28, C.navy, true, "thank-you");
  slide.speakerNotes.text = "Demo workflow: run `python -m src.playlist_curator`, then `streamlit run app.py`. The app expects the same features as those used during training. Limit the conclusion to this measured playlist-genre task. The archive README notes Spotify API data provenance. Current policy: https://developer.spotify.com/policy";
}

for (const [index, slide] of pres.slides.items.entries()) {
  const png = await pres.export({ slide, format: "png", scale: 1 });
  await fs.writeFile(path.join(buildDir, `slide-${String(index + 1).padStart(2, "0")}.png`),
    new Uint8Array(await png.arrayBuffer()));
}
const candidatePath = path.join(buildDir, "candidate.pptx");
await (await PresentationFile.exportPptx(pres)).save(candidatePath);
await fs.copyFile(candidatePath, finalPath);
console.log(finalPath);
