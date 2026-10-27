# Mara issues found in sooblivion

Problems with the Mara compiler, standard library and bindings met while
writing sooblivion. Each has a small program that shows it, checked
against Mara at the time written. When one is fixed, move it to Fixed
(with the commit) and sooblivion's workaround can come out.

## Open

- An if-expression choosing between a text literal and a longer slice
  stops the program: its value seems to go into a list of room 64.

  ```
  line : str1024
  &line + "one two three four five six seven eight nine ten eleven twelve thirteen"
  print("%", if line.len == 0 do "none" else line[:])
  ```

  stops with `runtime error: 71 items into a list with room for 64` at
  the print. Expected: the slice printed (the literal's room shouldn't
  bound the other side's), or a build error if the two can't share a
  type. sooblivion writes the two prints apart (sooblivion.mara,
  command_sky).

- mara.open_gl has Uniform1f, Uniform2f and Uniform3f but no Uniform4f
  (nor glUniform4f in its foreign block, and GL's functions come through
  gl_load, so a program can't declare its own). sooblivion passes a
  moon's direction and size as a vec3 and a float (render.mara, the sky
  program).

- A cast assigned into an f32 place lets the place's type through to
  what's cast: an untyped constant inside it becomes f32, and a dispatch
  on it can't choose.

  ```
  table : [4!]f32
  for i in 0:4 do table[i] = f32(cos(PI / 72 * f64(i)))
  ```

  fails with `ambiguous dispatch 'cos' — matches multiple overloads:
  cos_f32, cos_f64` and `mismatched types in arithmetic: f32 and f64`,
  while `z := f32(cos(PI / 72 * f64(i)))` builds and prints 0.991445.
  Expected: the cast's operand typed on its own (f64 here, from
  `f64(i)`), as it is when declaring. sooblivion puts the f64 first and
  calls cos_f64/sin_f64 (mp3.mara, build_tables).

## Answered (not issues)

- Struct values can't be compared (`part.diffuse != Vec3{1, 1, 1}`): not
  in the language, by design; a compare can be written as an overload, as
  strings have theirs. sooblivion compares the components (model.mara,
  add_shape).

## Fixed

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
