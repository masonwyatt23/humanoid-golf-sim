"""Extract R22-07 Fig 3 (launch vs impact height) from a LOCAL copy of the PDF. NOT run in CI (needs the PDF + PyMuPDF).
Source: R&A/USGA research report R22-07 'The effect of impact position on driving distance' (about 2022; header says 2006).
Raw per-series points -> $R2207_HELD_DIR if set (held locally, counsel-pending, never committed; skipped if unset). Averaged table -> data/references/r2207_fig3_launch_delta_table.csv
(label 'derived from digitized figure, approximate'). Usage: python data/extract_r2207_fig3.py <pdf_path>   (or set R2207_PDF)"""
import csv, sys, collections
from pathlib import Path
import numpy as np

import os
PDF = os.environ.get("R2207_PDF")                 # local PDF copy; never committed
HELD_DIR = Path(os.environ["R2207_HELD_DIR"]) if os.environ.get("R2207_HELD_DIR") else None
OUT = Path(__file__).resolve().parent / "references/r2207_fig3_launch_delta_table.csv"
CIT = "R&A/USGA research report R22-07 'The effect of impact position on driving distance' (about 2022; header says 2006), Fig 3"
URL = "https://www.usga.org/content/dam/usga/pdf/Equipment/R22-07%20The%20effect%20of%20impact%20position%20on%20driving%20distance.pdf"


def extract(pdf):
    import pymupdf as fitz
    pg = fitz.open(pdf)[2]; W = pg.get_text("words")
    xt = [((w[0] + w[2]) / 2, float(w[4])) for w in W if abs(w[1] - 718.4) < 1 and w[4] in ["0", "10", "20", "30", "40", "50"]]
    yt = [((w[1] + w[3]) / 2, float(w[4])) for w in W if w[0] < 160 and 480 < w[1] < 700 and w[4].isdigit()]
    ax = np.polyfit(*zip(*xt), 1); ay = np.polyfit(*zip(*yt), 1)
    names = {4: "forward", 1: "intermediate", 3: "neutral"}; pts = []
    for x in pg.get_drawings():                      # black filled markers = driver series
        f, r = x.get("fill"), x["rect"]
        if f != (0, 0, 0) or not 3 < r.width < 6: continue
        cy = (r.y0 + r.y1) / 2
        if 470 < cy < 695:
            dz = float(np.polyval(ax, (r.x0 + r.x1) / 2)) - 26.5
            if abs(dz - 10) < 0.5: continue          # legend markers
            pts.append(("driver_" + names[len(x["items"])], dz, float(np.polyval(ay, cy))))
    return sorted(pts)


def main(pdf):
    pts = extract(pdf)
    if HELD_DIR is not None:
        HELD_DIR.mkdir(parents=True, exist_ok=True)
        with open(HELD_DIR / "r2207_fig3_launch_digitized_HELD.csv", "w") as f:
            w = csv.writer(f); w.writerow(["series", "dz_mm", "launch_deg", "label"])
            for s, dz, l in pts: w.writerow([s, round(dz, 2), round(l, 3), "digitized from figure, approximate; counsel_pending"])
    cen = {s: l for s, dz, l in pts if abs(dz) < 0.3}; g = collections.defaultdict(list)
    for s, dz, l in pts: g[round(dz)].append(l - cen[s])
    with open(OUT, "w") as f:
        w = csv.writer(f); w.writerow(["dz_mm", "launch_change_deg_vs_centre", "n_series", "label", "source", "url"])
        for k in sorted(g): w.writerow([k, round(float(np.mean(g[k])), 2), len(g[k]), "derived from digitized figure, approximate", CIT, URL])


if __name__ == "__main__":
    pdf = sys.argv[1] if len(sys.argv) > 1 else PDF
    if not pdf:
        sys.exit("usage: extract_r2207_fig3.py <pdf_path> (or set R2207_PDF)")
    main(pdf)
