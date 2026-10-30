# throne

A source port of Throne of Darkness (Click Entertainment, 2001) in Mara,
reading the game's own files. Nothing is decompiled: the formats are
worked out from the data (FORMATS.md). Part of og, a source port of every
game, so what isn't Throne-specific should be written to be shared.

The game is all 2D: pre-drawn sprites in 8 directions, 16-shade colour
ramps, rooms and a wilderness built from placed pictures, up to 8 players
together. Quests are scripts that wait on events.

What's shared with the other ports (sooblivion so far) is written down in
project_og.md, in the folder above (project_og holds og/ and every port).


## Building and running

`build.bat` builds throne.exe with project_og's Mara compiler, the one
every port builds with (`..\compiler\`, not checked in):
`..\compiler\Mara.exe build`, which builds what build.mara says (the
build named throne, optimized). `..\update_compiler.bat` brings the
compiler from C:\Code\Mara\release, and ..\MARA_VERSION.txt says which it
is.

For now the program is the game's skeleton: one level, the Mori shrine
room, read from the game's World.lot (its layout and furniture set) and
drawn as the game laid it out, the window following its player (players
drawn easing toward where the server last said, so walking is smooth at
any frame rate); each player one of the seven samurai, read from the
game's Samurai.lot, its name over its head in the game's chat font,
striking toward where the right button is pressed (its attack, played
once over STRIKE_SECONDS, seen by everyone; nothing to strike yet),
walking where its player clicks (held, they follow the mouse): running
the way they go, standing once there; the level's music playing (its
track from Stream.lot, unpacked once into cache\music\). The server keeps
the world: it reads the level's area, walk grid and named spots, starts
players on open ground at the level's shrine (MORISHRINE, by the portal),
walks them where they ask 30 times a second by
a route round walls and furniture (A* on the grid, straightened) — a
click on a wall walks to the open spot nearest it — turns them the way
they're going, and tells everyone where everyone is and which level
they're in. Without the game's files the level is a bare room, open
everywhere, and the players coloured squares. Only the shrine's grid is
used: where a level's grid lies on it is known for the shrine alone
(fitted: walk_grid.mara). F2 shows what stops one, over the level: the
walk grid's blocked cells at the edge of where one can walk (red), and
the layout's outlines — things' footprints (yellow), plain collision
lines (orange), areas that set off events (blue), named spots (pink).

The controls are actions (og's game_controls): walk (the left button,
held: following the mouse), strike (the right), show_collision (F2), quit
(Escape). What does each is in throne_controls.txt beside the journal,
written with the game's own the first time and read every start after.
It's written as a Mara value (`controls :: Controls{`, a line an action,
`}`): change a line (`strike = "Mouse_Right, Space"`; keys by SDL's
names, any case, up to 4 an action, `""` for none) and it's so from the
next start; a line it can't take is passed over, and the journal says
which. (A file from before, its lines unquoted, reads the same.)
Pictures and checks use the game's own, never the file.

    throne                            the game: joins one on this machine, else hosts
    throne connect <address[:port]>   the game, joining the one at an address
    throne serve [port] [seconds] [open]   a server alone, no window
    throne bot [seconds] [address]    a player with no window, walking about
    throne picture <out.png> [seconds] [address] [click x y] [strike] [collision]   the game in a window never shown (silent), its last frame written (strike: the click is a right-click; collision: drawn as F2 shows it)
    throne sprite <archive> <path | folder> <out.png>   a sprite's frames as the game's atlas lays them out
    throne walk-grid <level>          a level's walk grid: its size and open cells
    throne music-cache <track>        a track ("music\castle.mp3") unpacked where the game plays it from
    throne controls [check]           what each action is on (the file written when there's none); check: og's game_controls tried on made-up input

Opened twice, the second copy joins the first's game (port 27200, this
machine only). Each run writes a journal: the first of throne.log,
throne_2.log, … not in use. The game's files are read from
`D:\Games\Disciples 2\Throne of Darkness\LotFiles` (art.mara's
LOT_FOLDER).

The modules: `world_state` (the world and its messages), `world_server`,
`world_copy` (a client's view of the world), `game_link` (join or host),
`lot` (the archives), `spr8` (the sprites), `art` (the samurai's
pictures on the card), `rex` (a level's bundles), `lex` (a level's
layout), `level` (World.ini, a level read), `level_art` (a level's
pictures on the card), `walk_grid` (where one can walk, and routes),
`music_cache` (a level's track where og's music plays it), `text` (the
game's fonts, text drawn), `throne` (the commands, the window). From
../og, the modules the ports share
(build.mara names the folder): `wire`, `logging`, `disk`,
`sdl_platform`, `game_controls` (actions and what does each), `png`,
`inflate`, `lzo`, `lzw`, `sprite_layer`, `audio` (the mixer and music),
`mp3`, `indexing`, `random`. Mara problems met here are in
MARA_ISSUES.md.


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
and its rules. ../project_og.md has the details.


## Tools

Python prototypes (run with `python -I`):

- `lotlist.py <archive.lot> [n]`: what's in an archive.
- `lotget.py <archive.lot> <out folder> <pattern…>`: unpacks matching
  files (`--limit=n` first to stop early).
- `spr8.py <sprite.s8> <out.png> [palette.s8 | -] [columns]`: draws every
  frame of a sprite on one sheet.
- `rex.py <file.rex>`: a resource bundle's table.
- `walk_lzw.py <file.walk.sp>`: tries LZW starts on a walk grid.
- `lex.py <file.lex>`: a layout's table and records.
- `walk.py <World.lot> <level folder> <lex name> <out.png> [cell_w cell_h x0 y0]`:
  a level's walk grid shaded over its picture (blocked red, open green):
  how the grid's place on the level was checked.
- `walk_fit.py <level folder>:<lex name> ...`: fits where levels' walk
  grids lie, on their walls' outlines and named spots (the Mori shrine:
  1612, −215; the Citadel02 shrine 1612, −200, but the Citadel03 one
  1482, 500: where a level's corner comes from isn't found yet).
- `level.py <World.lot> <level folder> <lex name> <out.png> [file|y]`:
  draws a whole level from its layout and bundles (the prototype of
  level_art.mara).
- `atlas_check.py <archive.lot> <sprite path> <atlas.png>`: builds the
  atlas `throne sprite` writes with the Python decoder and counts the
  pixels that differ (the Leader's run: none).
- `lzo.py`, `lot.py`: the LZO1X decoder and the archive reader they use.
