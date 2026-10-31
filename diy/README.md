# DIY Yard-Waste Digester: Open Build Spec

An open design for a farm-scale **batch dry (leach-bed) anaerobic digester** for grass silage + leaves,
built from off-the-shelf parts, with Raspberry Pi control code (Python, MIT).

> **DRAFT / NOT REVIEWED.** Biogas is flammable and H2S is lethal. Nothing here is a certified design.
> A licensed engineer, an electrician familiar with hazardous locations, and your local permitting
> authority must review any real build. See SAFETY.md.

| File | Contents |
|---|---|
| SPEC.md | Process choice, sizing math, diagram, heating, gas train, digestate |
| BOM.csv | Parts with sourced prices and links (blank = not yet priced) |
| BUILD.md | Build steps, wiring, commissioning, operating & troubleshooting |
| SAFETY.md | Hazards, gear, WA permits, electrical code, disclaimer |
| src/digester | Controller, simulator, dashboard, sizing calculator |
| tests/ | Unit tests (`python3 -m unittest discover -s tests`) |

Quick start (no hardware):
```
PYTHONPATH=src python3 -m digester.main --sim --hours 48 --web   # dashboard on http://127.0.0.1:8080
PYTHONPATH=src python3 -m digester.sizing
python3 -m unittest discover -s tests -v
```
Python 3.10+, stdlib only for sim/tests; `smbus2` on the Pi.

Why Raspberry Pi + Python (not ESP32): the job needs CSV logging, a web dashboard and readable,
testable logic more than microsecond timing; Python on a Pi lets farmers read and change it and lets the
same code run in the simulator and tests. Fast safety does not depend on it: a hard-wired gas detector
relay and a mechanical high-limit cut power independently of the Pi.
