# Mara issues found in sooblivion

Problems with the Mara compiler, standard library and bindings met while
writing sooblivion. Each has a small program that shows it, checked
against Mara at the time written. When one is fixed, move it to Fixed
(with the commit) and sooblivion's workaround can come out.

## Open

- `return []` in a fun that gives back a slice is refused: the `[]` is
  typed as an empty array, `[0!]utf8`, which (rightly) doesn't turn into a
  slice when given back. Checked against 3a5d0f3:

  ```
  none :: fun() -> []utf8 {
  	return []
  }
  ```

  says "can't return [0!]utf8 as a []utf8: an array doesn't turn into a
  view when it's given back", and the same with `-> []utf8, err`.
  Expected: `[]` is the zero of its place, and the place here is the
  result, a slice: an empty slice. sooblivion gives back an empty view of
  the storage it was handed (`storage[0:0]`, game_files.mara,
  read_player_plugins).

- An if-expression choosing between a text literal and a list (not a
  slice of it) passes the checker, then the program isn't made. Checked
  against 3a5d0f3:

  ```
  line : str1024
  &line + "one two three"
  print("%", if line.len == 0 do "none" else line)
  ```

  says "Codegen error: can't lower 'main' from the program graph: its
  write '' (the value's type)". With `line[:]` it works (29e2911).
  Expected: the list's slice, as for a slice; or a checker error saying
  to write `line[:]`. sooblivion writes `line[:]` (command_sky).

## Answered (not issues)

- Struct values can't be compared (`part.diffuse != Vec3{1, 1, 1}`): not
  in the language, by design; a compare can be written as an overload, as
  strings have theirs. sooblivion compares the components (model.mara,
  add_shape).

## Fixed

sooblivion builds with Mara's release, 3a5d0f3 (MARA_VERSION.txt;
update_compiler.bat pulls the next), so all of these are in its copy.

- There was no way to read an environment variable on Windows — 2f840bc
  (`env(name) -> Path, err`; Not_Set since 3a5d0f3). sooblivion reads the
  player's `%LOCALAPPDATA%\Oblivion\Plugins.txt` (game_files.mara), the
  data folder's DLCList.txt only without one. Oblivion.ini's archive list
  is still a constant.
- An if-expression choosing between a text literal and a longer slice
  stopped the program (its value went into a list of room 64) — 29e2911:
  an if-expression of an array and a slice is the slice. command_sky's
  two prints are one again.
- mara.open_gl had no Uniform4f — 95bb037. sooblivion's sky program
  passes a moon as a vec3 and a float still: it reads as well.
- A cast assigned into an f32 place let the place's type through to what
  was cast (`table[i] = f32(cos(PI / 72 * f64(i)))` couldn't choose a
  cos) — 1626ed5: a cast's operand is typed on its own. mp3.mara uses
  cos and sin (its output is the same to the bit).

- A variable named `all` was accepted, then `if x or all {` read `all {`
  as a broadcast, the errors landing on the next line — b3661d1: `all` is
  a keyword (declaring it is an error), and a condition's `{` is never a
  broadcast's. sooblivion renamed its two (`every_one`, `everything`).
- mara.sdl had no audio — 8336222 (SDL3's audio streams). sooblivion's
  audio.mara uses it; its stopgap foreign block is gone.
- An err couldn't be had as text (the journal's log could say what failed,
  not why) — b6926f2 (`e.text()`) and eb25281 (`e.where()`: where it was
  made, carried by `?`). sooblivion's journal writes both (note_error).
- An inner loop's index named as the outer loop's was the same variable
  (`for value, i in …` around `for i in 0:2`: the outer loop never ended)
  — 9d5d110: a loop's name hiding an enclosing one is an error, as a
  declaration's is. sooblivion's map command had loop items named `height`
  under the picture's `height`; renamed.
- Writing a field of a union variant's value (`box := Box{…}; box.height = 3`)
  failed in lowering ("a write to an unknown field") — 391e74c: the checker
  says to reach the field in a match arm. sooblivion builds its variants
  from finished values.
- Float literals with an exponent (`1.5e3`) weren't read — 8a8319d.
  (UNSET_BEYOND in nif_animation.mara is `1e12` now.)
- A loop over a literal array of arrays (`for point in [[4, 4], [16, 16]]`)
  failed in lowering — bcddc81.
- A module's constant couldn't size an array (`[render.GRASS_PER_CELL]T`) — d0b31c0.
- gl_load handed c_text's views (no room for the 0 after them) to
  GL_GetProcAddress, whose cstring() stopped the program — 4ef56de.
- Foreign blocks made private, the bindings wrapping them — 48033df
  (sooblivion converted: 968cd07, d60f499).
