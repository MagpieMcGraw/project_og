# Oblivion's assets in oblivion

What the game's data holds and what oblivion does with it, as of
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
- **Plants:** trees, grown from their SpeedTree files within 4096 units
  (bark with its normal maps, leaf cards facing the camera; a seed of the
  record's each) and billboards past that; grass.
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
  sounds, door sounds, the player's weapon swishes and blows
  (WPNSwish*, WPNHit*: on flesh, or on anything else).
- **NPCs, standing:** the people placed (ACHR), each put together from
  their race's body (its textures on the shared meshes) and head parts,
  their eyes and hair (tinted by their hair color), a tail for the beast
  races, and what they wear (the clothes and armor they carry, leveled
  lists taken at level 10, one item to a slot) — skinned to their skeleton
  (NiSkinInstance, NiSkinData) and playing `idle.kf` over and over (its
  B-spline keys read; their bones move them on the card, each NPC's idle
  put off by up to 10 s so no two breathe together), as tall as their
  race. Their faces are their own (FaceGen):
  the head and what sits on it shaped by their FGGS and FGGA through each
  part's `.egm`; the skin moved by their face map, the game's own in
  `textures\faces` (1,977 of 2,482 NPCs) or made from the head's `.egt`
  and their FGTS, added as the game's SKIN2000.pso adds it; hair colored
  as HAIR2000.pso does (a hair mesh's vertex green says how much shows).
- **Plugins:** Oblivion.esm and the downloaded content DLCList.txt names
  (Knights of the Nine, Battlehorn Castle, Frostcrag Spire, Thieves' Den,
  Vile Lair, the Orrery, Mehrunes' Razor, the Spell Tomes, Horse Armor),
  in the game's order (by when each file was written): their records over
  the master's, form ids by place in the load order, a cell's references
  from each file that places some. Their archives with the game's; the
  Shivering Isles, already merged into this Oblivion.esm (its esp is
  empty), take their meshes, textures and sounds from theirs.
- **The player, in first person:** their race's upper body and hands
  (or what they wear there) on `_1stperson\skeleton.nif`, its eyes
  (`Camera01`, as the animation moves them) on the camera's, drawn in a
  depth of its own and framed as the game frames it (75 degrees across a
  screen of any shape); an iron longsword in the `Weapon` bone (its
  scabbard, `Scb`, left out), playing `onehandidle.kf`, and on a left click
  `onehandattackright.kf`. A click during a swing queues the other
  (`onehandattackleft.kf`, then back), which cuts in at the swing's
  `a:L` or `a:R` key; each change mixes the poses over 0.12 s. At the
  Hit key, the nearest NPC within 160 units in front, short of a wall,
  is struck (the journal says whom).
- **Music:** `Data\Music`'s Explore, Public and Dungeon tracks (MP3,
  decoded by og's mp3), by the place's kind: an interior cell's XCMT, a
  world's SNAM (the cities public, Oblivion's planes dungeon), a region's
  RDMD.
- **Creatures, standing:** the creatures placed (ACRE), a leveled one
  (LVLC) as the one its list gives that placing at level 10 (the server
  picks, so every player sees the same), put together as NPCs are: their
  skeleton (MODL), the meshes beside it (NIFZ), their size (BNAM),
  skinned and playing the `idle.kf` beside their skeleton; their walk
  (`forward.kf`) and run (`fastforward.kf`, else `runforward.kf`) read.
  `oblivion creatures` puts every one together headless: 959 of 992
  whole (see below for the rest).
- **Animation:** Idle sequences' movement, scrolling textures, glow and
  opacity changes, NPCs' idle (see below for what's left).

## Not used yet

### Actors — the biggest piece

| What | Data | Notes |
|---|---|---|
| NPCs moving about | IDLE 650 (the idles their conditions pick), AI packages, the walking and turning `.kf` | they stand where they're placed, breathing (`idle.kf`) |
| Faces' age and expressions | the age maps (`headhuman{m,f}{10..60}.dds` and their normal maps: the skin shader's FaceGenMap1, times 4), which `facegen\si.ctl`'s age control picks; `.tri` 85 (expressions, the mouth for speech); the bodies' `.egt` | shapes and skins are used (see above); the skin is as if of no age |
| Weapons and shields worn | WEAP, their models on the back or side (a mesh's `Prn` names the bone: SideWeapon, BackWeapon) | the player holds one in first person |
| Combat | WEAP damage and reach, health, NPC reactions (stagger, recoil `.kf`), blocking, power attacks, the player's gear and inventory | a blow finds whom or what it meets, and sounds; nothing comes of it yet |
| Creatures moving, fighting, their sounds | CREA's AI packages, attacks (`handtohandattack*.kf`, `attackforward*.kf`), sound lists (CSCR, CSDT) | they stand, breathing; walked round as a person is (an upright cylinder 56 across: a horse's too, a rat's too) |
| Creatures not put together | 28 whose NIFZ names a mesh the archives haven't by that name (Knights of the Nine's: `MinionHead.NIF` where Knights.bsa has `ndminionhead.nif`), 5 templates with no skeleton (MS16OgreCreatureTemplate…) | how the game finds those meshes isn't known yet |
| Animations | `.kf` 1,843 (creatures 1,068, characters 775); IDLE 650 | read (B-splines too, and text keys); NPCs play idle.kf; the player's first-person idle and two attacks |
| Voices | Voices1/2 BSAs: 38,898 `.mp3` + `.lip`, 1.7 GB; DIAL 3,817, INFO 19,278 | og's mp3 decodes them (checked against ffmpeg); `.lip` drives FaceGen mouth morphs |

