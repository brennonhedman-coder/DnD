# DnD Building Floor Plans v2.0.3

Print and play floor plans for tabletop RPGs, maybe a One-shot: click a button, get a map, print it, bring it to game night.

Version 2.0 is designed around a "print and play" concept. Every map prints on 8.5 x 11 paper with a normal printer and can be used as is, so you have instant usable floor plans for your game. The buttons are designed to be satisfying to click: they generate maps as fast as you can click. If you like it, save it, print it.

## Requirements

- Python 3.8 or newer
- Pillow 10.1 or newer (`python3 -m pip install pillow`)
- Tkinter, which comes with the standard Python installer
- macOS, Windows or Linux
- Not actually a requirement, technically -- A common, home use printer and 8.5 x 11 paper, if you want to test the intent

## Quick Start

1. Open Terminal and go to the folder that holds the script.
2. Run the script:

```bash
python3 DnD-BuildingFloorPlans-v2.0.3.py
```

3. Click "Single building", "Bandit hideout" or "Dungeon".
4. Keep clicking until you see a map you like, then click "Yes" to save it.
5. Print the saved JPGs.

A full-size window opens with the three buttons centered at the top, the seed box under them, and a black preview area that shows each map as it is made.

## Features Walkthrough

### Make a map

1. Click one of the three buttons. The map appears in the preview straight away.
2. Read the line of text under the seed box. It says what kind of map was made, its seed, and its levels or size.
3. Don't like it? Click any button again. Each click throws the old map away and makes a new one.

### Save a map

1. When a map is showing, the question "Do you want to save the generated map?" appears under the line of text.
2. Click "Yes".
3. Type a name for the map and press "OK".
4. The map is saved in its own folder inside `Maps`, next to the script. The line of text shows where.

Click "No" to clear the preview without saving.

### Print and play

1. Open the map's folder inside `Maps`.
2. Pick the pictures you want: `_grid` files have the blue grid, `_walls` files are walls only.
3. Print each one on 8.5 x 11 paper with "Fit to page" (or "Scale to fit") switched on. Landscape suits most levels.
4. Bring the pages to the table. Each level is its own page, with a small header saying what kind of map it is, which level, and the seed.

The size cap on every level is there for this step. No level is bigger than 17 x 13 squares, so every level fits on a single sheet and can go straight from the printer to game night. The largest level prints with squares a little over half an inch; smaller levels print bigger.

### Get a map back with its seed

1. Every map has a seed, a string of digits shown in the line of text under the seed box.
2. Double-click the seed number to select it, then copy it (Cmd+C on a Mac, Ctrl+C elsewhere).
3. Later, paste it into the "Seed" box and click the same button. You get exactly the same map.

A seed gives a different map for each button, so note which button you used. The header on every saved picture records both.

### Use a map online

1. The grid is always 70 x 70 pixels per square.
2. Import a `_grid` or `_walls` JPG into your online platform and set its grid size to 70 pixels.
3. The walls sit on the grid lines, so the platform's grid lines up with the map's.

Online use works, but the primary focus of this version is print and play.

### Run without the window

1. Save a map straight from Terminal:

```bash
python3 DnD-BuildingFloorPlans-v2.0.3.py --save cave1 123456789012345 dungeon
```

2. Leave the seed off for a random map. Leave the last word off for a hideout.
3. Check the generator by making many maps of every kind and testing each against the rules:

```bash
python3 DnD-BuildingFloorPlans-v2.0.3.py --test 500
```

## Reference Tables

### The three buttons

| Button | Levels | Biggest level | JPGs saved |
|---|---|---|---|
| Single building | 1 floor, no stairs | 17 x 13 squares (1 time in 10), smaller the rest | 2 |
| Bandit hideout | 3 or 4, above and below ground | 17 x 13 squares | 7 or 9 |
| Dungeon | 4, 5 or 6, all below ground after level 1 | 17 x 13 squares | 9, 11 or 13 |

### Saved files

| File | What it is |
|---|---|
| `<name>_walls.jpg` | Single building, walls only |
| `<name>_grid.jpg` | Single building, walls with the grid |
| `<name>_level_<n>_walls.jpg` | One level of a hideout or dungeon, walls only |
| `<name>_level_<n>_grid.jpg` | One level of a hideout or dungeon, walls with the grid |
| `<name>_overview.jpg` | Every level of a hideout or dungeon on one sheet |

### Ways to run it

