"""Build data/references/amateur_launch_wedge_cg_refs.{json,csv} (sibling of goalcond refs; same row schema).

Committed: rules-body report aggregates (R&A/USGA R22-01, amateur CONGU categories 1-4 only; group means/SD published as text tables) and
patent / manufacturer text claims (aggregated, no model names). Vendor tables (TrackMan amateur averages,
component-supplier head-weight charts) are HELD at <local-path>/held_research_bands/goalcond/.
Sources opened 2026-10-25 (America/New_York). Nothing digitized from charts.
HELD at port (Repo Agent): R22-01 professional-group rows (tour radar data) and the single patent test example.
"""
import csv, json
from pathlib import Path

N1 = "single published spec (n=1)"
R2201 = "https://www.usga.org/content/dam/usga/pdf/Equipment/R22-01%20Launch%20conditions%20of%20male%20and%20female%20golfers%20of%20different%20skill%20levels.pdf"
R2201_AD = "R&A Rules Ltd / USGA, R22-01 'Launch conditions of male and female golfers of different skill levels', May 2019"
U = dict(
    acu="https://patents.google.com/patent/US9211450B2/en",
    endo="https://www.freepatentsonline.com/y2009/0176596.html",
    cutter="https://www.playcutter.com/pages/moment-of-inertia-moi-and-center-of-gravity-cg",
    drv="https://github.com/masonwyatt23/humanoid-golf-sim/blob/main/data/references/goalcond_club_shot_shape_dr_refs.json",
)
AD = dict(acu="US 9,211,450 B2 (Acushnet), granted 15 Dec 2015", endo="US 2009/0176596 A1 (K.K. Endo Seisakusho), 9 Jul 2009",
          cutter="Cutter Golf technical page (manufacturer's own measurements)", drv="this repo, goalcond_club_shot_shape_dr_refs.json (reference)")
rows = []


def R(section, club, quantity, nominal, rng, unit, label, n, url, ad, page, claim, note="", conf="high"):
    if n == 1 and not rng:
        rng = N1
    rows.append(dict(section=section, club=club, quantity=quantity, nominal=str(nominal), range=str(rng), unit=unit, label=label,
                     n=n, confidence=conf, source_url=url, author_date=ad, table_or_page=page, claim=claim, note=note))


