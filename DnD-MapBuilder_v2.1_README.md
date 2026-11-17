# DnD MapBuilder v2.1

Print and play adventures for tabletop RPGs like D&D: click a button for an outdoor area map, add adventure locations, give every location a floor plan, print it all, bring it to game night.

The area map comes from DnD MapBuilder Exterior v2.0, so a seed makes the same land and locations here as there. Buildings and hideouts are built and drawn by DnD MapBuilder Interior v1.0, with hallways, stairwells that line up from floor to floor, and secondary staircases, so a seed makes the same building or hideout here as there. The dungeon complex lays its rooms out on an even grid joined by short corridors, and the inside of every room is built by the Interior v1.0 builder too. Once the area map has its locations marked with a red x, you can pick a floor plan for each location by hand, or let the script pick them all, and save everything in one folder with a list that ties each location to its floor plan.

## Requirements

- Python 3.8 or newer, Pillow 10.1 or newer (`python3 -m pip install pillow`) and Tkinter (comes with the standard Python installer)
- macOS, Windows or Linux
- A printer and 8.5 x 11 paper, to play at the table

## Quick Start

```bash
python3 DnD-MapBuilder_v2.1.py
```

1. Click "Area map" until you like the land.
2. Click "Adventure locations" to put numbered locations marked with a red x on it.
3. Answer "Would you like to generate floor plans for the locations on your adventure?" with "Yes", "No" or "Make automatically".
4. At "Save?", click "Yes", type a name and press "OK". Everything is saved in its own folder inside `Maps`, next to the script.
5. Print the `_grid` (blue grid) or plain JPGs on 8.5 x 11 paper with "Fit to page" (or "Scale to fit") on.

A full-size window opens with the buttons at the top, the seed box under them, a line of text about the map, the question row, and a black preview area below.

## Features Walkthrough

### Area map

1. Click "Area map". The map is 17 x 13 squares of 70 x 70 pixels: thin wandering lines that cut the land into regions, with patches of forest (dark green trees), sand (grey dots and small triangles) and water (light blue waves).
2. Each line is drawn partly straight and partly wobbly. The same seed always draws the same lines.
3. The squares are named round the edge: "A" to "Q" along the top and bottom, "1" to "13" down both sides.
4. With no locations on the map, the window asks "Do you want to save the generated map?".

### Adventure locations

1. Click "Adventure locations". Up to 29 numbered locations marked with a red x appear, inside the map, at least 40 pixels apart and never in the water. There are at least 7 when the land has room; fewer only if it runs out.
2. Click it again for a new set. The land under them does not change.
3. Location 1 and the last location are the two farthest apart. The others are numbered in order between them.

### Floor plans: "Yes"

1. The top row changes to the white floor plan buttons: "Building", "Village", "Hideout", "Town" and "Dungeon complex".
2. Above them the window says which location is next, like "Location 3 of 12, square M9". The preview shows the area map with that location's x in red and every other x in grey, so you can see where it is.
3. Click any button to make a floor plan. Click again, or another button, until one suits the location.
4. Click "Use for this location". The window moves on to the next location.
5. At the last location it suggests a "Dungeon complex" or a "Town" for the finale.
6. After the last location the area map comes back with the question "Save?".

### Floor plans: "Make automatically"

1. Every location gets a floor plan at once, picked from the locations seed.
2. Every location but the last: Building 6 times in 10, Village 2 in 10, Hideout 2 in 10.
3. The last location: a Town or a Dungeon complex, 1 chance in 2 each.
4. The same code always gets the same floor plans.

### Floor plans: "No"

Goes straight to "Save?". The locations are saved without floor plans.

### The floor plans

- Building: one floor with rooms and hallways and no stairs, from 4 x 4 squares up to 17 x 13 squares. Every building has an entrance, and half have a second way out.
- Village: 6 to 11 buildings.
- Hideout: 3 or 4 levels, above and below ground. The ground level is 17 x 13 squares; each level fits inside the one nearer ground. A main stairwell links levels 1, 2 and -2, and often opens straight onto a hallway. Levels 3, 4, -3 and -4 are reached by secondary staircases, which the level headers name.
- Town: 12 to 29 buildings and a hideout.
- Dungeon complex: 15 to 99 rooms on an even grid, joined by short corridors that each join two rooms and never cross, with an entrance from the west edge and an exit to the east edge. Every room is cut into 2 to 11 inner rooms, about half of them with hallways, and comes with a room key.
- Village, town and dungeon complex previews are big: click "Open full size" to see them in your picture viewer.

### The hideout overview

The hideout overview shows every level side by side, each drawn where it sits over the ground floor, so the stairwells line up. Light blue squares show where the ground floor reaches past a level. Darker blue squares show the outline of the floor next to it, nearer ground, so you can see how each level sits on the one below or above it.

### Seeds and codes

