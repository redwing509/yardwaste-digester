# Q-02 pre-registered pass/fail band

**Written:** Sat 21 Nov 2026, 11:12 PM PST (America/Los_Angeles, UTC-8), before any
new Q-02 200-day full-state runs were started.

This file freezes the decision rule. It must not be edited to fit later
numbers. Prior S_ac / S_ch4 smoke figures already recorded in
`/workspace/validation-gaps/AUDIT.md` and the 21 Nov 2026 install logs were
not used to choose these percentages.

## Case

Rosen & Jeppsson 2006, section 7: constant influent from Table 5, 200-day
steady state, Q = 170 m3/d, T = 35 °C, HRT = 20 d, V_liq = 3400 m3,
V_gas = 300 m3. The reference values are the opened Table 6 in

https://iwa-mia.org/wp-content/uploads/2019/04/bmadm1_report061127.pdf

copied into `config/rosen-jeppsson-2006-sec7-table6.json`. The comparison is
a BSM2 ADM1 **code-verification** check. It is not a yard-waste feed
prediction, not a 55 °C prediction, and not a DIY leach-bed result.
All results remain model-only.

## Why these percentages (a priori, from the field standard)

Rosen §5.2 reports ODE versus DAE agreement near 1e-6 relative for the
**same implementation family**. That bar is too tight for independently
written codes (QSDsan 1.5.3, PyADM1 commit e7f806e1, and the Matlab
ode15s Table 6 reference). The same report (§5.3, §8.1) treats hydrogen
and especially Qgas as solver- and algorithm-sensitive, calls a hydrogen
dynamic mean error of about 0.01% "acceptable" between its own DAE
variants, and warns that Qgas can change with the integrator and the step
length. IWA BSM practice uses both relative and absolute errors. This
project already pre-registers a 5% engineering band for Fan E-01 current;
well-specified ADM1 liquid COD states should be tighter than that.

## Decision rule (frozen)

Let x be a predicted value after documented unit conversion into the
Table 6 unit, and x_ref the opened Table 6 value.

- If x_ref is not zero: e_rel = |x - x_ref| / |x_ref|.
- If x_ref is zero: the variable passes only if |x - x_ref| <= 1e-12 in
  the Table 6 unit.

A code **PASSES** the Rosen Table 6 check if and only if every required
variable meets its class rule:

- **Class A** (liquid and particulate states 1–7 and 9–26, Qad, Top, pH,
  SIC, SIN): e_rel <= 1.0%.
- **Class B** (hydrogen liquid and gas: Sh2, Sgas,h2, pgas,h2): e_rel <= 5.0%.
  Justification: Rosen §5.3 identifies the hydrogen state as the largest
  DAE difference.
- **Class C** (other gas-phase: Sgas,ch4, Sgas,co2, pgas,ch4, pgas,co2, Pgas):
  e_rel <= 2.0%.
- **Class D** (Qgas at atmospheric pressure, as in Table 6): e_rel <= 5.0%.
  Justification: Rosen §8.1, integrator-sensitive.

**Required variables:** states 1–26, pH, Sgas,h2, Sgas,ch4, Sgas,co2,
pgas,h2, pgas,ch4, pgas,co2, Pgas, Qgas, Qad, Top.

**Optional variables** (reported when a code exposes them; not required
for PASS): acid-base ion pairs and related splits (Sva–, Sbu–, Spro–,
Sac–, Shco3–, Sco2, Snh3, Snh4+, SH+). If reported, they are still
judged by the Class A rule, but a missing optional variable is "not
reported" rather than a completeness FAIL.

If a **required** variable cannot be read after the documented unit
conversion, it is "not reported" and the code **FAILS** for completeness.

A **three-way PASS** requires all of:

1. QSDsan 1.5.3 PASSES versus Table 6.
2. PyADM1 e7f806e1 PASSES versus Table 6. The official `simulate()` plus
   `DAESolve()` loop at 0.25 d steps for 200 days is the only accepted
   PyADM1 method. A single 200-day BDF call without `DAESolve` is not a
   valid check (documented in the 21 Nov 2026 install note).
3. Code-to-code: every required variable also meets the same class rule
   when x_ref is replaced by the other code's value (Table 6 units).

If only one code can be run, report the one-way Table 6 check and do not
declare a three-way PASS.

Pinned versions: QSDsan 1.5.3 / EXPOsan 1.5.3 / BioSTEAM 2.54.0;
PyADM1 commit e7f806e1984a382ce6d6c17ad595561e3e8b293d.
