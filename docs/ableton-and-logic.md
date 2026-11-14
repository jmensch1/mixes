# Ableton and Logic: what has been learnt

Gathered while making the billie-jean / riders mashup (2026-11). Ableton Live 12.4 (trial), Logic Pro.

## Ableton Live

**Warping**
- With Warp on, a clip follows the set's tempo: change the tempo and every warped clip follows.
- A clip's **Seg. BPM** is the tempo Ableton thinks the audio is at; for a clip already on the grid
  (as the stems here are), it is the grid's tempo.
- Warp modes: **Beats** for drums, **Complex Pro** ("Pro" in Live 12) for everything else.
- **Auto-warp is unreliable except on drums**: it read billie-jean's bass as 94 BPM and put its bars
  half a beat early. And one clip's warp markers can't be copied to another, so warping every stem by
  hand doesn't scale. Fix the timing on the whole song before splitting it (see the Logic steps in
  `mashups/billie-jean-riders/process-notes.md`).

**Clips**
- Every clip keeps its own settings (Pitch, Detune, warp, gain, key). A copy takes the settings the
  original had when it was copied; changing one later doesn't change the other. To change many, select
  them all (drag across tracks, or Command-click) and set the value once in the Clip view.
- In Live 12's Clip view the **Pitch** knob is the transposition in semitones; the two boxes under it
  are the semitones and, unlabelled on the right, the **detune in cents** (±50).
- Live 12 clips carry their **own key** (Scale, in the Clip view); the key menus at the top show the
  selected clip's key, not the set's.
- Stereo files show two waveforms per clip: left on top, right below.

**Tracks**
- There is no setting to give a new track the colour of the one above it. Duplicate a track instead
  (Command-D: same colour, group, devices, warp settings) and delete its clips; or select tracks
  together and pick the colour once.
- **Grooves**: right-click a clip › Extract Groove(s) puts its timing in the Groove Pool; a clip given
  that groove (Clip view › Groove) at Timing 100% moves its notes to that timing, on a 16th grid.
  **Command-U** quantises a warped audio clip's transients to the grid.

**Saving and history**
- Ableton shows only the last change (Edit › Undo ...); there is no list of changes. Each save moves
  the previous version into the project's `Backup/` folder (about ten kept). Git and a script that
  summarises two versions of an `.als` are the way to see what changed.

**Sound**
- If playback stops or nothing plays, check Settings › Audio › Output Device: unplugging headphones
  left it at "No Device".

**The `.als` file** (gzipped XML; how a set can be written or edited by a script)
- Copy track templates from an existing set rather than writing them from scratch.
- Every `AutomationTarget`, `ModulationTarget`, `Pointee` and `...ModulationTarget` element needs a
  unique `Id`, and `NextPointeeId` must be above them all: renumber whatever is copied.
- A clip's tempo comes from its warp markers: two at the start, 1/32 of a beat apart
  (SecTime 0 / BeatTime 0 and SecTime 0.03125·60/bpm / BeatTime 0.03125), make a steady clip at bpm.
- `WarpMode` 0 is Beats, 6 is Complex Pro. `PitchCoarse` and `PitchFine` are Pitch and Detune.
  Colours are indexes into Live's palette.
- Files are found relative to the project folder (`RelativePathType` 3), which Ableton recognises by
  an `Ableton Project Info` folder inside it, even an empty one. Without it every file "could not be
  opened". So a whole project folder can be moved; its audio can be hard links to files elsewhere.
- The set's key is the `ScaleInformation` near the end of the file (Root 4, Name 1 is E minor); each
  clip has its own `ScaleInformation` too.

## Logic Pro

- **Logic writes into the audio files it's given** (its tempo analysis): only ever give it copies.
  A read-only file leaves Smart Tempo's File Tempo at 0.00.
- Lining a song up with a steady grid: project tempo set, Smart Tempo mode **KEEP**; the region's
  Flex & Follow **On + Align Bars and Beats**; **Analyze** in the editor's Smart Tempo tab. File Tempo
  then reads "var" (a wandering song) or a tempo. Then **Bounce in Place** with effects bypassed.
- A **muted region bounces as silence** (dimmed region; Control-M unmutes).
- **Stem Splitter** gives six stems: vocals, drums, bass, guitar, piano, other.
- **Export All Tracks as Audio Files** writes every track each time; files that exist come out again
  with `_1` added (identical copies).
- Importing the same file again makes `_1`, `_2` copies in the project; File › Project Management ›
  Clean Up removes unused ones.
- A Logic project created with "copy audio files into project" holds its audio inside the `.logicx`
  package, so it can be moved as one.

## Measuring audio (what the scripts do)

- **Timing**: kicks found in a drums stem, compared with a steady grid (median and spread every 20 s).
- **Key**: pitch-class energy per bar, matched against major and minor key profiles over a few bars.
  It can't tell modes apart that share notes (E Dorian and B minor look the same); the bass shows
  which note a passage rests on.
- **Tuning**: strong spectral peaks of the pitched stems, folded onto one semitone; the average
  offset is the song's tuning in cents from A440. billie-jean measured about +32, riders −8, pc −9,
  toxic −6.
