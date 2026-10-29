# Mara issues found in sooblivion

Problems with the Mara compiler, standard library and bindings met while
writing sooblivion. Each has a small program that shows it, checked
against Mara at the time written. When one is fixed, move it to Fixed
(with the commit) and sooblivion's workaround can come out.

## Open

- A module's constant array of numbers can't be looped over or indexed:
  lowering fails (checked against Mara c322fb6, 2026-10-29):

      module const_loop
      use mara.core
      TURNS :: [180, 135, -135]
      main :: fun() {
          for turn in TURNS do print("%", turn)
      }

  `Codegen error: can't lower 'main' from the program graph: its index ''`.
  `TURNS[1]` and `TURNS[k]` fail the same way. A constant array of text
  works (`WORDS :: ["a", "b"]`, `WORDS[k]`: viewer.mara's MOON_PHASES),
  and so does the literal written in the loop. sooblivion's bot_join
  loops over the literal (bot_player.mara).

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

sooblivion builds with Mara's release, 9d90101a (MARA_VERSION.txt;
update_compiler.bat pulls the next), so all of these are in its copy.

- A struct holding a list couldn't be written into a byte buffer (the
  program wasn't made: "can't lower ... its view ''") — 9d90101a. The
  plugins' index (index_cache.mara) writes each Plugin_Span whole again,
  not a Kept_Span of some of its fields.
- mara.os couldn't add to the end of a file, and a program couldn't bind
  CreateFileA as mara.os did — 72fa281: file_open_append, and a foreign
  symbol may be bound again with the same C signature. logging.mara's
  full log appends with mara.os's; disk.mara still opens the cache's
  files for reading and writing both (CreateFileW), which mara.os
  doesn't.
- A generic fun's param couldn't have a default, so a generic couldn't
  take `#caller_span` or `#caller_name` — 2943553. sooblivion's check
  still takes the numbers, `fits(list.len + 1, list.cap)` (183 calls);
  it could take the list now (`room_for(&list)`).
- `-profile memory` gave an arena's peak as a number like an address —
  bdba31d: the most bytes in use at once.
- `-profile memory` didn't watch a list in an item made with `next()`
  from a carved slice, and put its len writes down to a list watched
  before at the same address — 5a34835; slices taken from storage are
  in the report too (105c8a4). The repro gives `Bytes.data` at 50000 of
  100000, `Part.texture` at 14.

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
