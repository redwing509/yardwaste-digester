# Bosnia 71 second-slice job files

These files are the Hermes bite-size outputs and the controller citation check for the second slice in `../../71-bosnia-and-herzegovina.md`. The wording in that note is the authoritative, controller-checked text. Official PDFs and eJN HTML were opened for the check and are not committed here.

- `SOURCES.json` — Hermes sources job (24 Nov 2026, 1:09–1:17 PM PST). The job process ended rc 1 after a max-turns message; this JSON was still extracted.
- `VERIFY-S01.json` — news article, verdict TRUE for spliced fragments. The country note uses contiguous page wording and labels the article as secondary.
- `VERIFY-S02.json` — official FPUO March 2026 draft, verdict UNKNOWN (capped extraction; recorded 10% sentence inserted “godine,”). The controller opened the full official PDF and quotes the page wording in the country note.
- `VERIFY-S03.json` — University of Tuzla ADM1 paper, verdict TRUE for two real sentences joined with an ellipsis. The country note quotes those sentences separately.
- `VERIFIED.json` / `VERIFIED-Sall.json` / `EXTRACT.json` — Hermes extract used only verdict-TRUE sources (S01 and S03), so it omitted the official FPUO draft. `EXTRACT-NOTE.md` is the Hermes extract job note, not the country note.
- `CITATION-CHECK-SOURCES.json` — controller fetch of the official PDFs, eJN notices, and the news page.
