# Mara issues found in sooblivion

Problems with the Mara compiler, standard library and bindings met while
writing sooblivion. Each has a small program that shows it, checked
against Mara at the time written. When one is fixed, move it to Fixed
(with the commit) and sooblivion's workaround can come out.

## Open

- A generic fun's param can't have a default, so a generic can't take
  `#caller_span` or `#caller_name`. Checked against 61bf180:

  ```
  room_for :: fun(list: ^[]$T, site: atom = #caller_span) -> bool {
  	if list.len < list.cap do return true
  	print("full at %", site)
  	return false
  }
  ```

  says "a generic's param with a default is not supported yet". Expected:
  defaults as on any fun. sooblivion's check takes the numbers instead,
  `fits(list.len + 1, list.cap)` (logging.mara), where it would take the
  list (`room_for(&list)`).

- mara.os can't add to the end of a file: file_open_write writes over
  it, and nothing opens one for appending. A program can't bind
  CreateFileA itself either, as mara.os binds it (privately). Checked
  against 61bf180:

  ```
  foreign static_lib "kernel32" {
  	fun CreateFileA(name: cstring, access: u32, share: u32, security: ^byte, disposition: u32, flags: u32, template: File_Id) -> File_Id
  }
  ```

  says "foreign symbol 'CreateFileA' is already declared in library
  'kernel32' (first declaration at os.mara:995); each external symbol
  may be bound by at most one foreign block". Expected: an append open in
  mara.os (`file_open_append`); and a private binding not keeping others
  from binding the same symbol. sooblivion binds CreateFileW for its full
  log (logging.mara, add_to_file).

- `-profile memory` gives an arena's peak as a number like an address.
  Checked against 61bf180 with Mara's own doc/memory_profiling.mara: its
  memory.txt ends

  ```
        size B       peak B   peak %  arena
       1048576 140702278017248 13418414880.49  Arena_Basic
  ```

  Expected: the most bytes in use at once, at most the size. sooblivion's
  runs give 140703099914000 for its 2 GB arena.

- `-profile memory` doesn't watch a list in an item made with `next()`
  from a carved slice, and that list's len writes are put down to a list
  watched before at the same address. Checked against 61bf180:

  ```
  Part :: struct {
  	texture: [160]utf8
  	count: i64
  }
  Bytes :: struct {
  	data: [100000]u8
  }
  make_parts :: fun(storage: ^[]byte) -> i64 {
  	parts := slice([:4]Part, storage)
  	for k in 0:4 {
  		&parts + Part{texture = [], count = k}
  		&parts[k].texture + "textures/a.dds"
  	}
  	return parts.len
  }
  make_bytes :: fun(storage: ^[]byte) -> i64 {
  	holders := slice([:1]Bytes, storage)
  	holder := next(&holders)
  	holder.data.len = 0
  	for k in 0:50000 do &holder.data + u8(k)
  	return holder.data.len
  }
  ```

  with `make_parts(&storage)`, `storage.len = 0`, `make_bytes(&storage)`
  in main, memory.txt has `Part.texture` at a peak of 50000 of its 160,
  and no `Bytes.data`. Expected: `Bytes.data` at 50000 of 100000, and
  `Part.texture` at 14. In sooblivion's profiles `Model_Part.texture`
  reaches 69243 of 160 (nifs: the model room is emptied for each mesh)
  and `read_npc_look.eyes_texture` 28856 of 128 (npc). Slices carved from
  storage (`slice([:n]T, storage)`) aren't in the report either; the
  doc says partial arrays only, but they're where most of sooblivion's
  room is (a model's parts, motions, flipbooks).

- A struct holding a list can't be written into a byte buffer: the
  program isn't made. Checked against 61bf180 and main Mara (Mara.exe):

  ```
  Span :: struct {
  	name: [8]utf8
  	start: i64
  }
  main :: () {
  	chunk : [256]byte
  	chunk.len = 64
  	span := Span{name = [], start = 3}
  	&span.name + "abc"
  	chunk[16] = span
  	print("span written: %", chunk.len)
  }
  ```

  says "Codegen error: can't lower 'main' from the program graph: its
  view ''" at `chunk[16] = span` (a struct of plain fields writes fine).
  Expected: its bytes written, the list's len and room with them, as a
  list's are on its own. sooblivion's plugin index (index_cache.mara)
  writes a Kept_Span of the fields it needs instead of the Plugin_Span.

## Answered (not issues)

- A local list costing its whole room each call (`room : [16 * MB]byte`
  cleared every time, 0.7 ms; 400 MB at a start, 150 ms of pages touched
  for the first time): `= void` leaves it unset (doc/basics.mara,
  example_void), its len then set — `room : [16 * MB]byte = void`,
  `room.len = 0`. The view commands' storages are so (viewer.mara).
- Struct values can't be compared (`part.diffuse != Vec3{1, 1, 1}`): not
  in the language, by design; a compare can be written as an overload, as
  strings have theirs. sooblivion compares the components (model.mara,
  add_shape).

## Fixed

sooblivion builds with Mara's release, 61bf180 (MARA_VERSION.txt;
update_compiler.bat pulls the next), so all of these are in its copy.

- An immutable slice param stored into a struct field (`hold(numbers)`
  giving back `Holder{numbers = numbers}`) made that field read-only in
  every Holder of the program — 61bf180: the copy rule follows values.
  sooblivion's tree_part still takes the growing tree (it reads as well).
- A struct made from a pointer to a local struct counted as holding every
  pointer the local held, so a pointer param kept in a local beside lists
  carved from storage was "stored into" the storage — 936e8ec: a struct's
  fields are kept apart. A tree's Growth holds its Speed_Tree again
  (speedtree.mara).
- mara.string's `parse_number` read no exponent (`-6.24607e-008`, as
  SpeedTree's curves have them) — 21d9d29. speedtree.mara's next_number
  reads its own no more.
- `return []` in a fun giving back a slice was refused (the `[]` typed an
  empty array) — 41194dd: `[]` where a slice goes is the empty slice.
  read_player_plugins (game_files.mara) gives back `[]`.
- An if-expression choosing between a text literal and a list passed the
  checker, then the program wasn't made — 9f29045. command_sky prints
  `line`, not `line[:]`.
- An array literal appended to a slice of arrays taken from storage
  (`&rows + [-1, -1, -1, -1, 0, 0, 0, 0]`) wasn't lowered — 161b24f.
  rig_skin (model.mara) appends the literal.

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