1. Every area map has a seed. Once locations are added the line of text shows a code instead: the map seed, a dash, and the locations seed, like `123456789012345-987654321098765`.
2. Paste a seed into the seed box and click "Area map" for that map, or "Adventure locations" for those locations on the map that is showing. Paste a code and click either button for both.
3. Every floor plan has a seed of its own, shown on the line of text and in the locations list. While choosing floor plans, paste a seed into the seed box and click the same button to get that floor plan again.

### Print and play

The area map prints on one sheet. Every floor, hideout level, dungeon room and building prints on one sheet of its own, with a 1 square margin and a small header inside it with its location, kind and seed.

## Reference Tables

### The question row

| Question | Buttons | What happens |
|---|---|---|
| Do you want to save the generated map? | "Yes", "No" | An area map with no locations: save it, or clear it |
| Would you like to generate floor plans for the locations on your adventure? | "Yes", "No", "Make automatically" | Pick floor plans by hand, skip them, or let the script pick them |
| Use this floor plan for location n? | "Use for this location", and "Open full size" for dungeon, village and town plans | Gives the plan to the location and moves on |
| Save? | "Yes", "No" | Save everything, or clear it |

### Saved files

Every map is saved inside `Maps/<name>/`. The name is the one you type at "Save map".

| File | What it is |
|---|---|
| `<name>.jpg`, `<name>_grid.jpg` | The area map, without and with the blue grid |
| `<name>_locations.txt` | The code, the number of locations, and every location with its square and its floor plan's kind and seed |
| `<name>_location_<nn>_building_walls.jpg`, `..._grid.jpg` | A location's building |
| `<name>_location_<nn>_hideout_level_<n>_walls.jpg`, `..._grid.jpg`, `<name>_location_<nn>_hideout_overview.jpg` | A location's hideout, level by level, and its overview. The ground level is 1, levels above it are 2, 3 and 4, and levels below it are -2, -3 and -4 |
| `<name>_location_<nn>_village_building_<nn>_walls.jpg`, `..._grid.jpg`, `<name>_location_<nn>_village_overview.jpg`, `<name>_location_<nn>_village_buildings.txt` | A location's village: every building, the overview and a buildings list |
| `<name>_location_<nn>_town_building_<nn>_...`, `<name>_location_<nn>_town_hideout_...`, `<name>_location_<nn>_town_overview.jpg`, `<name>_location_<nn>_town_buildings.txt` | A location's town: every building, its hideout, the overview and a buildings list |
| `<name>_location_<nn>_dungeon_room_<nn>_walls.jpg`, `..._grid.jpg`, `<name>_location_<nn>_dungeon_overview.jpg`, `<name>_location_<nn>_dungeon_room_key.txt` | A location's dungeon complex: every room, the overview and the room key |

### Example locations list

This is the start of a real list, made with the code `123456789012345-987654321098765` and "Make automatically":

| Location | Square | Floor plan |
|---|---|---|
| Location 1 | B7 | Village, Seed 922578354291723 |
| Location 2 | C7 | Building, Seed 295664097723414 |
| Location 4 | J9 | Hideout, Seed 491635992909220 |
| Location 11 | O6 | Dungeon complex, Seed 880856321995153 |

### Ways to run it

| Command ending | What it does |
|---|---|
| (nothing) | Opens the window |
| `SEED` | Opens the window already showing the area map with that seed |
| `SEED-SEED` (a code) | Opens the window showing that area map with those locations |

### Settings

In the AREA MAP SETTINGS and FLOOR PLAN SETTINGS sections of the script. Several area map settings share a line, so change only the value you need.

| Setting | Now | What it changes |
|---|---|---|
| `LINE_WIDTH`, `FRAME_WIDTH` | 1, 7 | Area map line and frame thickness in pixels |
| `FOREST_COLOR` | (20, 100, 40) | Colour of the trees (dark green) |
| `WATER_COLOR` | (110, 170, 235) | Colour of the water waves (light blue) |
| `TEXTURE_COLOR` | (90, 90, 90) | Colour of the sand marks |
| `X_COUNT` | (7, 29) | Fewest and most adventure locations asked for |
| `X_GAP2` | 1600 | Pixels kept between locations, squared (40 pixels) |
| `RED` | (220, 0, 0) | Colour of the red x marks and their numbers |
| `X_GREY` | (165, 165, 165) | Colour of the other x marks while choosing a floor plan (saved maps always show them red) |
| `GRID_COLOR`, `GRID_WIDTH` | (140, 190, 255), 1 | The blue grid on the area map's `_grid` sheet |
| `OUTER_WALL`, `INNER_WALL` | 7, 3 | Floor plan wall thickness in pixels |
| `PLAN_GRID_COLOR` | (140, 190, 255) | Floor plan grid colour |
| `NEXT_FLOOR_FILL` | (80, 130, 225) | The darker blue on the hideout overview |
| `LEVEL_COUNTS` | (3, 4) | How many levels a hideout may have |

## Features

