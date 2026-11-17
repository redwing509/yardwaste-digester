# Norway — yard-waste / green-waste / lignocellulosic anaerobic digestion (checked)

Status: DONE (checked). Prompt language: Norwegian (bokmål; nynorsk labels in SSB). Norway only. Hermes job 20261116-202630-digester-survey-23-norway-yard-waste-ad (key dg-survey-23-norway, rc 0, 8:26–8:38 PM America/Los_Angeles, 16 Nov 2026, about 12 minutes; worker status DONE). Hermes wrote a complete two-pass draft (12 Norwegian sources, findings, simulators table). Its main picture is right — Norway composts its garden waste — but it passed a UK food-waste yield off as a Norwegian plant result, spliced a permit quote, quoted a 404 page, and invented a "196 Nm³/t" figure and a "5.5 TWh strategy target". The checker corrected these, read the national statistics from SSB's open API, and opened an open copy of the Norwegian plant paper.

## Summary

Norway does not digest its garden waste; it composts it. SSB table 12359 (biological treatment, 1,000 t) shows "Park- og hageavfall" at 103 thousand t in 2024, all of it under "Kompostering" (103) and none under "Biogassproduksjon" (".."; 0 every year 2018–2023; 14 in 2017). IVAR (Stavanger region) explains why: "Tørre greiner fra hagen og plengress er dårlig mat for bakteriene på biogassanlegget som lager biogass. Men hageavfallet ditt kan brukes til å lage bra og næringsrik kompost." A 2012 Klif report (Mepex) estimated about 160,000 t of separately collected garden waste in 2010, "i hovedsak kompostert", and left it out of the biogas potential ("Hageavfall har lavt biogasspotensial og er ikke regnet med"). Norwegian food-waste digesters (Romerike, Mjøsanlegget, IVAR Grødaland, Ecopro Verdal) take food waste, sludge and by-products; garden waste is used only to make compost or soil products from digestate. No Norwegian yard-waste digester, yard-waste BMP or Norwegian simulator was found.

## Verified findings

