# og

The Mara modules the og ports share (og: a source port of every game).
A port uses them by naming this folder in its build.mara:

    sothrone :: Build(){release = true, dirs = ["../og"]}

A port then keeps no copy of these modules: a module found in two folders
is an error. A change here reaches every port that names this folder at
its next build, so rebuild each and rerun its checks after one.

C:\Code\project_og.md says which ports use which, what else could come
here, and the ways of working the ports share.

| Module | What it is |
|---|---|
| wire | messages between a game's server and its clients: a queue in one program, or TCP |
| logging | the journal (a log file and the console, lines stamped with the time); full.log for lists found full |
| disk | files opened to read and write, folders made, file stamps, a view filled whole (Windows, ASCII paths) |
| sdl_platform | the window, its OpenGL 4.5 context, keyboard and mouse; a hidden window for pictures |
| inflate | deflate (zlib) decoding |
| png | PNG writing |

All but wire came from sooblivion (83fce8a) as they were; wire is
sooblivion's less its own messages.
