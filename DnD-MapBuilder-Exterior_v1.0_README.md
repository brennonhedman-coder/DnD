# DnD MapBuilder Exterior v1.0

Print and play outdoor area maps for tabletop RPGs like D&D: click a button, get a map, add adventure locations, print it, bring it to game night.

Version 1.0 makes one outdoor area per map: wandering lines that cut the area into regions, with one patch of forest, one of sand and rock, and one of water. A second button scatters numbered locations marked with a red x over the map. The map and the locations each have their own seed, so you can keep a map you like and roll new locations on it as often as you want.

## Requirements

- Python 3.8 or newer, Pillow 10.1 or newer (`python3 -m pip install pillow`) and Tkinter (comes with the standard Python installer)
- macOS, Windows or Linux
- A printer and 8.5 x 11 paper, to play at the table

## Quick Start

```bash
python3 DnD-MapBuilder-Exterior_v1.0.py
```

1. Click "Area map". Each click throws the old map away and shows a new one in the preview.
2. Click "Adventure locations" to put numbered locations marked with a red x on that map. Click it again for different locations on the same map.
3. Click "Yes", type a name and press "OK". The map is saved in its own folder inside `Maps`, next to the script. "No" clears the preview.
4. Print the `_grid` (blue grid) or plain JPG on 8.5 x 11 paper with "Fit to page" (or "Scale to fit") on.

A full-size window opens with the two buttons at the top, the seed box under them, a line of text about the map, and a black preview area below.

## Features Walkthrough

### Area map

1. Click "Area map". The map is 17 x 13 squares of 70 x 70 pixels, with a thick frame round it.
2. Thin lines wander across the map and cut it into regions. They meet only at their ends and never cross.
3. Three regions, picked at random, get a texture each: forest (small trees), sand and rock (dots and small triangles), and water (small waves). Every other region stays blank.
4. The squares are named round the edge: "A" to "Q" along the top and bottom, "1" to "13" down both sides.

### Adventure locations

1. Make a map first with "Area map".
2. Click "Adventure locations". 7 to 29 locations marked with a red x appear, each with a number.
3. They sit inside the map, at least 40 pixels apart, and never in the water.
4. Click "Adventure locations" again for a new set. The map under them never changes.
5. Location 1 and the last location are the two farthest apart. The others are numbered in order between them.

### Seeds and codes

1. The line of text under the seed box shows the seed of every map. Once locations are added it shows a code instead: the map seed, a dash, and the locations seed, like `123456789012345-987654321098765`.
2. Select the seed or code and copy it (Cmd+C on a Mac, Ctrl+C elsewhere).
3. Paste a seed into the seed box and click "Area map" to get that map back.
4. Paste a seed and click "Adventure locations" to put those locations on the map that is showing.
5. Paste a code and click either button to get that map back with those locations.

### How the lines are made

Each square holds 3 hidden points at random spots. A line walks from point to point, always to one of the 3 nearest points where the bend is wider than a right angle and that is closer to where the line is going. That keeps the lines short-stepped and wandering, never straight. Three or five of the points are joined into a triangle or pentagon in the middle, and three lines run out from it to three different edges of the map.

### Print and play

Every sheet is the whole map plus a 1 square margin for the square names, and a header row with the seed or code. Print it on one sheet of 8.5 x 11 paper with "Fit to page" on.

### Online use

The sheets use 70 x 70 pixel squares. Import the `_grid` or plain JPG and set the platform's grid to 70 pixels.

## Reference Tables

### The two buttons

| Button | What it does | Seed box |
|---|---|---|
| Area map | Makes a new map with no locations | Empty: a new map. A seed: that map. A code: that map with its locations |
| Adventure locations | Puts new locations marked with a red x on the map that is showing | Empty: new locations. A seed: those locations. A code: that map with its locations |

### Map contents

| Thing | How many |
|---|---|
| Shape in the middle | A triangle or a pentagon, 1 chance in 2 each |
| Lines to the edge | 3, to three different sides |
| Textured regions | 3: forest, sand and rock, water |
| Locations marked with a red x | 7 to 29, only after "Adventure locations" |

### Saved files

| File | What it is |
|---|---|
| `<name>.jpg` | The map, with locations if they were added |
| `<name>_grid.jpg` | The same map with a blue 70 x 70 pixel grid |
| `<name>_locations.txt` | The code, the number of locations, and every location with its square, like "Location 3    M9". Only saved when the map has locations |

### Ways to run it

| Command ending | What it does |
|---|---|
| (nothing) | Opens the window |
| `SEED` | Opens the window already showing the map with that seed |
| `SEED-SEED` (a code) | Opens the window showing that map with those locations |

### Map measurements

