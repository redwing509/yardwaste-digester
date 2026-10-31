#!/usr/bin/env python3
"""Small-unit (USD 50-100k) yard-waste leach-bed digester: sizing + economics.
Every input is tagged S (sourced, URL in SOURCES) or E (estimate, unverified).
Run: python3 econ.py            (prints scale options + base/downside cases)
"""
import math

SOURCES = {
 "container": "https://used-shipping-containers.com/washington/spokane/20ft-standard-container-wind-water-tight/",
 "container_cw": "https://used-shipping-containers.com/washington/spokane/20ft-standard-container-cargo-worthy/",
 "container_deliv": "https://www.flexible7.com/wa/spokane-steel-shipping-containers.php",
 "polyiso": "https://www.dunnlumber.com/rmax-2-inches-r-13-1-thermosheath-3-foil-faced-closed-cell-polyisocyanurate-foam-insulation-4-x-8-panel-rmax2.html",
 "polyiso_hi": "https://www.mendwright.com/product/mule-hide-2-in-polyiso-insulation-board-4-ft-x-8-ft-sheet/",
 "epdm": "https://www.pondliner.com/20-x-30-elevate-pondgard-45-mil-epdm-pond-liner",
 "epdm_hi": "https://justpondliners.com/products/20-x-30-45mil-epdm-pond-liner",
 "pump": "https://www.homedepot.com/p/K2-1-2-HP-Heavy-Duty-Cast-Iron-Sump-Pump-with-Tethered-Switch-SPI05003TPK/312243462",
 "solenoid": "https://spwindustrial.com/asco-8215b050-120-60-new-surplus-genuine/",
 "solenoid_hi": "https://apexcontrols.com/product/8215b050-asco-solenoid-valve/",
 "ibc": "https://baltimore-ibc-tanks.com/products/new/",
 "ibc_hi": "https://www.thecarycompany.com/275-gallon-ibc-tote-new-un-rated-2-inch-camlock-valve-composite-pallet",
 "arrestor": "https://shop.plcsusa.com/1-x-1-male-npt-end-of-line-flame-arrester-with-hood/",
 "boiler": "https://www.supplyhouse.com/Peerless-Boilers-0104007-MI-04-e-75000-BTU-Output-Intermittent-Ignition-Packaged-Residential-Water-Boiler-LP-Gas",
 "contactor": "https://tanooga.com/product/8910dpa33v02-square-d-contactor-30-amp-3-pole-120v-coil/",
 "lowp": "https://www.dwyeromega.com/en-us/616kd-differential-pressure-transmitters-one-touch-calibration/p/Series-616KD",
 "diy_bom": "../diy/BOM.csv (controls, sensors, gas bag, meter, detector, iron sponge; each row linked there)",
 "srhd": "https://assets.srhd.org/assets/media/documents/2026-Approved-Fee-Schedule.pdf",
 "elec_wage": "https://wagedepth.com/occupations/electricians-47-2111/spokane-spokane-valley-wa-44060 (BLS OEWS May 2024)",
 "tip_spokane": "https://my.spokanecity.org/smc/?Section=13.02.0562",
 "tip_county": "http://www.spokanecounty.gov/m/newsflash/Home/Detail/5841",
 "tip_ca_median": "https://www2.calrecycle.ca.gov/Docs/Publications/135405",
 "propane_us": "https://www.eia.gov/petroleum/heatingoilpropane/",
 "avista_gas": "https://apiproxy.utc.wa.gov/cases/GetDocument?docID=50&docketNumber=260720&year=2026",
 "avista_elec": "https://www.myavista.com/-/media/myavista/content-documents/your-account/bill-inserts/2026/09/21898---avu---26-wa-pga-bpa-lirap-bill-insert.pdf",
 "compost": "https://www.goldsboronc.gov/public-utilities/compost-facility/",
 "yield": "../diy/SPEC.md (17 m3 CH4/day per 4 wet t/week, 2.56 bays per 4 t/week)",
}

# ---- process (from diy/SPEC.md, E) ----
CH4_M3_DAY_PER_TPW = 17 / 4          # E
BAYS_PER_TPW = 2.56 / 4              # E
THERM_PER_M3_CH4 = 35.8 / 105.5      # physics: 35.8 MJ/m3, 105.5 MJ/therm
BOILER_EFF = 0.846                   # S boiler page (AFUE)
PROPANE_THERM_PER_GAL = 0.915        # physics: 91,500 Btu/gal

