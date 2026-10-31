# Yard-Waste-Only Digester: Profitability Plan
Drafted 2026-10-30 (PT) by Grok Bot for James. [S] = sourced figure (link given). [E] = Grok Bot estimate, arithmetic shown. Nothing here is a quote or a design.

## 1. Core problem
- Lignin locks up cellulose; >100 g lignin/kg VS markedly cuts CH4, each +1% lignin ≈ -7.49 L CH4/kg TS [S] https://pmc.ncbi.nlm.nih.gov/articles/PMC6694284/
- Wood chips or leaves alone: 50-75 L CH4/kg VS; grass alone inhibits via ammonia; an equal grass/leaf/wood mix gave 143 L/kg VS at 55 °C, 22% TS, 45 d [S] https://doi.org/10.1021/acs.energyfuels.5b00301 ; http://rave.ohiolink.edu/etdc/view?acc_num=osu1500505570855855
- Grass 230-320, leaves 100-118 mL CH4/g VS [S] https://open.metu.edu.tr/bitstream/handle/11511/45590/index.pdf
- Seasonal mix swings (grass spring/summer, leaves fall, brush year-round) change yield and C:N [S] same OSU thesis.
- Low gate fee: CA median green-waste compost tip fee $30/t (range $0-127) [S] https://www2.calrecycle.ca.gov/Docs/Publications/135405 . Food waste brings more (Monterey: $38 vs $23.50 green) [S] https://www.biocycle.net/solid-waste-district-pilots-dry-fermentation-digester/

## 2. Key revenue facts
- D3 RIN ≈ $2.405 (Feb 3 2026) [S] https://www.wastedive.com/news/section-45z-draft-guidance-language-biogas-montlhy-news-waga/811454/ ; ~13 RINs/MMBtu [S] https://noreva.ai/fuels/rng/
- Separated yard waste is deemed entirely cellulosic -> D3-eligible, but needs an EPA-accepted collection plan and the RNG pathway lists agricultural/separated-MSW digesters, not yard-waste digesters by name: pathway confirmation needed [S] https://www.ecfr.gov/current/title-40/chapter-I/subchapter-C/part-80/subpart-M/section-80.1426 ; https://www.epa.gov/renewable-fuel-standard/approved-pathways-renewable-fuel
- CA LCFS $89.25/credit (Oct 29 2026) [S] https://usefuse.com/resources/credit-prices ; credits depend on pathway CI (not yet known for yard waste).
- Biochar CDR credits averaged ~$164-165/t CO2 in 2025 [S] https://25023219.fs1.hubspotusercontent-eu1.net/hubfs/25023219/Supercritical%20Biochar%20Offtakes%20Report.pdf ; bulk biochar ~$200/t delivered (CA) [S] https://www.linkedin.com/feed/update/urn:li:activity:7262634163701231617
- Compost wholesale $15-60/yd3 [S] https://www.goldsboronc.gov/public-utilities/compost-facility/ ; https://www.olympicbiochar.com/order-biochar-compost

## 3. Per-ton energy arithmetic [E]
Assumption [E, needs lab check]: yard waste 50% TS, 85% VS/TS -> 0.425 t VS per wet t.
- 130 m3 CH4/t VS -> 55 m3 CH4/t wet -> 1.87 MMBtu/t (35.8 MJ/m3). RIN value 1.87 × 13 × $2.40 = $58/t. Gas commodity at $3/MMBtu adds $6/t.
- 180 m3 CH4/t VS (pretreated) -> 76 m3/t -> 2.6 MMBtu/t -> $81/t RIN + $8 gas.

