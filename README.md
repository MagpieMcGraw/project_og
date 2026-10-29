# project_og

og: a source port of every game, in Mara. Each port reads its game's own
files; what isn't one game's own is written once and shared. This repo
holds them all: the shared modules in og/, each game's own code in its
folder beside it. A game is built from its folder and og/ (its build.mara
names `../og`), so og/ and one game's folder are all of that game's code.

| Folder | What it is |
|---|---|
| og | the modules the ports share (its README lists them) |
| oblivion | sooblivion: The Elder Scrolls IV: Oblivion |
| throne | sothrone: Throne of Darkness |

project_og.md says what each port has that the others can use, what's
still to be shared, and the ways of working the ports have in common.


## Building

One Mara compiler builds every game: compiler/ (not checked in), brought
from C:\Code\Mara\release by update_compiler.bat, run as
`cmd.exe /c "C:\Code\project_og\update_compiler.bat"`. MARA_VERSION.txt,
checked in, says which Mara it is. A game's build.bat builds it
(`..\compiler\Mara.exe build`, as its build.mara says). After an update,
or a change in og/, rebuild every game and rerun its checks.

Mara looks for a game's modules in its own folder and in og/, not in
their subfolders, so no game sees another's modules. A game's module
can't have the name of one in og/. og/ holds only shared modules: no
build.mara (a game naming og/ would find two), nothing one game alone
uses.