def capex(bays, hi):
    p = lambda lo, h: h if hi else lo
    per_bay = (p(1683, 2142)            # S container
               + p(150, 900)            # S/E delivery ($100-150 local quote; $901 implied delivered premium)
               + 20 * p(32.40, 61.88)   # S polyiso, qty E
               + p(552, 655)            # S EPDM 20x30 liner (fit to container E)
               + p(800, 2000)           # E gasketed door + liner seaming fabrication
               + p(119.99, 169.70)      # S pump
               + p(332, 526.30)         # S ASCO 1" NC gas valve (bay isolation)
               + p(300, 600))           # E pipe, spray bar, PEX loop, fittings
    ibcs = math.ceil(bays / 1.5) + 1
    shared = {
     "IBC percolate tanks": ibcs * p(200, 412.50),                 # S
     "Controls+sensors+gas bag+meter+detector (diy BOM priced rows)": p(1500, 2600),  # S sum of diy BOM non-structural rows, rounded
     "Extra gas bag (storage for bigger flow)": p(300, 400),       # S (diy BOM)
     "Flame arrestors x2": 2 * 349.47,                             # S
     "Flare NO-valve + main shutoff (ASCO x2)": 2 * p(332, 526.30),# S
     "Flare (DIY candlestick + pilot) - no US list price": p(800, 2500),  # E, get quote
     "Boiler 75 kBtu (LP model, biogas orifice conversion E)": 4001.53 + p(500, 1500),  # S + E
     "Low-range pressure transmitter": p(117.49, 204.15),          # S
     "Contactors x4 + enclosure": 4 * 58.99 + p(150, 400),         # S + E
     "Pressure relief/condensate trap (DIY PVC)": p(150, 400),      # E
     "Site pad gravel/drainage": p(3000, 8000),                     # E
     "Electrical service + hazardous-area wiring (electrician 60-100 h)": p(60, 100) * 39.64 * 2.0 + p(1500, 3000),  # S wage x2 burden E + materials E
     "Engineer review (PE) of gas train & layout": p(5000, 12000),  # E
     "Permits: SRHD solid waste facility + plan review": p(1400, 2500) + p(4, 15) * 180,  # S fee + hourly; hours E
     "Lab tests (BMP, feed)": p(500, 1500),                        # E
     "Owner build labor not counted (assumes landscaper crew/equipment)": 0,
    }
    sub = bays * per_bay + sum(shared.values())
    cont = 0.20 * sub                                               # E contingency
    return sub + cont, per_bay, shared

def annual(tpw, tip, fuel, heat_use_frac, compost_val, hi_opex):
    t = tpw * 52
    ch4 = CH4_M3_DAY_PER_TPW * tpw * 365
    net_therm = ch4 * THERM_PER_M3_CH4 * BOILER_EFF * (1 - 0.40) * heat_use_frac  # 40% self-heat E
    if fuel == "propane":
        heat_val = net_therm / PROPANE_THERM_PER_GAL * 2.73 / 0.846  # S US avg; no WA series
    else:
        heat_val = net_therm * 1.43171 / 0.846                       # S Avista proposed Nov 2026
    rev_tip = t * tip
    rev_comp = t * 0.4 * compost_val                                 # 0.4 yd3 sold per wet t E
    opex = (t * (12 if hi_opex else 8)                               # E loader/labor per t
            + 0.37 * 3 * (tpw / 4) * 24 * 365 * 0.3 * 0.14           # pumps 30% duty E, Avista ~$0.14/kWh S
            + t * 0.32                                               # S SRHD per-ton
            + (4000 if hi_opex else 2500)                            # E insurance, media, tests, maint
            + (1400 if hi_opex else 1400))                           # S annual permit renewal assumed = fee E
    return dict(tonnes=t, ch4=ch4, heat=heat_val, tip=rev_tip, compost=rev_comp, opex=opex,
                net=rev_tip + rev_comp + heat_val - opex)

CASES = {
 "base":     dict(tip=60, fuel="propane", heat_use_frac=0.6, compost_val=15, hi_opex=False, hi_capex=False),
 "downside": dict(tip=30, fuel="natgas",  heat_use_frac=0.3, compost_val=0,  hi_opex=True,  hi_capex=True),
}

def run(tpw):
    bays = math.ceil(tpw * BAYS_PER_TPW)
    out = {}
    for name, c in CASES.items():
        cap, _, _ = capex(bays, c["hi_capex"])
        a = annual(tpw, c["tip"], c["fuel"], c["heat_use_frac"], c["compost_val"], c["hi_opex"])
        out[name] = (cap, a, cap / a["net"] if a["net"] > 0 else float("inf"), a["net"] / cap)
    return bays, out

if __name__ == "__main__":
    for tpw in (4, 8, 12, 16, 20):
        bays, out = run(tpw)
        print(f"\n== {tpw} wet t/week ({tpw*52} t/yr), {bays} container bays ==")
        for n, (cap, a, pb, roi) in out.items():
            print(f"  {n:8s} capex ${cap:,.0f} | tip ${a['tip']:,.0f} heat ${a['heat']:,.0f} compost ${a['compost']:,.0f} "
                  f"opex ${a['opex']:,.0f} | net ${a['net']:,.0f}/yr | payback {pb:.1f} yr | ROI {roi*100:.0f}%")
