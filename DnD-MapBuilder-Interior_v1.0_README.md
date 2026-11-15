# DnD MapBuilder Interior v1.0

Print and play floor plans for tabletop RPGs like D&D: click a button, get a map, print it, bring it to game night.

Version 1.0 is designed around a "print and play" concept. Every map prints on 8.5 x 11 paper with a normal printer and can be used as is, so you have instant usable floor plans for your game. The buttons are designed to be satisfying to click: they generate maps as fast as you can click. If you like it, save it, print it.

Version 1.0 also has the "Dungeon complex": one big underground complex of 15 to 99 rooms, where every room prints on its own sheet and a room key tells you how to lay the sheets out at the table.

## Requirements

- Python 3.8 or newer
- Pillow 10.1 or newer (`python3 -m pip install pillow`)
- Tkinter, which comes with the standard Python installer
- macOS, Windows or Linux
- A normal printer and 8.5 x 11 paper, if you want the maps on the table

## Quick Start

1. Open Terminal and go to the folder that holds the script.
2. Run the script:

```bash
python3 DnD-MapBuilder-Interior_v1.0.py
```

3. Click "Single building", "Bandit hideout", "Small dungeon" or "Dungeon complex".
4. Keep clicking until you see a map you like, then click "Yes" to save it.
5. Print the saved JPGs.

A full-size window opens with the four buttons centered at the top, the seed box under them, and a black preview area that shows each map as it is made.

## Features Walkthrough

### Make a map

1. Click one of the four buttons. The map appears in the preview straight away.
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
4. Bring the pages to the table. Each level, or each room of a dungeon complex, is its own page, with a small header saying what kind of map it is, which level or room, and the seed.

The size cap on every level and every room is there for this step. Nothing printed on its own is bigger than 17 x 13 squares, so every page fits on a single sheet and can go straight from the printer to game night. The largest pages print with squares a little over half an inch; smaller ones print bigger.

### Make a dungeon complex

1. Click "Dungeon complex". The preview shows the whole complex from above, with every room numbered and the entrance marked "IN" (and the exit, if it has one, marked "OUT").
2. Click "Open full size" to see the overview in your picture viewer, where you can zoom in.
3. Save it with "Yes" as usual.

A dungeon complex is built like this:

1. It has 15 to 99 rooms. Smaller complexes are much more likely: about 6 in 10 have fewer than 30 rooms, and only about 1 in 50 has 90 or more.
2. Each room is a rectangle from 7 x 5 squares up to 17 x 13. Rooms are packed into clusters with bare rock between them, and joined by corridors 1 square wide.
3. Each room is built inside like a floor of the other maps: cut into 2 to 11 inner rooms. About half of the rooms, and most of the big ones, also get hallways. When a doorway lines up with a hallway, the corridor leads straight into it.
4. No room has more than 2 doorways to the corridors. Corridors branch and meet outside the rooms, so every room can still be reached. Some rooms are dead ends and some corridors make loops.
5. One entrance corridor runs straight out to the edge of the complex. 6 complexes in 7 also have an exit on a different side.
6. The 1 complex in 7 with no exit has a shortcut instead: a corridor from the deepest room back to a room 2 to 6 corridors from the entrance. "Deepest" and "corridors from the entrance" count the corridors as they were made, room to room. The shortcut mostly makes its own way across the complex, and it is quicker to walk than the normal way back in all but about 1 in 170 complexes that have one.
7. A dungeon complex has no stairwells.

### Lay out a dungeon complex at the table

1. Print the room sheets you need. Each sheet shows one room and its inside, with each doorway as a small bump out in the margin where the corridor starts. The header says "Room n of N" and the seed.
2. Open `<name>_room_key.txt`. After a short how-to, it lists the entrance, then the exit or the shortcut.
3. For each room, the key says which rooms it is reached from (nearer the entrance), which it leads on to, and which it loops round to.
4. Each doorway is listed by its wall and square, for example "west wall, 2nd square from the north end", whether it opens into a hallway or an inner room, and how many squares of corridor lead to which room.
5. Start at the entrance room and add sheets as the party explores.
6. Keep the overview beside the key. The key lists each corridor as it was made, from one room to another, but corridors branch and meet outside the rooms. About half of all doorways lead to a corridor that also reaches rooms the key does not name for that doorway. The overview shows every corridor and every junction, so check it whenever the party comes to a fork.

### Get a map back with its seed

1. Every map has a seed, a string of digits shown in the line of text under the seed box.
2. Double-click the seed number to select it, then copy it (Cmd+C on a Mac, Ctrl+C elsewhere).
3. Later, paste it into the "Seed" box and click the same button. You get exactly the same map.

A seed gives a different map for each button, so note which button you used. The header on every saved picture records both. Every room sheet of a dungeon complex carries the seed of the whole complex.

### Use a map online

1. The grid on every level and room sheet is 70 x 70 pixels per square. The dungeon complex overview uses 20 x 20 pixels per square.
2. Import a `_grid` or `_walls` JPG into your online platform and set its grid size to 70 pixels.
3. The walls sit on the grid lines, so the platform's grid lines up with the map's.

