"""Build data/references/goalcond_club_shot_shape_dr_refs.{json,csv}.

Every row: quantity, section, club, nominal, range, unit, label, n, confidence, source_url,
author_date, table_or_page, claim, note. n = number of independent published sources/models;
n=1 rows say 'single published spec (n=1)' in `range` and never present a range.
Per-model (n=1) manufacturer spec rows, per-site turf rows and the TrackMan tour-average rows are held locally pending counsel (not tracked).
All sources opened 2026-10-25 (America/New_York).
"""
import csv, json
from pathlib import Path

N1 = "single published spec (n=1)"
U = dict(
    ping="https://ping.com/en-us/golf-clubs/irons/i230-iron",
    vokey="https://www.titleist.com/golf-clubs/wedges/sm10",
    wishon="https://wishongolf.com/989cla-irons/",
    usga6="https://www.usga.org/equipment-standards/equipment-rules-2019/equipment-rules/part-2-rule-6.html",
    pga="https://support.trackmangolf.com/hc/en-us/article_attachments/7349802113051/PGA_Tour_average.pdf",
    tmftp="https://www.trackman.com/blog/golf/face-to-path",
    tmdp="https://support.trackmangolf.com/hc/en-us/articles/39726207070875-Parameters-D-Plane-Tilt-Tee-to-Green",
    tit="https://www.titleist.com/learning-lab/performance/golf-club-face-angle",
    tut="https://tutelman.com/golf/ballflight/3dlaunch.php",
    r45="https://assets.randa.org/c42c7bf4-dca7-00ea-4f2e-373223f80f76/df3cf55d-4c47-4dbd-8600-3c10d121d248/R45%20-%20Preliminary%20Results%20of%20Turf%20Testing%20at%20Pinehurst.pdf",
    r04="https://assets.randa.org/c42c7bf4-dca7-00ea-4f2e-373223f80f76/2887f275-0659-4812-a1be-30ab00a8472c/R04%20-%20An%20Investigation%20into%20Ball-Turf%20Impact%20Characteristics%20_Master%20Copy_%20_5.pdf",
    biber="https://link.springer.com/article/10.1007/s12283-023-00442-4",
    asgca="https://asgca.org/wp-content/uploads/2016/07/Building-a-Practical-Golf-Facility.pdf",
    brauer="https://golfnewsstoriesonline.com/news/all/golf_news/using_fairway_slopes_for_strategy.html",
    ijgs="https://www.golfsciencejournal.org/article/4980-impact-position-variability-in-golfers-of-differing-skill-level.pdf",
    deleva="https://ebm.ufabc.edu.br/wp-content/uploads/2013/12/Leva-1996.pdf",
    clauser="https://ntrs.nasa.gov/api/citations/19700027497/downloads/19700027497.pdf",
)
AD = dict(
    ping="PING, i230 key specifications page (design specs)", vokey="Titleist, Vokey SM10 specifications page",
    wishon="Wishon Golf, 989CLA irons specifications page",
    usga6="USGA/R&A Equipment Rules 2019, Part 2 Rule 5 (Club Face)",
    pga="TrackMan, PGA Tour Averages PDF (PDF metadata 16 Jul 2020)",
    tmftp="TrackMan blog, What is Face-to-Path", tmdp="TrackMan Help Center, D Plane Tilt (Tee to Green)",
    tit="Titleist Learning Lab, Face Angle (citing TrackMan data)", tut="D. Tutelman, 6 Mar 2007 (after Jorgensen D-plane)",
    r45="USGA, Preliminary Results of Turf Testing at Pinehurst #2, Spring 2005 (R&A Distance Insights R45)",
    r04="A.D.G. Johnson, S.R. Otto, P.C.W. Richardson, R&A, Sep 2008 (R04)",
    biber="S.W. Biber et al., Sports Engineering, 1 Dec 2023 (open access), citing Johnson et al. 2008",
    asgca="ASGCA, Building a Practical Golf Facility (booklet, 2016 upload)", brauer="J.D. Brauer (ASGCA architect), Cybergolf column",
    ijgs="B.L. Langdown, M.W. Bridge, F.-X. Li, Int J Golf Sci 2013;2:142-151",
    deleva="P. de Leva, J Biomech 1996;29(9):1223-1230, Table 4", clauser="C.E. Clauser, J.T. McConville, J.W. Young, AMRL-TR-69-70, 1969 (NASA NTRS copy)",
)
rows = []


