# DnD

Dungeons & Dragons stuff to make life easier.

This repo holds print and play tools for tabletop RPGs like D&D. Each tool is a single Python file that opens a window: click a button, get a map, print it, bring it to game night. Every map fits one 8.5 x 11 sheet of paper, with a 70 pixel grid, and every map is saved as a JPG.

The tools so far make two kinds of map:

- Area maps: outdoor land with forests, sand and rock, and water, plus numbered adventure locations marked with a red x.
- Floor plans: buildings, hideouts, villages, towns and dungeon complexes.

The newest tool, DnD MapBuilder v1.1, joins the two in one window. Pick a floor plan for each adventure location, or let the script pick them all.

## Which script do I use?

| Script | What it makes | Status |
|---|---|---|
| `DnD-MapBuilder_v1.1.py` | Area map, adventure locations and a floor plan for each location, in one window | Newest |
| `GitHib/DnD-MapBuilder-Interior_v2.1.1.py` | Floor plans: Building, Village, Hideout, Town, Dungeon complex | Current floor plan tool |
| `DnD-MapBuilder-Exterior_v2.0.py` | Area maps with adventure locations | Current area map tool |
| `GitHib/DnD-MapBuilder-Interior_v2.1.py` | Floor plans, before the 2.1.1 changes | Earlier |
| `GitHib/DnD-MapBuilder-Interior_v2.0.py` | Floor plans: Building, Hideout, Dungeon | Earlier |
| `GitHib/DnD-MapBuilder-Interior_v1.0.py` | Floor plans: bigger and more detailed, with hallways and more kinds of stairs | Earlier |
| `DnD-MapBuilder-Exterior_v1.0.py` | Area maps | Earlier |

Each script has a README next to it with the full walkthrough. The newest version of each tool is the one to start with.

## Requirements

- Python 3.8 or newer
- Pillow 10.1 or newer: `python3 -m pip install pillow`
- Tkinter, which comes with the standard Python installer
- macOS, Windows or Linux
- A printer and 8.5 x 11 paper, to play at the table

## Quick Start

Install Pillow once:

```bash
python3 -m pip install pillow
```

Start the newest tool:

```bash
python3 DnD-MapBuilder_v1.1.py
```

1. Click "Area map" until you like the land.
2. Click "Adventure locations" to add numbered locations.
3. Answer "Would you like to generate floor plans for the locations on your adventure?" with "Yes", "No" or "Make automatically".
4. At "Save?", click "Yes", type a name and press "OK". Everything is saved in its own folder inside `Maps`, next to the script.
5. Print the `_grid` JPG (blue grid) or the plain JPGs on 8.5 x 11 paper with "Fit to page" (or "Scale to fit") on.

To make only a floor plan, start the floor plan tool instead:

```bash
python3 GitHib/DnD-MapBuilder-Interior_v2.1.1.py
```

Click "Building", "Village", "Hideout", "Town" or "Dungeon complex", then "Yes" and a name to save.

## The tools

### DnD MapBuilder v1.1

The area map comes from DnD MapBuilder Exterior v2.0 and the floor plans from DnD MapBuilder Interior v2.1.1, both built in unchanged. A seed makes the same map in v1.1 as in those scripts.

Once the area map has its locations, the question "Would you like to generate floor plans for the locations on your adventure?" appears:

- "Yes" lets you pick a floor plan for each location by hand. Click a floor plan button, then "Use for this location" to move on. The last location suggests a "Dungeon complex" or a "Town" for the finale.
- "Make automatically" gives every location a floor plan at once. Every location but the last is a Building 6 times in 10, a Village 2 in 10, or a Hideout 2 in 10. The last is a Town or a Dungeon complex, one chance in two each.
- "No" saves the locations without floor plans.

Everything is saved in one folder with `<name>_locations.txt`, a list that ties each location to its square and its floor plan's kind and seed.

### DnD MapBuilder Exterior v2.0

