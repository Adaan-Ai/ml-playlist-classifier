"""Extract and validate spotify_songs.csv from the supplied archive."""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = {
    "track_id", "playlist_genre", "danceability", "energy", "key", "loudness",
    "mode", "speechiness", "acousticness", "instrumentalness", "liveness",
    "valence", "tempo", "duration_ms",
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", help="Path to archive (1).zip or compatible archive")
    parser.add_argument("--output", default="data/raw/spotify_songs.csv")
    args = parser.parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.archive) as archive:
        candidates = [name for name in archive.namelist() if Path(name).name == "spotify_songs.csv"]
        if len(candidates) != 1:
            raise SystemExit("Expected exactly one spotify_songs.csv in the archive.")
        with archive.open(candidates[0]) as source:
            frame = pd.read_csv(source)
    missing = REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        raise SystemExit(f"Dataset is missing required columns: {', '.join(sorted(missing))}")
    frame.to_csv(output, index=False)
    print(f"Validated {len(frame):,} rows and wrote {output}.")


if __name__ == "__main__":
    main()