def R(section, club, quantity, nominal, rng, unit, label, n, src, page, claim, note="", conf="high"):
    if n == 1 and rng in ("", None):
        rng = N1
    rows.append(dict(section=section, club=club, quantity=quantity, nominal=str(nominal), range=str(rng), unit=unit,
                     label=label, n=n, confidence=conf, source_url=" ; ".join(U[s] for s in src.split("+")),
                     author_date=" ; ".join(AD[s] for s in src.split("+")), table_or_page=page, claim=claim, note=note))

S1 = "1_equipment"
R(S1, "7-iron", "loft (standard)", 32, "31-33", "deg", "manufacturer spec (aggregate)", 2, "wishon+ping", "spec tables, #7",
  "range across 2 manufacturer spec sheets; per-model values held pending counsel", "nominal is midpoint of range (derived)")
R(S1, "7-iron", "lie (standard)", 62.0, "62.0-62.0", "deg", "manufacturer spec (aggregate)", 2, "wishon+ping", "spec tables, #7", "range across 2 manufacturer spec sheets; per-model values held pending counsel")
R(S1, "PW", "loft", 45, "45-46", "deg", "manufacturer spec (aggregate)", 3, "wishon+ping+vokey", "spec tables PW / 46 deg wedge", "range across 3 manufacturer spec sheets; per-model values held pending counsel", "nominal is median (derived)")
R(S1, "PW", "lie", 64.1, "64.0-64.5", "deg", "manufacturer spec (aggregate)", 3, "wishon+ping+vokey", "spec tables", "range across 3 manufacturer spec sheets; per-model values held pending counsel", "nominal is median (derived)")
R(S1, "PW", "length", 35.5, "35.5-35.75", "in", "manufacturer spec (aggregate)", 2, "ping+vokey", "spec tables", "range across 2 manufacturer spec sheets; per-model values held pending counsel")
R(S1, "PW", "swingweight", "D2", "D2-D3", "", "manufacturer spec (aggregate)", 2, "ping+vokey", "spec tables", "range across 2 manufacturer spec sheets; per-model values held pending counsel")
R(S1, "GW", "loft", 50, "50-52", "deg", "manufacturer spec (aggregate)", 3, "wishon+ping+vokey", "spec tables", "range across 3 manufacturer spec sheets; per-model values held pending counsel")
R(S1, "GW", "length", 35.5, "35.5-35.5", "in", "manufacturer spec (aggregate)", 2, "ping+vokey", "spec tables", "range across 2 manufacturer spec sheets; per-model values held pending counsel")
R(S1, "iron", "steel iron shaft mass (stock options)", 106, "93-130", "g", "manufacturer spec (aggregate)", 2, "ping+vokey",
  "shaft tables", "range of listed steel options across 2 manufacturer spec sheets; per-model values held pending counsel", "nominal = approximate median of listed options (derived)", "medium")
for q, v, c in [("groove width max", "0.9", "W must not exceed 0.035 in (0.9 mm), 30-degree method"),
                ("groove spacing min", "1.905", "S >= 3W and >= 0.075 in (1.905 mm)"),
                ("groove depth max", "0.508", "depth <= 0.020 in (0.508 mm)"),
                ("groove area/pitch max (non-driving clubs)", "0.0762", "A/(W+S) <= 0.0030 in^2/in (0.0762 mm^2/mm)"),
                ("groove edge radius (loft >= 25 deg)", "0.254-0.508", "effective radius 0.010-0.020 in"),
                ("face centre decorative square", "9.53", "square sides 0.375 in (9.53 mm)")]:
    R(S1, "iron/wedge", q, v, "rule (n=1)", "mm" if "pitch" not in q else "mm^2/mm", "rule", 1, "usga6", "Part 2 Rule 5c/5d", c)
R(S1, "iron/wedge", "CG location (depth/height)", "not sourced", "", "mm", "gap", 1, "usga6", "-", "no CG data opened for irons/wedges", "GAP -- do not use", "low")

