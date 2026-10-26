# Mara issues found in sooblivion

Problems with the Mara compiler, standard library and bindings met while
writing sooblivion. Each has a small program that shows it, checked
against Mara at the time written. When one is fixed, move it to Fixed
(with the commit) and sooblivion's workaround can come out.

## Open

### 1. An inner loop's index named as the outer loop's is the same variable

Found 2026-10-26. A `for` loop inside another, its index named as the
outer one's, isn't reported as hiding it (other hiding is an error:
"variable 'name' shadows an enclosing binding"). It is the outer index:
after the inner loop, the outer loop goes on from where the inner one
left it, so here it never ends.

```
for value, i in [10, 20, 30, 40] {
	for i in 0:2 { }
	print("% at %", value, i)   // "10 at 2", then "40 at 2" forever
}
```

Expected: an error (the inner `i` hides the outer), or a new variable.
sooblivion's `nifs` command looped for 20 minutes on it (fixed there by
naming the inner index `b`).

### 2. Writing a field of a union variant's value fails in lowering

Found 2026-10-26. A value built with a variant's constructor passes the
checker when a field of it is written, then lowering stops:
`Graph error: lower: a write to an unknown field`.

```
Shape :: union {
	Other = 0
	Box {
		width: f32
		height: f32
	}
}

main :: fun(args: [][]utf8) {
	box := Box{width = 1, height = 2}
	box.height = 3      // Graph error: lower: a write to an unknown field
}
```

Expected: the write works, or the checker says why it can't. sooblivion
builds its variants (Transform_Data, Sequence in nif_animation.mara) from
finished values instead.

### 3. Float literals with an exponent aren't read

Found 2026-10-26. `1.5e3` is read as `1.5` followed by a name, `e3`:

```
A :: 3.4e38        // at a module's top: "this module statement is not supported yet (Expr_Stmt)"

main :: fun(args: [][]utf8) {
	x : f32 = 1.5e3     // in a fun: "undefined identifier 'e3'"
}
```

A negative constant without an exponent is fine (`B :: -3.4`). The
module-level message doesn't point at the cause. sooblivion writes the
number out (UNSET_BEYOND in nif_animation.mara).

## Fixed

- A loop over a literal array of arrays (`for point in [[4, 4], [16, 16]]`)
  failed in lowering — bcddc81.
- A module's constant couldn't size an array (`[render.GRASS_PER_CELL]T`) — d0b31c0.
- gl_load handed c_text's views (no room for the 0 after them) to
  GL_GetProcAddress, whose cstring() stopped the program — 4ef56de.
- Foreign blocks made private, the bindings wrapping them — 48033df
  (sooblivion converted: 968cd07, d60f499).
