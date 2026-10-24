# Golfphys spin + launch audit (Data Agent, 2026-10-24 ET)

Question: the v5 sim (which uses golfphys for impact) reports 3850-4900 rpm at spin loft ~16-18 deg and ~72-77 mph. Is golfphys's spin wrong?

## How golfphys computes spin (golfphys/impact.py, `impact_vec`)
Oblique impact, centre strike: normal ball speed `(1+e) m_eff/(m_eff+m_ball) * v_n`; tangential impulse `Jt = s_t_eff * m_ball * v_t / 3.5`
(full rolling contact at s_t=1), `omega = R*Jt/I`. So backspin ~ `s_t_eff * v_club * sin(spin_loft) / (1.4 R)`. `s_t_eff = s_t + s_t_slope*(spin_loft-12)`;
defaults s_t 0.866, s_t_slope 0 (CALIBRATED earlier to TrackMan 2010 optimizer rows). Off-centre: bulge/roll tilt the effective normal, plus
Tutelman vertical gear effect 25 rpm per (mph ball speed * inch), so a LOW strike raises spin and lowers launch.
`spin_k 130` is NOT golfphys: it is the old v4 env hand-set model `rpm = spin_k*|v_ball|*sin(launch+2)` (env/humanoid_golf_env.py). v5 does not use it.

## Measured rows (data/references/golfphys_spin_audit_rows.csv)
Only rows that publish club speed, AoA, dynamic loft, spin loft, launch and spin: TrackMan Combine averages (male 5 bands, female 4 bands) and
TrackMan PGA/LPGA Tour averages, from trackman.com/blog pages what-is-club-speed, ball-speed, attack-angle, dynamic-loft, spin-loft, launch-angle,
spin-rate (all opened 2026-10-24). Label: measured, published aggregate means. Caveats: each parameter is a separate mean (from separate pages),
n and year not published; published spin loft exceeds DL-AoA by 1-3.6 deg on most rows (TrackMan's 3D definition and/or different samples).
R22-01 rows (77 / 85.8 mph) do NOT publish dynamic or spin loft, so they are context only, not fit or scored (deriving SL by inverting golfphys's
launch model would be circular). TrackMan 2010 chart rows are counsel_pending and model output: used in an analysis-only check kept OUTSIDE the repo.
Data are thin: no measured row with spin loft below 79 mph.

## Split (pre-declared, by source)
train = Combine male + Tour (7); held_out = Combine female (4; 79-90 mph, closest to 74 mph). No policy results used.

## Results (centre strike; inputs club speed, AoA, DL = AoA + published spin loft)
| | train bias / RMSE rpm | held-out bias / RMSE rpm | launch bias train / held |
|---|---|---|---|
| golfphys default | +532 / 581 | +236 / 291 | +1.09 / +1.05 deg |
| proposal (s_t 0.6065, s_t_slope 0.02894) | -4 / 158 | -30 / 105 | +1.51 / +1.29 deg |
With PUBLISHED DL as input instead (SL = DL-AoA, smaller): default gives held-out -61 / 172 rpm, launch -0.35 deg; train +213 / 351.
So the verdict depends on which TrackMan loft number is trusted; default golfphys is within roughly -2% to +8% on held-out spin and its largest
error is at tour speeds (PGA +42% in SL-matched mode). The proposal improves spin but worsens launch (+1.3-1.5 deg high) and moves away from
the TrackMan-2010 optimizer rows, so it is recorded as OPT-IN only (`data/golfphys_spin_audit.py: proposed_params()`); defaults are unchanged.

## 74 mph probe (AoA +1, centre)
SL 16/17/18: default 2522/2675/2827 rpm (launch 14.3/15.1/16.0); proposal 2104/2321/2548 rpm.
Measured context: R22 female Cat2 77 mph, AoA 1.4 -> 2784 rpm, launch 13.2 (SL not reported).

## K30 sanity case (Trainer-reported MODEL inputs, not data): 74 mph, DL 17.3, AoA +1, LH
Centre strike: 2568 rpm, launch 14.55. Reproducing the sim's 4206 rpm / 10.9 deg needs a strike ~22 mm BELOW face centre
(-22 mm: 4210 rpm, launch 11.1). So the 3850-4900 rpm is not golfphys's centre-strike spin; it is consistent with low-face contact
(vertical gear effect + roll) or with a larger effective 3D spin loft at contact than the reported DL-AoA. The launch/spin coupling
(low launch with high spin at ~17 deg DL) is the signature of low strikes. Recommendation: log `y_high_m`/`x_toe_m` from v5_shot per swing.
Unverified: the strike offset of K30 itself (not logged in the fit files I read).

## Limits
Aggregate means, not shots; no measured spin-loft rows below 79 mph; 2-parameter fit on 7 rows; ball type/conditions not stated by TrackMan;
roll radius (12 in) and gear-effect rates are unverified/vendor-derived and dominate the off-centre result.

## Evaluator review and decision (2026-10-24)

Independent review by the Golf Style Evaluator reproduced every number above with no leakage. **Decision: the opt-in `s_t` proposal is DEFERRED, not adopted. Defaults in `golfphys/` are unchanged.**

Reasons for deferral:
- **Loft definition drives the result.** TrackMan's published spin loft (3D, a separately published mean) is 0.9-2.3° higher than published dynamic loft minus AoA on all 11 rows. Feeding the model dynamic loft = AoA + spin loft overstates loft. With published dynamic loft, the default model's held-out spin error is about -2% to +8% (bias -61, RMSE 172 rpm), so "default spin too high" is not supported.
- **Unstable across splits.** Leave-one-group-out: hold out male Combine gives s_t 0.539 and held-out -107/196 rpm; hold out Tour gives s_t 0.663, +261/324 rpm and launch +2.2°. Leave-one-row-out RMSE is 182 rpm (PGA row +429). The 105 rpm held-out RMSE reported above is the most favourable split. A refit on published dynamic loft (s_t 0.729, slope 0.0267) gives held-out -86/161 rpm with launch -0.33°.
- **Worsens launch** by +1.3 to +1.5°.
- **Would mask the real cause.** Diagnostic (not harness) runs show the sim's high spin comes from low-face strikes: K30a about 25 mm low, K30b about 31 mm low. Lowering `s_t` would push a centre strike at the K30 inputs to about 2168 rpm, near the 2000 rpm floor.

Open issue: the low-strike penalty size is itself unverified. The gear-effect rate is extrapolated past ±0.5 in, the roll and bulge radii are unverified, and the 64 mm box head still gives smash 1.35-1.37 at 25-31 mm low, which is not realistic. Face-geometry and off-centre sourcing is in progress separately.
