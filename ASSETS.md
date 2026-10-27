# Oblivion's assets in sooblivion

What the game's data holds and what sooblivion does with it, as of
2026-10-27. Scripts (SCPT) are left out on purpose. Counts are from
Oblivion.esm and the base game's archives; sizes are as stored.

## In use

- **World:** cells and their references, land (heights, normals, colors,
  texture layers), LTEX land textures, worlds, distant land (LOD pieces
  and far water), distant objects (`_far.nif`).
- **Things placed:** every base object with a model is drawn where it's
  placed — statics, activators, doors (swinging ones animated), lights,
  containers, furniture, flora, and items lying about.
- **Plants:** trees (as billboards only), grass.
- **Light and sky:** cell lighting and fog, point lights (flicker, pulse),
  climate (its likeliest weather only), weather colors, fog and two cloud
  layers, the sun.
- **Water:** WATR colors, ripples and scroll, cell water heights.
- **Meshes:** NIF geometry, base and glow textures, normal maps (`_n`,
  with their tangent space) and specular (the normal map's alpha, the
  material's specular color and glossiness), alpha, stencil and z-buffer
  properties, billboard nodes, flipbook textures, particle systems (box,
  cylinder and sphere emitters), Havok collision for walking, door
  Open/Close sequences and their sound keys.
- **Land normal maps:** each layer's `_n`, blended as its colors are.
- **Sound:** WAV files, SOUN records, placed sounds, light and activator
  sounds, door sounds.

## Not used yet

### Actors — the biggest piece

| What | Data | Notes |
|---|---|---|
| NPCs placed | ACHR 2,190; NPC_ 2,482 | none drawn |
| Bodies and skinning | NiSkinInstance/Data/Partition in 731 meshes; `meshes\characters` | skinned meshes need a skeleton and bone matrices |
| Heads (FaceGen) | `.egm` 141, `.tri` 85, `.egt` 20; `textures\faces` 3,854 (each NPC's face tint) | morphs per NPC from NPC_ FaceGen data |
| Hair, eyes | HAIR 57, EYES 13, RACE 15 | |
| Worn clothing, armor | ARMO 996, CLOT 604 (their worn models, male and female) | only their ground models are drawn now |
| Creatures | ACRE 1,473 placed; CREA 914; 34 creature folders | none drawn |
| Animations | `.kf` 1,843 (creatures 1,068, characters 775); IDLE 650 | idles, walking; needs skinning first |
| Voices | Voices1/2 BSAs: 38,898 `.mp3` + `.lip`, 1.7 GB; DIAL 3,817, INFO 19,278 | MP3 decoding; `.lip` drives FaceGen mouth morphs |

### World and sky

| What | Data | Notes |
|---|---|---|
| 3D trees | 113 SpeedTree `.spt`; `textures\trees\branches` 90, `leaves` 78 | near trees are billboards now |
| Regions | REGN 211 | ambient sounds, per-region weather chances, map colors |
| Weather changes | CLMT weather lists, WTHR transitions | only the likeliest weather is shown, never changing |
| Rain, snow, lightning | `meshes\sky\rainheavy`, `rainlight`, `snow`; WTHR precipitation, lightning, thunder | |
| Stars, moons, sun glare, sunbeams | `meshes\sky\stars.nif`, moon textures, CLMT sun glare, `sunbeam01–03.nif` | |
| Weather sounds, HDR | WTHR SNAM; WTHR HNAM | |
| Water reflections | — | framebuffers are in now; left for later earlier |
| `.cmp` files | 55 in `distantlod` | purpose not known yet |

### Animation on objects

| What | Data | Notes |
|---|---|---|
| Objects that move | NiControllerManager in 423 meshes (doors done); NiTransformController 164; ANIO 34 | windmills, waterwheels, traps, banners |
| Scrolling textures | NiTextureTransformController in 42 meshes | lava, waterfalls, Oblivion gates |
| Color and fade changes | NiMaterialColorController 127, NiAlphaController 21, NiVisController 35 | |
| Morphs | NiGeomMorpherController in 62 meshes | |
| Moving along paths | NiPathInterpolator in 9 | |

### Materials

| What | Data | Notes |
|---|---|---|
| Specular on land, and point lights on land | — | land is lit by the sun and ambient light only |
| Parallax | some normal maps' height | |
| Other texture slots | dark, detail, gloss, bump, decal | base and glow are read (normal maps by name) |

### Effects

| What | Data | Notes |
|---|---|---|
| Magic visuals | MGEF 145, EFSH 102 effect shaders; `meshes\magiceffects`, `textures\magic` 116 | mostly with gameplay; enchanted items glow |
| Rest of particles | mesh emitters (29 meshes), planar colliders (9), drag (14), bomb, mesh particles; emitter speed, radius and life controllers; systems driven by a controller manager | |

### Sound and music

| What | Data | Notes |
|---|---|---|
| Music | `Data\Music`: 28 `.mp3` (Explore, Public, Dungeon, Battle, Special) | needs an MP3 decoder (shared with voices) |
| Outdoor ambience | REGN sound lists | wind, birds, insects by region, weather and time |
| Footsteps | — | by surface material |
| Creature, magic, menu sounds | CREA sound lists; MGEF sounds; 12 menu SOUNs | with actors and UI |

### Text, menus and maps

| What | Data | Notes |
|---|---|---|
| Menus, HUD | Misc BSA: 89 menu `.xml`; `textures\menus` 1,999 (+ 80% and 50% copies, 3,545) | |
| Fonts | 5 `.fnt` + `.tex` | |
| Loading screens | LSCR 337 | a texture and a line of text each |
| Books | BOOK 887 | HTML-ish text |
| Maps | world and local map textures | |
| Item icons | ICON fields; `textures\menus\icons` (~1,160, each in three sizes) | |
| Video | 9 Bink `.bik` | a closed codec; likely left out |

### Plugins not loaded

| What | Data |
|---|---|
| Shivering Isles | DLCShiveringIsles.esp; Meshes 3,017 files, Textures 1,869, Sounds 499, Voices 19,089 (430 MB) |
| Knights of the Nine | Knights.esp/.bsa: 4,810 files (mostly voices) |
| Small DLC | Battlehorn Castle, Frostcrag Spire, Thieves Den, Vile Lair, Orrery, Horse Armor, Mehrunes Razor, Spell Tomes |

Loading these means plugins over the master: overriding records and new
forms (load-order form ids), and their archives.

### Probably left alone (gameplay)

Scripts (SCPT 2,393, by choice), quests (QUST 390), AI packages (PACK
7,209), path grids (PGRD 8,228), combat styles, factions, classes, skills,
birthsigns, spells and enchantments, leveled lists, ROAD (AI roads), game
settings (GMST 382, GLOB 94; some visual ones are copied in as constants),
Havok constraints and ragdolls, furniture markers.