### World and sky

Played now: weathers chosen by region (the cell's XCLR) or climate,
changing over game hours and blending in; rain and snow from the
weathers' precipitation meshes; stars, nebula, Masser and Secunda in
their phases, the sun's glare; weather sounds (rain, wind, thunder with
lightning) and the regions' sounds (birds, insects, wind).

| What | Data | Notes |
|---|---|---|
| Trees' wind, fronds, collision | `.spt` flexibility curves (6002, 6003), wind (9000s, 16000s), fronds (13000s, 14002), collision (5000s); TREE CNAM leaf angles, dimming, rock and rustle speeds | trees stand still; their trunks are walked round as cylinders (not the files' collision shapes) |
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
| Menus, HUD | Misc BSA: 89 menu `.xml`; `textures\menus` 1,999 (+ 80% and 50% copies, 3,545) | menus.mara reads the menus' XML (tiles, traits worked out by their operations, `<include>`d prefabs, &true; 2 and &false; 1) and draws it; the HUD is drawn from `hud_main_menu.xml`, `hud_reticle.xml` and `hud_info_menu.xml` with what the game sets in them (the ribbons full: no stats yet). F1 opens `stats_menu.xml` (pages 1 and 2 filled: the player's record's name, race, class, level, attributes; health, magicka and fatigue worked out from them), F4 `map_menu.xml` (the world map page: the WRLD's ICON picture placed by its MNAM corners, centered on the player, their arrow from the map_world_icon template; the place and the date from GameDay/GameMonth/GameYear); clicking a tab turns the page. Escape's pause menu, Options, Audio (five volumes) and Controls (`controls_menu.xml`: the mouse's sensitivity and invert Y; the controls listed, rows copied from its template, scrolled by the wheel or arrows and cut to the list's window, one clicked listening for its key, a key another had swapped). The skills, factions and misc pages, the local map and the quest log are empty; `listclip`, NIF tiles and scrolling aren't done |
| Fonts | 5 `.fnt` + `.tex` | read: a 296-byte header (the line's height first), 256 glyphs of 14 numbers (the texture, its corners' u and v, width, height, room before and after, height above the baseline); the `.tex` its width, height and RGBA |
| Loading screens | LSCR 337 | a texture and a line of text each |
| Books | BOOK 887 | HTML-ish text |
| Maps | world and local map textures | |
| Item icons | ICON fields; `textures\menus\icons` (~1,160, each in three sizes) | |
| Video | 9 Bink `.bik` | a closed codec; likely left out |

### Plugins and archives not used

| What | Data | Notes |
|---|---|---|
| The player's chosen plugins | `Plugins.txt` in their local app data | oblivion loads what DLCList.txt names (all the DLC here); the path needs an environment variable Mara can't read yet |
| Loose files | `Data\Textures` and the like | the game takes them over the archives' |

### To check against the game (a decompile, later)

How the engine uses data whose meaning the files don't give; oblivion
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
- A material's diffuse color: used here only on untextured parts
  without vertex colors (the sewer gates' black backing); textured ones
  without colors are white (the game's object shaders take MatAlpha and
  MatEmit but no diffuse; a silver battleaxe's blade is black by its
  material; the Skingrad-style bridges' SkingradBridgeEdge01 pieces lie
  on a copy of their railing in SkingradBridgeMain01, gray 0.588 against
  its white vertex colors, and flickered).
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
- Walking into trees and people: a tree's trunk is an upright cylinder
  as thick as its grown trunk's foot here (or its ring above, the
  thinner), shrubs (thinner than 8 across) walked through; a person a
  cylinder 56 across and 128 tall. The game has the trees' `.spt`
  collision shapes and the actors' own.
- A swing's swish by the weapon's kind and weight (two-handed: large; a
  one-handed blade under 6: small; else medium), played as the swing
  starts; a blow's sound as it lands, by edge (blunt or blade), on flesh
  or on anything else.
- What E aims at: the collision here, a door counting up to 48 units
  behind a wall's collision (the castles' tower walls close their
  collision over their load doors' doorways). The game may aim at what's
  drawn instead.
- NPCs' gear: leveled lists taken at level 10 here, one entry picked by
  the NPC and the list (the game picks at random by the player's level);
  enable parents (XESP) aren't followed, so NPCs a quest brings in later
  stand there already.
- Which archive's file wins where two have one: the plugins' own here,
  the last loaded first, then the master's.
- Trees, grown here as SpeedTree's library isn't to be had (see
  speedtree.mara): lengths as shares of the file's size times its scale
  (2006, in percent: what makes young trees small); the children's curves
  read along their parent's whole length; a branch's count its frequency
  times its length's share of the size; gravity bending each segment down
  by how far it reaches sideways. Then fitted to the billboard: as tall
  as its silhouette and stretched sideways (0.6 to 1.8 times) to be as
  wide, with as many leaf cards as cover the crown 1.6 times over in
  their opaque parts. Which of a record's seeds a reference grows (its form id
  picks one here), and how far away the game turns trees to billboards
  (4096 units here).
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
