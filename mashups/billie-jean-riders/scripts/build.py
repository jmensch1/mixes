"""Build a new Ableton set with the 24 grid stems (and each song's bounced grid version, muted), grouped by song,
from the old bj-riders-pc set's tracks as templates. Writes only into the new project folder."""
import gzip, os, re, struct, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
# old.xml: the first set, unzipped (gunzip -c "~/Music/Ableton/bj-riders-pc Project/bj-riders-pc.als"); not kept here
OLD = open(os.path.join(HERE, "old.xml"), encoding="utf-8").read()
PROJECT = os.path.expanduser("~/src/mixes/mashups/billie-jean-riders/ableton/mashup Project")
STEMS = os.path.expanduser("~/src/mixes/mashups/billie-jean-riders/audio/stems")
LOGIC_AUDIO = os.path.expanduser("~/src/mixes/mashups/billie-jean-riders/logic/mashup-grid.logicx/Media/Audio Files")
TEMPO = 117.0
SR = 44100

SONGS = [  # name, group colour (Live's palette index), the clips' own tempo, transposition, bounced grid file
    ("bj", 0, 117.0, -2, "bj-grid.wav"),
    ("riders", 22, 117.0, 0, "riders-grid.wav"),
    ("pc", 5, 116.99, 0, "pc-grid_3.wav"),     # pc falls ~25 ms behind 117 over the song: a hair slower
    ("toxic", 14, 117.0, 0, "toxic-grid.wav"),
]
PARTS = ["vocals", "drums", "bass", "other", "guitar", "piano"]
GRID_START_SAMPLES = {"bj": 10379, "riders": 55618}   # where each bounced song starts after bar 1 (measured); others below


def wav_info(path):
    b = open(path, "rb").read(1 << 16); i = 12; fmt = None
    while i < len(b):
        cid, size = b[i:i+4], struct.unpack("<I", b[i+4:i+8])[0]
        if cid == b"fmt ": fmt = struct.unpack("<HHIIHH", b[i+8:i+24])
        if cid == b"data": return size // fmt[4], fmt
        i += 8 + size + (size & 1)
    raise ValueError(path)


def read_mono(path):
    from wav import readwav
    return readwav(path)


def grid_start(song, gridfile):
    """Samples from bar 1 to the start of the bounced song: line its sum of stems up with it."""
    if song in GRID_START_SAMPLES: return GRID_START_SAMPLES[song]
    g = read_mono(os.path.join(LOGIC_AUDIO, gridfile))
    total = None
    for p in PARTS:
        x = read_mono(os.path.join(STEMS, f"{song}-{p}.wav"))
        if total is None: total = np.zeros(len(g) + SR * 10, np.float32)
        total[:len(x)] += x
    seg = slice(SR * 60, SR * 90); w = SR * 3
    c = np.correlate(total[seg.start - w:seg.stop + w], g[seg], "valid")
    return int(np.argmax(c)) - w


# --- templates ---------------------------------------------------------------------------------------------
def block(tag, ident):
    m = re.search(rf"\t\t\t<{tag} Id=\"{ident}\".*?\n\t\t\t</{tag}>\n", OLD, re.S)
    return m.group(0)

GROUP_T = block("GroupTrack", 36)
AUDIO_T = block("AudioTrack", 21)          # bj-vocals: one warped clip, no devices
CLIP_T = re.search(r"\t*<AudioClip Id=\"0\" Time=\"0\">.*?</AudioClip>\n", AUDIO_T, re.S).group(0)

next_pointee = [30000]
ID_TAGS = re.compile(r"<(AutomationTarget|ModulationTarget|Pointee|[A-Za-z]+ModulationTarget) Id=\"\d+\"")

def renumber(xml):
    def f(m):
        next_pointee[0] += 1
        return f'<{m.group(1)} Id="{next_pointee[0]}"'
    return ID_TAGS.sub(f, xml)

def set_value(xml, tag, value, count=1):
    new, n = re.subn(rf"<{tag} Value=\"[^\"]*\" />", f'<{tag} Value="{value}" />', xml, count=count)
    assert n == count, (tag, n)
    return new

def name(xml, text):
    xml = set_value(xml, "EffectiveName", text)
    return set_value(xml, "UserName", text)

def clip(file_rel, label, colour, frames, seg_bpm, warp_mode, pitch, start_beats):
    beats = frames / SR * seg_bpm / 60
    end = start_beats + beats
    path = os.path.join(PROJECT, file_rel)
    st = os.stat(path)
    c = CLIP_T.replace('<AudioClip Id="0" Time="0">', f'<AudioClip Id="0" Time="{start_beats!r}">')
    c = set_value(c, "CurrentStart", repr(start_beats))
    c = set_value(c, "CurrentEnd", repr(end))
    for tag in ["LoopEnd", "OutMarker", "HiddenLoopEnd"]: c = set_value(c, tag, repr(beats))
    for tag in ["LoopStart", "StartRelative", "HiddenLoopStart"]: c = set_value(c, tag, "0")
    c = set_value(c, "Name", label)
    c = set_value(c, "Color", colour)
    c = set_value(c, "RelativePath", file_rel)
    c = set_value(c, "Path", path)
    c = set_value(c, "OriginalFileSize", st.st_size)
    c = set_value(c, "OriginalCrc", 0)
    c = set_value(c, "LastModDate", int(st.st_mtime))
    c = set_value(c, "DefaultDuration", frames)
    c = set_value(c, "WarpMode", warp_mode)
    c = set_value(c, "PitchCoarse", pitch)
    c = re.sub(  # the clip's own key, the same as the set's: E minor
r"(<ScaleInformation>\s*<Root Value=\")\d+(\" />\s*<Name Value=\")\d+", r"\g<1>4\g<2>1", c)
    c = re.sub(r"<WarpMarkers>.*?</WarpMarkers>",
               '<WarpMarkers>\n\t\t\t\t\t\t\t\t\t\t\t<WarpMarker Id="0" SecTime="0" BeatTime="0" />\n'
               f'\t\t\t\t\t\t\t\t\t\t\t<WarpMarker Id="1" SecTime="{0.03125 * 60 / seg_bpm!r}" BeatTime="0.03125" />\n'
               '\t\t\t\t\t\t\t\t\t\t</WarpMarkers>', c, flags=re.S)
    c = re.sub(r"<ScrollerTimePreserver>.*?</ScrollerTimePreserver>",
               "<ScrollerTimePreserver>\n<LeftTime Value=\"0\" />\n<RightTime Value=\"16\" />\n</ScrollerTimePreserver>", c, flags=re.S)
    return c

