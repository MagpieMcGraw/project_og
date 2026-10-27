# Mara issues found in sooblivion

Problems with the Mara compiler, standard library and bindings met while
writing sooblivion. Each has a small program that shows it, checked
against Mara at the time written. When one is fixed, move it to Fixed
(with the commit) and sooblivion's workaround can come out.

## Open

- There's no way to read an environment variable on Windows: mara.os
  declares `getenv` only in its Linux foreign block (file-private), and
  nothing public wraps it or GetEnvironmentVariable. sooblivion wants
  `%LOCALAPPDATA%\Oblivion\Plugins.txt` (the player's chosen plugins) and
  `%USERPROFILE%\Documents\My Games\Oblivion\Oblivion.ini`. Expected: an
  `env(name) -> text, bool` (or similar) on both systems. sooblivion reads
  the Data folder's DLCList.txt instead, and keeps the ini's archive list
  as a constant (game_files.mara).

## Answered (not issues)

- Struct values can't be compared (`part.diffuse != Vec3{1, 1, 1}`): not
  in the language, by design; a compare can be written as an overload, as
  strings have theirs. sooblivion compares the components (model.mara,
  add_shape).

## Fixed

- An if-expression choosing between a text literal and a longer slice
  stopped the program (its value went into a list of room 64) — 29e2911:
  an if-expression of an array and a slice is the slice. sooblivion's two
  prints in command_sky can be one again once its compiler copy has it.
- mara.open_gl had no Uniform4f — 95bb037. sooblivion's sky program
  still passes a moon as a vec3 and a float, until its compiler copy has
  it.
- A cast assigned into an f32 place let the place's type through to what
  was cast (`table[i] = f32(cos(PI / 72 * f64(i)))` couldn't choose a
  cos) — 1626ed5: a cast's operand is typed on its own. mp3.mara's
  explicit cos_f64/sin_f64 can go once sooblivion's compiler copy has it.

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
  (UNSET_BEYOND in nif_animation.mara is still written out; it could be `1e12`.)
- A loop over a literal array of arrays (`for point in [[4, 4], [16, 16]]`)
  failed in lowering — bcddc81.
- A module's constant couldn't size an array (`[render.GRASS_PER_CELL]T`) — d0b31c0.
- gl_load handed c_text's views (no room for the 0 after them) to
  GL_GetProcAddress, whose cstring() stopped the program — 4ef56de.
- Foreign blocks made private, the bindings wrapping them — 48033df
  (sooblivion converted: 968cd07, d60f499).