- One window for a whole adventure: the land, the locations, and a floor plan for every location
- Floor plans picked by hand, one location at a time, or all at once with "Make automatically"
- Buildings and hideouts with hallways, stairwells that line up, and secondary staircases
- Dungeon complexes on an even grid, with hallways inside about half the rooms
- Every map fits one 8.5 x 11 sheet and is saved with and without the grid
- One text list ties every location to its square and its floor plan's seed
- Separate seeds for the land, the locations and each floor plan, so any piece can be brought back
- Makes the same area maps as DnD MapBuilder Exterior v2.0, and the same buildings and hideouts as DnD MapBuilder Interior v1.0
- Every button white, whether the Mac is in Light or Dark Mode
- While choosing floor plans, the location being chosen stays red and the others turn grey

## Integration

```
Python/
├── DnD-MapBuilder_v2.1.py              <-- this tool
├── DnD-MapBuilder_v2.1_README.md       <-- this file
└── Maps/                               <-- made on the first save
    └── quest1/
        ├── quest1.jpg
        ├── quest1_grid.jpg
        ├── quest1_locations.txt
        ├── quest1_location_01_village_building_01_walls.jpg
        ├── ...
        ├── quest1_location_02_building_walls.jpg
        ├── ...
        └── quest1_location_11_dungeon_room_key.txt
```

The script is a single file and stands on its own. It needs only Python, Tkinter and Pillow. It does not need the Exterior or Interior scripts: their map builders are inside it. It reads no other files, and the only thing it saves is the `Maps` folder next to itself ("Open full size" also uses a temporary file, see Security Notes).

## Common Use Cases

### Game Master: A whole adventure for next session

1. Click "Area map", then "Adventure locations", until the land and the spread of locations feel right.
2. Click "Make automatically", then save it.
3. Print the area map's `_grid` sheet for the table. Keep `<name>_locations.txt` behind your screen and print each location's sheets as the party gets there.

### Game Master: Hand-picking the important places

1. Make the area map and its locations, then click "Yes".
2. For each location, click buttons until the floor plan fits your story, then "Use for this location".
3. Finish with a "Dungeon complex" or a "Town" at the last location for the big finale.

### Game Master: Same land, new adventure

1. Paste the old area map's seed into the seed box and click "Area map".
2. Click "Adventure locations" for new locations, and give them floor plans.
3. Save it under a new name. The new code is in the header and the locations list.

### Online Game Master: Running the adventure on a virtual tabletop

1. Save the adventure as usual.
2. Import the area map and each floor plan's `_grid` or plain JPG.
3. Set the platform's grid to 70 pixels per square.

## Troubleshooting

| Issue | Solution |
|---|---|
| `ModuleNotFoundError: No module named 'PIL'` | Run `python3 -m pip install pillow` |
| `ModuleNotFoundError: No module named 'tkinter'` | Install Python from python.org, which includes Tkinter |
| The window does not appear | Run the script from the Terminal app rather than from inside another program |
| "Make a map first with the "Area map" button." | Click "Area map" before "Adventure locations" |
| "No map could be made from this seed." | Rare. Click "Area map" again for a new map |
| "A seed is digits only ..." | Type digits only, or two seeds joined by a dash for a code. While choosing floor plans only a single seed works |
| The floor plan question does not appear | It only appears once the map has locations. Click "Adventure locations" first |
| The area map buttons are gone | You are choosing floor plans. Give every location a floor plan with "Use for this location" and they come back |
| A big floor plan preview is too small to read | Click "Open full size" and zoom in |
| A floor plan seed from v1.5 or older gives a different plan | Buildings, villages, hideouts, towns and dungeon room insides are made differently since v2.0. Area maps, locations and dungeon layouts are unchanged |
| The saved folder has hundreds of files | A town or dungeon complex saves every building, level or room. That is normal |
| "Use: [SEED or CODE]" | The script was started with something it does not know. Use only a seed or a code |
| "There is already a folder called ..." | Pick another name. A saved map is never overwritten |
| `Use a name without / \\ : * ? ...` | Take those characters out of the name, and do not start it with a dot |
| The printed map is cut off at the edges | Switch on "Fit to page" or "Scale to fit" in the print window |
| Cannot find the saved maps | Look in the `Maps` folder next to the script. The line of text in the window shows the full path after saving |

## Security Notes

- Offline: The script never uses the network.
- Writes Only To Maps: The only files it saves are JPG pictures and text files (the locations list, buildings lists and room keys), in the `Maps` folder next to the script.
- Open Full Size: "Open full size" hands a temporary copy of the preview to your picture viewer, saved in the system's temporary folder.
- Never Overwrites: Saving stops if a folder with that name already exists.
- Safe Names: Map names with path characters, or starting with a dot, are refused, so a save cannot land outside `Maps`.
- No Personal Data: The pictures and text files hold only the maps, their seeds and codes, and the locations.
- Standalone: One file with no installer. Deleting the script and the `Maps` folder removes everything it saved.