- **National statistics — SSB table 12359** (https://www.ssb.no/statbank/table/12359; data via https://data.ssb.no/api/v0/no/table/12359): "Park- og hageavfall", 1,000 t, 2017–2024: total 82, 76, 73, 115, 103, 92, 98, 103; biogas 14, 0, 0, 0, 0, 0, 0, ".."; composting 68, 76, 73, 115, 103, 92, 98, 103. All biological treatment in 2024: 746 (biogas 528, composting 218).
- **Klif 2012 (Mepex Consult, Jarle Marthinsen), TA-2957/2012** (https://www.miljodirektoratet.no/globalassets/publikasjoner/klifsft/publikasjoner/2957/ta2957.pdf): "Hage-/parkavfall innsamlet separat og levert til behandlingsanlegg utgjør iht SSBs anleggsstatistikk ca. 160 000 tonn i 2010"; "Hageavfallet blir i hovedsak kompostert og brukes delvis som strukturmateriale for kompostering av avløpsslam. Noe hageavfall kan gå til forbrenning"; "Hageavfall har lavt biogasspotensial og er ikke regnet med"; leaves and grass "har lav brennverdi og inneholder mye aske".
- **IVAR IKS** (https://www.ivar.no/hageavfall-ut-av-matavfallet): food waste goes to "IVARs biogassanlegg på Grødaland i Hå kommune"; clean garden waste goes to Sele (Klepp) and Nordmarka (Strand) for "kompostjord og torvfrie jordblandinger"; "Det er nå lovpålagt at alle norske kommuner må sørge for at mat- og hageavfall fra husholdningene sorteres hver for seg."
- **Romerike biogassanlegg (Esval, Nes; Oslo kommune REG)** — permit decision of 03.09.2025 (norskeutslipp.no, https://www.norskeutslipp.no/WebHandlers/PDFDocumentHandler.ashx?aar=0&companyID=25218&documentID=953466&documentType=T&epslanguage=no): up to 50,000 t/yr (permitted maximum, not throughput) of source-sorted food waste and category 2 animal by-products; no garden waste in the permitted types. The permit restates avfallsforskriften § 10a-13: plants receiving "utsortert matavfall og park- og hageavfall" must ensure material recovery.
- **Mjøsanlegget Biogass (Lillehammer)** (https://www.mjosanlegget.no/om-oss): food waste from 18 owner municipalities, "45 000 tonn kapasitet", gas upgraded "til 97–99 % metan"; the solid digestate "blir kompost som blandes med hageavfall, sand og bark til ulike jordprodukter".
- **Ecopro, Verdal (Nord-Trøndelag)** — Mustafa, Calay & Román, Procedia Engineering 146 (2016) 310–317, doi 10.1016/j.proeng.2016.06.397 (open repository record https://hdl.handle.net/10037/10459): "organic household waste, sludge from wastewater and a minor part of ensilage waste from fish farms"; "total capacity of 30000 to 45000 tons of organic waste". No garden waste named.
- **Policy** — Avfall Norge (Jens Måge, Blest 2024, https://www.avfallsforumrogaland.no/wp-content/uploads/2024/06/12_Biogass-eller-kompostering-eller-ja-takk-begge-deler-BLEST-Jens-Mage-6.6.24-1.pdf): bio-waste = "Matavfall og hage/parkavfall"; sorting required "fra 1. januar 2023 (utsorteringsforskriften §10a)"; exception for source composting of garden waste. Miljødirektoratet M-2275 (2022, *Biogass i Skandinavia*): 612,000 t went to biological treatment in 2020; chapter 10a requires material recovery (not specifically biogas).
- **Potential (scenario only)** — NORSUS OR 06.23 (Lyng & Berntsen 2023, https://norsus.no/wp-content/uploads/OR-06.23-Mulighetsrommet-for-produksjon-av-biogass-i-Norge-1.pdf): household garden waste "Energipotensial (GWh)" 940 for **gasification** (methane from syngas, 70 % efficiency factor applied to the total); total extra gasification potential about 7.6 TWh; AD potential from today's feedstock 5.5 TWh; Norway produced about 0.7 TWh biogas in 2021.

## Simulators and modeling tools

Simulators found (after check): no Norwegian tool. Three real open tools listed by Hermes were added to the candidate list (not installed): OpenAD-lib (MIT, https://github.com/benmola/OpenAD-lib), Simplified ADM1 Matlab/Simulink by Sören Weinrich (MIT, https://github.com/soerenweinrich/ADM1), and the R package biogas by Sasha D. Hafner et al. (GPL-2, not GPL-3; https://cran.r-project.org/package=biogas). PyADM1 (MIT) was already listed. OsloMet's "MaxBiogas Web Simulation" is a work-in-progress demo for sewage-sludge digestion, not downloadable. None has a Norwegian yard-waste case.

## Not taken (unverified or contradicted)

- "642 m³ tonne⁻¹ VS methane yield, 62 % CH₄" for Ecopro/Norway — this is Banks et al. (2011), a UK food-waste digester (University of Southampton), cited in the Norwegian paper's literature review; and it is a biogas yield.
- Romerike permit "lists park and garden waste"; permit year 2022; "ØRAS".
- "Miljødirektoratet: 103 000 tonn in 2024" (page returns 404; the figure is SSB's).
- "Biogass i Skandinavia: garden waste to be treated in biogas plants" (not in the report).
- "~196 Nm³ per tonne" for garden waste (not in NORSUS); "940 GWh biogas potential" (energy potential for gasification).
- "Biogassstrategi 2022–2030 with a 5.5 TWh target" (no such strategy found).
- Vest Biogass AS application (link does not resolve); "Nord Biogass AS (planned)" (not in the cited report).
- Enova garden-waste rule; thermal hydrolysis / steam explosion; SEPURAN membranes; Mjøsanlegget "fixed-bed digester".

NOT FOUND: a Norwegian digester taking mainly yard/garden waste; a measured Norwegian BMP or biogas yield for garden waste, leaves or grass; a Norwegian yard-waste AD pilot; a Norwegian-developed released digester simulator.

## Hermes status

Hermes job rc 0 on the we-research profile, about 12 minutes. 12 Norwegian URLs (8 openable: one 404, one 403, one non-resolving host). One foreign (UK) result passed off as Norwegian, one quote from a 404 page, spliced permit quote, invented figure (196 Nm³/t) and invented strategy target. Simulators section present; tools real, one licence wrong. Hermes did not touch git, email or code.
