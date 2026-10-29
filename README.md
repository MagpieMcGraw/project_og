# sothrone

A source port of Throne of Darkness (Click Entertainment, 2001) in Mara,
reading the game's own files. Nothing is decompiled: the formats are
worked out from the data (FORMATS.md). Part of og, a source port of every
game, so what isn't Throne-specific should be written to be shared.

The game is all 2D: pre-drawn sprites in 8 directions, 16-shade colour
ramps, rooms and a wilderness built from placed pictures, up to 8 players
together. Quests are scripts that wait on events.

What's shared with the other ports (sooblivion so far) is written down in
C:\Code\project_og.md.


## Building and running

`build.bat` builds sothrone.exe with the project's own copy of the Mara
compiler (`compiler\`, not checked in): `compiler\Mara.exe build`, which
builds what build.mara says (the build named sothrone, optimized).
`update_compiler.bat` brings the compiler from C:\Code\Mara\release, and
MARA_VERSION.txt says which it is.

For now the program is the game's skeleton: one room (800 × 600), players
as coloured squares, each walking where its player clicks (held, they
follow the mouse). The server keeps the world: players say where they want
to go, it walks them there 30 times a second and tells everyone where
everyone is.

    sothrone                            the game: joins one on this machine, else hosts
    sothrone connect <address[:port]>   the game, joining the one at an address
    sothrone serve [port] [seconds] [open]   a server alone, no window
    sothrone bot [seconds] [address]    a player with no window, walking about
    sothrone picture <out.png> [seconds] [address]   the game in a window never shown, its last frame written

Opened twice, the second copy joins the first's game (port 27200, this
machine only). Each run writes a journal: the first of sothrone.log,
sothrone_2.log, … not in use.

The modules: `world_state` (the world and its messages), `world_server`,
`world_copy` (a client's view of the world), `game_link` (join or host),
`sothrone` (the commands, the window); copied from sooblivion: `wire`
(cut loose from sooblivion's messages), `logging`, `disk`,
`sdl_platform`, `png`, `inflate`.


## What sooblivion already has

From sooblivion at 83fce8a.

**Usable as they are** (they use nothing of Oblivion's):

- `mp3.mara`, `mp3_tables.mara`: the game's music is MP3.
- `inflate.mara`, `png.mara`: PNG pictures, to check decoders without a
  window (sooblivion's `picture` way of working).
- `disk.mara`: opening files, folders, file stamps.
- `logging.mara`: log files and the full.log room checks.
- `wire.mara`: messages on a queue or over TCP. Throne is a co-op game for
  8, so the same client/server shape fits from the start.
- `sdl_platform.mara`: the window, the GL context, keyboard and mouse.

**Usable once a seam is cut:**

- `audio.mara`: the mixer (voices, resampling to the mix rate, loudness
  by distance and side, volumes, the SDL stream) is general; only loading
  a clip goes through `bsa.Archives` and `world.Key_Index`. Split it so
  the mixer takes a clip's bytes and each game loads its own. Throne's
  sounds are plain PCM WAV like Oblivion's.
- `Key_Index`, now inside `world.mara`: a general hash index, worth its
  own module.
- `music.mara`: streaming an MP3 into the mixer is general; choosing a
  track by cell kind is Oblivion's (Throne takes it from World.ini).
- `game_settings.mara`: the settings file written as Mara text; tied to
  `audio.Volumes`.
- `file_cache.mara`: the cache of unpacked files. LZO is quick to unpack,
  so Throne may not need it at first.
- The 2D layer of `render.mara` (`ui_begin`, `ui_image`, `draw_ui`):
  Throne is that kind of drawing everywhere. The 3D renderer stays
  behind.

**Ways of working to carry over** (not code): the world split from the
view, server and client from day one (`world_state`, `world_server`,
`world_copy`); the bot player for testing multiplayer alone; headless
commands and `picture` for looking at results; MARA_ISSUES.md; an
inventory of game data not used yet (ASSETS.md); A* over a grid
(`pathing.mara`) for Throne's walk grids.

**Not useful here:** bsa, esm, nif and nif_*, dds, speedtree, facegen,
land, grass, sky, distant, model, npc. `menus.mara` reads Oblivion's
own XML menu dialect; Throne's interface XML is a different one, so only
an XML reader would carry.

**New for Throne:** lzo, lot, spr8 (sprites and palettes), the levels
(rex, lex, walk grids), an XML reader, cfg, the .seq script interpreter,
and later Bink video.


## Toward og

The shared layer would be: platform (window, input, GL), the audio mixer,
codecs (inflate, png, mp3, wav, lzo, lzw, later Bink), disk, logging and
caches, wire, Key_Index, XML. Each game brings its archives, its formats
and its rules. C:\Code\project_og.md has the details and the open
question of how modules get shared.


## Tools

Python prototypes (run with `python -I`):

- `lotlist.py <archive.lot> [n]`: what's in an archive.
- `lotget.py <archive.lot> <out folder> <pattern…>`: unpacks matching
  files (`--limit=n` first to stop early).
- `spr8.py <sprite.s8> <out.png> [palette.s8 | -] [columns]`: draws every
  frame of a sprite on one sheet.
- `rex.py <file.rex>`: a resource bundle's table.
- `walk_lzw.py <file.walk.sp>`: tries LZW starts on a walk grid.
- `lzo.py`, `lot.py`: the LZO1X decoder and the archive reader they use.