def audio_track(track_id, group_id, label, colour, clip_xml, active=True):
    t = AUDIO_T.replace('<AudioTrack Id="21"', f'<AudioTrack Id="{track_id}"', 1)
    t = name(t, label)
    assert CLIP_T in t
    t = t.replace(CLIP_T, clip_xml)
    t = set_value(t, "Color", colour)                     # the track's own colour (it comes before the clip's)
    t = set_value(t, "TrackGroupId", group_id)
    t = re.sub(r"(<Speaker>.*?<Manual Value=\")true(\" />)", rf"\g<1>{'true' if active else 'false'}\2", t, count=1, flags=re.S)
    return renumber(t)

def group_track(track_id, label, colour):
    t = GROUP_T.replace('<GroupTrack Id="36"', f'<GroupTrack Id="{track_id}"', 1)
    t = name(t, label)
    t = set_value(t, "Color", colour)
    return renumber(t)


# --- build ---------------------------------------------------------------------------------------------------
os.makedirs(os.path.join(PROJECT, "stems"), exist_ok=True)
tracks = []; tid = 100
for song, colour, seg_bpm, pitch, gridfile in SONGS:
    gid = tid; tid += 1
    tracks.append(group_track(gid, song, colour))
    # the bounced song, muted, as a reference: it starts a little after bar 1
    rel = f"stems/{song}-grid.wav"; dst = os.path.join(PROJECT, rel)
    if not os.path.exists(dst): os.link(os.path.join(LOGIC_AUDIO, gridfile), dst)
    frames, _ = wav_info(dst)
    start = grid_start(song, gridfile) / SR * TEMPO / 60
    print(song, "grid starts", round(start, 4), "beats after bar 1")
    tracks.append(audio_track(tid, gid, f"{song}-grid", colour,
                              clip(rel, f"{song}-grid", colour, frames, seg_bpm, 6, pitch, start), active=False)); tid += 1
    for p in PARTS:
        rel = f"stems/{song}-{p}.wav"; dst = os.path.join(PROJECT, rel)
        if not os.path.exists(dst): os.link(os.path.join(STEMS, f"{song}-{p}.wav"), dst)
        frames, _ = wav_info(dst)
        mode = 0 if p == "drums" else 6                    # Beats for drums, Complex Pro for the rest
        tracks.append(audio_track(tid, gid, f"{song}-{p}", colour,
                                  clip(rel, f"{song}-{p}", colour, frames, seg_bpm, mode, 0 if p == "drums" else pitch, 0.0)))
        tid += 1

start = OLD.index("\t\t<Tracks>\n") + len("\t\t<Tracks>\n")
first_return = OLD.index("\t\t\t<ReturnTrack ")
xml = OLD[:start] + "".join(tracks) + OLD[first_return:]

xml = xml.replace('<Manual Value="117.120003" />', f'<Manual Value="{TEMPO}" />')
xml = xml.replace('Value="117.120003" />', f'Value="{TEMPO}" />')
song_scale = re.search(r"\t\t<ScaleInformation>\n\t\t\t<Root Value=\"0\" />\n\t\t\t<Name Value=\"0\" />", xml)
xml = xml[:song_scale.start()] + "\t\t<ScaleInformation>\n\t\t\t<Root Value=\"4\" />\n\t\t\t<Name Value=\"1\" />" + xml[song_scale.end():]
xml = re.sub(r"<LoopStart Value=\"136\" />", '<LoopStart Value="0" />', xml)
xml = re.sub(r"<CurrentTime Value=\"[^\"]*\" />", '<CurrentTime Value="0" />', xml, count=1)

ids = [int(x) for x in re.findall(r"<(?:AutomationTarget|ModulationTarget|Pointee|[A-Za-z]+ModulationTarget) Id=\"(\d+)\"", xml)]
assert len(ids) == len(set(ids)), "duplicate pointee ids"
xml = re.sub(r"<NextPointeeId Value=\"\d+\" />", f'<NextPointeeId Value="{max(ids) + 1}" />', xml)

xml_check = xml.encode("utf-8")
import xml.etree.ElementTree as ET   # well-formedness check
ET.fromstring(xml_check)

out = os.path.join(PROJECT, "mashup.als")
if os.path.exists(out): sys.exit("mashup.als already exists: not overwriting")
with gzip.open(out, "wb") as f: f.write(xml_check)
print("wrote", out, len(tracks), "tracks; pointee ids up to", max(ids))
