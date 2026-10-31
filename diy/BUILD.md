# BUILD, COMMISSIONING & OPERATION

Get the reviews in SAFETY.md first. Start with the pilot drum rig to measure your feed's gas yield.

## Build steps
1. Site: level gravel/concrete pad, drainage, separation from buildings; layout reviewed for hazardous zones.
2. Bays: set 3 containers; weld/seal floor drain sump to percolate line; install perforated floor (pallet + mesh or slotted HDPE) for drainage; fit a gas-tight liner and a gasketed loading door (critical unknown, see open questions); add gas outlet at the high point with condensate trap.
3. Insulation: 2 layers 2 in polyiso outside or inside under cladding, plus floor insulation; PEX loops on floor and walls.
4. Percolate tank: IBC(s) in an insulated, heated box; submersible pump per bay with check valve; spray bar in each bay roof.
5. Gas train in order per SPEC section 5; leak-test with soapy water at operating pressure before any biogas.
6. Controls: Pi 5 + relay HATs in a ventilated control room OUTSIDE classified areas. Relays switch contactor coils, never motors directly. Hard-wire the gas detector alarm relay and a mechanical high-limit thermostat in series with the heater/pump contactor coils so they trip without the Pi. Wire the flare-path valve normally-open.
   - Wiring: DS18B20s on 1-Wire (GPIO4, 4.7 k pull-up); EZO-pH I2C 0x63 via isolated carrier; ADS1115 I2C 0x48 for pressure/H2S analog; CH4 NDIR on UART; gas meter pulse on a HAT input; hw detector relay on a HAT input.
7. Software: `pip install smbus2`, enable I2C and 1-Wire, finish `PiHardware` drivers for your parts, run `--sim` and tests first.

## Commissioning / startup
1. Pressure-test and leak-check gas train; test every interlock by simulating each fault (test gas for detectors) and confirm outputs go safe and flare valve opens.
2. Water test: fill percolate tank with water, run pumps, verify drainage and level sensor.
3. Inoculum: fill percolate tank with digestate from a working digester (dairy or wastewater plant, with permission) or fresh dairy manure slurry; mix inoculum into first loads (aim ISR ~0.2-0.5 on VS basis [E; 0.22 used in cited pilot]).
4. Heat percolate to 35 C before loading; load bay 1 only, close, purge headspace with biogas or let initial gas vent to flare.
5. Flare everything until biogas CH4 > 45% for several days; then allow boiler use.
6. Stagger bays 2 and 3 by ~2 weeks each so gas output is steady.

## Operating
Daily: check dashboard, alarms, pressure, detector status. Weekly: pH, percolate level, scrubber outlet H2S, VFA/alkalinity test kit if available (target VFA/alkalinity ratio < 0.3-0.4 [E]). Per batch: log feed weight and grass share; keep grass 40-50% of VS.

## Troubleshooting
| Symptom | Likely cause | Action |
|---|---|---|
| pH < 6.5, gas falls | too much fresh grass, VFA build-up | controller pauses recirc below 6.0; add old digestate, reduce recirc rate, add leaves |
| pH > 8.3, gas falls | ammonia from grass-heavy batch | more leaves next batch, dilute percolate |
| CH4 < 45% | air leak, young batch | leak check door/liner; wait if new batch |
| Low temperature | heat loss, low gas | check insulation/boiler, backup heat |
| H2S after scrubber rising | spent iron sponge | regenerate/replace media (outdoors, it heats up) |
| Pressure high | flare/valve blocked, frozen trap | clear trap, check NO valve; controller trips at 2 kPa |
| Trip latched | see dashboard reasons | fix cause, ventilate, reset (refused while unsafe) |
