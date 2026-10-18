"""Generate data/references/kinematic_sequence_torque_reference.json (published literature only)."""
import json, os, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT)
from data import kinematic_sequence_torque_reference as K
from data import speed_gap_100_120 as sg

# tag legend: F=fetched full text / table read; X=search-result excerpt of body text; A=abstract only; S=search synthesis only (unverified)
SRC = {
 "cheetham2008": dict(cite="Cheetham PJ, Rose GA, Hinrichs RN, Neal RJ, Mottram RE, Hurrion PD, Vint PF. Comparison of kinematic sequence parameters between amateur and professional golfers. In: Crews D, Lutz R (eds) Science and Golf V, Mesa AZ: Energy Media/LPGA, 2008, 30-36",
   url="http://www.waddengolfacademy.com/biomechanics/Cheetham%20Rose%20Neal%20Comparison_of_Kinematic_Sequence.pdf", tag="F", note="Table 1 values re-used from docs/SPEED_GAP_100_120_SPEC.md (fetched there). Year 2008 confirmed by the reference list of Parker 2018."),
 "parker2018": dict(cite="Parker J, Hellstrom J, Olsson MC. Relationships between golf swing kinematics and driver performance in elite golfers. (Halmstad Univ.; accepted ms, c.2018)",
   url="https://www.diva-portal.org/smash/get/diva2:1242118/FULLTEXT01.pdf", tag="F", note="15 elite (10 M, 5 F, age 22, hcp <= -2), electromagnetic 240 Hz, driver, FlightScope CHS 46.0 +- 4.3 m/s; resultant (3-axis) segment speeds"),
 "myers2008": dict(cite="Myers J, Lephart S, Tsai Y-S, Sell T, Smoliga J, Jolly J. The role of upper torso and pelvis rotation in driving performance during the golf swing. J Sports Sci 2008;26(2):181-188",
   url="https://exss.unc.edu/wp-content/uploads/sites/779/2013/01/Myers_jss_2008.pdf", tag="F", note="100 recreational golfers (hcp 8.1+-7.3), driver, 200 Hz optical; groups by BALL velocity (low/med/high); CHS not measured"),
 "nesbit2005a": dict(cite="Nesbit SM, Serrano M. Work and power analysis of the golf swing. J Sports Sci Med 2005;4:520-533",
   url="https://www.jssm.org/volume04/iss4/cap/jssm-04-520.pdf", tag="F", note="4 amateurs (scratch, 5, 13 hcp male, 18 hcp female), single swings, driver; inverse-dynamics model; Tables 2-3"),
 "nesbit2005b": dict(cite="Nesbit SM. A three dimensional kinematic and kinetic study of the golf swing. J Sports Sci Med 2005;4:499-519",
   url="https://www.jssm.org/volume04/iss4/cap/jssm-04-499.pdf", tag="F", note="84 male + 1 female amateurs (mean hcp 5.8); Table 3. Stated n=84 stats but several ranges equal the 4-subject subset: ambiguous"),
 "hume2005": dict(cite="Hume PA, Keogh J, Reid D. The role of biomechanics in maximising distance and accuracy of golf shots. Sports Med 2005;35(5):429-449",
   url="http://www.waddengolfacademy.com/biomechanics/Hume%20Keogh%20Role%20of%20golf_biomechanics.pdf", tag="F", note="Review, full text read (upgrades the 'snippet only' tag in the speed-gap spec). Numbers are secondary (cites Geisler 2001 textbook, Barrentine 1994, Milburn 1982, McTeigue 1994)."),
 "cheetham2001": dict(cite="Cheetham PJ, Martin PE, Mottram RE, St Laurent BF. The importance of stretching the X-factor in the downswing of golf: the X-factor stretch. In: Thomas PR (ed) Optimising performance in golf, Brisbane: Australian Academic Press, 2001, 192-199",
   url="https://www.philcheetham.com/wp-content/uploads/2011/11/Stretching-the-X-Factor-Paper.pdf", tag="F", note="10 skilled (8 pros + 1 long-drive champion + 1 collegiate) vs 9 hcp>=15; 5-iron; 30 Hz, T3/pelvis sensors"),
 "zheng2008a": dict(cite="Zheng N, Barrentine SW, Fleisig GS, Andrews JR. Kinematic analysis of swing in pro and amateur golfers. Int J Sports Med 2008;29(6):487-493",
   url="https://doi.org/10.1055/s-2007-989229", tag="A", note="18 pros, 18 low, 18 mid, 18 high hcp, 240 fps optical; abstract values only"),
 "zheng2008b": dict(cite="Zheng N, Barrentine SW, Fleisig GS, Andrews JR. Swing kinematics for male and female pro golfers. Int J Sports Med 2008;29:965-970",
   url="https://pubmed.ncbi.nlm.nih.gov/18563677/", tag="A", note="25 PGA + 25 LPGA; abstract only"),
 "worsfold2007": dict(cite="Worsfold P, Smith NA, Dyson RJ. A comparison of golf shoe designs highlights greater ground reaction forces with shorter irons. J Sports Sci Med 2007;6:484-489 (PMC3794489)",
   url="https://pmc.ncbi.nlm.nih.gov/articles/PMC3794489/", tag="A", note="24 golfers, natural-turf force plates; abstract values"),
 "worsfold2008": dict(cite="Worsfold P, Smith NA, Dyson RJ. Low handicap golfers generate more torque at the shoe-natural grass interface when using a driver. J Sports Sci Med 2008;7:... (PMC3761900)",
   url="https://pmc.ncbi.nlm.nih.gov/articles/PMC3761900/", tag="X", note="search excerpt of body text, includes the Barrentine 1994 torque comparison"),
 "han2019": dict(cite="Han KH, Como C, Kim J, Lee S, Kim J, Kwon Y-H, et al. Effects of the golfer-ground interaction on clubhead speed in skilled male golfers. Sports Biomech 2019",
   url="https://www.tandfonline.com/doi/full/10.1080/14763141.2019.1586983", tag="A", note="63 skilled (hcp<=3); the 1.12 BW driver lead-foot peak vertical GRF comes only from a search summary of a 2023 meta-analysis (Appl Sci 13:7209), NOT read: UNVERIFIED"),
 "hirano2023": dict(cite="Hirano T, Kashiwagi Y, Shimatani S, Tsunoda N, Funato K. Ground reaction forces during the full driver shot of a Japanese male professional golfer: a case study. Kokushikan Soc Sport Sci 2023;23:17-22",
   url="https://kokushikan.repo.nii.ac.jp/records/2000021", tag="A", note="n=1 pro (+1 collegiate); abstract gives front-leg peak vertical GRF 1.51 BW; CHS not in abstract"),
 "okuda2010": dict(cite="Okuda I, Gribble P, Armstrong C. Trunk rotation and weight transfer patterns between skilled and low skilled golfers. J Sports Sci Med 2010;9:127-133",
   url="https://www.jssm.org/volume09/iss1/cap/jssm-09-127.pdf", tag="X", note="13 skilled (hcp 0.8) vs 17 low skilled (hcp 30.8); force plates; excerpt"),
 "sprigings2000": dict(cite="Sprigings EJ, Neal RJ. An insight into the importance of wrist torque in driving the golfball: a simulation study. J Appl Biomech 2000;16(4):356-366",
   url="https://doi.org/10.1123/jab.16.4.356", tag="S", note="3-segment simulation; torque limits and 9% wrist-torque effect from a search summary only (PDF fetch timed out): UNVERIFIED"),
 "nealwilson1985": dict(cite="Neal RJ, Wilson BD. 3D kinematics and kinetics of the golf swing. Int J Sport Biomech 1985;1(3):221-232",
   url="https://doi.org/10.1123/ijsb.1.3.221", tag="S", note="not read; Nesbit 2005b states club-level torque agreement; hip/shoulder peak torques were NOT reported there"),
 "kwon2013": dict(cite="Kwon Y-H, Han KH, Como C, Lee S, Singhal K. Validity of the X-factor computation methods and relationship between the X-factor parameters and clubhead velocity in skilled golfers. Sports Biomech 2013;12(3):231-246",
   url="https://pubmed.ncbi.nlm.nih.gov/24245049/", tag="S", note="18 skilled males; search summary only; X-factor values are method-dependent and not correlated with CHS there"),
 "holt2013": dict(cite="Holt LE, Holt J. Long driving: the Sadlowski case. Int J Golf Sci 2013;2:86-91",
   url="https://www.golfsciencejournal.org/article/4958-long-driving-the-sadlowski-case.pdf", tag="F", note="Qualitative case note; claims CHS >150 mph / 400 yd drives for one long-drive champion with NO measurement data: not used for numbers"),
 "tinmark2007": dict(cite="Tinmark F. Analysis of elite golfers' kinematic sequence in full and partial shots. GIH master thesis 17:2007 (later Tinmark, Hellstrom, Halvorsen, Thorstensson, Sports Biomech 2010;9:236-244)",
   url="https://www.diva-portal.org/smash/get/diva2:25224/FULLTEXT01.pdf", tag="F", note="47 skilled (11 pro, 23 M amateur, 13 F amateur); results only in figures (no numeric table in the text)"),
}

