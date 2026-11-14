"""Add a "mashup" group at the top of Jake's set, holding a MIDI track "clicks" (the old set's Click Vinyl
Simpler) with one clip: a click on each of the first 16 beats, from bar 1."""
import gzip, os, re
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SET = os.path.expanduser("~/src/mixes/mashups/billie-jean-riders/ableton/mashup Project/mashup.als")
CUR = open(os.path.join(HERE, "current.xml"), encoding="utf-8").read()
OLD = open(os.path.join(HERE, "old.xml"), encoding="utf-8").read()
COLOUR = 23          # Live's palette index: the old set's mashup group colour, unused by the four song groups
GROUP_ID, TRACK_ID = 200, 201
BEATS = 16           # one click per beat for the first 16 beats (4 bars)

assert f'Id="{GROUP_ID}"' not in CUR and f'Id="{TRACK_ID}"' not in CUR

def block(src, tag, ident):
    return re.search(rf"\t\t\t<{tag} Id=\"{ident}\".*?\n\t\t\t</{tag}>\n", src, re.S).group(0)

ID_TAGS = re.compile(r"<(AutomationTarget|ModulationTarget|Pointee|[A-Za-z]+ModulationTarget) Id=\"(\d+)\"")
used = [int(i) for _, i in ID_TAGS.findall(CUR)]
nxt = [max(used + [int(re.search(r'<NextPointeeId Value="(\d+)"', CUR).group(1))])]

def renumber(xml):
    def f(m):
        nxt[0] += 1
        return f'<{m.group(1)} Id="{nxt[0]}"'
    return ID_TAGS.sub(f, xml)

def set_value(xml, tag, value, count=1):
    new, n = re.subn(rf"<{tag} Value=\"[^\"]*\" />", f'<{tag} Value="{value}" />', xml, count=count)
    assert n == count, (tag, n)
    return new

# the group: a copy of the bj group
g = block(CUR, "GroupTrack", 100).replace('<GroupTrack Id="100"', f'<GroupTrack Id="{GROUP_ID}"', 1)
g = set_value(g, "EffectiveName", "mashup"); g = set_value(g, "UserName", "mashup")
g = set_value(g, "Color", COLOUR)
g = renumber(g)

# the track: the old set's click track, its clip replaced
t = block(OLD, "MidiTrack", 39).replace('<MidiTrack Id="39"', f'<MidiTrack Id="{TRACK_ID}"', 1)
t = set_value(t, "EffectiveName", "clicks"); t = set_value(t, "UserName", "clicks")
t = set_value(t, "Color", COLOUR)                       # the track's own colour (the first one in it)
t = set_value(t, "TrackGroupId", GROUP_ID)
clip = re.search(r"<MidiClip Id=\"0\" Time=\"0\">.*?</MidiClip>", t, re.S).group(0)
c = clip
c = set_value(c, "CurrentStart", 0); c = set_value(c, "CurrentEnd", BEATS)
c = set_value(c, "LoopStart", 0); c = set_value(c, "LoopEnd", BEATS); c = set_value(c, "LoopOn", "false")
c = set_value(c, "OutMarker", BEATS); c = set_value(c, "HiddenLoopStart", 0); c = set_value(c, "HiddenLoopEnd", BEATS)
c = set_value(c, "Name", "clicks", count=1)
c = set_value(c, "Color", COLOUR)
c = set_value(c, "GrooveId", -1)
c = re.sub(r"(<ScaleInformation>\s*<Root Value=\")\d+(\" />\s*<Name Value=\")\d+", r"\g<1>4\g<2>1", c)
c = re.sub(r"<AnchorTime Value=\"[^\"]*\" />", '<AnchorTime Value="0" />', c)
c = re.sub(r"<OtherTime Value=\"[^\"]*\" />", '<OtherTime Value="0" />', c)
notes = "".join(f'\n\t\t\t\t\t\t\t\t\t\t\t\t\t\t<MidiNoteEvent Time="{b}" Duration="0.25" Velocity="100" OffVelocity="64" NoteId="{b + 1}" />'
                for b in range(BEATS))
c = re.sub(r"(<KeyTrack Id=\"0\">\s*<Notes>).*?(\s*</Notes>\s*<MidiKey Value=\"60\" />)", lambda m: m.group(1) + notes + m.group(2), c, flags=re.S)
c = re.sub(r"(<NoteIdGenerator>\s*<NextId Value=\")\d+", rf"\g<1>{BEATS + 1}", c)
assert c.count("<MidiNoteEvent ") == BEATS
t = t.replace(clip, c)
t = renumber(t)

start = CUR.index("\t\t<Tracks>\n") + len("\t\t<Tracks>\n")
xml = CUR[:start] + g + t + CUR[start:]
ids = [int(i) for _, i in ID_TAGS.findall(xml)]
assert len(ids) == len(set(ids)), "duplicate ids"
xml = re.sub(r"<NextPointeeId Value=\"\d+\" />", f'<NextPointeeId Value="{max(ids) + 1}" />', xml)
data = xml.encode("utf-8"); ET.fromstring(data)
with gzip.open(SET, "wb") as f: f.write(data)
print("added the mashup group and clicks; ids up to", max(ids))
