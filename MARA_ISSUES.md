# Mara issues found in sooblivion

Problems with the Mara compiler, standard library and bindings met while
writing sooblivion. Each has a small program that shows it, checked
against Mara at the time written. When one is fixed, move it to Fixed
(with the commit) and sooblivion's workaround can come out.

## Open

- An immutable slice param stored into a struct field makes that field
  read-only everywhere in the program, not just in the values made from
  the param. Checked against 3a5d0f3:

  ```
  Holder :: struct {
  	numbers: []i64
  }
  hold :: fun(numbers: []i64) -> Holder {
  	return Holder{numbers = numbers}
  }
  fill :: fun(storage: ^[]byte) -> i64 {
  	holder := Holder{numbers = slice([:4]i64, storage)}
  	&holder.numbers + 1
  	return holder.numbers.len
  }
  ```

  says, at the append in fill, "`holder.numbers` is a copy of the
  immutable param `numbers` (in hold)". In sooblivion a tree's part made
  from a slice param turned every `part.vertices` write (model.mara,
  npc.mara) into an error. Expected: fill's holder, carved from mutable
  storage, can be appended to; or, if a field is meant to take one
  mutability for the whole program, an error at hold saying so. sooblivion
  passes the growing tree itself (speedtree.mara, tree_part), so the
  slices come from its mutable lists.

- A struct made from a pointer to a local struct counts as holding every
  pointer that local holds, though it takes only some of its fields; so a
  pointer param kept in a local beside lists carved from storage is "stored
  into" the storage. Checked against 3a5d0f3:

  ```
  Work :: struct {
  	settings: ^Settings
  	numbers: []i64
  }
  Summary :: struct {
  	numbers: []i64
  }
  summary_of :: fun(work: ^Work) -> Summary {
  	return Summary{numbers = work.numbers}
  }
  fill :: fun(settings: ^Settings, storage: ^[]byte) -> i64 {
  	work := Work{settings = settings, numbers = slice([:16]i64, storage)}
  	for k in 0:work.settings.count do &work.numbers + k
  	summaries := slice([:2]Summary, storage)
  	&summaries + summary_of(&work)
  	return summaries[0].numbers.len
  }
  run :: fun(storage: ^[]byte) -> i64 {
  	settings := Settings{count = 4}
  	return fill(&settings, storage)
  }
  ```

  says, at `fill(&settings, storage)`, "`fill(...)` stores its `settings`
  argument into its `storage` argument: reference to local `settings`
  would escape". Without the summary it builds. Expected: no error, as a
  Summary has no place for settings. sooblivion passes the Speed_Tree
  beside its Growth instead of keeping it in there (speedtree.mara).

- mara.string's `parse_number` reads no exponent: `parse_number("-6.24607e-008")`
  is false. SpeedTree's curves are written so (`%g`). Expected: exponents
  read, as Mara's own float literals now are (8a8319d). sooblivion reads
  the exponent itself (speedtree.mara, next_number).

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

- An array literal appended to a slice of arrays taken from storage isn't
  lowered. Checked against 3a5d0f3:

  ```
  fill :: fun(count: i64, storage: ^[]byte) -> i64 {
  	rows := slice([:count][8!]f32, storage)
  	for k in 0:count do &rows + [-1, -1, -1, -1, 0, 0, 0, 0]
  	return rows.len
  }
  ```

  says "Graph error: lower: an array literal as an operand". Appended to
  a list (`rows : [4][8!]f32`) it works. Main Mara's Mara.exe (61bf180
  checked out, 2026-10-28) compiles it and gives 4: fixed there, not in a
  release yet. sooblivion appends a typed local holding the literal
  (model.mara, rig_skin) till the release has it.

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