def row(src, pop, n, chs, seg, val, sd=None, unit="deg/s", tag="measured", note=""):
    return dict(source=src, population=pop, n=n, chs_mph=chs, segment=seg, value=val, sd=sd, unit=unit, tag=tag, note=note)

ms = K.MS_TO_MPH
PEAK = [
 row("cheetham2008","amateur",19,88,"pelvis",395,tag="measured"), row("cheetham2008","amateur",19,88,"thorax",583),
 row("cheetham2008","amateur",19,88,"lead_arm",763), row("cheetham2008","amateur",19,88,"club",1790),
 row("cheetham2008","pro",19,109,"pelvis",477), row("cheetham2008","pro",19,109,"thorax",727),
 row("cheetham2008","pro",19,109,"lead_arm",980), row("cheetham2008","pro",19,109,"club",2254),
 row("parker2018","elite_amateur",15,round(46.1*ms,1),"pelvis",475.4,75.0,note="resultant 3-axis speed; mixed M/F"),
 row("parker2018","elite_amateur",15,round(46.1*ms,1),"thorax",708.3,70.2),
 row("parker2018","elite_amateur",15,round(46.1*ms,1),"lead_arm",1054.7,149.2,note="humerus rel. to thorax"),
 row("myers2008","recreational_low_ball_speed",21,None,"pelvis",357.6,58.3,note="ball speed 55.7 m/s; CHS est ~86 mph if smash 1.45 (assumption)"),
 row("myers2008","recreational_mid_ball_speed",65,None,"pelvis",410.4,66.4,note="ball 65.6 m/s; CHS est ~101 mph (smash 1.45 assumed)"),
 row("myers2008","recreational_high_ball_speed",14,None,"pelvis",433.6,90.9,note="ball 75.4 m/s; CHS est ~116 mph (smash 1.45 assumed)"),
 row("myers2008","recreational_low_ball_speed",21,None,"thorax",591.2,66.8), row("myers2008","recreational_mid_ball_speed",65,None,"thorax",675.1,84.4),
 row("myers2008","recreational_high_ball_speed",14,None,"thorax",766.6,73.0),
 row("hume2005","pro",None,None,"pelvis",498,note="secondary (Geisler 2001); CHS and n not given",tag="measured-secondary"),
 row("hume2005","pro",None,None,"thorax",723,note="shoulder",tag="measured-secondary"),
 row("hume2005","pro",None,None,"lead_arm",1165,tag="measured-secondary"), row("hume2005","pro",None,None,"club",2090,tag="measured-secondary"),
 row("zheng2008a","pro",18,None,"club",2413,442,note="club shaft peak angular velocity; CHS not in abstract"),
 row("zheng2008a","pro",18,None,"right_elbow_extension",854,150),
 row("zheng2008a","pro",18,None,"right_wrist",1183,299), row("zheng2008a","pro",18,None,"left_wrist",1085,338),
 row("zheng2008b","pro_female_LPGA",25,None,"club",2049,512), row("zheng2008b","pro_female_LPGA",25,None,"right_wrist",864,198),
 row("zheng2008b","pro_female_LPGA",25,None,"left_wrist",816,186), row("zheng2008b","pro_female_LPGA",25,None,"right_elbow_extension",705,109),
 row("nesbit2005b","amateur",84,round(46.37*ms,1),"club",1756,123,note="alpha (swing-plane) club angular velocity; range 1600-1910 over CHS 39-52 m/s: barely scales with CHS; definition differs from Cheetham"),
]
TIMING = [
 dict(source="cheetham2008",population="pro",pelvis_peak_ms_before_impact=87,thorax=68,lead_arm=65,club=0,note="SD 19/14/8; every pro pelvis decelerates before impact",tag="measured"),
 dict(source="cheetham2008",population="amateur",pelvis_peak_ms_before_impact=78,thorax=59,lead_arm=64,club=0,note="mean order pelvis, arm, thorax",tag="measured"),
 dict(source="tinmark2007",population="pro and amateur, M and F",note="peak-speed order pelvis -> upper torso -> hand at every condition (wedge..driver) and group; timing not significantly affected by group or expertise; numeric % of downswing only in a figure",tag="measured-qualitative"),
 dict(source="nesbit2005a",population="amateur (4)",note="peak joint work occurs distal->proximal (hips/spine first, wrists last); total body work peaks ~4 ms before impact; wrist torques cross zero before impact; max club swing angular velocity ~25 ms before impact (scratch) and -20 to +10 ms (others)",tag="measured-qualitative"),
 dict(source="hume2005",population="elite",note="downswing 0.23 s, backswing 0.82 s (Cochran & Stobbs 1968 via review); hip-first transition",tag="measured-secondary"),
 dict(source="okuda2010",population="skilled vs low skilled",note="skilled start pelvis rotation and weight shift to the lead foot earlier in the downswing",tag="measured-qualitative"),
]
XF = [
 dict(source="parker2018",population="elite_amateur",n=15,x_factor_top_deg=54.9,sd=7.9,x_factor_stretch_deg=2.9,stretch_sd=3.4,note="joint-coordinate method; X-factor at top NEGATIVELY associated with CHS (beta -0.24); stretch positively (beta 0.27)",tag="measured"),
 dict(source="myers2008",population="recreational_by_ball_speed",n="21/65/14",x_factor_top_deg=[44.2,49.5,59.1],x_factor_max_deg=[45.6,51.7,61.8],x_factor_stretch_deg=[1.4,2.2,2.7],max_sep_velocity_deg_s=[278.1,311.8,389.6],note="low/med/high ball speed; stretch = max minus top (derived)",tag="measured"),
 dict(source="cheetham2001",population="skilled vs hcp>=15",n="10 vs 9",x_factor_stretch_pct=[19,13],note="5-iron, 30 Hz; top-of-backswing X-factor difference n.s.; one skilled player 60.1 -> 73.5 deg (+13.4)",tag="measured"),
 dict(source="hume2005",population="PGA / senior PGA / amateur / long vs short hitters",x_factor_deg={"mclean_long_hitters":38,"mclean_short_hitters":24,"mcteigue_pga":32,"mcteigue_senior_pga":29,"mcteigue_amateur_hcp17":34,"burden_amateur_hcp7":70},note="method-dependent; Burden et al. values larger",tag="measured-secondary"),
 dict(source="kwon2013",population="skilled males",n=18,note="three X-factor computation methods give significantly different values; X-factor parameters not directly correlated with CHS",tag="synthesis-only"),
]
GRF = [
 dict(source="worsfold2007",population="golfers (hcp 0-14), natural turf",n=24,club="driver",metric="peak vertical force BW",back_foot=0.49,front_foot=0.84,tag="measured",note="Fz range (peak-to-trough) 0.33 back / 0.83 front BW in metal spikes; much lower than force-plate-on-lab-floor values"),
 dict(source="hume2005",population="pro/amateur review (Barrentine 1994 et al.)",club="driver/5-iron",metric="peak GRF vertical / AP / ML in BW",vertical=[1.6,2.0],ap=[0.4,0.6],ml=[0.2,0.3],tag="measured-secondary",note="unclear whether per foot or summed; conflicts with Worsfold (0.84) and Han (1.12)"),
 dict(source="hume2005",population="Barrentine 1994",metric="left (lead) leg 0.02 s after impact",lateral_N=133,vertical_N=950,torque_Nm=23,right_knee_ant_shear_pct_bw=10,left_leg_vertical_comp_pct_bw=80,tag="measured-secondary"),
 dict(source="han2019",population="skilled hcp<=3",n=63,club="driver",metric="peak lead-foot vertical GRF BW",value=1.12,sd=0.22,tag="synthesis-only",note="from search summary of a meta-analysis; unverified; peak lead-foot force and trail-foot F/B force correlate with CHS"),
 dict(source="hirano2023",population="1 Japanese pro (case)",n=1,club="driver",metric="peak front-leg vertical GRF BW",value=1.51,tag="abstract",note="CHS not in abstract"),
 dict(source="okuda2010",population="skilled and low skilled",club="driver",metric="peak lead-foot vertical GRF",value=">1 BW in both groups, no group difference; timing differs (skilled earlier)",tag="measured"),
 dict(source="hume2005",population="elite",metric="weight distribution",value="50-60% on back foot at set-up; lead leg ~40% BW at top; transfer to lead foot during downswing",tag="measured-secondary"),
 dict(source="worsfold2008",population="golfers on natural grass",metric="foot torque about vertical axis (N*m)",front_foot_Tzmax=[17,19],back_foot_Tzmax=[6,7],front_foot_torque_generated=40,back_foot_torque_generated=[10,16],barrentine1994_pga_lowhcp={"back":[17,18],"front":[23,26]},tag="measured",note="excerpt; Barrentine numbers quoted by Worsfold"),
]
UNVERIFIED = [
 "All values above ~116 mph club speed (130/132 mph rows) are extrapolated beyond every published group; the highest measured CHS in a retrieved study with segment data is Cheetham pros at 109 mph, and Nesbit's fastest swing is 116.3 mph.",
 "No retrieved study reports kinematic sequence, GRF or joint torque for a measured 120+ mph (long-drive) population. Holt & Holt 2013 only asserts >150 mph for one player without data.",
 "Joint work (Nesbit & Serrano) is a single-swing, 4-subject, model-derived quantity; spherical-joint work is mapped onto the env's single-axis joints crudely (an upper bound on the yaw part).",
 "Work scales with CHS as v^2.55 (least squares) from four swings of mixed skill and one female; the downswing duration is held at 0.23 s although faster swings are probably shorter (would raise power).",
 "Peak/average power ratio 2.5 comes from Nesbit's club model only (peak 3875 W vs 355 J / 0.23 s); not measured for body joints.",
 "Peak lumbar, hip and shoulder torques (N*m) per swing were NOT found in any retrieved source; only joint work (J) and the grip/hand torque at the club (Nesbit), plus simulation limits (Sprigings & Neal, summary only).",
 "GRF magnitudes differ by up to 2x between studies (surface, shoes, definition of peak, per-foot vs summed); no single target is defensible.",
 "Lynn, Ball & Best, Wallace/Koenig/Mann (primary), Ae, Hellstrom 2009 and TPI items requested were not retrieved in usable numeric form; only qualitative statements (Koenig/Wallace/Ball via the Hume review, Okuda) are used.",
 "Han 2019 1.12 BW and the Sprigings & Neal limits (180/120/60 N*m, 9%) come from search summaries, not read primary text.",
]
CHS_LIST = [90, 100, 110, 120, 132]
SCALING = []
for v in CHS_LIST:
    SCALING.append(dict(chs_mph=v, tag=K.tag_for_chs(v)+("; below Nesbit range" if v < 94.2 else ""),
        segment_peak_deg_s={s: round(sg.target_deg_s(s, v), 1) for s in sg.ORDER},
        segment_peak_tag="interpolated" if 88 <= v <= 109 else "extrapolated",
        total_body_work_J=round(K.total_work_J(v), 1),
        group_work_J={g: round(K.group_work_J(g, v), 1) for g in K.GROUPS},
        avg_power_W={g: round(K.avg_power_W(g, v), 0) for g in K.GROUPS if g != "legs"},
        grip_torque_Nm=round(K.grip_torque_Nm(v), 1),
        club_peak_power_W=round(K.NESBIT_CHS_PEAK_POWER[-1][1]*(K.mph_to_ms(v)/K.NESBIT_CHS_MS)**K.POWER_EXPONENT, 0),
        pro_joint_speed_scaled_deg_s={j: round(x*v/109.0, 0) for j, x in (("right_wrist",1183),("left_wrist",1085),("right_elbow_extension",854))},
        pro_joint_speed_note="Zheng 2008 pro value scaled linearly by v/109 mph: Zheng CHS not reported, 109 mph is an ASSUMPTION"))