| Thing | Size |
|---|---|
| Grid square | 70 x 70 pixels |
| Area map | 17 x 13 squares (1190 x 910 pixels) |
| Whole sheet | 1330 x 1120 pixels, margin and header included |
| Map Border (keeps the shape and the locations off the edge) | 105 pixels in from the frame |
| Hidden points | 3 per square, 663 per map |
| Frame | 7 pixels |
| Lines and the blue grid | 1 pixel |

### Settings

In the SETTINGS section at the top of the script.

| Setting | Now | What it changes |
|---|---|---|
| `PER_SQUARE` | 3 | Hidden points in each square |
| `CHOICES` | 3 | How many of the nearest points a line picks between at random |
| `LINE_WIDTH`, `FRAME_WIDTH` | 1, 7 | Line and frame thickness in pixels |
| `GRID_COLOR`, `GRID_WIDTH` | (140, 190, 255), 1 | The blue grid on the `_grid` sheet |
| `TEXTURE_COLOR` | (90, 90, 90) | Colour of the forest, sand and water marks |
| `SMALLEST` | 400 | Smallest region that can get a texture, in 5 x 5 pixel cells |
| `X_COUNT` | (7, 29) | Fewest and most locations |
| `X_GAP` | 40 | Pixels kept between locations |
| `RED` | (220, 0, 0) | Colour of the red x marks and their numbers |
| `SHOW_NODES` | False | True draws the hidden points in blue |

## Features

- Two buttons: a map, then adventure locations on it, made as fast as you can click
- Every map fits one 8.5 x 11 sheet and is saved with and without the grid
- Wandering lines that never cross, with forest, sand and rock, and water
- Numbered locations with square names, and a text list of them for the Game Master
- Separate seeds for the map and the locations, joined into one code
- Thin, light marks that use little toner
- White save buttons, whether the Mac is in Light or Dark Mode

## Integration

```
Python/
├── DnD-MapBuilder-Exterior_v1.0.py           <-- this tool
├── DnD-MapBuilder-Exterior_v1.0_README.md    <-- this file
└── Maps/                                     <-- made on the first save
    └── meadow1/
        ├── meadow1.jpg
        ├── meadow1_grid.jpg
        └── meadow1_locations.txt
```

The script is a single file and stands on its own. It needs only Python, Tkinter and Pillow. It reads no other files, and the only thing it saves is the `Maps` folder next to itself.

## Common Use Cases

### Game Master: The party heads into the wilds

1. Click "Area map" until the shape suits the scene.
2. Click "Adventure locations" until the spread of locations feels right.
3. Save it, print the `_grid` sheet for the table, and keep the `_locations.txt` list behind your screen.

### Game Master: Same land, new adventure

1. Paste the old map's seed into the seed box and click "Area map".
2. Click "Adventure locations" for a fresh set of locations on the same land.
3. Save it under a new name. The new code is in the header and the text file.

### Game Master: Keeping a map for later

1. Copy the code from the line of text under the seed box into your notes.
2. If the pages are lost, paste the code into the seed box and click either button to get the same map and locations back.

### Online Game Master: Running the map on a virtual tabletop

1. Save the map as usual.
2. Import the `_grid` or plain JPG.
3. Set the platform's grid to 70 pixels per square.

## Troubleshooting

| Issue | Solution |
|---|---|
| `ModuleNotFoundError: No module named 'PIL'` | Run `python3 -m pip install pillow` |
| `ModuleNotFoundError: No module named 'tkinter'` | Install Python from python.org, which includes Tkinter |
| The window does not appear | Run the script from the Terminal app rather than from inside another program |
| "Make a map first with the "Area map" button." | Click "Area map" before "Adventure locations" |
| "No map could be made from this seed." | Rare (about 1 seed in 150). Click "Area map" again for a new map |
| "A seed is digits only ..." | Type digits only, or two seeds joined by a dash for a code, with no spaces or letters |
| The seed gives a different map than before | Use the same version of the script. A code needs both halves to bring back the same locations |
| Two seeds give the same map | A seed that cannot be finished is built from the next seed value instead, so it can match the next seed's map |
| "Use: [SEED or CODE]" | The script was started with something it does not know. Use only a seed or a code |
| "There is already a folder called ..." | Pick another name. A saved map is never overwritten |
| "Use a name without / \\ : * ? ..." | Take those characters out of the name, and do not start it with a dot |
| The printed map is cut off at the edges | Switch on "Fit to page" or "Scale to fit" in the print window |
| Cannot find the saved maps | Look in the `Maps` folder next to the script. The line of text in the window shows the full path after saving |

## Security Notes

- Offline: The script never uses the network.
- Writes Only To Maps: The only files it saves are JPG pictures and the locations text file, in the `Maps` folder next to the script.
- Never Overwrites: Saving stops if a folder with that name already exists.
- Safe Names: Map names with path characters, or starting with a dot, are refused, so a save cannot land outside `Maps`.
- No Personal Data: The pictures and text file hold only the map, the seed or code, and the locations.
- Standalone: One file with no installer. Deleting the script and the `Maps` folder removes everything it saved.
