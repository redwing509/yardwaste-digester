# Philippines — yard-waste / green-waste / lignocellulosic anaerobic digestion (checked)

Status: DONE (checked). Prompt language: English. Philippines only. Hermes job 20261117-003220-digester-survey-49-philippines-yard-wast (key dg-survey-49-philippines, rc 0, 12:32–12:51 AM America/Los_Angeles, 17 Nov 2026, about 19 minutes; worker status DONE). Hermes did not save its draft file; it printed a two-pass report (12 sources, findings, six simulator rows marked NOT OPENED) to its log, which the checker recovered. Its negative headline is right — the Philippines has no yard-waste digester — but it wrote "organic yard waste" into almost every source although only one mentions it, invented quotes and percentages, moved a 300 kVA generator from a Zamboanga farm story to a Quezon City bid document, presented a Mexican study as a Philippine policy review, invented verbatim clauses of Philippine laws, and listed six simulators that appear in none of its sources. The checker corrected these and added a Laguna rice-straw biogas trial.

## Summary

No Philippine digester taking mainly yard, garden or park waste was found. Philippine biogas is small digesters on food scraps, market waste and livestock manure, plus large farm digesters. The government ITDI portable digester lists "organic yard waste" as a possible substrate, but no yield for it was found. The only measured lignocellulosic digestion run found is a rice-straw trial in Victoria, Laguna (Straw Innovations with UP Los Baños and Aston University): 39,950 kg of rice straw and 10,000 kg of cattle manure gave 1,409,744 L of biogas in a lagoon digester (June–October 2021). Philippine law defines yard waste (RA 9003) and steers garden waste to composting; the Renewable Energy Act encourages biogas from manure and agricultural waste. Metro Manila's WtE feasibility study recommends incineration, not digestion.

## Verified findings

