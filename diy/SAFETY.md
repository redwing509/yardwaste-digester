# SAFETY & REGULATORY

**Disclaimer:** This is an unreviewed draft. It is not a certified design and the software is not a
safety-rated system. Do not build, energize or fill anything until a licensed professional engineer,
a licensed electrician experienced with hazardous (classified) locations, and your permitting
authorities have reviewed the actual build. You assume all risk.

## Hazards
- **Explosion/fire:** methane is flammable roughly 5-15% in air. Biogas + air in a bay, bag or room can explode. No ignition sources near gas equipment; vent and purge before opening bays.
- **H2S:** toxic, deadens sense of smell at higher levels; can kill quickly at high concentration. Never rely on smell.
- **Asphyxiation/confined space:** a digester bay or tank is a permit-required confined space; entry under a confined-space program (WA: WAC 296-809) with gas testing, ventilation and an attendant.
- **Others:** heavy loads, loaders, electrical, hot water, frozen condensate blocking relief paths.

## Required gear
Personal 4-gas meter (LEL, O2, H2S, CO), fixed CH4 and H2S detectors with relay, ABC extinguishers, no-smoking/no-spark signs, intrinsically safe or rated flashlight, PPE (gloves, eye protection), lockout/tagout kit, confined-space gear if entry is ever planned.

## Electrical code
Areas around gas equipment are hazardous (classified) locations under NFPA 70 (NEC) Articles 500-505;
classification guidance in NFPA 497. Equipment in Class I Div 1/2 (or Zone) areas must be rated for it or
located outside the classified area. The Pi, relays, sump pump motors and boiler controls in this design are
NOT hazardous-location rated: put them in a separate ventilated room outside the classified zone, and have an
electrician design the area classification, seals and wiring. WA electrical work requires L&I permits/licensed electricians.

## Washington permits (verify; not legal advice)
- Ecology's on-farm digester exemption (WAC 173-350-250) is built around livestock manure (>= 50% manure); a yard-waste-only digester likely does **not** qualify and probably needs a solid-waste handling permit from the local health jurisdiction (Spokane: Spokane Regional Health District). Sources: https://apps.leg.wa.gov/wac/default.aspx?cite=173-350-250 , https://www.ecology.wa.gov/waste-toxics/reducing-recycling-waste/organics-and-food-waste/anaerobic-digesters
- Air: flare/boiler may need registration with the local clean air agency (Spokane Regional Clean Air Agency).
- Building/fire: county building permit and fire marshal review for gas storage and the flare.
- Digestate land application: nutrient management; check Ecology and WSDA rules.
