# Membrane research for yard-waste processing

Desk research (Oct 2026) into membranes that could pair with yard-waste
digestion/processing. Every figure below comes from a page that was opened
and is cited in the CSVs. **Nothing here is vendor-quoted or field-validated.**

## Dataset (from `yw.sqlite`)
| Table | Rows | File |
|---|---|---|
| membranes | 45 | [membranes.csv](membranes.csv) |
| applications | 132 | [applications.csv](applications.csv) |
| process options | 4 | [process_options.csv](process_options.csv) |
| evidence rows | 252 (DB only) | 13-row pricing/verification subset exported: [pricing_and_verification_evidence.csv](pricing_and_verification_evidence.csv) |
| open gaps | 10 | [gaps.csv](gaps.csv) |

Each row has a `source_url` and a `verify` column.

## Top 5 pairings
| # | Membrane | Process | Re-check verdict |
|---|---|---|---|
| 1 | AIRLIQ-M01 Air Liquide MEDAL biogas upgrading | PO1-01 dry AD + membrane upgrading -> RNG | **verified** (RV-AIRLIQ-E01) |
| 2 | EVONIK-M01 SEPURAN Green | PO1-01 | **unverified**: official PDF gives no matching figure (RV-EVONIK-E01) |
| 3 | VEOLIA-M02 ZeeWeed 500 AnMBR | PO4-01 wet AD + AnMBR + nutrient recovery | not re-checked |
| 4 | MICRODYN-M01 BIO-CEL MBR | PO4-01 | not re-checked |
| 5 | TORAY-M03 HFUG-2020AN UF | PO2-01 HTC + AD of process water + membranes | not re-checked |

Separately, TORR-A01 (torrefaction condensate, belongs to PO3-01, not to the Toray pairing) is **unverified**: the official source has no matching number (RV-TORR-E01).

Also: DUPONT-M01 FilmTec BW30-PRO-400 RO is **verified**: 99.6% rejection (RV-DUPONT-E01).

## Pricing (3 of 5 pairings have figures. All are estimates; see sources)
- **Air Liquide + PO1-01:** 0.05-0.15 USD per 1000 scf feed gas (trade site, year not stated). [source](https://www.oilngasprocess.com/gas/natural-gas-sweetening-medal-membrane-co2-removal-process-by-air-liquide.html)
- **Evonik + PO1-01:** capex ~2000 EUR per Nm3/h and opex ~25,000 EUR/yr (literature estimate, [PMC9821904](https://pmc.ncbi.nlm.nih.gov/articles/PMC9821904/)). Evonik publishes no vendor price.
- **Veolia AnMBR + PO4-01:** membrane 40-60 $/m2 (low-confidence [vendor blog](https://thewaymembranes.com/post/the-true-cost-of-mbr-membranes-why-theway-saves-you-40-60-vs-premium-brands)); capex 0.080-0.147 EUR/kg COD removed ([peer-reviewed](https://www.sciencedirect.com/science/article/pii/S2213343723010060)); treatment 0.05-0.12 EUR/m3 ([peer-reviewed](https://riunet.upv.es/bitstreams/47f3d571-82a5-47b3-82f3-df573c3c3898/download)).
- **Microdyn BIO-CEL:** no vendor price found (open gap).
- **Toray HFUG-2020AN with HTC + AD:** no vendor price found (open gap).

Unconfirmed marketplace prices and figures from blocked pages were left out on purpose.

## Open gaps (10)
Pricing; yard-waste-specific feedstock evidence; process-option verification;
single-source yields; techno-economics; empty evidence values; fouling on
yard-waste particulates; VFA valuation; nutrient recovery on yard-waste
digestate; scale-up beyond lab or pilot. See [gaps.csv](gaps.csv).

Simulation work on these processes lives in [../sim/](../sim/).