## 4. Candidate trains
| Train | CH4 yield (m3/t VS) | Capex | Opex | Revenue/t [E unless noted] | Payback [E] | TRL | Main risks |
|---|---|---|---|---|---|---|---|
| A. Batch dry "garage" AD (BEKON/SmartFerm) + compost, CHP | 121-143 [S OSU] | €320-360 per t/yr (BEKON 25k tpa) [S epem.gr] | ~$45-50/t (Monterey pilot) [S BioCycle/Stormwater] | tip $30 + power ~$19.64/t [S Monterey] + compost | >15 yr on yard waste alone (rev ≈ opex) | 9 (proven, but mostly with food waste) | Low gas yield; power price; yard-only references thin |
| B. A + membrane RNG upgrade + D3 RINs | same 121-143 | A + upgrading (not yet sourced) | A + 0.2-0.26 kWh/Nm3 raw biogas for membranes [S Evonik/HoSt in Hermes DB] | tip $30 + RIN $58 + gas $6 + compost ≈ $94-100 | ~8-10 yr [E: $370/tpa ÷ ~$45 margin] | 8-9 | D3 pathway approval; RIN price; small-scale upgrading cost |
| C. Steam explosion + continuous high-solids AD -> RNG (Verbio-style straw model) | +32% to +118% vs untreated (rice straw, birch) [S MDPI/Biotech Biofuels]; ~180 [E] | Verbio Iowa Phase I $35M for 75-100k t stover/yr = $350-467 per t/yr [E from S saf.org.ua] | not sourced; steam heat is the big item | tip $30 + RIN $81 + gas $8 + digestate ≈ $120 | ~6-8 yr at ≥75k t/yr [E] | 7-8 (commercial on straw, not on mixed yard waste) | Grit/contaminants in yard waste; inhibitors at high severity (-10 to -76%) [S MDPI] |
| D. Fractionate: grass/leaves -> AD-RNG; woody overs -> pyrolysis biochar + CDR | AD fraction 230-320 grass [S METU] | AD per B/C; pyrolysis capex wide, not reliable yet | not sourced | woody t: 0.25 t char [E] × $200 + 0.7 t CO2e [E] × $164 ≈ $165/t + tip | ~5-8 yr [E, wide] | AD 9; biochar 8-9 | CDR buyer demand/price fall; permitting air; biochar yield & permanence certification |
| E. AD + HTC on digestate (hydrochar + process water back to AD) | HTC liquor 102-187 mL CH4/g COD [S MDPI Energies 13/6262] | not sourced for lignocellulose | not sourced | hydrochar sale + extra CH4; food-waste AD-HTC IRR 9-18.6% [S EUBCE 2026] | unknown | 6-7 | Wood at 200-250 °C lowers CH4 [S MDPI Energies 15/1418]; hydrochar market thin |

Capex reference band, US high-solids organics->RNG: ~$200-320 per t/yr (Bloomington 2023 study) [S] https://bloomington.in.gov/sites/default/files/2023-04/EPP%20Resource%20Recovery%20Feasibility_CBU_Final%20Report%203%2021%2023.pdf
Scale reference: ZWEDC San Jose dry AD 90,000 tpy (food + green), 3,100 ft3 biogas/t input, ZWE contract $6.2M [S] https://zerowasteenergy.com/wp/wp-content/uploads/2017/03/2015-05-13-ZWE-Quals-English.pdf

## 5. Recommendation
Train D+C hybrid, at ≥75,000 t/yr regional hub: screen and split incoming yard waste; send grass/leaf fines through mild steam-explosion (low severity) into continuous high-solids AD with membrane upgrading to RNG for D3 RINs (+LCFS if CI pathway works); send woody overs (which AD barely digests) to pyrolysis for biochar + CDR credits and process heat that runs the steam explosion; compost/sell digestate. Biochar heat -> steam pretreatment is the integration that makes the energy balance work.
Why: yard-waste-only AD fails on economics mainly because wood carries little methane; taking wood out of the digester and monetising it as carbon removal plays to each fraction's strength.

