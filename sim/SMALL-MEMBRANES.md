# Can membrane systems be made small/modular? (research prep, Oct 31, 2026)

Status: desk research + a simple model. **Run, not validated.** [S] = sourced (link), [E]/[A] = estimate/assumption.

## Our flows vs what is sold
| Case | Biogas flow | Basis |
|---|---|---|
| DIY leach-bed, 4 wet t/week | ~1.3 m3/h (31 m3/day) | [E] 17 m3 CH4/day (diy/SPEC.md; batch conversion of BMP), 55% CH4 [E] (diy simulator test-fixture value, not from SPEC) |
| Small unit, 12 wet t/week | ~3.9 m3/h | [E] small-unit/econ.py, 55% CH4 [E] (diy simulator test-fixture value) |
| Small unit, 20 wet t/week | ~6.4 m3/h | same |

Smallest commercial packaged membrane upgraders found [S]:
- HoSt "Mini": 30-60 Nm3/h biogas, containerized — https://www.host-bioenergy.com/us/technology/biogas-upgrading-translation-test/
- Bright PurePac Mini: 30-65 Nm3/h, one 40 ft container (via making.com listing) — https://making.com/equipment/small-scale-biogas-upgrading-system ; PurePac Compact 100-750 Nm3/h, 0.26 kWh/Nm3 raw biogas — https://www.bright-renewables.com/us/solutions/renewable-gas/biogas-upgrading/purepac-compact/
- Prodeval VALOPUR: from 40 Nm3/h (3-stage, container) — https://www.prodeval.com/en/biomethane-production/membrane-upgrading-valopur
- DMT Carborex MS (older, 2017 paper): Gold (fixed capacity) and Platinum systems, 50-200 Nm3/h; turndown to min 50 Nm3/h applies to Platinum only, Gold is fixed capacity — https://biogasworld.com/wp-content/uploads/2017/08/Small-scale-biogas-upgrading-Green-gas-with-the-DMT-Carborex%C2%AEMS-system.pdf

**Finding:** our flows are about 5-50x below the smallest packaged units. A packaged upgrader does not fit; the only membrane route is a self-built skid from single modules.

## Single modules (the "modular" building block)
- Evonik SEPURAN Green G5X (CO2/CH4 selectivity ~30 is an UNVERIFIED older vendor claim; current Evonik pages state no numeric selectivity): smallest is 4" (~105 mm x ~1,300 mm, ~22 kg, up to 20 barg); also 6", 6"L, 11" — https://products.evonik.com/assets/94/81/Sepuran_Green_Product_Specification_EN_Asset_4429481.pdf . No per-module Nm3/h published (GAP).
- UBE CO2 Separator (polyimide): housing types down to CO-0302SES (1.7 kg, 24 barg) and CO-C07F (4.2 kg, 16 barg), "pilot" sizes — https://ube.es/products/biogas-upgrading-biomethane-co2-separator/ . Capacity per module not published on that page (GAP; ask UBE).
- Mairui/Qingdao MCH-3032A polysulfone: vendor table shows 2-stage (1+4 modules), 16 barg, 83 Nm3/h feed, 97% CH4 / 97% recovery, 25% recycle — https://www.noveson.com/products/ultra.htm (vendor claim, unverified).
**Best lead for 1-6 m3/h: a single UBE small housing or one Evonik 4" module.** Need vendor capacity curves before sizing.

## Single- vs two-stage at low flow, and compressor penalty
- MDPI Membranes 11(12):938 (2021), 5 m3/h agricultural biogas (52% CH4): >=96% CH4 reachable; recovery up to 87.5% (polyimide) / 71.6% (polysulfone); 0.21-0.33 kWh el per m3 biogas; two-stage beat one-stage on energy at some pressures — https://www.mdpi.com/2077-0375/11/12/938
- TU Wien thesis (mobile upgrading): 0.307 kWh/m3 incl. 200 bar CNG compression, 0.213 without — https://doi.org/10.34726/hss.2020.60127

## Model sweep (sim/models/membrane_small.py, sweeps/membrane_small.json) — run, not validated
243 runs: flows 4/12/20 t/wk x layouts 1 / 2R (retentate in series) / 2RR (2R + stage-2 permeate recycle) x alpha 20/30/40 x 4/8/16 bar x stage cut 0.3-0.5.
- Figures below are for 12 t/wk (purity/recovery do not depend on flow in this model).
- Single stage: never reached 96% CH4 (max 87.6% at alpha 40, 16 bar, cut 0.5, recovery 79.7%). Fine for **boiler/CHP-grade gas enrichment**, not grid/vehicle.
- 2R: 4/27 combos >=96% (max 97.9%), recovery only ~44-63%.
- 2RR: 6/27 >=96% (max 98.6% at 59.7% recovery); best recovery 96.8% CH4 at 83.3% recovery (alpha 40, 16 bar, cut 0.4); compressor ~0.78 kW at 3.9 m3/h.
- Model specific compressor energy 0.076-0.205 kWh/m3 raw biogas is still **below** the cited 0.21-0.33 because it omits pretreatment, drying, cooling and real small-compressor losses — treat as a lower bound.
- Membrane area/module count not computed (no sourced permeance) — GAP.

## AnMBR and UF/RO for process water at small scale
- Aquabio AnMBR LE (tubular UF, 6"x4 m): 30-60 m3/day per bank, economic plant 90-230 m3/day, 1.5-2.5 kWh/m3 permeate — https://www.aquabio.co.uk/wp-content/flipbooks/AnMBR%20LE%20Product%20Sheet/files/basic-html/page1.html
- Pilot AnMBR (REWAISE Vigo): 4 m3 digester + 28 m2 hollow-fibre UF — https://rewaise.eu/2023/07/17/anmbr-in-the-vigo-living-lab-first-weeks-of-operation/
- Containerized leachate RO: 30-400 m3/day (AST; RO with UF only as optional pretreatment), up to 200 m3/day in 40 ft (DeFraWater) — https://ast-ambiente.com/leachate/ , https://www.defrawater.com/Landfill
**Finding:** [E] the DIY percolate loop is ~1-2 m3 total (diy/SPEC.md) — orders of magnitude below these. AnMBR and leachate RO are large-plant options; deprioritized for diy/ and small-unit/.

## Adaptable ideas (for the small-systems PR; all unverified)
1. Single small module (UBE pilot housing / Evonik 4") as **gas enrichment** before the boiler — biggest fit, no grid spec needed.
2. 2-stage with recycle (2RR) only if a vehicle/grid use appears. Model compressor power (lower bound), per size: 12 t/wk, 0.57-0.79 kW for the cases at >=96% CH4; 20 t/wk, 0.62-1.32 kW across all 2RR cases and 0.95-1.32 kW for the six cases at >=96% CH4.
3. Skip AnMBR/RO; if percolate polishing is needed, look at cartridge filters, not membranes (to research).

Assumption [A]: CH4 LHV 35.8 MJ/m3 (diy sizing constant, ~0 °C/1 atm basis) used for energy figures; not externally sourced here.