S2 = "2_launch"
# TrackMan PGA/LPGA tour-average rows: held pending counsel (counsel questions section 10); not tracked.
R(S2, "SW", "typical elite landing speed/angle/spin (sand wedge)", "22 m/s, 51 deg, 9060 rpm", "", "", "model (USGA Indoor Test Range simulation)", 1,
  "biber", "Sec 2.1 citing Johnson et al. [19]", "22 m/s, 51 deg, 9060 rpm for a ball launched with a sand wedge", "simulated, not measured; 5-iron: 25 m/s, 44 deg, 4440 rpm")
R(S2, "7-iron/wedge", "amateur launch by handicap / 60-75 mph range", "not sourced", "", "", "gap", 1, "pga", "-",
  "no amateur-by-handicap iron/wedge table opened", "GAP -- below 70 mph only extrapolation possible", "low")

S3 = "3_shot_shape"
R(S3, "all", "face-to-path definition", "face angle - club path", "definition (n=1)", "deg", "spec (definition)", 1, "tmftp", "Technical Definition",
  "FACE ANGLE minus CLUB PATH; positive = face right of path regardless of dexterity")
R(S3, "all", "D-plane tilt = expected spin axis (no gear effect)", "0 when face-to-path = 0", "definition (n=1)", "deg", "spec (definition)", 1, "tmdp",
  "Definition", "expected spin axis disregarding gear effect... if face-to-path is zero, D Plane Tilt will be zero")
R(S3, "iron", "start direction share due to face angle (irons)", 0.75, "", "fraction", "manufacturer claim (citing TrackMan data)", 1, "tit", "body text",
  "on iron shots face angle is approximately 75% responsible; club path 25%", "NOTE: irons are LOWER than driver, not higher", "medium")
R(S3, "driver", "start direction share due to face angle (driver)", 0.85, "", "fraction", "manufacturer claim (citing TrackMan data)", 1, "tit", "body text",
  "driver: club face 85%, path 15%", "", "medium")
R(S3, "all", "total obliqueness", "cos(Phi)=cos(A)cos(L)", "model (n=1)", "deg", "model", 1, "tut", "Finding the effective angle of obliqueness",
  "cos(Phi) = cos(A) cos(L); A face-to-path, L spin loft", "encoded in data/shot_shape_model.py")
R(S3, "all", "spin axis vs face-to-path and spin loft", "tan(axis)=tan(A)/tan(L)", "model (n=1)", "deg", "model", 1, "tut", "Spin section",
  "tan(SpinAngle) = tan(A)/tan(L)", "centered strike; encoded in data/shot_shape_model.py; author reports agreement with TrackMan (anecdotal, 2011)")
R(S3, "all", "horizontal launch", "LAx = A(0.96-0.0071 Phi) + P", "model (n=1)", "deg", "model", 1, "tut", "Summary step (2)-(3)",
  "DAx = A(0.96 - 0.0071 Phi); LAx = DAx + P", "implies face share ~0.78 at Phi 25 deg and ~0.87 at Phi 13 deg (derived; consistent with 75/85 claim)")
R(S3, "iron/wedge", "curvature (lateral yd per deg face-to-path)", "not sourced", "", "yd/deg", "gap", 1, "tmftp", "-",
  "no published measured curvature-per-degree for irons/wedges opened", "GAP -- derive from trajectory sim + spin_axis_deg (label model)", "low")

S4 = "4_domain_rand"
R(S4, "turf", "fairway impact-tester COR (vertical drop)", 0.35, "0.34-0.35 (SD 0.03-0.04)", "", "measured", 3, "r45", "Table 1, 3 fairways",
  "COR 0.34+/-0.04, 0.35+/-0.03, 0.35+/-0.04", "one course, one study; n = fairways; impact-tester plunger, not ball", "medium")