FEAS = {}
for tier in ("stock","elite"):
    FEAS[tier] = {str(v): K.g1_feasibility(v, tier) for v in (100, 120, 132)}
# speed feasibility vs rated speed
spd = {}
for v in (100,120,132):
    spd[str(v)] = {
      "pelvis_yaw_rad_s": round(sg.target_deg_s("pelvis", v)*3.14159265/180, 2),
      "lead_arm_rad_s": round(sg.target_deg_s("lead_arm", v)*3.14159265/180, 2),
      "wrist_rel_club_minus_arm_rad_s": round((sg.target_deg_s("club", v)-sg.target_deg_s("lead_arm", v))*3.14159265/180, 2),
      "right_wrist_pro_scaled_rad_s": round(1183*v/109.0*3.14159265/180, 2)}
SIMPLE = {}
for name in ("v3","v4_power"):
    SIMPLE[name] = {"actuator_peak_torque_Nm": K.SIMPLE_ENV_TORQUE[name], "damping_Nms_per_rad": K.SIMPLE_ENV_DAMPING[name],
        "wrist_drag_at_24.5rad_s_Nm": round(K.SIMPLE_ENV_DAMPING[name]["right_wrist"]*24.5,1)}
out = {
 "_meta": dict(title="Published kinematic-sequence, joint work/torque and GRF reference for the humanoid golf env, with actuator feasibility",
   contains_instagram_or_mason_derived_data=False, generated="2026-10-17 America/New_York", branch="kseq-reference (from speed-gap-public)",
   status="published-only; model-only extrapolations above 116 mph; unverified where tagged",
   tag_legend=dict(F="full text/table read", X="search excerpt of body text", A="abstract only", S="search synthesis only (unverified)",
     measured="value printed in the cited source", **{"measured-secondary":"printed in a review citing another source","measured-qualitative":"qualitative statement","interpolated":"between published groups","extrapolated":"beyond all published groups","derived":"computed here from published numbers + stated assumptions","synthesis-only":"unread primary; from search summary"})),
 "sources": SRC,
 "populations": dict(amateur="Cheetham 88 mph; Myers recreational; Nesbit 84/4 amateurs; Zheng mid/high hcp (not extracted)",
   pro_elite="Cheetham tour pros 109 mph; Parker elite 46.1 m/s (103 mph); Zheng PGA/LPGA; Hume/Geisler pro means",
   long_drive=dict(status="NO numeric biomechanics found", note="Cheetham 2001 included one long-drive champion inside a 10-player skilled group (not separable). Holt 2013 is qualitative.")),
 "kinematic_sequence": dict(peak_angular_speed=PEAK, timing=TIMING),
 "x_factor": XF,
 "ground_reaction_forces": GRF,
 "joint_work_power": dict(
   source="nesbit2005a Table 2 and 3 (scratch male, CHS 52.0 m/s = 116.3 mph, top of backswing -> impact)",
   joint_work_J=K.NESBIT_WORK_J, total_body_work_J=K.NESBIT_TOTAL_J,
   group_share_pct={"hips+spine(core)": [71.8,72.2,70.0,68.7], "shoulders+arms": [24.7,24.2,26.2,28.0], "legs": [3.6,3.6,3.8,3.3]},
   other_subjects_total_work_J={"male 5 hcp (49.7 m/s)":1429,"male 13 hcp (46.3)":1105,"female 18 hcp (42.1)":878},
   club_model=dict(max_grip_alpha_torque_Nm={"scratch":42.1,"hcp5":36.8,"hcp13":24.6,"hcp18F":24.0}, peak_club_power_W={"scratch":3875,"hcp5":3005,"hcp13":2310,"hcp18F":1720},
      club_kinetic_energy_J={"scratch":334,"hcp5":302,"hcp13":264,"hcp18F":216}, total_club_work_J={"scratch":355,"hcp5":289,"hcp13":288,"hcp18F":235}),
   nesbit2005b_n84=dict(alpha_torque_Nm="30.9 +- 9.2 (22-40)", beta_torque_Nm="10.8 +- 2.6", gamma_torque_Nm="1.4 +- 3.3", linear_force_N="395 +- 84", total_work_J="291.8 +- 49.1", total_power_W="2727 +- 928", note="source table ambiguous (see sources)"),
   fits=dict(work_exponent_k=round(K.WORK_EXPONENT,3), power_exponent_k=round(K.POWER_EXPONENT,3), grip_torque_slope_Nm_per_ms=round(K.GRIP_TORQUE_SLOPE,3),
             note="power-law/linear fits through 4 single swings; derived; extrapolated above 116 mph"),
   other_published=dict(sprigings_neal_2000="simulation inputs: max isometric 180 N*m spine, 120 shoulder, 60 wrist; optimised peak wrist ~20-25 N*m; wrist torque worth ~9% CHS at 44 m/s (99 mph) [synthesis-only, unverified]",
      hume2005_linear_contribution_to_club_velocity_pct={"wrist":70,"shoulders":20,"spine":5,"hips":5, "note":"velocity contribution (Milburn 1982 via review); different metric from Nesbit work shares"},
      hume2005_grip_force_N=44)),
 "scaling_to_chs": dict(rows=SCALING, assumptions=["segment peaks: Cheetham two-group power law (data/speed_gap_100_120.py)","joint work: Nesbit scratch work x (v/52 m/s)^2.55","avg power = work / 0.23 s","grip torque: linear fit through 4 Nesbit swings"]),
 "env_joint_mapping": dict(
   note="Two env families. G1 env (env/g1_golf_env.py): G1 29-DoF names with _joint suffix + pelvis_yaw; tiers stock/elite; torque derates linearly to 0 at rated speed. Simple env (env/models/humanoid_golf_v3|v4_power.xml, humanoid_golf_env/residual_golf_env): no pelvis yaw; chest_yaw; left_shoulder_roll and left_elbow are UNACTUATED; peak torque = forcerange*gear; no rated speed.",
   rows=[
    dict(body="pelvis yaw",published="Cheetham/Parker/Myers pelvis peak 358-519 deg/s; hip work 423 J (Nesbit)",g1="pelvis_yaw (stand-in for both hips)",simple="none (right/left_hip_pitch are pitch; legs not yaw)"),
    dict(body="thorax / spine rotation",published="thorax peak 583-803 deg/s; X-factor 44-62 deg; spine work 619 J",g1="waist_yaw_joint (+waist_roll/pitch)",simple="chest_yaw (+-45 deg v3, +-60 deg v4_power)"),
    dict(body="lead arm / shoulder",published="arm peak 763-1097 deg/s; shoulder work 57-63 J each",g1="{left}_shoulder_pitch/roll/yaw_joint",simple="right_shoulder_pitch/roll (trail); left_shoulder_pitch; left_shoulder_roll passive"),
    dict(body="elbow",published="elbow extension 854 deg/s (pro); work 125 J right, 23 J left",g1="{side}_elbow_joint",simple="right_elbow; left_elbow passive"),
    dict(body="wrist / club release",published="wrist 1085-1183 deg/s (pro); grip torque 24-42 N*m; wrist work 56/34 J",g1="{side}_wrist_pitch_joint (+roll, yaw)",simple="right_wrist (hinge; v3 60, v4 120, h12wrist 25 N*m); no left wrist"),
    dict(body="legs / GRF",published="peak lead-foot Fz ~0.84-1.51 BW; foot pivot torque 17-26 N*m",g1="legs held rigid by PD, no GRF realism",simple="hip/knee/ankle pitch only; no yaw or pivot torque")]),
 "actuator_limits_read_from_env": dict(g1_tiers=K.G1_TIERS, simple_env=SIMPLE),
 "feasibility_g1_env": dict(ratio_definition="required average power (Nesbit work scaled to CHS / 0.23 s) / maximum power available (tau*w/4 at best operating speed, summed over DOFs); >1 infeasible; est_peak uses x2.5", by_tier_and_chs=FEAS, speed_check_rad_s=spd,
   rated_speed_rad_s={"stock":{"pelvis_yaw":32,"waist":32,"shoulder_elbow":37,"wrist_roll":37,"wrist_pitch_yaw":22},"elite":45.0}),
 "unverified": UNVERIFIED,
}
p = os.path.join(ROOT, "data", "references", "kinematic_sequence_torque_reference.json")
json.dump(out, open(p, "w"), indent=1)
print("wrote", p)
