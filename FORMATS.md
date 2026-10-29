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

A frame: u16 canvas width and height (640 × 480 for characters; guess:
the character stands at its centre), then top, bottom, left and right of
what's drawn, u16 0, u16 1. Then its rows, top first. Each byte's low 2
bits say what it is and its high 6 bits are a number n:

- `00`: skip n see-through pixels
- `01`: one pixel with alpha n (0–63); its colour is the next byte
  (soft edges, hair, smoke)
- `10`: the next row, starting after n see-through pixels
- `11`: n + 1 solid pixels; their colours follow

A frame's bytes are padded to an even count with a 0.

One file holds a whole action: 8 directions × its frames (a run is 80 =
8 × 10). Checked by drawing them: `pictures\bake_run.png` is the haunted
armour (BakeYoroi) running, all 80 frames.

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

A level's folder holds:

- **.rex**, a bundle of what the level shows and plays: `IRES`, u32
  count, then entries (4 letters for the kind: `RSND` sound, `RANI`
  animated sprite, `RGRA` picture, `RPLT` palette; u8 name length; name;
  u32 where its data is), then `IDAT` chunks (kind, u32 size, the bytes:
  a .s8 or a RIFF WAV). A room's `(FUR).rex` is its furniture set. The
  wilderness comes in pieces, `Quad_01(x,y).rex`, a grid; their entries
  carry 16 more bytes (where it goes? not decoded).
- **.lex**, the layout: a header (the shrine's says 800 and 600: its size,
  guess), a copy of the .rex's table, then placed things: `EGRA` records
  with x, y, an index into the table and flags (guess).
- **.walk.mp / .walk.sp**: u32 0, u32 200, u32 200, then LZW (9-bit codes,
  lowest bit first) over a bitmap, 1 bit per cell: where one can walk.
  My decoder gets 60% through before a code runs ahead of its table, so
  one dictionary rule is still off. mp and sp differ a little:
  multiplayer and single player (guess).
- **.stripped.mp / .sp**: named spots with positions (`MORISHRINE`,
  `TOPOFSTAIRS`, `DIAMYOITEM01`): what the scripts point at.
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
