# Small unit: $50k-$100k yard-waste digester (Spokane first)

> DRAFT. Not an engineered design. [S] = from a linked public page, [E] = estimate, not checked. Run `python3 econ.py` for the numbers (`results.txt` has the output). Every price and its link is in `SOURCES` inside `econ.py`.

## Verdict
**It can work, on two conditions.** Build about **8 container bays for ~12 wet tonnes a week (~620 t/yr)**, and **get paid to take the yard waste**. Base-case cost is **~$77k** and payback is **~2 years**. In the downside case, cost rises to ~$144k (over budget) and payback is ~24 years.

The money comes from **tipping fees, not gas.** At 12 t/week the gas is worth only ~$7k a year in offset propane (base) or ~$1.6k (downside). A plain compost yard earns the same tipping fees for far less money. So this unit only beats composting if you need its heat, its smaller footprint, or less odor. If tipping fees can't be had, there's no reason to build it.

## Scale options (output of econ.py)
| wet t/week | bays | base capex | base payback | base ROI | downside capex | downside payback |
|---|---|---|---|---|---|---|
| 4 | 3 | $48k | 4.9 yr | 21% | $93k | never (loses money) |
| 8 | 6 | $65k | 2.7 yr | 36% | $124k | 56 yr |
| **12** | **8** | **$77k** | **2.0 yr** | **49%** | **$144k** | **24 yr** |
| 16 | 11 | $94k | 1.8 yr | 55% | $175k | 18 yr |

Simple ROI = net yearly cash / capex. These figures don't account for financing, taxes, or depreciation.

## Cases
- **Base:** gate fee of $60/t [E]. That's below what Spokane already charges for clean green: $76.95/t at the City WTE [S] and $73.31/t at the County transfer stations [S]. A landscaper who hauls their own waste avoids that full ~$73-77/t. Base also assumes:
  - Heat replaces propane at the US average of $2.73/gal [S EIA]. EIA publishes no Washington series; Idaho is $2.69 [S].
  - 60% of the net heat is actually used [E].
  - Finished compost sells for $15/yd3 [S, low end of $15-60], at 0.4 yd3 per wet tonne [E].
  - The low end of every capex price.
- **Downside:**
  - Gate fee of $30/t, the California median for green-waste compost [S CalRecycle], used here as a stand-in for "lose the price war".
  - Heat replaces Avista natural gas at $1.43/therm [S, proposed Nov 2026], and only 30% of it gets used.
  - No compost sales.
  - The high end of every capex price and higher opex.

## Build (on top of ../diy)
It's the same batch leach-bed process as `../diy/SPEC.md`, just more bays:
- **8 bays** made from 20 ft containers:
  - Each bay has polyiso insulation, a 45-mil EPDM liner, a gasketed door, a pump, and an ASCO NC valve for isolation.
  - Loading is staggered so gas output stays steady.
- **Shared equipment:**
  - IBC percolate tanks
  - two gas bags
  - an iron-sponge scrubber
  - two flame arrestors
  - a normally-open flare valve
  - a DIY candlestick flare
  - a 75 kBtu boiler feeding PEX loops
  - a Dwyer 616KD low-range pressure transmitter
  - contactors
  - the same Pi controller, with hard-wired trips
- **Assumed on site:** a loader and crew. A landscaper or farmer already has these, so they aren't costed.

### Formerly unpriced items, now priced
| Item | Price | Status |
|---|---|---|
| Liner (EPDM 20x30 45 mil) | $552-655 | S (pondliner.com, justpondliners.com) |
| Liner fit + door gasket fabrication | $800-2000/bay | **E: needs a fabricator quote** |
| Flame arrestor 1" end-of-line, ATEX IIB3 | $349.47 | S (plcsusa) |
| Biogas/gas solenoid ASCO 8215B050 1" | $332-526 | S |
| Boiler: Peerless MI-04-e LP 75 kBtu | $4,001.53 | S, plus a biogas conversion that is **E (not offered by maker)** |
| Flare | $800-2500 | **E: no US list price found, only Indian 500 m3/h units** |
| Contactor Square D 8910DPA33V02 | $58.99 | S |
| Low-range pressure transmitter Dwyer 616KD | $117-204 | S |
| Pressure relief / condensate trap (DIY PVC) | $150-400 | E |

Other costs:
- **Permits:** SRHD solid-waste facility permit, $1,400 for a single activity or $2,500 for two or more activities [S], plus $180/h plan review [S], plus $0.32/t [S].
- **Labor:** electrician at $39.64/h mean wage [S BLS], doubled for billing [E], 60-100 h [E].
- **Other estimates:** PE review $5-12k [E], site pad $3-8k [E], 20% contingency [E].

## Key risks
1. **Tipping fee is everything.** Without at least ~$45/t the unit doesn't pay back within its life. Barr-Tech is full and turned away 9,405 t in 2025 (see ../plan), which helps.
2. **Gas-tight containers are unproven.** Liner and door fabrication is the biggest unknown in cost and safety.
3. **Gas yield is a lab-style estimate.** Run the 4-drum pilot and a BMP test first.
4. **Permitting.** A yard-waste-only digester gets no farm exemption, so expect a SRHD solid-waste permit and possibly SEPA review. Timing and cost beyond the listed fees are unknown.
5. **Heat use.** The gas only has value if there's a nearby year-round heat load (shop, greenhouse, drying). Otherwise most of it goes to the flare.
6. **Cheaper alternative.** An aerated static-pile or windrow compost yard earns the same tipping fees. Price one before you build this.

## Cheapest viable option
1. Run the 4-drum pilot from `../diy` (about $400 in drums plus the controls, which are reused later).
2. If the pilot works, build the 4 t/week, 3-bay unit for ~$48k in the base case.
3. Expand bay by bay once a tipping-fee contract is signed.