## 5b. Best grass blend (digester feed = grass + leaves/soft fines; woody overs -> pyrolysis)
Recommendation [E]: 40-50% grass by VS (30-60% acceptable). Blend C:N ~20-22; est. CH4 ~175-190 m3/t VS (BMP upper bound; continuous SS-AD usually lower).
| Grass % VS | C:N [E] | CH4 m3/t VS range [E] | mid [E] |
|---|---|---|---|
| 0 | 35.8 | 100-118 | 109 |
| 10 | 31.1 | 113-138 | 126 |
| 20 | 27.4 | 126-158 | 142 |
| 30 | 24.6 | 139-179 | 159 |
| 40 | 22.3 | 152-199 | 175 |
| 50 | 20.3 | 165-219 | 192 |
| 60 | 18.7 | 178-239 | 209 |
| 70 | 17.3 | 191-259 | 225 |
| 80 | 16.1 | 204-280 | 242 |
| 90 | 15.1 | 217-300 | 258 |
| 100 | 14.2 | 230-320 | 275 (grass alone inhibits by ammonia [S]) |
Inputs [S]: C:N grass 14.2, maple leaves 35.8, TC 41.5-46.4% (OSU thesis osu1500505570855855); BMP grass 230-320, leaves 100-118 (METU); grass silage TS 31.2%, VS/TS 93%, BMP 316, spoiled 265 L/kg VS (Ervasti 2019 doi 10.1515/opag-2019-0065).
Method [E]: 1/CN = x/14.2+(1-x)/35.8 (equal C per VS); CH4 linear VS-weighted; ignores mix synergy (+80-200% in OSU) and high-grass inhibition.
Limits [S]: thermophilic SS-AD TAN 4.6-5.6 g N/kg -> poor yield, 5.6 g/L ~ -50% (OSU); mesophilic SS-AD yield falls above 2.5 g/kg TAN, -50% at 6.0 (Xu 2013); grass mono-AD fails by ammonia (Thamsiriroj & Murphy 2010) or pH drop (Qi 2021). Sludge co-digestion optimum C:N 10-13 (Bioresour Technol 2014; Energy 2021) -> 20-30 is a safe zone, trial to 60% with TAN monitoring.
Seasonal: May-Sep feed ~50% fresh grass, ensile surplus (sealed; spoilage -16% BMP); Oct-Dec stockpile leaves covered, blend silage to hold 40%; Jan-Apr draw down silage + leaves at 40-50%; size silage for ~4-6 months [E]; change blend <=10%/week; weekly TAN, VFA/alk, pH.
Economics [E]: 185 m3/t VS x 0.425 t VS/wet t = 79 m3/wet t = 2.67 MMBtu -> ~$83/t RIN + ~$8 gas; matches the Train C 180 assumption without needing steam explosion. Payback 5-8 yr unchanged, lower downside risk. Wet-basis caveat: fresh grass is wetter than 50% TS.

## 6. Proven vs novel
- Proven: dry batch AD on green waste (BEKON, SmartFerm); straw mono-digestion to RNG at scale (Verbio Schwedt/Iowa); membrane upgrading; biochar pyrolysis of wood.
- Novel: running all of it on yard waste only, with pyrolysis heat feeding steam explosion; seasonal blend control (equal grass/leaf/wood synergy); D3 pathway for a yard-waste-only digester.

## 7. Open questions
1. Real TS/VS/lignin/C:N by season for James's feedstock (lab BMP tests on 4 seasonal samples).
2. EPA D3 pathway: does a dedicated separated-yard-waste digester qualify as-is or need a petition? CARB CI score?
3. Pyrolysis capex/opex at 20-40k t/yr woody input (current sources vary from portable units ~$0.55M to very large).
4. Steam explosion capex/heat demand at 50k t/yr; grit tolerance.
5. Nitrogen: grass supplies N in summer; winter leaves/wood may need N (digestate recycle).

## 8. Next steps for the agents
- Hermes: add a "yardwaste-econ" table to the DB (sourced rows only): capex/opex/yield per train, plus CI pathway facts. Don't disturb running r8 chain.
- Claude: build a mass+energy+cash model (Python) for train D+C with seasonal feed mix, sensitivity on RIN $1.5-3.0, CDR $100-250, tip $0-60.
- Codex (or Cursor stand-in): review the model code and check every number traces to a source row.
- James: decide target region (sets tip fee and LCFS access) and whether to fund lab BMP tests.

