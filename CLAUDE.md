# mixes

Jake's mixes and mashups, made in Logic Pro and Ableton Live (12, Suite trial at first) on the Mac. It
is his own music project; it split off on 2026-11-13 from the dancing-robot project (`~/src/pi-robots`),
where the first mashup began because the robot dances to some of the same songs.

## What is here

    docs/mashup-tool-plan.md     a plan for a script that preps songs for a mashup (not started)
    docs/ableton-and-logic.md    how Ableton and Logic behave, as learnt so far
    mashups/NAME/                one mashup each:
        *.md                     notes: the arrangement, the process that worked, analyses
        ableton/NAME Project/    the Ableton project (the .als in git, its audio not)
        logic/*.logicx           the Logic project (its project data in git, its Media/ not)
        audio/originals/         copies of the songs as recorded (not in git)
        audio/stems/             the stems the set uses (not in git)
        scripts/                 one-off analysis and set-building scripts for this mashup

The first mashup is `mashups/billie-jean-riders/`: Billie Jean, Riders on the Storm, Planet Claire and
Toxic at 117 BPM in E minor. Start with its `process-notes.md`.

## Audio is not in git

Sets, notes and scripts are; audio files are left out (`.gitignore`): there are gigabytes of them, they
rarely change, and git would keep a second copy. Time Machine backs them up. A fresh clone of this
repo therefore can't play anything; the working folder on this Mac is the one that counts.

`.gitattributes` marks `.als` files (gzipped XML) so git can show what changed in one, with this local
setting (not stored in the repo; run once per clone):

    git config diff.als.textconv "gzip -dc"

## Working together

- **Jake does the Ableton and Logic steps himself**; he wants to learn the tools. Explain where things
  are and why, step by step, in plain words. Live 12 and Logic change their menus between versions:
  when unsure where something is, ask for a screenshot rather than guess.
- **Claude edits an Ableton set directly only when asked, and only after Jake has saved and quit
  Ableton**, with a copy of the set first in the project's `Backup/` folder. Check the edit (the XML
  parses, the numbers are unique: see docs/ableton-and-logic.md) and ask Jake to open it and check.
- Claude can read a saved set and report on it (clips, pitch, detune, warp), and analyse audio
  (timing against a grid, key, tuning) with Python and numpy.
- Never drag files from `~/src/pi-robots/tracks/` into Logic or Ableton: Logic writes into the files
  it's given. Work from copies (`audio/originals/`), and keep them writable.
- Process notes record only what worked, not the experiments that didn't.
- Before any script is written, problems found while using a set go into the plan
  (docs/mashup-tool-plan.md, "Imperfections found while using the set").
- Jake makes the commits, or asks for one. Packages and installs need his go-ahead.

## Python

The Mac's Homebrew and `python3` are Intel builds running under Rosetta: no wheels for PyTorch and
friends. Apple's `/usr/bin/python3` is arm64 and is what Demucs and PyTorch work with. The scripts here
so far need only numpy; they were run with `~/src/pi-robots/.venv/bin/python` (a venv of this repo's own
is still to make). Run a script from its own folder (it imports `wav.py` beside it).