| Command ending | What it does |
|---|---|
| (nothing) | Opens the window |
| `123456789012345` | Opens the window already showing the hideout with that seed |
| `123456789012345 dungeon` | The same, for a dungeon (`building` for a single building) |
| `--save NAME [SEED] [kind]` | No window. Saves one map in `Maps/NAME` |
| `--test N` | No window. Makes N maps of each kind and checks them |

### Map measurements

| Thing | Size |
|---|---|
| Grid square | 70 x 70 pixels |
| Ground level | 17 x 13 squares |
| Smallest level | 4 x 4 squares |
| Smallest room | 3 x 3 squares |
| Hallways and doorways | 1 square wide |
| Outer walls and main stairwell walls | 7 pixels |
| Inner walls | 3 pixels |
| Main stairwell | 2 x 2 squares |
| White margin on saved level pictures | 1 square all round |

## Features

- Three kinds of map from three buttons: single building, bandit hideout, dungeon
- Maps are made as fast as you can click, with nothing to set up first
- Every level fits on one sheet of 8.5 x 11 paper
- Each level is saved twice, with the grid and without it
- Hideouts and dungeons also save an overview sheet with every level lined up over the ground level
- Stairwells line up from floor to floor, so the levels really stack
- Every map has an entrance, and half of them have a second exit
- The same seed always makes the same map, on any computer
- The seed number can be selected and copied straight from the window
- 70 pixel grid for importing into online platforms
- Every number you may want to change is in the SETTINGS section at the top of the script
- Test mode checks every kind of map against the rules

## Integration

```
Python/
├── DnD-BuildingFloorPlans-v2.0.3.py          <-- this tool
├── DnD-BuildingFloorPlans-v2.0.3_README.md   <-- this file
└── Maps/                                     <-- made on the first save
    └── cave1/                                <-- one folder per saved map
        ├── cave1_level_1_walls.jpg
        ├── cave1_level_1_grid.jpg
        ├── cave1_level_-2_walls.jpg
        ├── cave1_level_-2_grid.jpg
        ├── ...
        └── cave1_overview.jpg
```

The script is a single file and stands on its own. It needs only Python, Tkinter and Pillow. It reads no other files, and the only thing it writes is the `Maps` folder next to itself.

## Common Use Cases

### Game Master: I need to make a One-shot, fast!

1. Open the window and click "Single building" until one fits the scene.
2. Click "Yes" and name it. Go back to step one, if needed.
3. Print the `_grid` picture and put it on the table.

### Game Master: Preparing a hideout for next session

1. Click "Bandit hideout" until you like the layout.
2. Save it, then print one `_grid` page per level for the table.
3. Print the `_overview` page for yourself, to see how the levels stack.

### Game Master: A dungeon crawl over several sessions

1. Plan six weekends of dungeon crawling.
2. Click "Dungeon" and save six that you like. Print a set.
3. Play your session and end by finding a tunnel leading to the next set of maps.

### Online Game Master: Running the same map on a virtual tabletop

1. Save the map as usual.
2. Import the `_walls` or `_grid` JPG for each level.
3. Set the platform's grid to the desired pixels per square as needed.

## Troubleshooting

| Issue | Solution |
|---|---|
| `ModuleNotFoundError: No module named 'PIL'` | Run `python3 -m pip install pillow` |
| `ModuleNotFoundError: No module named 'tkinter'` | Install Python from python.org, which includes Tkinter |
| The window does not appear | Run the script from the Terminal app rather than from inside another program |
| The printed map is cut off at the edges | Switch on "Fit to page" or "Scale to fit" in the print window |
| The printed squares are too small | Print in landscape, and use the single-level files rather than the overview |
| "A seed is digits only" | Type digits only in the seed box, with no spaces or letters |
| The seed gives a different map than before | Click the same button as before. Each button makes its own map from a seed |
| "There is already a folder called ..." | Pick another name. A saved map is never overwritten |
| "Use a name without / \\ : * ? ..." | Take those characters out of the name, and do not start it with a dot |
| Cannot find the saved maps | Look in the `Maps` folder next to the script. The line of text in the window shows the full path |

## Security Notes

- Offline: The script never uses the network.
- Writes Only To Maps: The only files it creates are JPG pictures in the `Maps` folder next to the script.
- Never Overwrites: Saving stops if a folder with that name already exists.
- Safe Names: Map names with path characters, or starting with a dot, are refused, so a save cannot land outside `Maps`.
- No Personal Data: The pictures hold only the map, its kind, level and seed.
- Standalone: One file with no installer. Deleting the script and the `Maps` folder removes everything.