## 9. Pacific Northwest siting (added 2026-10-30 PT; region chosen by James)
### 9.1 Feedstock [S unless marked]
- WA statewide 2023 composted: 805,685 t organics; 298,561 t pure yard debris; 269,294 t mixed yard/food. https://apps.ecology.wa.gov/publications/documents/2507062.pdf
- Spokane: Barr-Tech (Sprague) capacity 110,000 t/yr, processed ~107,000 t in 2025; City of Spokane had to divert 9,405 t of yard waste because Barr-Tech was full; City diverted 30,629 t organics in 2025. https://static.spokanecity.org/documents/bcc/boards/climate-resilience-and-sustainability-board/presentations/2026/05/14/mandatory-organics-management-law-impacts.pdf (via search summary; PDF fetch failed) ; https://static.spokanecity.org/documents/publicworks/environmental/2025-environmental-highlights.pdf ; https://compostsystems.com/case-studies/barr-tech-composting/
- Spokane curbside cart takes food + food-soiled paper with yard waste (https://my.spokanecity.org/solidwaste/locations/) -> curbside stream is NOT yard-only; clean-green self-haul and landscaper loads are.
- Seattle/King/Snohomish: Cedar Grove composts >350,000 t/yr yard+food at two sites. https://cedar-grove.com/about-us
- Portland metro: DEQ 2024 report gives only the change (-13,364 t yard debris vs 2023), not the total. https://www.oregon.gov/deq/recycling/Documents/2024MRWGRates.pdf (total not found yet)
- Boise: ~30-35k t/yr yard+food at city-owned Twenty-Mile South Farm, Kuna. https://www.boisestatepublicradio.org/news/2023-11-30/reducing-greenhouse-gas-emissions-one-apple-core-at-a-time
### 9.2 Tipping fees 2026 [S]
| Site | $/t |
|---|---|
| Spokane WTE clean green self-haul | 76.95 (https://my.spokanecity.org/smc/?Section=13.02.0562) |
| Spokane County transfer stations, organics | 73.31 (+10% for 2026) (http://www.spokanecounty.gov/m/newsflash/Home/Detail/5841) |
| King County transfer stations, yard waste | 129.38 (https://kingcounty.gov/en/dept/dnrp/waste-services/garbage-recycling-compost/solid-waste-facilities/disposal-fees) |
| Cedar Grove Everett, residential yard/food (hauler) | 94.18 from Apr 1 2026 (https://www.utc.wa.gov/casedocket/2026/260090) |
| Cedar Grove Everett bulk yard/land-clearing | 69.50 (https://cedar-grove.com/organic-waste-recycling) |
| Portland Metro clean yard debris | 56 (FY26-27) (https://www.oregonmetro.gov/sites/default/files/2026-06/metro-transfer-stations-what-to-know-2026.pdf) |
Note: public transfer-station fees include transfer/haul; a processor gate fee will be lower. Model uses $60/t [E] in Spokane (undercuts $73-77).
### 9.3 Competitors / existing plants [S]
- Barr-Tech (Spokane, in-vessel compost, full). Spokane WTE burns MSW, not a yard-waste competitor (takes clean green for transfer). Cedar Grove (Puget Sound, compost). Divert Longview WA food-waste AD ~100,000 t/yr -> RNG into Cascade Natural Gas (https://www.enbridge.com/Stories/2023/September/Enbridge-Divert-break-ground-converting-wasted-food-to-RNG-facility-Longview-Washington). PSE RNG from Klickitat PUD H.W. Hill landfill (https://www.pse.com/en/green-options/Renewable-Energy-Programs/Renewable-Natural-Gas-Business). King County acquiring Cedar Hills landfill RNG plant (KC 2026 fee proposal). No yard-waste-only AD found in PNW.
### 9.4 Seasonality [E, not yet sourced with climate data]
- East (Spokane): dry hot Jul-Sep -> grass peak Apr-Jun, little summer regrowth on unirrigated lawns; leaf pulse Oct-Nov; snow Dec-Feb -> near-zero inflow. Needs larger silage store (~5-6 mo).
- West (Puget/Portland): mild wet winters -> grass Mar-Oct, longer season, wetter feed (lower TS). Silage ~3-4 mo.
### 9.5 Credit stack [S prices]
- D3 RIN: $2.03-2.20 (D3-26, wk Oct 19-23 2026) (https://pflpetroleum.com/reports/wp-content/uploads/2026/10/PFL_RIN_RECAP_V6_2026_10_26.pdf); model $2.10.
- WA CFS: $82 ref (Oct 29 2026), Ecology-reported Aug 2026 avg $75.93; CCM cap $259.26 (https://usefuse.com/resources/credit-prices ; https://ecology.wa.gov/air-climate/reducing-greenhouse-gas-emissions/clean-fuel-standard/requirements). Book-and-claim RNG allowed; North American injection OK through 2034, from 2035 must be WA-produced or on pipelines flowing into WA (https://apps.leg.wa.gov/wac/default.aspx?cite=173-424-600). Needs certified CI pathway (yard-waste CI not yet known).
- OR CFP: $85 ref (Oct 29 2026); DEQ-reported Sep 2026 avg $136.55.
- CFS/CFP credits only if the gas is claimed as transport fuel (CNG/LNG). Selling to a utility RNG program (Avista RFP) usually transfers attributes -> cannot stack with CFS for the same MMBtu. [E, confirm in contract]
- Utilities: Avista (Spokane) runs RNG supply RFPs (2024 RFP) (https://www.myavista.com/about-us/integrated-resource-planning/rng-rfp); Cascade Natural Gas takes Divert RNG; PSE and NW Natural run RNG programs (https://www.nwnatural.com/about-us/environment/renewable-natural-gas).
- Biochar PNW bulk $300-600/short ton delivered (Pacific Biochar 2023 sheet) (https://pacificbiochar.com/wp-content/uploads/Pacific-Biochar_Blacklite-Pure_Price-Sheet_Zone-Map_BULK_6.19.2023.pdf); CDR ~$164/t CO2 (sec 2).
- WA HB 1799 (2022): cities/counties >25k must adopt compost procurement ordinances and must use compost in funded projects unless cost/availability exceptions; must report organics diverted and facilities (https://app.leg.wa.gov/rcw/default.aspx?cite=43.19a&full=true). -> steady buyer for digestate compost.
- Grants: WA Commerce digester grants are dairy-only (closed; $9.7M later-2026 round) (https://www.commerce.wa.gov/sustainable-dairy-digester-programs-receive-13-8-million-commerce-investment/); Ecology Sustainable Food Management grants not until rule ~summer 2027 (https://ecology.wa.gov/regulations-permits/laws-rules-rulemaking/rulemaking/wac-173-316). USDA (REAP, 9003 loan guarantee) not checked yet.
### 9.6 Updated economics, Spokane base case [E, all arithmetic]
Assume incoming split 60% digester fines (40-50% grass blend), 25% woody overs, 15% rejects.
- Digester fines: 185 m3 CH4/t VS x 0.425 = 79 m3 = 2.67 MMBtu/wet t -> RIN 2.67x13x$2.10 = $73; gas $8; CFS ~0.17 t CO2e/t (assumes CI ~20 g/MJ vs ~88 diesel std, EER 0.9) x $82 = $14 -> $95/fines t.
- Woody: 0.25 t char x $300 = $75 + 0.7 t CO2e x $164 = $115 -> $190/woody t.
- Per incoming t: tip $60 + 0.6x95 ($57) + 0.25x190 ($48) + compost ~$5 = ~$170/t. Opex ~$70/t -> margin ~$100/t.
- 75,000 t/yr: margin ~$7.5M/yr. Capex AD+RNG $350-467 per t/yr ($26-35M) + pyrolysis ~$10M (unsourced) = $36-45M -> payback ~5-6 yr.
- Downside (no CFS, CDR $100, RIN $1.80, tip $50): ~$128/t revenue, margin ~$58 -> $4.3M/yr -> 8-10 yr.
- Puget Sound alternative: tip ~$70-90 -> +$10-30/t -> payback ~4-5 yr, but land/permits costlier and Cedar Grove incumbent.
### 9.7 Recommendation
1. Spokane hub (West Plains or Spokane Valley industrial land near an Avista main; site not picked): Barr-Tech is full (9,405 t turned away in 2025), gate fees $73-77, James is local. Problem: 75k t yard-only is most of the county stream; plan a partnership with Barr-Tech / City (digest the grass-leaf fraction, return digestate to their compost) and pull clean-green from landscapers + north Idaho. Phase 1 could start ~30-40k t.
2. Snohomish/King County (scale alternative): far more tonnage and $94-129 fees, wetter, longer grass season, Cascade/PSE pipelines.
Not recommended: Portland metro ($56 fee, lowest) and Boise (30-35k t, city-run).
### 9.8 Top risks
1. D3 pathway for yard-waste-only AD unconfirmed; curbside carts with food make gas D5 or need separation.
2. Feedstock control: Barr-Tech/Cedar Grove incumbents and hauler contracts.
3. Credit prices: D3 fell from ~$2.73 (Jul) to ~$2.10 (Oct 2026); CFS/CFP volatile; can't stack CFS with utility sale.
4. East-side seasonality: dry summers and snow -> big silage storage.
5. Pyrolysis capex and CDR demand unsourced; no WA grant program fits.