Online use works, but the primary focus of this version is print and play.

### Run without the window

1. Save a map straight from Terminal:

```bash
python3 DnD-MapBuilder-Interior_v1.0.py --save cave1 123456789012345 complex
```

2. Leave the seed off for a random map. The last word picks the kind: "building", "hideout", "dungeon" (the small dungeon) or "complex". Leave it off for a hideout.
3. Check the generator by making many maps of every kind and testing each against the rules:

```bash
python3 DnD-MapBuilder-Interior_v1.0.py --test 500
```

## Reference Tables

### The four buttons

| Button | Levels | Biggest page | Files saved |
|---|---|---|---|
| Single building | 1 floor, no stairs | 17 x 13 squares about 1 time in 9, usually smaller | 2 JPGs |
| Bandit hideout | 3 or 4, above and below ground | 17 x 13 squares | 7 or 9 JPGs |
| Small dungeon | 4, 5 or 6, all below ground after level 1 | 17 x 13 squares | 9, 11 or 13 JPGs |
| Dungeon complex | 1 level of 15 to 99 rooms, no stairs | 17 x 13 squares per room | 2 JPGs per room, 2 overviews and the room key |

### Dungeon complex odds

| Rooms | How often |
|---|---|
| 15 to 29 | about 6 in 10 |
| 30 to 59 | about 3 in 10 |
| 60 to 89 | about 1 in 10 |
| 90 to 99 | about 1 in 50 |

| Way out | How often |
|---|---|
| Entrance and exit | 6 in 7 |
| Entrance and a shortcut, no exit | 1 in 7 |

### Saved files

| File | What it is |
|---|---|
| `<name>_walls.jpg` | Single building, walls only |
| `<name>_grid.jpg` | Single building, walls with the grid |
| `<name>_level_<n>_walls.jpg` | One level of a hideout or small dungeon, walls only |
| `<name>_level_<n>_grid.jpg` | One level of a hideout or small dungeon, walls with the grid |
| `<name>_overview.jpg` | Hideout or small dungeon: every level on one sheet. Dungeon complex: the whole complex, grid on the bare rock only |
| `<name>_overview_grid.jpg` | Dungeon complex: the whole complex, grid on the floors only |
| `<name>_room_<n>_walls.jpg` | One room of a dungeon complex and its inside, walls only |
| `<name>_room_<n>_grid.jpg` | One room of a dungeon complex and its inside, with the grid |
| `<name>_room_key.txt` | Dungeon complex: how the rooms join up, for laying out the sheets |

### Ways to run it

| Command ending | What it does |
|---|---|
| (nothing) | Opens the window |
| `123456789012345` | Opens the window already showing the hideout with that seed |
| `123456789012345 complex` | The same, for a dungeon complex (`building` or `dungeon` for the others) |
| `--save NAME [SEED] [kind]` | No window. Saves one map in `Maps/NAME` |
| `--test N` | No window. Makes N maps of each kind and checks them |

### Map measurements

| Thing | Size |
|---|---|
| Grid square | 70 x 70 pixels (20 x 20 on the dungeon complex overview) |
| Ground level | 17 x 13 squares |
| Smallest level | 4 x 4 squares |
| Dungeon complex rooms | 7 x 5 to 17 x 13 squares |
| Smallest room or inner room | 3 x 3 squares |
| Hallways, corridors and doorways | 1 square wide |
| Outer walls and main stairwell walls | 7 pixels |
| Inner walls | 3 pixels |
| Main stairwell | 2 x 2 squares |
| White margin on saved level and room pictures | 1 square all round |

### Dungeon complex settings

These are in the SETTINGS section at the top of the script.

| Setting | Now | What it changes |
|---|---|---|
| `COMPLEX_ROOM_COUNT` | (15, 99) | Fewest and most rooms |
| `COMPLEX_ROOM_FALLOFF` | 2 | How fast bigger complexes get rarer: 1 = more big ones, 3 = fewer, 0 = every count equally likely |
| `COMPLEX_ROOM_WIDTH`, `COMPLEX_ROOM_HEIGHT` | (7, 17), (5, 13) | Smallest and largest room |
| `COMPLEX_EXIT_CHANCE` | (6, 7) | Chance of an exit. The rest get a shortcut |
| `SHORTCUT_TO_STEPS` | (2, 6) | How many corridors from the entrance the shortcut may end |
| `COMPLEX_EXTRA_LINK_CHANCE` | (1, 4) | Chance of a loop between two near rooms |
| `COMPLEX_INNER_ROOMS_LEAST` | 2 | Fewest inner rooms in each room |

## Features

