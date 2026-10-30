# Throne of Darkness: its files

What the game's files hold and how they're laid out, worked out from the
files alone (nothing taken from Throne.exe). "Guess" marks what isn't
proven yet.

The game: the GOG copy at `D:\Games\Disciples 2\Throne of Darkness`,
v1.2.18 (Patch 2), Click Entertainment 2001. Its data is in
`LotFiles\*.lot` (1.2 GB). `Config\Throne.cfg` holds the player's settings
in UTF-16; `options.cfg` and `DedicatedServer.cfg` are plain text.

The Python prototypes in `tools\` read everything described here.


## .lot archives

A .lot is its files' data, then a packed directory, then a u32: the size
of that directory.

Everything packed (each file, the directory) is a run of blocks closed by
a 0 byte. A block starts with its kind:

- low 7 bits: 4 = LZO1X, 1 = stored as is
- 0x80: a small block, its sizes one byte each

then its size − 1 and its packed size − 1 (u16 each, or u8 in a small
block), then the packed bytes. A block unpacks to 64 KB at most. The LZO
is the standard LZO1X (it ends with `11 00 00`).

The directory, unpacked: u32 `0xBEEFFACE`, then the root folder. A folder
is u32 file count, the files, u32 subfolder count, the subfolders (u8
name length, name, then the folder). A file is u8 name length, name, u32
size, u32 offset in the archive, u32 kind (0 = blocks, 1 = raw bytes, as
the movies and music in Stream.lot are) and a u32 that's always 0.

| Archive | Files | What's in it |
|---|---|---|
| Base.lot | 2,474 | 2,226 sprites (interface, fonts, cursors, effects), 234 sounds |
| Characters.lot | 1,240 | monsters and people: 774 sprites, 465 sounds |
| Samurai.lot | 1,711 | the seven samurai: 831 sprites (armour × weapon × action), 880 sounds |
| Config.lot | 2,431 | 1,213 XML files, each also compiled to .xml.bin; default.cfg, options.cfg |
| Quests.lot | 395 | 10 .seq scripts, 384 spoken lines (.wav) |
| World.lot | 2,491 | World.ini and 55 levels: .lex, .rex, .mp/.sp, Map.map |
| Stream.lot | 29 | 19 Bink movies, 9 MP3 tracks (raw) |
| LoadSequence.lot, Patch2.lot | ? | encrypted (below) |

**Encrypted: LoadSequence.lot and Patch2.lot.** Their directory is a
16-byte stored block (u32 1, `0xBEEFFACE`, u32 1, a u32 that looks like a
key) and then bytes that look random (116 in LoadSequence, 20,185 in
Patch2); their file data looks random too. It's not a repeating XOR, nor
the MSVC, Borland, glibc or Numerical Recipes generators XORed or added
with that key. In each archive the file data and the directory's
encrypted part start with the same byte, so the cipher seems to start
over for each piece. Patch2 holds v1.2.18's changes (fixes, the
Chil-ji-do weapon, free key binding); the other archives are a whole game
without it.


## .s8 sprites

`SPR8v3.1`, then:

| at | what |
|---|---|
| 8 | u32 file size |
| 12 | 4 × u16: a box round all frames (order unsure) |
| 20 | u16 1, u16 frame count, u16 1, u16 0, u32 0 |
| 32 | u32 where the palette is |
| 36 | u32 where the frame table is (40): a u32 offset per frame |

The palette: a u32 (its colours' own offset), then 256 colours, RGB565.
Colour 0 is `0xF81F`, magenta, the see-through key. The other 255 are 16
ramps of 16 shades, each ramp rising from black: a pixel's high nibble
picks the ramp, its low nibble the shade. Guess: the engine lights pixels
by moving along the ramp (Throne.cfg has light radius settings).

`PAL_n.s8` files are one-frame sprites that only carry a palette: colour
variants of the same drawings (monsters have up to six, samurai armour
four).

A frame: u16 canvas width and height (640 × 480 for characters, who stand
at its centre: every samurai's frames are centred across it, and drawn so
in the game their feet meet the spot they stand on), then top, bottom, left and right of
what's drawn, u16 0, u16 1. Then its rows, top first. Each byte's low 2
bits say what it is and its high 6 bits are a number n:

- `00`: skip n see-through pixels
- `01`: one pixel with alpha n (0–63); its colour is the next byte
  (soft edges, hair, smoke)
- `10`: the next row, starting after n see-through pixels
- `11`: n + 1 solid pixels; their colours follow

A frame's bytes are padded to an even count with a 0.

One file holds a whole action: 8 directions × its frames, direction by
direction — toward the viewer (down the screen) first, then turning
clockwise as seen on the screen: down-left, left, up-left, up, up-right,
right, down-right. A monster's run is 80 = 8 × 10; a samurai's run 96 =
8 × 12, its standing (neutral) 80 = 8 × 10. Checked by drawing them
(`pictures\bake_run.png`: the haunted armour, BakeYoroi, running) and by
the game: samurai walking left and down-right face that way.

Fonts (Base.lot, `Fonts\ANIM_<name>\000.s8`: AndySmall, ChatFont, Console,
GameFont, Georgia24, Scar24, ToolTip, …) are sprites of 256 frames, frame
k the character k; a frame's box on its canvas (8 × 16 for the chat font)
is the letter, its right edge where the next starts. Empty frames (the
control characters) still hold one stored pixel, as palettes' frames do.

Where they are: `Characters\<Name>\Weapon<n>\ANIM_<action>\*.s8` for
monsters and people, `Characters\<Class>\Armor<n>\Weapon<n>\ANIM_<action>`
for the samurai. Actions: attack, attack2, death, hit, jump, neutral, run,
special. The action's sounds sit beside it (`...Attack1.WAV`). Portraits:
`Head\ANIM_Head01\Head.s8` (48 × 60). Interface folders have a
`files.txt` listing their sprites, each with a number after it (0, 1, 2:
meaning not known).


## Levels (World.lot)

`World\World.ini` has a line per level: name, folder, LEX file, FUR file,
music, ambient light, environment type (for the sound: castle, cave,
wilderness, …) and the name shown on the map. Its own comments explain
the columns. 55 levels: four samurai citadels of four to six rooms each,
the Dark Warlord's citadel, four wilderness quarters, mountainsides and
caves.

A level's place is in its own pixels, down the screen positive: an
isometric picture of it, as the game drew it (the shrine is about 2100 ×
1200; its floor's diamond tiles, 512 × 256, step 256 across and 128 down).
The window shows 800 × 600 of it round the player.

A level's folder holds:

- **.rex**, a bundle of what the level shows and plays: `IRES`, u32
  count, then entries (4 letters for the kind: `RSND` sound, `RANI`
  animation, `RGRA` picture, `RPLT` palette; u8 name length; name; u32
  where its chunk is), then the chunks: `IDAT`, the kind again (where the
  entry points), u32 size, the bytes. A picture or an animation is a .s8
  with no palette of its own (its palette offset is its first frame's); a
  palette is 512 bytes, 256 colours in RGB565 and nothing else; a sound
  is a RIFF WAV. A room's furniture set is `<FUR>(FUR).rex`. The
  wilderness also comes in pieces, `Quad_01(x,y).rex`, a grid; their
  entries carry 16 more bytes (where it goes? not decoded). The biggest
  bundle is 10.7 MB.
- **.lex**, the layout: a header (800, 600, 4 in every level: the screen
  it was made for, a guess), then `IRES` and a table like the bundle's —
  but in place of where each resource is, its size: a picture (RGRA) its
  width and height, an animation (RANI) its width, height and frames, a
  palette or a sound nothing (so in all 55 levels). Then `IGRL` (u32 0),
  `IOBJ` (u32: how many things follow) and the things, each a 4-letter
  tag and its fields, drawn in their order:
  - `EGRA`, a picture placed: i32 x, y (its canvas's top left), 2 numbers
    (0, 0 or 0, 65536), its resource, its palette (numbers in the table),
    and some a count after (1–3) with as many `OCOL`s following.
  - `EANI`, an animation placed: i32 x, y, its kind (u8 length, text:
    `AnimRunLooped`), 7 bytes, its resource, its speed (f32, 1.0), 1, 0.
  - `OCOL`, an outline: u32 count, the points (i32 x, y each), more after
    (not worked out). It belongs to the record before it: after a picture
    or animation it's where that stands (a wall's runs along its foot, a
    piece of furniture's footprint, the portal's disc); after an `ECOL` it's
    that record's. Not closed: a polygon's last point isn't joined back.
  - `ECOL`, a collision record of its own, with an `OCOL`: plain (no
    properties: the shrine's front edges, 133,1094 – 1148,1602 –
    2175,1090, where no wall is drawn), a named spot (`Name "MORISHRINE"`:
    one point, the .stripped.sp spots), or an area that sets off an event
    when entered (`TriggerEvent`, its event's name: `SQ01_ShrineRoom`).
    `throne picture … collision` (F2 in the game) draws them all: things'
    outlines yellow, plain lines orange, events' areas blue, spots pink.
  - Stairs, a level's ways to the next: a group (`EGRP`) with two
    properties (each a u8 length and its name, a u8 length and its value
    in quotes) — `TheDestLevel "Citadel1_Bedroom"`, `TheDestPointName
    "BottomOfStairs"` — then a script record, `ESRT` `TriggerStairs`
    (u32 2, its params `DestLevel ::TheDestLevel`, `DestPointName
    ::TheDestPointName`), then the bytes 0, 1, 0, 1 and its place, i32 x,
    y, on the stairs' picture (the shrine's: 1564,1287; the stairwell
    at 1527,1233 is the picture after it). The Mori citadel's rooms are a
    chain by them: Ground Floor ↔ Throne Room ↔ Dining Room ↔ Bedroom ↔
    Shrine, each way arriving at the named spot BottomOfStairs or
    TopOfStairs, 80 to 120 pixels from the stairs back. The Ground Floor's
    door to the outer citadel (INSIDEOFDOOR, OUTSIDEOFDOOR) is something
    else, not found yet. How the game set the stairs off (walking onto
    them, a click) isn't known: throne takes them when a player walks into
    40 pixels of the place, and moves the whole party.
  - `ELIT` lights (x, y, a radius?), `ESND` sounds, `ESRT`, `EGRP`
    (groups?), `EMLT` (things with states: the portal; `ParentGenerator
    "Chest#A"` before each of the shrine's two chests, which are animations
    placed), `SNDJ`, `CHRW`: not worked out; some hold text and parts of
    their own, so their sizes aren't known yet. The picture, animation and
    outline records are found by their tags, each checked against the
    table or the file's size.
  Checked by drawing the shrine (tools/level.py, then the game): every
  picture where it belongs, the walls on their outlines, nothing missing.
  The busiest layout (the Oda wilderness) places 8,439 pictures.
- **.walk.mp / .walk.sp**, where one can walk: u32 0, u32 width, u32
  height (cells; the shrine 200 × 200, the biggest 1200 × 2300, a
  wilderness), then blocks to the file's end, each a byte (its size less
  1: `0xFF` for 256) and its bytes — the same size-less-1 habit as the
  archives' blocks. The blocks' bytes joined are LZW, from their bit 3:
  9-bit codes, a bit wider each time the table fills its width (to 12),
  lowest bit first, new entries from 256, no clear or end codes; at 4096
  entries the table starts over (9 bits, none past the bytes, the next
  code a first one). Unpacked: a bit per cell, row by row, the low bit
  of each byte first (as the codes go), 1 blocked — width × height bits
  exactly, all 110 of the game's files (Mara's lzw.mara and tools/walk.py
  agree on them, open cell for open cell). The rows run from the level's
  far end (the first row is the one lowest on the screen).
  (Read high bit first, every run of 8 cells comes out backwards: the
  shrine's floor showed a blocked band 4 cells in from its bottom-right
  edge, an open strip 4 cells past its bottom-left wall, and furniture's
  blocks beside the furniture. Lowest first, its open cells are one piece
  that fills the room to its walls' feet on all four sides.)
  A cell is a 32 × 16 diamond of the level's pixels: cell gx of row up
  (counted from the far end) has its middle at x0 + (gx − up) × 16,
  y0 + (gx + up) × 8. Where (x0, y0) lies isn't known yet: for the shrine
  it's (1612, −215), fitted by tools/walk_fit.py on the outlines' wall
  lines (open on the room's side) and its named spots, and checked by
  eye with tools/walk.py: the open area meets the back walls' outlines
  and the front edges' (the shrine's last OCOL, 133,1094 – 1148,1602 –
  2175,1090) all round. The Citadel02 shrine (the same 200 × 200) fits
  at (1612, −200), but the Citadel03 shrine at (1482, 500): each level
  has its own corner, or it follows something not found yet (the lex
  header holds only 800, 600, 4; `IGRL` is 0).
  tools/walk_fit.py now takes each wall line's open side from what its
  outline belongs to (a picture's wall foot: open below; a plain ECOL
  front edge: open above), and finds the shrine again (1608, −213). The
  bedroom (200 × 300, two rooms in an L) won't fit: one corner puts the
  tatami room right and the other room off its walls, another (63 cells
  along) the other room right and the tatami room off — something about
  a grid that isn't square isn't understood yet (its axes?), so it and
  the other rooms are walked anywhere.
  The shrine's grid blocks two table-sized spots of bare floor just in
  front of its two low tables (in both mp and sp): the game's own data —
  the tables moved after the grid was made, perhaps. Most furniture
  isn't in the grid at all (chests, screens, the rack, the tables
  themselves): their outlines (OCOL) may be what stops one there. mp and
  sp differ a little (the shrine: 17 cells, the folding screen by the
  front corner blocked in sp only): multiplayer and single player
  (guess).
- **.stripped.mp / .sp**: named spots: u32 0, u32 count, then each a u8
  name length, its name, i32 x, i32 y in the level's pixels (the shrine's:
  `1` at 813, 689; `DIAMYOITEM01` at 878, 782, beside the dead body;
  `MORISHRINE` at 1210, 1283, beside the portal; `TOPOFSTAIRS` at 1445,
  1292, beside the stairs). What the scripts point at.
- **.order.mp / .sp**: lists of u32 numbers: an order of some kind
  (drawing? spawning?).
- **Map.map**: the map screen's picture of the level; the same LZW after a
  short header.


## Configuration (Config.lot)

XML for the characters (stats, weapon skills, attacks, AI), items (59
files, plus random generators), spells, every interface screen's layout,
and the warlords. Each .xml has an .xml.bin twin, the game's compiled
form (itself packed in blocks inside the archive's blocks). The XML text
is enough; the .bin files can be left alone.

`.cfg` files are console scripts in Quake's manner: `seta "Name" "value"`,
`set`, `setr`, `bind`.


## Scripts (Quests.lot)

`.seq` files run the quests and dialogue. C-like: `const`, nested tables
(a spoken line is its text and its .wav), if/else, labels and
`GotoLabel`, waits (`WaitForEvent(thing, EVENT_ACTION_CLICK)`, `…_ENTER`,
`…_DONE`), engine calls (`CharacterSpeak`, …), `include_file`, and
sections kept or skipped by game mode (`__skip_if_multiplayer__` …
`__skip_end__`). Each quest reads like a thread that waits on events. It
needs an interpreter and the engine calls the scripts use.


## Sound, music, movies

- Sounds: RIFF WAV, 16-bit PCM (22 kHz seen).
- Music: MP3, in Stream.lot's `Music\`.
- Movies: Bink (`BIKf`), in Stream.lot's `Movies\`: logos, the intro, the
  ending, quest scenes. Playing them needs a Bink decoder.


## Still open

- The encryption of Patch2.lot and LoadSequence.lot.
- The walk grid's LZW rule; then the map pictures.
- The wilderness .rex entries' extra bytes, the .lex records' fields,
  what .order is.
- The order of the sprite file's box; files.txt's numbers.
- How the shade ramps are lit.