- **Rice-straw biogas trial (Laguna)** — Gomez, Demafelis et al. (UPLB), Chong & Roeder (Aston), Jamieson (Straw Innovations), IOP Conf. Ser.: Mater. Sci. Eng. 1318 (2024) 012016, doi 10.1088/1757-899X/1318/1/012016 (https://iopscience.iop.org/article/10.1088/1757-899X/1318/1/012016, open access): trial lagoon run June–October 2021 at Victoria, Laguna; 39,950 kg rice straw + 10,000 kg cattle manure + 52,033 kg water gave 1,409,744.48 L biogas. The paper's "296.19 L/kg VS" (8,803,567.99 L) is a projection of the Aston Mass-Energy Balance model, about six times the measured run; the authors note the trial "was not optimized". A related LCA of the "1000 m3 rice straw biogas pilot plant in Laguna" found up to 68 % GHG reduction against burning or soil incorporation (Röder et al., Biomass and Bioenergy 2024, doi 10.1016/j.biombioe.2024.107072, CC BY). PhilRice 2016: "70 percent of rice farmers burn rice straws" (as cited by SEARCA, 23 Apr 2024).
- **ITDI portable digester** — DOST-ITDI Livelihood Technology Series 32 (4th ed. 2020, open copy via WIPO GREEN): 200 L and 1,000 L units; "The substrates fed to the digesters can be kitchen waste, animal manure and organic yard waste"; biogas 50–70 % CH4; sludge as organic fertilizer or soil conditioner. No yield data.
- **LGU digesters (Cavite)** — Gen. Mariano Alvarez, designed by MHE Biogas Technology (M. S. Templonuevo, municipal ENRO): three fixed-type (16 m³/400 kg and 80 m³/2 t per day) and five IBC digesters (2 m³, 50 kg/day of household or public-market biodegradables). Feedstock is household and market waste (fish gills, intestines, rotten vegetables), not yard waste.
- **Quezon City** — FY2025 bid for a 2.1 m³ community-farm biodigester (1,200 L digester, 700 L gas tank) on "food scraps and animal manure"; max energy 4.4 kWh, cooking up to 2 hours a day.
- **San Pablo, Laguna** — Reurasia/Alterna Verde containerized biogas plant (Gold Standard stakeholder report, meeting 7 Apr 2026): four containers, 1,200 t/yr of household organic fraction, restaurant food waste and industrial organic waste, ~256 MWh/yr; installation planned Q4 2026. No yard waste named.
- **Farm digesters** — Rockefeller Farm, Dipolog City: manure of over 100,000 chickens and pigs runs a 300 kVA generator for 15 hours (DOST-STII, 13 Aug 2026). Evergreen Swine Breeder, Umingan, Pangasinan: 2,500 sows, 16,000 m³ biogas tank facility (EIS summary).
- **Metro Manila** — MMDA WtE Feasibility Study (Nov 2023): yard waste was 9.9 % (1982), 7.45 % (1997), 20.4 % (2003) and 2.10 % (2015) of Metro Manila waste; digestion was reviewed but stoker-type incineration is recommended.
- **Law** — RA 9003 Sec. 3(uu): "Yard waste shall refer to wood, small or chipped branches, leaves, grass clippings, garden debris…"; Sec. 34: composting of "garden wastes, shall be encouraged". RA 9513 Sec. 30: DOE shall "encourage the adoption of waste-to-energy facilities such as, but not limited to, biogas systems" for "animal manure or agricultural waste". DOE DC2022-02-0002 ("Prescribing the Policies and Programs to Promote and Enhance the Development of Biomass WTE Facilities") exists; its text was not opened.

## Simulators and modeling tools

Simulators found (after check): one candidate, not Philippine-developed. **Aston Bioenergy Mass-Energy Balance (MEB) Model** — Röder & Chong, Energy and Bioproducts Research Institute, Aston University (UK), 2021; Excel scoping model for bioenergy/biogas CHP mass and energy balances (10 kWe–5 MWe); free download, © 2021 The Authors, no open-source license stated; https://publications.aston.ac.uk/id/eprint/42963/ ; used (modified) by UPLB in Gomez et al. 2024 for the Laguna rice-straw trial. Hermes's six rows (ASPEN Plus, ADM1, an ITDI "Biogas Potential Calculator", MATLAB/Simulink, LEAP-IBC, a UP "Open-Source BMP Calculator") appear in none of the cited sources and were dropped.

## Not taken (unverified or contradicted)

- "All documented digesters explicitly list organic yard waste" — only the ITDI brochure does; the Cavite, Quezon City, San Pablo, UP Diliman, Aurora and Pangasinan sources do not.
- San Pablo dump site "food and kitchen wastes (44 %), garden and yard wastes (28 %)" — not in the report; report is 2026, not 2022, and the plant is not built yet.
- Quezon City "300 KVA generator for 15 h" — moved from the Zamboanga farm story.
- Cavite "designed to treat 60 % of biodegradable wastes", "450 L metal drum", "2.5 t/yr" — source says 50–60 % of waste is biodegradable; other specs invented.
- UP Diliman fixed-film digester "for yard waste", "0.21 m³", "1998" — it was for liquid wastewaters, 10 L/100 L, published 1988.
- Aurora fixed-dome "5–12 m³ day⁻¹", yard waste — the URL does not resolve; the real record (Anselmo 2009, CLSU thesis) is on hog-manure digesters and gives no numbers.
- "Frontiers 2022 policy review on WtE in the Philippines (paywalled)" — the DOI is an open-access Mexican BMP study of Guadalajara waste.
- MMDA "concluded AD viable" — it recommends incineration.
- Verbatim clauses of RA 9513, DC2022-02-0002, RA 9003 and "DAO 2021-06" on yard waste — not real quotations.
- DOST Region 1 "Bioreactor" as a digester — it is a composter. eLib "Biogas digester suited to rural areas" quote — catalog record only, no text. "Barangay Biñan (Cavite)" case study — not opened (Biñan is in Laguna).

NOT FOUND: Philippine BMP or digester data for yard, garden or park waste; a Philippine plant digesting mainly yard waste; a Philippine law or incentive aimed at yard-waste digestion; a Philippine-developed released digester simulator.

## Hermes status

Hermes job rc 0 on the we-research profile, about 19 minutes. It did not write its draft file (the report went only to its log; the checker recovered it) and claimed "Result file written". 12 sources: 9 real and reachable, one dead handle (real thesis), one not openable, one foreign. Invented quotes and percentages, yard waste inserted into sources that do not mention it, a figure moved between sources, a Mexican paper passed off as Philippine, invented law clauses, wrong years (1988, 2025, 2026), and six unsourced simulator rows. No Philippine number format was misread. Hermes did not touch git, email or code.