R(S4, "turf", "green impact-tester COR", 0.20, "0.20-0.21 (SD 0.03-0.06)", "", "measured", 3, "r45", "Table 2, 3 greens", "0.20, 0.20, 0.21", "same study", "medium")
R(S4, "turf", "fairway max penetration (impact tester)", 0.47, "0.45-0.48", "in", "measured", 3, "r45", "Table 1", "0.48, 0.47, 0.45 in")
R(S4, "turf", "fairway TruFirm stiffness", 4.2, "2.2-8.2", "MPa", "measured (aggregate)", 5, "r04", "Table 3 fairway rows", "5 fairway sites", "median of 5 (derived); per-site rows held")
R(S4, "turf", "fairway TruFirm resilience", 0.27, "0.18-0.34", "", "measured (aggregate)", 5, "r04", "Table 3", "5 fairway sites")
R(S4, "turf", "fairway TruFirm penetration", 11.5, "8.9-15.4", "mm", "measured (aggregate)", 5, "r04", "Table 3", "5 fairway sites")
R(S4, "turf", "green TruFirm stiffness", 5.5, "2.4-8.7", "MPa", "measured (aggregate)", 6, "r04", "Table 3 green rows", "6 green sites", "median (derived)")
R(S4, "turf", "ball-turf friction coefficient", "not sourced", "", "", "gap", 1, "biber", "Table 3 (image only)",
  "rigid-bounce mu and r fitted from >1000 bounces; values not in HTML text", "GAP -- open Table 3/supplement before using", "low")
R(S4, "terrain", "ideal site slope for golf", "2-10", "guidance (n=1)", "%", "estimate (design guidance)", 1, "asgca", "p.8 Slope", "ideal site has slopes between 2% and 10%", "", "medium")
R(S4, "terrain", "max fairway cross-slope, bent/Bermuda, level zone", 7, "", "%", "estimate (architect opinion)", 1, "brauer", "Steep Cross-Slopes",
  "maximum cross-slope is probably 7 percent on level zones, and 4-5 percent if the fairway also slopes downhill; ~10%+ possible on bluegrass/Zoysia", "", "medium")
R(S4, "setup", "within-golfer variability of stance-midpoint-to-ball distance at impact (skilled)", 10.23, "SD across golfers 2.48; single study (n=1)", "mm", "measured", 1,
  "ijgs", "Table 2", "VE 10.23 +/- 2.48 mm high-skill (n=10 golfers, 10-15 mid-iron shots); whole group 11.01 +/- 3.05",
  "variable error (within-golfer SD-like); measured at impact, not address; ball-position proxy", "medium")
R(S4, "setup", "within-golfer pelvis-to-stance alignment variability", 1.92, "SD 0.43; single study (n=1)", "deg", "measured", 1, "ijgs", "Table 2", "high-skill VE 1.92 +/- 0.43 deg")
for seg, f, m in [("head", 6.68, 6.94), ("trunk", 42.57, 43.46), ("upper arm", 2.55, 2.71), ("forearm", 1.38, 1.62), ("hand", 0.56, 0.61),
                  ("thigh", 14.78, 14.16), ("shank", 4.81, 4.33), ("foot", 1.29, 1.37)]:
    R(S4, "human", f"segment mass fraction, {seg} (male)", m, f"female {f}; single study (n=1)", "% body mass", "derived (adjusted from measured, mean only)", 1, "deleva",
      "Table 4", f"{seg}: F {f}%, M {m}%", "means only; no SD in de Leva")
for seg, mean, sd, cv in [("head", 7.28, 0.59, 8.16), ("trunk", 50.70, 2.06, 4.07), ("upper arm", 2.63, 0.22, "~8.4 (OCR partial)"), ("thigh", 10.27, 0.82, 8.00),
                          ("calf", 4.35, 0.36, 8.38), ("foot", 1.47, 0.10, 6.92), ("total leg", 16.10, 0.94, 5.84), ("head+trunk", 58.01, 2.00, 3.45)]:
    R(S4, "human", f"segment mass fraction variability, {seg}", mean, f"SD {sd}; CV {cv}%; single study (n=1)", "% body mass", "measured (13 male cadavers)", 1, "clauser",
      "Tables 9-22 'Ratio of the weight of a segment as a percent of total body weight'", f"mean {mean}, SD {sd}, CV {cv}",
      "values read from OCR of scanned report; SD/CV cross-checked (SD/mean = CV); verify against scan before tight use", "medium")

out = Path(__file__).resolve().parent / "references"
doc = dict(generated="2026-10-25 (America/New_York)", schema="each row: label, n, source_url required; n=1 -> 'single published spec (n=1)' or '(n=1)' in range",
           held_locally="held pending counsel, not tracked: per-model (n=1) manufacturer spec rows, per-site turf rows, TrackMan tour-average rows", rows=rows)
(out / "goalcond_club_shot_shape_dr_refs.json").write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
with open(out / "goalcond_club_shot_shape_dr_refs.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]))
    w.writeheader(); w.writerows(rows)
print(len(rows), "rows")
