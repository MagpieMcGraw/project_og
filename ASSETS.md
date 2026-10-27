# Oblivion's assets in sooblivion

What the game's data holds and what sooblivion does with it, as of
2026-10-27. Scripts (SCPT) are left out on purpose. Counts are from
Oblivion.esm and the base game's archives; sizes are as stored.

## In use

- **World:** cells and their references, land (heights, normals, colors,
  texture layers; a world that's part of another, as a city's is of
  Tamriel, shows its parent's land: its own LAND records are left over),
  LTEX land textures, worlds, distant land (LOD pieces and far water),
  distant objects (`_far.nif`).
- **Things placed:** every base object with a model is drawn where it's
  placed — statics, activators, doors (swinging ones animated), lights,
  containers, furniture, flora, and items lying about.
- **Plants:** trees (as billboards only), grass.
- **Light and sky:** cell lighting and fog, point lights (flicker, pulse),
  climates and their weathers (see below), weather colors, fog and two
  cloud layers, the sun; interiors that behave like exteriors (the
  Temple of the One, the Arena, Oblivion's towers) lit by the sky.
- **Water:** WATR colors, ripples and scroll, cell water heights.
- **Meshes:** NIF geometry, base and glow textures, normal maps (`_n`,
  with their tangent space) and specular (the normal map's alpha, where it
  has an alpha channel; the material's specular color and glossiness),
  alpha, stencil and z-buffer
  properties, billboard nodes, flipbook textures, particle systems (box,
  cylinder and sphere emitters), Havok collision for walking, door
  Open/Close sequences and their sound keys.
- **Land normal maps:** each layer's `_n`, blended as its colors are.
- **Sound:** WAV files, SOUN records, placed sounds, light and activator
  sounds, door sounds.
- **Music:** `Data\Music`'s Explore, Public and Dungeon tracks (MP3,
  decoded by mp3.mara), by the place's kind: an interior cell's XCMT, a
  world's SNAM (the cities public, Oblivion's planes dungeon), a region's
  RDMD.
- **Animation:** Idle sequences' movement, scrolling textures, glow and
  opacity changes (see below for what's left).

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
| Voices | Voices1/2 BSAs: 38,898 `.mp3` + `.lip`, 1.7 GB; DIAL 3,817, INFO 19,278 | mp3.mara decodes them (checked against ffmpeg); `.lip` drives FaceGen mouth morphs |

### World and sky

Played now: weathers chosen by region (the cell's XCLR) or climate,
changing over game hours and blending in; rain and snow from the
weathers' precipitation meshes; stars, nebula, Masser and Secunda in
their phases, the sun's glare; weather sounds (rain, wind, thunder with
lightning) and the regions' sounds (birds, insects, wind).

| What | Data | Notes |
|---|---|---|
| 3D trees | 113 SpeedTree `.spt`; `textures\trees\branches` 90, `leaves` 78 | near trees are billboards now |
| Sunbeams | `sunbeam01–03.nif` | |
| HDR (eye adapting, bloom) | WTHR HNAM | |
| Water reflections | — | framebuffers are in now; left for later earlier |
| Region map colors | RCLR | |
| Rain kept off under roofs | — | it falls through them now |
| `.cmp` files | 55 in `distantlod` | purpose not known yet |

### Animation on objects

Played now: Idle and SpecialIdle sequences' node movement (hanging
corpses, ship sails, sigil stones…), and controllers moving a base
texture across or up (waterfalls, light beams), changing a material's
glow or opacity — their own, or an Idle's.

| What | Data | Notes |
|---|---|---|
| Sequences started by use or by scripts | Forward/Backward (130/66), Open/Close of activators, Equip/Unequip | traps, platforms, levers |
| Visibility over time | NiVisController in 35 meshes | Oblivion gates' meteors |
| Particle controllers in sequences | emitter on/off and speed keys in SpecialIdles | Oblivion gates |
| Textures turned or scaled | NiTextureTransformController's rotate and scale | sigil stones |
| Material diffuse and other colors | NiMaterialColorController's non-emissive targets | |
| Morphs | NiGeomMorpherController in 62 meshes | mostly creatures |
| Moving along paths | NiPathInterpolator in 9 | butterflies, moths, spell effects |

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
| Battle and special music | `Data\Music\Battle` 8, `Special` 3 (title, death, success) | with combat and menus |
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

### To check against the game (a decompile, later)

How the engine uses data whose meaning the files don't give; sooblivion
guesses for now.

- The sun's arc from the climate's hours (on the horizon at 6:00 and
  20:00 here), the moons' orbits and sizes, when the stars fade in (with
  the sky's colors here: half in at 18:00, the sun still up).
- How long a weather stays and comes in (4 to 8 hours here; its
  transition byte mapped to a quarter to a whole hour).
- The scale of a region sound's chance (ten-millionths of a try every
  2 s here).
- Which parts shine (specular only where a normal map has an alpha
  channel here, the material's specular color tinting it).
- Point lights' falloff (the game reads a lookup texture), and the mist
  near ruin lamps looking brighter than remembered.
- Placed sounds that don't loop (played again after 6 to 12 s here).
- Grass in small worlds (the walled cities', the Imperial City districts',
  the Oblivion realms): none grows here. A city's world shows Tamriel's
  land, and with the cities put back in Tamriel (Open Cities) grass is
  known to come up through their streets from that land.
- An interior that behaves like an exterior: lit by the weather's sun
  and ambient here, its own XCLL unused; the sky drawn, no rain or
  snow; one naming no climate (the Temple of the One) under the one
  outside's.
- The weather through a gate: it goes on into a world of the same
  climate here (a city has its parent Tamriel's); another climate's
  world (an Oblivion realm) starts its own at once.
- Music: what an interior cell of the default type plays (Explore here);
  how loud it is beside the sounds (the Oblivion.ini here: 0.3 to 0.8);
  whether tracks have pauses between them (none here), and how a change
  of kind fades (2 s out, then the next starts).

### Probably left alone (gameplay)

Scripts (SCPT 2,393, by choice), quests (QUST 390), AI packages (PACK
7,209), path grids (PGRD 8,228), combat styles, factions, classes, skills,
birthsigns, spells and enchantments, leveled lists, ROAD (AI roads), game
settings (GMST 382, GLOB 94; some visual ones are copied in as constants),
Havok constraints and ragdolls, furniture markers.
