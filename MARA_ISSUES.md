# Mara issues found in sooblivion

Problems with the Mara compiler, standard library and bindings met while
writing sooblivion. Each has a small program that shows it, checked
against Mara at the time written. When one is fixed, move it to Fixed
(with the commit) and sooblivion's workaround can come out.

## Open

- A parameter (or variable) named `all` is accepted, but then `if x or all {`
  reads `all {` as the start of a broadcast, and the errors land on the
  next line, about its tokens:

  ```
  show :: fun(count: i64, all: bool) {
  	if count < 25 or all {
  		print("shown %", count)
  	}
  }
  ```

  gives `[7:8] Parse error: unexpected token Left_Paren "(" (expected
  statement)` and three more like it, all on the `print` line; nothing
  names `all`. Expected: either `all` refused as a name where it's
  declared ("`all` is a keyword"), or `all` read as the variable where a
  broadcast can't start (after `or`). sooblivion renamed its parameter
  (`every_one`, sooblivion.mara command_cell).

## Answered (not issues)

- Struct values can't be compared (`part.diffuse != Vec3{1, 1, 1}`): not
  in the language, by design; a compare can be written as an overload, as
  strings have theirs. sooblivion compares the components (model.mara,
  add_shape).

## Fixed

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
