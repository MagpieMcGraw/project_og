# og

The Mara modules the og ports share (og: a source port of every game).
A port uses them by naming this folder in its build.mara:

    sothrone :: Build(){release = true, dirs = ["../og"]}

A port then keeps no copy of these modules: a module found in two folders
is an error. A change here reaches every port that names this folder at
its next build, so rebuild each and rerun its checks after one.

project_og.md, here, says which ports use which, what else could come
here, and the ways of working the ports share.

| Module | What it is |
|---|---|
| wire | messages between a game's server and its clients: a queue in one program, or TCP |
| logging | the journal (a log file and the console, lines stamped with the time); full.log for lists found full |
| disk | files opened to read and write, folders made, file stamps, a view filled whole (Windows, ASCII paths) |
| sdl_platform | the window, its OpenGL 4.5 context, keyboard and mouse; a hidden window for pictures |
| inflate | deflate (zlib) decoding |
| png | PNG writing |
| lzo | LZO1X unpacking, every read and write checked |
| sprite_layer | pictures drawn flat on the window (textured rectangles in pixels, tinted, blended), and textures made from pixels |
| audio | the sound: a mixer of WAV clips (the game reads their bytes) through SDL3, each voice its pitch, side and kind's volume; MP3 music streamed from a folder, faded between folders |
| mp3 | MP3 decoding (MPEG-1 Layer III) |
| indexing | Key_Index, a table from u64 keys to numbers; text_hash and folded_hash, the keys of text |
| random | numbers from a seed, and rolls that come out the same for every player |
| file_cache | files unpacked from a game's archives kept on disk, found again by key |
| xml | XML read a piece at a time: tags with any attributes, the text between |
| settings_file | settings kept as a Mara struct literal, a `name = number` line each |

wire, logging, disk, sdl_platform, inflate and png came from sooblivion
(83fce8a), as they were but for wire, which is sooblivion's less its own
messages. sprite_layer is sooblivion's 2D layer (render.mara's ui_begin,
ui_image, draw_ui) with no Renderer round it. lzo was written for
sothrone (Throne of Darkness's archives). audio, mp3, indexing, random,
file_cache, xml and settings_file came from sooblivion too, its
Oblivion-only parts left there (its game_sound, menus, game_settings).
