"""Sizing calculator. Every input is an assumption; replace with your lab data.
Run: python -m digester.sizing"""
from dataclasses import dataclass


@dataclass
class SizingInputs:
    feed_t_per_week: float = 4.0        # wet tonnes/week [assumption]
    ts_frac: float = 0.35               # total solids of grass-silage/leaf blend [E, test it]
    vs_of_ts: float = 0.85              # [E, matches PLAN.md assumption]
    bmp_m3ch4_per_t_vs: float = 180.0   # blend BMP, PLAN.md estimate 175-190 [E]
    batch_conversion: float = 0.55      # leach beds reached ~50-67% of BMP in studies [S]
    bulk_density_t_m3: float = 0.45     # loaded bay density [E]
    fill_depth_m: float = 1.5           # pile depth in bay
    bay_floor_m2: float = 5.9 * 2.35    # 20 ft container internal floor (approx) [E]
    cycle_days: float = 42              # 35 d digestion + load/unload/aerate [E]
    ch4_mj_per_m3: float = 35.8


def size(i: SizingInputs = SizingInputs()):
    vs_t_week = i.feed_t_per_week * i.ts_frac * i.vs_of_ts
    ch4_week = vs_t_week * i.bmp_m3ch4_per_t_vs * i.batch_conversion
    bay_vol = i.bay_floor_m2 * i.fill_depth_m
    bay_t = bay_vol * i.bulk_density_t_m3
    batches_per_week = i.feed_t_per_week / bay_t
    bays_needed = batches_per_week * i.cycle_days / 7
    olr = (vs_t_week * 1000 / 7) / (bays_needed * bay_vol) if bays_needed else 0
    return {
        "vs_t_per_week": round(vs_t_week, 2),
        "ch4_m3_per_week": round(ch4_week, 1),
        "ch4_m3_per_day": round(ch4_week / 7, 1),
        "avg_thermal_kw": round(ch4_week / 7 * i.ch4_mj_per_m3 / 86.4, 2),
        "bay_volume_m3": round(bay_vol, 1),
        "bay_load_t": round(bay_t, 1),
        "bays_needed": round(bays_needed, 2),
        "bays_to_build": int(-(-bays_needed // 1)),
        "avg_olr_kg_vs_per_m3_day": round(olr, 2),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(size(), indent=2))
