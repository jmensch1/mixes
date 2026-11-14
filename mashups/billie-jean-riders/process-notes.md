# Mashup: how it's done

The mashup of Billie Jean (bj), Riders on the Storm (riders), Planet Claire (pc) and Toxic (toxic),
built in Ableton from stems made in Logic. These notes keep only the steps that worked.

## The idea

Line each whole song up with a steady grid **before** splitting it into stems. Stems split from the
lined-up song inherit its timing, so every bar of every stem lands on the grid and can be cut and
dropped anywhere without warp markers.

(Splitting first and warping each stem afterwards doesn't work: auto-warp is reliable only on drums,
and Ableton can't share one clip's warp markers with another.)

## The songs

| Song | Original tempo | Key | Timing |
|---|---|---|---|
| bj | about 117.1, wanders slightly (tape) | F# minor | lined up beat by beat (Logic: var) |
| riders | about 104.8, wanders (live band) | E minor | lined up beat by beat (Logic: var) |
| pc | about 141.6, steady | E minor (by ear, to check) | steady stretch |
| toxic | about 143, steady | usually given as C minor (to check) | steady stretch |

The mashup's grid: **117 BPM, E minor**. bj is transposed down 2 semitones (not its drums), in Ableton.

## 1. The originals

- Copies of the robot project's recordings, in `audio/originals/`:
  `bj-original.wav`, `riders-original.wav`, `pc-original.wav`, `toxic-original.wav`.
- Never drag files from the robot project's `tracks/` folder (`~/src/pi-robots/tracks/`) into Logic: Logic writes into the files
  it's given (it stores its tempo analysis inside them). The copies must stay writable for the same
  reason: a read-only file leaves Logic's File Tempo at 0.00.

## 2. Lining each song up and making its stems (Logic)

One Logic project, `logic/mashup-grid.logicx`, holds all four songs.

1. A new empty Logic project with one audio track, saved straight away as `mashup-grid` in
   `~/Music/mashup` (since moved to `logic/` here; copying audio files into the project).
2. Project tempo **117**; Smart Tempo mode (next to the tempo in the control bar) **KEEP**, so the
   project stays at 117 instead of following the song.
3. For each song, a new audio track; drag the song's original from `audio/originals/` onto
   it at bar 1. Check the region isn't muted (a muted region is dimmed; Control-M unmutes it): a
   muted region bounces as silence.
4. In the Region Inspector, **Flex & Follow: On + Align Bars and Beats**.
5. Double-click the region, open the **Smart Tempo** tab in the editor and click **Analyze**. File
   Tempo in the Region Inspector then reads **var** (bj, riders) or a tempo.
6. Logic moves the region so the song's bars fall on its bar lines; the region's start may sit a
   little after bar 1 (the song starts partway through a bar). Check with the metronome (K) at the
   start, middle and end.
7. **Bounce in Place** (Control-B): name `SONG-grid`, Destination **New Track**, Bypass Effect
   Plug-ins on, volume/pan automation off, Normalize **Off**. The new region's File Tempo reads
   **117.00**: the lining up is now built into the audio. Play it once to check it isn't silent.
8. **Stem Splitter** on the bounced region, all six stems, at the song's own pitch: transposing comes
   later, in Ableton, so the drums aren't shifted and the split works on the untouched sound.
9. Rename the six stem tracks `SONG-vocals`, `SONG-drums`, `SONG-bass`, `SONG-guitar`, `SONG-piano`,
   `SONG-other` (the exported files take the tracks' names).
10. **File › Export › All Tracks as Audio Files** to `~/Music/mashup/stems` (now `audio/stems/` here): WAVE, 24-bit, 44.1 kHz,
    Bypass Effect Plug-ins on, Normalize Off, volume/pan automation off, Range "Trim Silence at File
    End", Include Audio Tail and Include Tempo Information off. Doing several songs before one export
    saves duplicates: each export writes every track again, and files that already exist come out a
    second time with `_1` added (identical; delete them).

Tidying: importing the same file again makes copies named `_1`, `_2` in the project. Rename the track
and region by hand; **File › Project Management › Clean Up** (Delete Backups unticked) removes the
unused copies.

## 3. What came out (checked)

`audio/stems/` holds 24 files, six per song, 24-bit 44.1 kHz. All of them start at **bar 1**
of the 117 grid (the export starts at the project's start, not the region's). Each song's stems add
back up to its bounced song within 2.3 to 3.9%. A stem ends at its own last sound, so lengths differ;
pc's piano stem is near silence (pc has no piano).

Timing of each song's kicks against a steady 117 (measured from the drums stems):

| Song | At the start | Over the song |
|---|---|---|
| bj | on the beat | stays on it (the original drifted by up to 65 ms) |
| riders | on the beat | stays on it |
| pc | on the beat | slowly falls behind: about 25 ms late by the end |
| toxic | about 27 ms late | stays the same: a fixed lateness, no drift |

pc's and toxic's small errors are left for Ableton (next section) rather than redone in Logic.
