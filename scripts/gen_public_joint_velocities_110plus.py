"""Joint-velocity (deg/s) channels derived from data/references/public_joint_trajectories_110plus.json.

DERIVED / SYNTHETIC: velocity = central finite difference (np.gradient, dt = 0.01 s) of the already-synthetic angle curves.
Nothing here is measured. Published peak speeds are copied from the trajectory file (with their citations) for comparison only.
No Instagram/CMU/MultiSense/AMASS/GolfDB data. Run: python scripts/gen_public_joint_velocities_110plus.py
"""
import json
import pathlib
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "references" / "public_joint_trajectories_110plus.json"
OUT = ROOT / "data" / "references" / "public_joint_velocities_110plus.json"


def fd_velocity(t, a):
    """Central difference (second order interior, first order at the two ends), deg/s."""
    return np.gradient(np.asarray(a, float), np.asarray(t, float))


def build():
    d = json.loads(SRC.read_text())
    out = {"_meta": {
        "title": "Joint angular-velocity channels (deg/s) derived from public_joint_trajectories_110plus.json",
        "version": 1, "generated_by": "scripts/gen_public_joint_velocities_110plus.py",
        "derived": True, "synthetic_interpolation": True,
        "contains_instagram_or_mason_derived_data": False, "derived_from_cmu_multisense_amass_golfdb": False,
        "status": "DERIVED from SYNTHETIC curves (finite difference of angle_deg). NOT measured. Only the cited peak speeds/timings are published; "
                  "the shape between them is the generator's construction.",
        "method": "velocity_deg_s = np.gradient(angle_deg, t_s) on the 10 ms grid. A 10 ms grid smears sharp peaks, so the finite-difference peak is "
                  "slightly below the analytic generator speed (kept as generator_speed_deg_s for comparison; see max_fd_vs_generator_deg_s).",
        "sign": "Signed d(angle)/dt of the channel as defined in the trajectory file (rotation: + toward target / open; arm-to-trunk and elbow flexion "
                "decrease in the downswing so their velocity is negative; wrist set angle increases = uncocking = positive). speed_deg_s is |velocity|.",
        "time_axis": d["_meta"]["sampling_grid"], "speed_classes_mph": d["_meta"]["speed_classes_mph"],
        "left_handed_mirror_rule": "velocities mirror like their angle channels: negate pelvis/thorax/x_factor, no change for planar channels (see docs/HANDEDNESS.md and the trajectory file).",
        "extrapolation_warning": "120 and 130 mph classes extrapolate beyond published support (see trajectory file); 130 mph especially.",
        "peak_speed_citation_keys": list(d["sources"].keys()),
    }, "channels": {}}
    for ch, e in d["channels"].items():
        ent = {"unit": "deg/s", "derived": True, "synthetic_interpolation": True, "role": e.get("role"), "lh_mirror": e.get("lh_mirror"),
               "peak_speed_published": e.get("peak_speed_published"), "peak_time_published": e.get("peak_time_published"),
               "speed_at_impact_published_or_assumed": e.get("speed_at_impact"), "speed_class_curves": {}}
        if ch == "x_factor":
            ent["peak_speed_published"] = ("none directly: velocity = thorax velocity minus pelvis velocity (derived). Cited peaks live on the pelvis (Madrid 2020 hip line, "
                                           "Cheetham 2008) and thorax (Madrid 2020 shoulder line, Cheetham 2008) channels.")
        for mph, cur in e["speed_class_curves"].items():
            t = cur["t_s"]
            v = fd_velocity(t, cur["angle_deg"])
            gen = np.asarray(cur.get("angular_speed_deg_s")) if cur.get("angular_speed_deg_s") is not None else None
            i = int(np.argmax(np.abs(v)))
            rec = {"t_s": t, "velocity_deg_s": [round(float(x), 2) for x in v], "speed_deg_s": [round(abs(float(x)), 2) for x in v],
                   "peak_speed_fd_deg_s": round(abs(float(v[i])), 1), "peak_time_fd_s": t[i],
                   "peak_time_ms_before_impact_fd": round(-t[i] * 1000.0, 1),
                   "generator_speed_deg_s": None if gen is None else [round(float(x), 2) for x in gen]}
            if gen is not None:
                rec["max_fd_vs_generator_deg_s"] = round(float(np.max(np.abs(v - gen))), 1)
                rec["peak_speed_generator_deg_s"] = round(float(np.max(np.abs(gen))), 1)
            if "peak_speed_used_deg_s" in cur:
                rec["peak_speed_used_by_generator_deg_s"] = cur["peak_speed_used_deg_s"]
                rec["speed_at_impact_used_by_generator_deg_s"] = cur.get("speed_at_impact_used_deg_s")
            ent["speed_class_curves"][mph] = rec
        out["channels"][ch] = ent
    return out


def main():
    OUT.write_text(json.dumps(build(), indent=1) + "\n")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
