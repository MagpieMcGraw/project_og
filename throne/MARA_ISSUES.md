# Mara issues found in throne

Problems with the Mara compiler, standard library and bindings met while
writing throne (the Throne of Darkness port). Each has a small program
that shows it, checked against Mara at the time written. When one is
fixed, move it to Fixed (with the commit) and throne's workaround can
come out.

## Open

- A module's constant array of text handed whole to a `[][]utf8` param
  compiles, but the callee reads garbage (checked against Mara 373ba2b7,
  2026-10-30):

      module textarray
      use mara.core
      NAMES :: ["walk", "Mouse_Left"]
      first :: fun(names: [][]utf8) {
          print("count % first %", names.len, names[0])
      }
      main :: fun(args: [][]utf8) {
          print("by index: % %", NAMES[0], NAMES[1])
          first(NAMES)
      }

  prints `by index: walk Mouse_Left`, then `count 2 first (nul`: the
  count is right, the slices aren't. In throne it crashed reading address
  0x7466 — "ft" of "Mouse_Left", the text's own bytes taken for a
  pointer. Indexing the constant (`NAMES[k]`) and looping over it work;
  throne hands its actions over one at a time (throne.mara,
  game_own_controls). Either it should pass slices or refuse to compile.

## Fixed
