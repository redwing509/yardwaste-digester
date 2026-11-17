# Turkey — yard-waste / green-waste / lignocellulosic anaerobic digestion (checked)

Status: DONE (checked). Researched directly by Grok Bot, no Hermes (James t1114u/t1115u, 16 Nov 2026, about 8:55–8:58 PM America/Los_Angeles). Prompt language: Turkish (all searches in Turkish). Turkey only. Two passes (James t1084u): Pass 1 = sources opened; Pass 2 = findings below, each with a quote copied from the opened source and its link. Anything not found in an opened source is marked NOT FOUND.

## Summary

Turkey has good lab data on yard-waste digestion but no full-scale yard-waste digester was found. A METU thesis (Kalaycıoğlu 2020) digested yard waste and got "the highest CH4 yield … with AP-yard waste at 5% TS as 313 mL CH4/g VS" (alkaline pretreatment), and found two-stage digestion "not sufficient … for yard wastes". Kahramanmaraş Sütçü İmam University measured park grass waste at "0.39 to 0.42 m3/kg ODM" methane with "59.01% and 60.19%" methane (HBT, *IJABE* 2025). Istanbul's first source-separated biowaste digester (İBB/İSTAÇ, 2021, 130 t/day) takes "yemek atıkları, sebze-meyve atıkları ve gıda atıkları" (food, fruit-vegetable and food waste); garden waste is not named in the opened İSTAÇ sources. İzmir's planned Bergama plant was to digest "yiyecek ve bahçe atıkları gibi organik atıklar" (food and garden waste), but whether it was built and what it takes: NOT FOUND. No Turkish-developed released digester simulator was found.

## Verified findings

- **METU — yard-waste one- and two-stage AD with pretreatment** — Kalaycıoğlu N. N. (supervisor Bayramoğlu T. H.), *Energy production from yard wastes via one-stage and two-stage anaerobic digestion and investigation of pretreatment effect*, MSc thesis, METU Department of Environmental Engineering, 2020 (https://open.metu.edu.tr/handle/11511/45590). Abstract: "Solubility increase was obtained via AP, TP and UP by 43%, 51% and 17%, respectively. OSAD batch experiments showed that the highest CH4 yield was obtained with AP-yard waste at 5% TS as 313 mL CH4/g VS"; TSAD dark fermentation "30.5 mL H2/g VS"; methanogenesis stage "40 mL CH4/g VS"; "OSAD of yard waste provided 11 MJ/kg VS energy recovery. Yet only 2 MJ/kg VS could be achieved via TSAD"; "TSAD is not sufficient to apply for yard wastes even if it is pretreated with AP, TP and UP." A Turkish-language 2019 conference version exists (https://open.metu.edu.tr/handle/11511/76667, "Bahçe atıklarının biyokimyasal metan potansiyelinin …", 2019-10-11); its PDF (cmo.org.tr) returned HTTP 500 and was not read.
- **KSÜ — park grass waste HBT** — Güler A. S., Üçok S. (Kahramanmaraş Sütçü İmam University), "Biogas production efficiency of park grass waste using HBT method", *Int J Agric & Biol Eng* 18(1), Feb 2025, 299–, DOI 10.25165/j.ijabe.20251801.9070 (resolves, HTTP 302 to ijabe.org; open PDF https://www.ijabe.org/index.php/ijabe/article/download/9070/pdf): "The average cumulative biogas production values ranged from 0.65 to 0.71 m3/kg ODM, while cumulative methane production values ranged from 0.39 to 0.42 m3/kg ODM. The methane content in biogas varied between 59.01% and 60.19%. There was no statistical difference found among methane, biogas, and methane ratios derived from grass materials and silage." Also: "These organic wastes are often left to decay in an uncontrolled manner."
- **Istanbul İBB/İSTAÇ biomethanisation plant (food waste)** — İSTAÇ news (https://www.istac.istanbul/basin-odasi/haberler-ve-duyurular/organik-atiklar-kompost-ve-elektrik-enerjisine-donusuyor): "Günlük 130 ton atık işleme kapasitesine sahip Biyometanizasyon Tesisi ile birlikte İstanbul'da ilk defa kaynağında ayrı toplanan yemek atıkları, sebze-meyve atıkları ve gıda atıkları işlenerek … kompost gübre ve elektrik enerjisine dönüştürülecek. Her gün 40 ton kompost gübre ve saatte 1,4 MW elektrik enerjisi"; "yıllık 81 bin ton sera gazı salımını da önleyerek". KobiEfor, 1 Nov 2022 (https://www.kobi-efor.com.tr/istac-hem-cevreyi-koruyor-hem-ekonomiye-katki-sagliyor): "2021 yılında günlük kapasitesi yaklaşık 130 ton organik atık olan Biyometanizasyon tesisini kurduk." Whether park/garden waste is accepted: the İBB plant page (cevre.ibb.istanbul) timed out (curl and WebFetch 504), so NOT VERIFIED.
- **İzmir Bergama integrated plant (planned 2019)** — e-Belediye, 3 Jul 2019 (https://www.ebelediye.info/haberler/Izmir-buyuksehir-belediyesi-bir-yesil-enerji-yatirimini-daha-hayata-geciriyor): four units "Mekanik Ayırma", "Biyometanizasyon", "Kompost" and electricity; "Biyometanizasyon Tesisi'nde yiyecek ve bahçe atıkları gibi organik atıklar oksijensiz ortamda (reaktörlerde) işlemden geçirilerek elde edilen biogaz elektrik enerjisine dönüştürülmek üzere". Tender stage only; operation and garden-waste tonnage: NOT FOUND.

## Simulators and modeling tools

Simulators found (after check): none added.

- METU applied the IWA ADM1 to the full-scale sludge digester of Ankara Central WWTP: Ozkan-Yucel U. G., Gökçay C. F., 2010 (https://open.metu.edu.tr/handle/11511/56470): "The IWA Anaerobic Digestion Model No. 1 (ADM1) was used to simulate the full-scale anaerobic sludge digester of Ankara Central Wastewater Treatment Plant." This is use of an existing international model on sludge, not a released Turkish tool. A Hacettepe ADM1 manure thesis (hdl.handle.net/11655/3773) returned HTTP 500 and was not used.

## Not taken (unverified)

- İBB Kemerburgaz biomethanisation and compost-plant pages saying park-garden and branch waste are accepted (seen only in search snippets; pages timed out).
- Tezara thesis records on park grass (773823) and autumn leaves (791753) — HTTP 403; not used.

NOT FOUND: a Turkish full-scale digester taking mainly yard/garden waste; national tonnage of yard waste digested; an LCA of yard-waste AD in Turkey; a Turkish HTC or torrefaction pilot for yard waste; a Turkish-developed released digester simulator.

## Method status

No Hermes job (direct research per James t1114u/t1115u). 13 URLs attempted: 7 opened with HTTP 200 and quoted, 2 timed out (İBB), 2 HTTP 403 (Tezara), 2 HTTP 500. One DOI checked (resolves).