# R22-01 Tables 5-7 (group mean, SD). Groups 1-4 = CONGU categories 1-4 (group 0 = professional/tour radar data HELD, values not in git).
CAT = {0: "professional", 1: "CONGU cat 1 (<=5.4)", 2: "CONGU cat 2 (5.5-12.4)", 3: "CONGU cat 3 (12.5-20.4)", 4: "CONGU cat 4 (20.5-28)"}
T = {  # (gender, club): {group: (n_shots, CHS, CHS_sd, BS, BS_sd, LA, LA_sd, spin, spin_sd, carry, carry_sd, attack, eff_loft)}
 ("female", "6-iron"): {1: (108, 74.7, 4.1, 102.8, 8.2, 14.2, 2.9, 4685, 955, 132.0, 23.4, -2.9, 20.9),
                        2: (148, 64.7, 11.1, 90.5, 15.1, 15.1, 3.2, 4096, 1252, 106.7, 32.7, -0.5, 22.9), 3: (183, 56.5, 4.6, 77.6, 9.5, 13.7, 5.2, 3712, 1230, 75.1, 29.3, -1.8, 21.9),
                        4: (237, 52.6, 7.2, 71.2, 13.5, 14.3, 4.9, 3460, 1565, 64.5, 32.5, -0.4, 21.8)},
 ("female", "driver"): {1: (364, 86.3, 5.7, 122.2, 10.6, 14.1, 2.9, 3067, 1057, 173.6, 25.4, 0.5, 12.7),
                        2: (236, 77.0, 6.5, 109.6, 9.8, 13.2, 4.6, 2784, 983, 135.8, 25.9, 1.4, 13.4), 3: (243, 68.4, 5.2, 97.0, 9.1, 11.3, 3.9, 2671, 909, 100.1, 29.3, -0.2, 11.2),
                        4: (296, 62.6, 8.5, 86.8, 13.9, 10.4, 5.1, 3095, 1392, 76.5, 37.5, -1.0, 12.5)},
 ("male", "6-iron"): {1: (1341, 85.7, 5.6, 120.2, 9.9, 12.4, 3.0, 5171, 925, 164.4, 23.1, -4.5, 19.3),
                      2: (1010, 81.0, 8.1, 112.2, 13.2, 12.1, 4.0, 4835, 1191, 145.5, 31.5, -3.7, 19.7), 3: (321, 77.4, 9.1, 105.9, 15.0, 12.5, 4.7, 4354, 1333, 129.9, 39.3, -2.0, 21.2),
                      4: (196, 78.5, 8.9, 103.8, 19.2, 11.7, 5.1, 4942, 1492, 119.2, 47.6, -3.1, 19.8)},
 ("male", "driver"): {1: (433, 100.5, 6.8, 143.8, 9.9, 11.4, 2.8, 3274, 780, 215.1, 23.4, 0.4, 13.0),
                      2: (400, 91.4, 9.2, 130.6, 13.1, 10.7, 3.6, 3313, 1140, 183.6, 34.5, 0.7, 13.2), 3: (164, 85.8, 9.5, 121.9, 15.3, 12.2, 4.9, 3202, 1250, 163.3, 33.6, 0.9, 12.0),
                      4: (101, 89.6, 9.9, 125.6, 16.6, 10.2, 4.8, 3839, 1309, 163.1, 49.7, -0.7, 11.0)},
}
S = "A_amateur_launch_by_handicap"
HELD = []   # rows built but not committed (copied to <local-path>/held_research_bands/amateur/, pending counsel)
for (g, club), groups in T.items():
    for k, v in groups.items():
        if k == 0:   # HELD: professional group = tour radar data (no TrackMan/tour averages in git)
            continue
        ns, chs, chs_sd, bs, bs_sd, la, la_sd, sp, sp_sd, ca, ca_sd, aoa, eloft = v
        for q, m, sd, u, tab in [("clubhead speed", chs, chs_sd, "mph", "Table 5"), ("ball speed", bs, bs_sd, "mph", "Table 6"),
                                 ("launch angle", la, la_sd, "deg", "Table 6"), ("spin rate", sp, sp_sd, "rpm", "Table 6"),
                                 ("carry", ca, ca_sd, "yd", "Table 7"), ("attack angle", aoa, None, "deg", "Table 5"), ("effective loft", eloft, None, "deg", "Table 5")]:
            if m is None:
                continue
            R(S, club, f"{g} {CAT[k]} {q}", m, (f"SD {sd} across shots; " if sd is not None else "") + f"{ns} shots; one collated report (n=1)", u,
              "measured (rules-body collated aggregate)", 1, R2201, R2201_AD, tab, f"{g} {club} group {k}: mean {m}" + (f" SD {sd}" if sd is not None else ""),
              "6-iron is the only iron in this report (7-iron excluded there); professional male driver group is PGA Tour radar data" if club == "6-iron" or k == 0 else "",
              "high" if ns >= 150 else "medium")
R(S, "driver/6-iron", "finding: launch angle and spin vs handicap", "no consistent relationship", "one collated report (n=1)", "", "measured (report conclusion)", 1, R2201, R2201_AD,
  "Sec 3-4", "there does not appear to be a strong relationship between handicap and launch angle or spin", "clubhead and ball speed do fall with handicap")
pass  # HELD: patent single test example (one shot, n=1, vendor patent) not committed
if False: R(S, "wedge (54 deg)", "single test example (held)", "held", "", "", "measured? (patent example, conditions unstated)", 1,
  U["acu"], AD["acu"], "description, Performance Ratio example", "held",
  "golfer/robot, speed and handicap not stated", "low")
for club in ("PW", "GW", "SW", "LW"):
    R(S, club, "amateur launch/spin by handicap or club speed", "not sourced", "", "", "gap", 1, R2201, R2201_AD, "-", "no rules-body or peer-reviewed wedge launch-by-handicap numbers found",
      "GAP -- R22-01 covers driver and 6-iron only", "low")
