# Plan: a mashup tool

Written 2026-11-12. Not started: waiting while Jake works with the first Ableton set made this way, so
that anything wrong with the process shows up before it is built into a script.

The aim: give a script some songs and a tempo, and get back an Ableton set ready for making a mashup.
Every song is split into its six stems, every stem is stretched onto one steady grid at the chosen tempo
with bar 1 at the start, and the set holds them grouped by song, named and coloured, so that any bar of
any stem can be cut and dropped on any bar line with no warp markers and no nudging. What key a
mashup should be in is a musical choice, so the tool asks rather than decides; it measures each song's
key and tuning and sets the clips to match once told (see "Tuning").

## Where this comes from

The billie-jean / riders-on-the-storm / planet-claire mashup (mashups/billie-jean-riders/arrangement.md), with toxic
added, was rebuilt on 2026-11-12, by hand in Logic and then with a set generated for Ableton. The steps
that worked, and what was measured, are in Jake's notes, `mashups/billie-jean-riders/process-notes.md`. What was
learnt:

- **The timing has to be fixed on the whole song, before or across all its stems at once.** The first
  attempt split each song into stems and then warped each stem in Ableton. Ableton's auto-warp is good
  on drums but misread billie-jean's bass (it guessed 94 BPM, then put its bars half a beat early), and
  Ableton can't copy one clip's warp markers to another, so every stem needed its own markers by hand.
  Doing it the other way round worked: Logic lined the whole song up with its grid (Smart Tempo, Flex &
  Follow), the result was bounced, and the stems split from that inherited its timing.
- **Even a drum-machine song drifts.** billie-jean's kicks wander up to 65 ms from any steady tempo over
  the song (tape, mastering). riders, a live band, wanders more. Both need lining up beat by beat; pc and
  toxic are steady and a single stretch is enough.
- **A steady stretch can still be a hair off.** Logic gave pc one tempo, and it ended about 25 ms behind
  the grid; toxic came out a fixed 27 ms late. The tool should measure this on every song, not assume it.
- **Songs start partway through a bar.** billie-jean starts half a beat before its first downbeat (a
  hi-hat, then the second half of a bar), so "the start of the file" is not "bar 1". The grid has to be
  anchored on the first real downbeat.
- **Making an Ableton set from a script works.** A set is gzipped XML. The one made on 2026-11-12
  (`mashups/billie-jean-riders/ableton/mashup Project/mashup.als`) took the old set's tracks as templates. Things learnt
  doing it:
  - A clip's tempo is set by its warp markers: two at the start, 1/32 of a beat apart, make a steady
    clip at that tempo (what Ableton writes itself for an unwarped long clip).
  - Every automation and modulation target in the file needs its own number, and `NextPointeeId` must
    be above them all.
  - Clips point at their files relative to the project folder, and Ableton recognises the project folder
    by an empty `Ableton Project Info` folder inside it. Without it, every file "could not be opened".
  - Warp modes are numbered: 0 Beats (drums), 6 Complex Pro (everything else). Track colours are
    numbers in Live's palette (bj 0, riders 22, pc 5, toxic 14).
  - The stems were hard links to the exported files, so the set's folder costs no extra space.

## The tool

`scripts/mashup.py`, run on the Mac:

    scripts/mashup.py --tempo 117 --name mashup  billie-jean.wav riders.wav planet-claire.wav toxic.wav

For each song:

1. **Find the beats and downbeats.** Beat This! (an open-source beat and downbeat tracker, 2024) in
   place of Logic's Analyze. Its result is a list of times, each beat numbered within its bar.
2. **Split it into six stems** from the untouched recording: Demucs's six-stem model (`htdemucs_6s`:
   vocals, drums, bass, guitar, piano, other), as pi-robots' `scripts/stems.py` does with four for the robot's
   tracks.
3. **Stretch the song and its stems onto the grid with one map.** Each found beat is sent to its place
   on a steady grid at the chosen tempo, with the first downbeat on a bar line (the bit before it padded
   so it lands on bar 1's last beats, or on bar 2). Rubber Band does the stretching, following a map of
   where each beat goes (its "time map"). The same map is used for every stem of the song, so they stay
   together to the sample; this is why the split can come first, on the cleaner, unstretched sound.
4. **Check it.** As was done by hand: the drums stem's kicks against the grid, start to end (report the
   worst and any slow drift), and the stems added together against the stretched song.