- Four kinds of map from four buttons: single building, bandit hideout, small dungeon, dungeon complex
- Maps are made as fast as you can click, with nothing to set up first
- Every level, and every room of a dungeon complex, fits on one sheet of 8.5 x 11 paper
- Each level and room is saved twice, with the grid and without it
- Hideouts and small dungeons also save an overview sheet with every level lined up over the ground level
- Stairwells line up from floor to floor, so the levels really stack
- Dungeon complexes save an overview of the whole complex and a room key for laying the sheets out
- Every room of a dungeon complex has its own inner rooms and doorways, and about half have hallways
- Every map has an entrance. Most dungeon complexes have an exit, and the rest have a shortcut back towards the entrance
- The same seed always makes the same map, on any computer
- The seed number can be selected and copied straight from the window
- 70 pixel grid for importing into online platforms
- Every number you may want to change is in the SETTINGS section at the top of the script
- Test mode checks every kind of map against the rules

## Integration

```
Python/
├── DnD-MapBuilder-Interior_v1.0.py           <-- this tool
├── DnD-MapBuilder-Interior_v1.0_README.md    <-- this file
└── Maps/                                     <-- made on the first save
    ├── cave1/                                <-- a hideout or small dungeon
    │   ├── cave1_level_1_walls.jpg
    │   ├── cave1_level_1_grid.jpg
    │   ├── cave1_level_-2_walls.jpg
    │   ├── ...
    │   └── cave1_overview.jpg
    └── deep1/                                <-- a dungeon complex
        ├── deep1_overview.jpg
        ├── deep1_overview_grid.jpg
        ├── deep1_room_01_walls.jpg
        ├── deep1_room_01_grid.jpg
        ├── ...
        └── deep1_room_key.txt
```

The script is a single file and stands on its own. It needs only Python, Tkinter and Pillow. It reads no other files, and the only thing it saves is the `Maps` folder next to itself ("Open full size" also uses a temporary file, see Security Notes).

## Common Use Cases

### Game Master: The party walks into a building you did not plan

1. Open the window and click "Single building" until one fits the scene.
2. Click "Yes" and name it.
3. Print the `_grid` picture and put it on the table.

### Game Master: Preparing a hideout for next session

1. Click "Bandit hideout" until you like the layout.
2. Save it, then print one `_grid` page per level for the table.
3. Print the `_overview` page for yourself, to see how the levels stack.

### Game Master: A dungeon crawl over several sessions

1. Click "Small dungeon" and save one you like.
2. Print the levels as the party reaches them.
3. Copy the seed into your notes. If the pages are lost, the seed brings the same dungeon back.

### Game Master: A sprawling underground complex

1. Click "Dungeon complex" until the size and shape suit the adventure. Most are under 30 rooms.
2. Save it, then print the entrance room's sheet and the rooms near it.
3. Keep the room key and the overview behind your screen. As the party goes through a doorway, find that doorway in the key and put down the next room's sheet. At a fork in a corridor, check the overview: it shows junctions the key does not list.
4. If the key says "No exit", note where the shortcut runs. It is a quick way back for a party deep inside.

### Online Game Master: Running the same map on a virtual tabletop

1. Save the map as usual.
2. Import the `_walls` or `_grid` JPG for each level or room.
3. Set the platform's grid to 70 pixels per square.

## Troubleshooting

| Issue | Solution |
|---|---|
| `ModuleNotFoundError: No module named 'PIL'` | Run `python3 -m pip install pillow` |
| `ModuleNotFoundError: No module named 'tkinter'` | Install Python from python.org, which includes Tkinter |
| The window does not appear | Run the script from the Terminal app rather than from inside another program |
| The printed map is cut off at the edges | Switch on "Fit to page" or "Scale to fit" in the print window |
| The printed squares are too small | Print in landscape, and use the single-level or room files rather than an overview |
| The dungeon complex preview is too small to read | Click "Open full size" and zoom in, or open `<name>_overview.jpg` |
| A corridor leads to a room the key did not mention | Corridors branch and meet outside the rooms. The key lists each corridor as it was made; the overview shows every junction |
| "A seed is digits only" | Type digits only in the seed box, with no spaces or letters |
| The seed gives a different map than before | Click the same button as before. Each button makes its own map from a seed. A seed from an older version may also give a different dungeon complex |
| `--save` made a hideout instead of a dungeon complex | Add the word `complex` at the end of the command |
| "There is already a folder called ..." | Pick another name. A saved map is never overwritten |
| "Use a name without / \\ : * ? ..." | Take those characters out of the name, and do not start it with a dot |
| Cannot find the saved maps | Look in the `Maps` folder next to the script. The line of text in the window shows the full path |

## Security Notes

- Offline: The script never uses the network.
- Writes Only To Maps: The only files it saves are JPG pictures and the dungeon complex room key text file, in the `Maps` folder next to the script.
- Open Full Size: "Open full size" hands a temporary copy of the overview to your picture viewer, saved in the system's temporary folder. On a Mac it is deleted about 20 seconds later; on Windows and Linux the system clears it with its other temporary files.
- Never Overwrites: Saving stops if a folder with that name already exists.
- Safe Names: Map names with path characters, or starting with a dot, are refused, so a save cannot land outside `Maps`.
- No Personal Data: The pictures and room key hold only the map, its kind, level or room, and seed.
- Standalone: One file with no installer. Deleting the script and the `Maps` folder removes everything it saved.
