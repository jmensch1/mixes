# Scripts used for this mashup

One-off scripts, written while making it (2026-11-12 and 13), kept as a start for the tool in
docs/mashup-tool-plan.md. Rough and specific to these songs. Run them from this folder (they import
`wav.py`), with a Python that has numpy. Their paths were changed to this repo's folders when the
mashup moved here; they haven't been run since.

| Script | What it does |
|---|---|
| `wav.py` | Reads a WAV (16/24-bit or 32-bit float) into mono floats |
| `gridcheck.py FILE BPM` | Finds the kicks in a drums file and reports how far they sit from a steady grid, every 20 s |
| `stemgrid.py`, `stemgrid_r.py` | billie-jean's and riders' stems against their bounced song: offset, and how closely they add back up |
| `checksong.py SONG GRIDFILE` | The same for any song |
| `build.py` | Built `ableton/mashup Project/mashup.als` from the stems, using tracks of the first set as templates (needs `old.xml`: see its top) |
| `add_mashup.py` | Added the "mashup" group and its "clicks" MIDI track to the set (needs the set unzipped as `current.xml`) |
| `keymap.py SONG` | The key, bar by bar, from the pitched stems, and each bar's bass note |
| `tuning.py SONG...` | Each song's tuning in cents from A440 |
| `fit.py`, then `fit2.py` | Riders' bars against billie-jean's two bass loops: the analysis behind `riders-over-billie-jean.md` |