5. **Estimate its key and its tuning** (pi-robots works out a key from its `pitches.json`). Not every
   recording is tuned to A440: billie-jean sits about 32 cents sharp, riders, pc and toxic about 8 flat.
   See "Tuning" below.

Then the set: a folder `mashups/NAME/ableton/NAME Project/` with `Ableton Project Info`, the stems and
stretched songs in `stems/`, and `NAME.als`:

- the project tempo; each song a group in its own colour, holding the stretched whole song (switched
  off, for reference) and its six stems, named `SONG-vocals` and so on;
- every clip at bar 1, Warp on at the project tempo, Beats for drums and Complex Pro for the rest, no
  transposition;
- the set built from a small template kept beside the script (one group, one audio track, one clip),
  not from any of Jake's sets.

### Tuning (to work out)

A section of the tool, added 2026-11-13, after billie-jean turned out to be about 40 cents sharp of
riders. That's close to half a semitone: the notes can match and still sound sour together. The idea:

- Claude analyses every song and reports its key, how far its tuning is from A440, and, if useful, a map
  of where its harmony moves. The 2026-11-13 map of riders' bars against billie-jean's two bass loops
  (on E and on A) showed this is worth having.
- It then asks Jake what key the mashup should be in and which songs to move, and works out each song's
  transposition (semitones) and detune (cents) to bring them all to one key and one tuning.
- The answers go into the set: every clip of a song (drums can be left alone) gets that Transpose and
  Detune. Clips copied later carry them along. A clip's settings are its own, so fixing them after
  copying means selecting every copy.

Not decided: whether the tool asks its questions as it runs or takes them as options; whether detune is
done in the clips (Ableton's Detune, ±50 cents) or by retuning the stems' audio; and how sure the
analysis must be before it suggests anything.

## Steps

1. **The set builder on its own**, working from stems already made (by Logic, as on 2026-11-12):
   rebuild `mashup.als` from them and compare with the hand-made one. No installs.
2. **The stretching and the checks**, on billie-jean, with Logic's stems from 2026-11-12 as the thing to
   match: Beat This! and Rubber Band installed (only with Jake's go-ahead).
3. **Demucs's six stems**, compared by ear with Logic's on billie-jean, especially guitar and piano.
4. The whole tool, on all four songs; Jake tries the set.

## Open questions

- Is Demucs's six-stem split good enough next to Logic's Stem Splitter? If not, the tool could take
  stems made by Logic and still do the stretching and the set.
- Does Beat This! find riders' downbeats as well as Logic did? A song with a long free intro, a tempo
  change or a bar of 2/4 needs a way to correct the beats by hand (a small file of corrections).
- Half time and double time: pc (141.6) and toxic (about 143) were slowed to 117. Another mashup might
  rather run a song at double or half speed; a per-song choice, `--fit half`.
- Installs: Rubber Band (the command-line tool) and Beat This! (PyTorch, in Apple's arm64 Python as for
  Demucs: this Mac's Homebrew and Python are Intel builds).

## Imperfections found while using the set

(To fill in as Jake works with the 2026-11-12 set; each may change the plan above.)

- **The key showed as C major.** The set's own key was written as E minor (`ScaleInformation` near the
  end of the file: Root 4, Name 1), but in Live 12 every clip also carries a key, and the key menus at
  the top show the selected clip's. The clips, copied from a template clip, were all C major (Root 0,
  Name 0). The tool should give every clip the set's key too (the key setting is then just a label for
  audio clips; it matters to MIDI clips and scale-aware devices). By hand: select every clip
  (Command-A in the Arrangement) and set the key once; it applies to all of them.
- **billie-jean is out of tune with the others.** Measured from the stems: billie-jean about +32 cents
  from A440, riders −8, pc −9, toxic −6. Fix by hand: select every billie-jean clip except the drums,
  copies included, and set Detune to about −40. This led to the "Tuning" section above.
