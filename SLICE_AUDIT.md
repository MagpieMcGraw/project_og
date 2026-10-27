# `[:]` in sooblivion: an audit

2026-10-27, sooblivion at 8edd526, built with Mara release 3a5d0f3.
Applied in 80f92e5: the 266 not needed are out; the 4 needed and the
declarations stay (12 `[:]` left).

## In short

276 `[:]` in 20 of sooblivion's 36 files (23,478 lines). Taken out of a
copy of the sources, all but 4 build, and every headless check gives
the same output as before. Those checks cover the plugins, archives,
models, NPCs, skinning, sky, the NIF survey, all 139 trees, a tree
picture, the MP3 decode and the music mix. The viewer's frame code isn't
run by them.

| What the `[:]` does | Uses | Needed |
|---|---|---|
| A list passed to a `[]T` param | 167 | 0 |
| An append of a list (`&line + name[:]`, `&line + int_text(n)[:]`) | 69 | 0 |
| A compare (`entry.name[:] == type_name`, `riff[:] != "RIFF"`) | 12 | 0 |
| A list passed to the journal's `note` (a dispatch of text and number) | 10 | 0 |
| A declaration (`folder_path := kind.path[:]`) | 7 | 1 |
| A branch of an if-expression | 6 | 1 |
| A slice field of a struct literal (`Model{parts = built[:], …}`) | 3 | 0 |
| A return | 2 | 2 |

So about 266 are habit: a list already goes into a slice param, an
append, a compare or a slice field without one. sooblivion grew them by
spelling every list-to-slice place out.

## The 4 the compiler needs

- `npc.mara:345` and `:353`: `return kept.bones[:]` from a fun giving back
  `[]Pose_Bone`. Returns don't decay, by the rule chosen on 2026-10-17.
- `bsa.mara:110`: `header_view := header_bytes[:]`, a fixed array
  (`[36!]byte`), so that `&header_view` can be the `^[]byte` that
  read_exactly moves the length of.
- `sooblivion.mara:1729`: `if chances.len == 0 do "the climate's" else
  line[:]`. Without `[:]` it fails in codegen, not in the checker. It's
  in MARA_ISSUES.md's Open list.

## Declarations: building isn't the same as meaning the same

Without `[:]`, `x := list` is a copy of the list, not a view of it. It
builds, but it means something else: a copy costs the list's whole room
(a Path is 512 bytes), and writes to it don't reach the original. The
other 6 in sooblivion only read, so they happen to give the same output:

- `audio.mara:165`, `sooblivion.mara:1555`: `folder_path := kind.path[:]`
- `game_files.mara:119`: `name := order.plugins[…].name[:]`
- `npc.mara:449`: `bone := part.bone[:]`, later `bone = parent` (a slice)
- `speedtree.mara:370`: `points := curve.points[:]`, on every curve read
- `tree_picture.mara:120`: `Canvas{pixels = canvas_pixels[:], depth = canvas_depth[:], …}`.
  This one is a struct field of slice type, so it's a view either way.

In a declaration, `[:]` is the one way to say "a view, not a copy",
unless the type is written: `x : []utf8 = list`.

## What it suggests for Mara

- **Passing, appending, comparing:** these need no `[:]`, and they're
  87% of sooblivion's uses. The compiler could say so: a warning,
  or `mara fix`.
- **Returns and declarations:** these are where `[:]` still means
  something. A return needs it by rule. In a declaration it's the
  difference between a view and a copy.
- **If-expressions:** an if-expression of a literal and a list needs it
  only because of the codegen bug. Two lists of one type don't.

## How it was found

The scripts are in this session's scratchpad (`py/strip_slices.py` and
`py/sort_slices.py`). They strip every `[:]` from a copy, build, and put
back the ones on lines the compiler rejects. An error on a line without
one puts back the nearest one above it. The loop repeats until the copy
builds, then sorts each use by its line. Every use's file, line, kind
and whether it's needed is in the scratchpad's `slice_kinds.json`.
