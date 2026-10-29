# Project og

og: a source port of every game, in Mara. Each port reads its game's own
files and is its own project; what isn't one game's own should be written
once and shared. This file is for sharing what's known across the
projects: what each has that others can use, how they share it, and the
ways of working they have in common. Read it when starting work in any of
them; when a shared part changes in one project, say so here.


## The projects

All in one repo, project_og (C:\Code\project_og, since 2026-10-29; its
history keeps each one's from before): the shared modules in og\, each
game's own code in its folder beside it. og\ and one game's folder are all
of that game's code.

| Project | Game | Folder | Game data | Port |
|---|---|---|---|---|
| oblivion | The Elder Scrolls IV: Oblivion (3D) | C:\Code\project_og\oblivion | D:\SteamLibrary\steamapps\common\Oblivion\Data | 27100 |
| throne | Throne of Darkness (2D sprites) | C:\Code\project_og\throne | D:\Games\Disciples 2\Throne of Darkness\LotFiles | 27200 |

The port is the one a game hosts on: different, so both can run at once.
Each project's folder, module and program share its name; till
2026-10-29 they were sooblivion and sothrone, as older commits and notes
call them.


## How modules are shared now

Mara finds a program's modules in the compiler's `code\` folder, each
folder directly inside it (`code\SDL\`, `code\Open_GL\`, …), the
project's own folder (not its subfolders), and, since Mara 373ba2b7, the
folders its build.mara names (`dirs`):

    module build
    use mara.build
    throne :: Build(){release = true, dirs = ["../og"]}

A module found in two of those folders is an error (373ba2b7): a project
can't keep its own copy of a module that's also in a folder it names. (A
project's module may still take the place of one of Mara's own.)

**The shared modules are in og\** (since 2026-10-29; its README lists
them). A port names it in its build.mara's dirs and keeps no copies. og\
has no build.mara (a port naming it would find `module build` twice) and
nothing one port alone uses. As the search doesn't go into subfolders,
no port sees another's modules: both have a world_state.
A change to one of them reaches every port that names the folder at its
next build: rebuild each and rerun its checks after one.

| Module | What it is | Came from |
|---|---|---|
| disk | files opened read+write, folders made, file stamps, read_exactly (Windows, ASCII paths) | oblivion 83fce8a, unchanged |
| logging | the journal (log file + console, time-stamped lines), `fits` / `add_what_fits` / full.log | oblivion 83fce8a, unchanged |
| sdl_platform | the window, GL 4.5 core context, keyboard and mouse (`Input`), present, vsync, read_pixels; can open hidden | oblivion 83fce8a, unchanged |
| inflate, png | deflate decoding; PNG writing (encode_png) | oblivion 83fce8a, unchanged |
| wire | messages on a queue or over TCP: Wire_Queue, wire_put / wire_put_list / wire_take / wire_value / wire_count, wire_connect / wire_send / wire_receive | oblivion 83fce8a, less its messages; `wire_connect(address, game_port)` takes the game's port |
| lzo | LZO1X unpacking (`lzo_unpack`), every read, write and match checked | written for throne |
| lzw | LZW unpacking, 9- to 12-bit codes lowest bit first, entries from 256, no clear or end codes, the table starting over at 4096 entries (`lzw_unpack(packed, start_bit, &out)`) | written for throne (its walk grids) |
| sprite_layer | textured rectangles on the window in pixels, tinted and blended, batched by texture (`layer_open`, `layer_begin`, `layer_image`, `layer_draw`); `texture_from_pixels` | oblivion's 2D layer (render.mara ui_begin / ui_image / draw_ui) with no Renderer round it |
| indexing | `Key_Index` (`key_index`, `index_put`, `index_get`: open addressing, u64 key → u32, carved from a storage; `Index_Error.Index_Full`); `text_hash` (FNV-1a, never 0) and `folded_hash` (the same, any case) | oblivion's world.mara, and its three copies of the hash made one |
| random | `next_random` (xorshift), `random_share` (0 up to 1), `chance_at` (a roll by hashing: the same for every player with the same seed and numbers) | oblivion's world.mara |
| mp3, mp3_tables | MP3 decoding (MPEG-1 Layer III; `mp3_start`, `mp3_next_frame`) | oblivion, unchanged |
| audio (audio.mara, music.mara) | the mixer: SDL3 stream kept AHEAD of what's heard, voices resampled with gain ramps (`start_voice` with a pitch and a kind of sound), clips added from WAV bytes the game read into `mixer.clip_room` (`known_clip`, `clip_fits`, `add_clip`), `side_gains`, `distance_loudness`, volumes (`master`, `kind_volumes`, `music_volume`), `hear_start` / `voice_of` / `keep_hearing` / `hear_finish`; music: MP3s streamed from the folder the game wants (`want_music`), a random track not the last, faded between folders | oblivion's audio.mara and music.mara, Oblivion's sound records, volumes and music kinds left there (game_sound) |
| file_cache | files unpacked from a game's archives kept on disk (append-only, safe against crashes), found by key | oblivion, unchanged but for Key_Index's module |
| xml | XML a piece at a time (`next_piece`, `read_tag`): a tag's name as written and any attributes (`attribute(text, &tag, name)`, any case; values as places in the text), text between, comments passed over; `trim_xml_text` | oblivion's menus.mara tokenizer, which kept only three attributes and lowered names |
| settings_file | settings kept as a Mara struct literal, `name = number` lines (`read_settings_file`, `write_settings_file`) | oblivion's game_settings.mara, its volumes left there |

Which ports use og:

- **throne:** all of them, through og (build.mara `dirs = ["../og"]`).
- **oblivion:** all of them but lzo, through og (build.mara `dirs =
  ["../og"]`, since 2026-10-29), keeping no copies. Its messages and
  DEFAULT_PORT are in its world_state. What stays its own on top of og's
  modules: game_sound (SOUN records, their loudness and pitch, placed
  sounds, the menu's Volumes, music kinds as folders of Data\Music),
  game_settings (its keys), menus (the menu dialect, lowering tag names
  in `menu_piece`).
- A module named like a local or a param of a file that uses it is an
  error there (`param 'audio' would hide the module 'audio'`): oblivion
  calls its mixer params `mixer`.


## What oblivion has that could be shared, once cut loose

From a survey of oblivion at 83fce8a. "Ties" are what makes a part
Oblivion's now; the size is how much cutting it takes.

**Moved to og on 2026-10-29** (the table above; oblivion a2117d5,
059ba8e): the audio mixer and music, Key_Index and the hash (indexing),
chance (random), mp3, file_cache, the XML tokenizer (xml), the settings
file (settings_file), and the 2D layer (sprite_layer: throne's cut;
oblivion draws its HUD and menus with it). Gaps the audio still has:
no 8-bit or ADPCM WAVs; MP3s must be 44100 Hz (not resampled).

What's left, not cut yet because nothing but Oblivion needs it so far:

**Textures (render.mara).** The texture cache (`Cached_Texture`,
`texture_for`, `known_texture`), batched texture names and bindless
handles (`make_waiting_handles`), shader compiling (`compile_program`),
framebuffers for pictures (`size_framebuffers`, `bind_frame_for_reading`).
Ties: all of it lives on `Renderer`, and textures come from `Archives` as
DDS. Cut: medium — a `Texture_Cache` of its own, loading from pixels or
bytes, found by key; best cut when a second game loads textures the way
it wants them (sprite_layer's `texture_from_pixels` is the plain one).
Bitmap text: `text_width`, `draw_text` (hud.mara), `wrap_text`
(menus.mara) are general; the font files are Oblivion's.

**Index cache (index_cache.mara).** Stamps of files + the exe
(`plugins_stamp`), tables written and read whole, the header written
last — the tables are Oblivion's (small).

**Paths (pathing.mara).** A* (`find_route`'s body, `open_push` /
`open_pop` heap), `Path_Grid` (8192 points, 65536 links, fixed),
`Route`, `route_way` (its nearness in Oblivion's units). Ties: start and
goal are found through the Scene (line-of-walking checks); grids come
from PGRD records. Cut: medium — A* over node numbers in the caller's
storage, the game choosing start and goal and its distances. Left until
Throne's walk grids are read: a grid of cells may want A* over cells, not
a graph.

**Smaller pieces.** Keyframes (`key_between`, `rotation_at` in
animation.mara); particles worked out from the time alone, no state kept
(particles.mara: the idea carries to 2D); triangle and line tests
(walking.mara).

**The client/server skeleton.** `World_Server` / `Server_Client` slots,
`server_join`, `server_leave`, the fixed-tick loop (WORLD_TICK 1/30 s,
late ticks let go), the dirty flags for what's to be told, `copy_take`'s
shape, `open_link` / `join_local` / `host_listen`, the bot reading orders
from a file and writing its status to another. throne has this cut down
(world_state, world_server, world_copy, game_link); the message tables
and the state are each game's.

**Pictures and frames (oblivion.mara, viewer.mara).** The `picture`
command: the game in a hidden window, settled frames counted, the frame
read back and written as a PNG (`take_picture`); frame pacing
(`wait_for_next_frame`: sleep, then spin the last millisecond); slow-frame
notes; GL errors noted once each.


## Ways of working the projects share

- **Building.** One compiler builds every project: project_og's
  `compiler\` (not checked in), brought from C:\Code\Mara\release by the
  root's update_compiler.bat (run as
  `cmd.exe /c "C:\Code\project_og\update_compiler.bat"`);
  MARA_VERSION.txt at the root, checked in, says which. A project's
  build.bat builds it through its build.mara (`..\compiler\Mara.exe
  build`). Batch files need CRLF line ends. After an update, or a change
  in og\, rebuild every project and rerun its headless checks.
- **Commits.** Each session commits its own project's files, by path
  (never `git add -A`), and only with its user's word; a change to og\
  is told to the other sessions working in project_og.
- **Server and client from the start.** The world lives on the server
  (World_State); a client knows only what it's told (World_Copy) and says
  what its player does. Started plain, the game joins one hosted on this
  machine (300 ms to answer), else hosts one — its own player client 0,
  queues passed directly — so opening it twice puts two players in one
  game. `serve` runs a server alone; `bot` is a player with no window.
- **No windows of mine.** Results are checked headless: commands that
  print, and `picture` (a hidden window, a PNG I read). Seeing and feeling
  the game in a window is the user's.
- **Journal.** Each run writes a log (throne picks the first free
  throne.log, throne_2.log, … so two copies can run in one folder).
- **Mara issues.** Problems with Mara met in a project go in its
  MARA_ISSUES.md (Open / Fixed, each with a small program that shows
  it); another chat works on Mara. oblivion's is the model.

## Mara notes met in these projects

- Mara finds modules in the project folder, the compiler's code folders
  and build.mara's dirs (above). A module can't be named like a common local
  (oblivion: `files`, `cache`, `world`, `scene` as locals clash), nor a
  param in a file that uses it (`audio`).
- A project's folder can't be in another's dirs when both have a
  build.mara: `module build` is then in two folders. A check program in a
  scratch folder copies the project modules it needs instead.
- An error variant two error types used together both have is ambiguous
  where it's written bare (`Shader_Failed`: sprite_layer's and
  oblivion's Render_Error): write `Render_Error.Shader_Failed`.
- A struct holding views of an immutable param's text can't be written
  through after (`tag.attributes` in xml): keep places in the text
  (start, stop) and slice when asked.
- In `for &x in list`, x is already a pointer: pass `x`, not `&x`.
- Big locals: `x : [N * MB]byte = void` then `x.len = 0`, or they're
  cleared every call.
- Open in oblivion's MARA_ISSUES.md: an untyped constant array of numbers
  (`TURNS :: [180, 135, -135]`) can't be indexed or looped. A typed one
  indexes fine in throne (`PLAYER_COLOURS :: [8!][3!]f32{…}`, Mara
  6bbdec03) — maybe a way round it.