Makes one outdoor area per map: wandering lines that cut the land into regions, with one patch of forest, one of sand and rock, and one of water. "Adventure locations" scatters 7 to 29 numbered locations marked with a red x. The map and the locations each have their own seed, so you can keep a map you like and roll new locations on it.

### DnD MapBuilder Interior v2.1.1

Makes floor plans, five kinds in all:

- Building: one floor, with an entrance and sometimes an exit.
- Village: 6 to 11 buildings, saved in one go with a list of every building and its seed.
- Hideout: 3 to 6 levels, up to 3 above ground and the rest below, with one stairwell through them all.
- Town: 12 to 29 buildings and a hideout.
- Dungeon complex: 15 to 99 rooms on an even grid, joined by corridors that never cross, with a room key.

Each floor, dungeon room and building prints on one sheet of its own.

## Walkthrough

### Seeds

Every map has a seed, a number that always makes the same map. Paste a seed into the seed box and click the same button to get that map again.

In v1.1 the line of text shows a code once locations are added: the map seed, a dash, and the locations seed, like `123456789012345-987654321098765`. Paste a code and click "Area map" or "Adventure locations" to bring back that land and those locations. Every floor plan has a seed of its own, shown in the locations list.

### Print and play

Every map fits one 8.5 x 11 sheet. Turn on "Fit to page" (or "Scale to fit") in the print window, or the edges get cut off.

Maps are saved with and without the grid. The `_grid` JPGs have the blue 70 pixel grid for playing on the table. The plain or `_walls` JPGs are for printing without it, or for an online virtual tabletop, where the grid should be set to 70 pixels per square.

### Saved files

Each save makes its own folder inside `Maps`, next to the script. A saved map is never overwritten: pick another name if the folder already exists.

| File | What it is |
|---|---|
| `<name>.jpg`, `<name>_grid.jpg` | The area map, without and with the blue grid |
| `<name>_locations.txt` | The code, the number of locations, and every location with its square and floor plan |
| `<name>_location_<nn>_...` | One location's floor plan: its building, hideout, village, town or dungeon rooms |
| `<name>_..._overview.jpg` | The overview of a village, town, hideout or dungeon complex |
| `<name>_..._buildings.txt`, `<name>_..._room_key.txt` | The list of buildings, or the room key, for a village, town or dungeon complex |

A town or dungeon complex saves every building, level or room, so a folder can hold hundreds of files. That is normal.

## Troubleshooting

| Issue | Solution |
|---|---|
| `ModuleNotFoundError: No module named 'PIL'` | Run `python3 -m pip install pillow` |
| `ModuleNotFoundError: No module named 'tkinter'` | Install Python from python.org, which includes Tkinter |
| The window does not appear | Run the script from the Terminal app, not from inside another program |
| "No map could be made from this seed." | Rare. Click "Area map" again for a new map |
| The printed map is cut off at the edges | Turn on "Fit to page" or "Scale to fit" in the print window |
| Cannot find the saved maps | Look in the `Maps` folder next to the script. The line of text in the window shows the full path after saving |
| "There is already a folder called ..." | Pick another name. A saved map is never overwritten |
| "Use a name without / \ : * ? ..." | Take those characters out of the name, and do not start it with a dot |

## Security Notes

- Offline: the scripts never use the network.
- Writes only to `Maps`: the only files they save are JPG pictures and text files, in the `Maps` folder next to the script.
- No personal data: the pictures and text files hold only the maps, their seeds and codes, and the locations.
- Standalone: each script is a single file with no installer. Deleting the script and its folder in `Maps` removes everything it saved.

## Older versions

Older versions stay in the repo with their READMEs, so you can run any of them. Each version's README says what changed. Old scripts that are no longer in use go to an archive folder rather than being deleted.

## About this repo

I can read a Python script but I only speak English and PowerShell. AI generates, edits and reviews the code. Each script is published with a README next to it.

The tools are for personal use at the table and have not been tested with any online platforms.

## License

Unlicense. See the `LICENSE` file.