R(S, "7-iron", "amateur launch/spin by handicap", "not sourced", "", "", "gap", 1, R2201, R2201_AD, "-", "R22-01 excluded its 7-iron shots (cat 1 females only)", "GAP -- use 6-iron rows as nearest", "low")

W = "B_wedge_cg_mass_moi"
R(W, "wedge", "CG height above ground, conventional wedges", 19.8, "19.3-20.4 (3 statements: 19.8, 20.4, 19.34 avg of 'several')", "mm", "manufacturer/patent claim (aggregate)", 2,
  U["endo"] + " ; " + U["cutter"], AD["endo"] + " ; " + AD["cutter"], "Endo detailed description; Cutter CG findings",
  "conventional ones ... in the order of 19.8 mm or 20.4 mm; traditional wedges measured averaged 19.34 mm (from leading edge)", "reference planes differ (sole plane vs leading edge)", "medium")
R(W, "wedge", "CG height, prior-art statement (patent)", ">20", "patent text (n=1): prior art >20, e.g. 21-23", "mm", "patent claim", 1, U["acu"], AD["acu"], "Background/FIG 1", "d1 ... may generally be greater than 20 mm")
R(W, "wedge", "CG height, claimed low-CG designs", 18, "16-20 (claim 1); preferred about 18; one patent (n=1)", "mm", "patent claim", 1, U["acu"], AD["acu"], "claim 1; d15", "between about 16 mm and about 20 mm away from said ground")
R(W, "wedge", "CG height, claimed high-CG design", 23, ">=21.335 (claim 1); example 23; one patent (n=1)", "mm", "patent claim", 1, U["endo"], AD["endo"], "claim 1; description", "at least 21.335 mm ... may be set at 23 mm")
R(W, "wedge", "typical impact height above ground", 15, "10-20 (patent text, n=1)", "mm", "patent claim", 1, U["acu"], AD["acu"], "FIG 2 description", "impact point ... 10 mm to 20 mm from ground ... most preferably 15 mm")
R(W, "wedge", "CG depth behind face", "not sourced", "", "mm", "gap", 1, U["endo"], AD["endo"], "-", "only qualitative ('anterior to the face surface' in claim)", "GAP", "low")
R(W, "SW", "MOI vertical axis (Izz), conventional sand wedges", 2603, "average of several heads (count not given); one source (n=1)", "g*cm^2", "manufacturer claim (own measurement)", 1,
  U["cutter"], AD["cutter"], "IZZ MOI findings", "several traditional sand wedges with an average IZZ MOI of 2603", "", "medium")
R(W, "wedge", "MOI about heel-toe x-axis, claimed", 1200, ">1200 (claim: >120 kg*mm^2; >1290 preferred); one patent (n=1)", "g*cm^2", "patent claim", 1, U["acu"], AD["acu"], "claims 1-3",
  "moment of inertia about an x-axis greater than about 120 kg*mm2", "x-axis = heel-to-toe (face up/down rotation)")
R(W, "wedge", "toe height, traditional wedges", 61.2, "one source (n=1)", "mm", "manufacturer claim", 1, U["cutter"], AD["cutter"], "CG findings", "toe height on traditionally shaped wedges peaks around 61.2mm")
for club in ("PW", "GW", "SW", "LW"):
    R(W, club, "head mass (committed source)", "not sourced", "", "g", "gap", 1, U["cutter"], AD["cutter"], "-", "only clubmaker/supplier tables (held) give wedge head mass", "GAP in git; held value exists", "low")
for club in ("PW", "GW", "LW"):
    R(W, club, "MOI (Izz/Ixx) per club", "not sourced", "", "g*cm^2", "gap", 1, U["acu"], AD["acu"], "-", "no per-loft wedge MOI opened", "GAP", "low")

out = Path(__file__).resolve().parent / "references"
doc = dict(generated="2026-10-25 (America/New_York)", schema="same as goalcond_club_shot_shape_dr_refs", held_locally="<local-path>/held_research_bands/goalcond/", rows=rows)
(out / "amateur_launch_wedge_cg_refs.json").write_text(json.dumps(doc, indent=1) + "\n", encoding="utf-8")
with open(out / "amateur_launch_wedge_cg_refs.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(len(rows), "rows")
