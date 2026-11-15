# DnD MapBuilder Interior v2.0

Print and play floor plans for tabletop RPGs like D&D: click a button, get a map, print it, bring it to game night.

Version 2.0 is designed around a "print and play" concept. Every floor and every dungeon room prints on one sheet of 8.5 x 11 paper with a normal printer and can be used as is. The buttons are designed to be satisfying to click: they make maps as fast as you can click. If you like it, save it, print it.

Version 2.0 has three buttons: "Building", "Hideout" and "Dungeon". The "Dungeon" lays its rooms out on an even grid joined by short, simple corridors, and comes with a room key for laying the printed sheets out at the table.

## Requirements

- Python 3.8 or newer, Pillow 10.1 or newer (`python3 -m pip install pillow`) and Tkinter (comes with the standard Python installer)
- macOS, Windows or Linux
- A printer and 8.5 x 11 paper, to play at the table

## Quick Start

```bash
python3 DnD-MapBuilder-Interior_v2.0.py
```

1. Click "Building", "Hideout" or "Dungeon". Each click throws the old map away and shows a new one in the preview.
2. Click "Yes", type a name and press "OK". The map is saved in its own folder inside `Maps`, next to the script. "No" clears the preview.
3. Print the `_grid` (blue grid) or `_walls` (walls only) JPGs on 8.5 x 11 paper with "Fit to page" (or "Scale to fit") on.

A full-size window opens with the three buttons at the top, the seed box under them, a line of text about the map, and a black preview area below.

## Features Walkthrough

### Print and play

Every sheet is one floor or one dungeon room of at most 17 x 13 squares, plus a 1 square margin and a header row with the map kind, level or room, and seed. Entrances, exits and corridor doorways show as a small bump out into the margin.

### Building

- One floor, no stairs. 1 time in 10 it is a full 17 x 13 floor of 6 to 11 rooms; otherwise it is any size from 4 x 4 up, with about 1 room per 20 squares.
- An entrance on the south, west or east wall, never at a corner. Half of them also have an exit on a different wall.

### Hideout

- 3, 4, 5 or 6 levels, equal odds. Ground is level 1, always 17 x 13, with the entrance and, half the time, an exit.
- Each level after ground goes up or down on a coin flip, with at most 3 above ground (2, 3, 4). The rest go below, down to -6.
- Every level fits inside the one nearer ground. One 2 x 2 stairwell sits in the same spot on every level, drawn with staggered dashed tread lines.
- The overview sheet shows every level in 2 rows, each where it sits over the ground level: 2 across for 3 or 4 levels, 3 across for 5 or 6.

### Dungeon

- 15 to 99 rooms, smaller ones much more likely (see the odds table).
- Rooms sit on an even grid, numbered left to right and top to bottom. Each is 7 x 5 to 17 x 13 squares with bare rock all round it.
- Rooms next to each other are joined by corridors 1 square wide. Every room can be reached, some corridors make loops, and every corridor joins exactly two rooms and never crosses another.
- The entrance ("IN") comes in from the west edge into room 1. The exit ("OUT") leaves the last room to the east edge.
- Every room is cut into 2 to 11 inner rooms joined by doorways.
- The preview is white, with the blue grid inside rooms and corridors only. "Open full size" opens it in your picture viewer to zoom in.

### Lay out a dungeon at the table

1. Each room sheet shows one room and its inside, with "Room n of N" and the seed in the header.
2. Open `<name>_room_key.txt`. For each room it lists every doorway by wall and square (counted from the north or west end), the corridor length, and the room it leads to.
3. Start with room 1 and add sheets as the party explores. Keep the overview beside the key.

### Seeds

The line of text under the seed box shows the seed of every map, and can be selected and copied (Cmd+C on a Mac, Ctrl+C elsewhere). Paste it into the seed box and click the same button to get exactly the same map. Each button makes a different map from the same seed.

### Online use

Floor and room sheets use 70 x 70 pixel squares, with walls on the grid lines. Import a `_grid` or `_walls` JPG and set the platform's grid to 70 pixels. Print and play stays the main focus.

## Reference Tables

### The three buttons

| Button | Levels | Biggest page | Files saved |
|---|---|---|---|
| Building | 1 floor, no stairs | 17 x 13 squares about 1 time in 10, usually smaller | 2 JPGs |
| Hideout | 3 to 6, up to 3 above ground, the rest below | 17 x 13 squares | 7, 9, 11 or 13 JPGs |
| Dungeon | 1 level of 15 to 99 rooms, no stairs | 17 x 13 squares per room | 2 JPGs per room, the overview and the room key |

### Dungeon odds

| Rooms | How often |
|---|---|
| 15 to 29 | about 6 in 10 |
| 30 to 59 | about 3 in 10 |
| 60 to 99 | about 1 in 10 |

### Saved files

| File | What it is |
|---|---|
| `<name>_walls.jpg`, `<name>_grid.jpg` | Building |
| `<name>_level_<n>_walls.jpg`, `<name>_level_<n>_grid.jpg` | One level of a hideout |
| `<name>_overview.jpg` | Hideout: every level on one sheet. Dungeon: the whole dungeon |
| `<name>_room_<n>_walls.jpg`, `<name>_room_<n>_grid.jpg` | One room of a dungeon and its inside |
| `<name>_room_key.txt` | Dungeon: every doorway, its corridor and where it leads |

### Ways to run it

| Command ending | What it does |
|---|---|
| (nothing) | Opens the window |
| `SEED` | Opens the window already showing the hideout with that seed |
| `SEED building` or `SEED dungeon` | The same, for the other kinds |

### Map measurements

| Thing | Size |
|---|---|
| Grid square | 70 x 70 pixels (20 x 20 on the dungeon overview) |
| Floors | 4 x 4 to 17 x 13 squares (hideout ground level 17 x 13) |
| Dungeon rooms | 7 x 5 to 17 x 13 squares |
| Dungeon grid slot | 21 x 17 squares |
| Smallest room or inner room | 3 x 3 squares |
| Corridors and doorways | 1 square wide |
| Stairwell | 2 x 2 squares |
| Walls | 7 pixels outer, 3 pixels inner |
| Margin on sheets | 1 square all round, plus a 1 square header row |

### Settings

In the SETTINGS section at the top of the script.

| Setting | Now | What it changes |
|---|---|---|
| `SQ` | 70 | Pixels per square on the sheets |
| `GW`, `GH` | 17, 13 | Ground floor and largest floor or room, in squares |
| `OUTER`, `INNER` | 7, 3 | Wall thickness in pixels |
| `TREAD` | 14 | Pixels between stair tread lines |
| `BLUE` | (140, 190, 255) | Grid colour |

## Features

- Three kinds of map from three buttons, made as fast as you can click, with nothing to set up
- Every floor and room fits one 8.5 x 11 sheet and is saved with and without the grid
- Hideout levels line up over the ground level, with one stairwell through them all
- Dungeons on an even grid with short corridors that never cross, and a room key
- The same seed always makes the same map, on any computer
- White save buttons, whether the Mac is in Light or Dark Mode

## Integration

```
Python/
├── DnD-MapBuilder-Interior_v2.0.py           <-- this tool
├── DnD-MapBuilder-Interior_v2.0_README.md    <-- this file
└── Maps/                                     <-- made on the first save
    ├── cave1/                                <-- a hideout
    │   ├── cave1_level_1_walls.jpg
    │   ├── cave1_level_1_grid.jpg
    │   ├── cave1_level_-2_walls.jpg
    │   ├── ...
    │   └── cave1_overview.jpg
    └── deep1/                                <-- a dungeon
        ├── deep1_overview.jpg
        ├── deep1_room_01_walls.jpg
        ├── deep1_room_01_grid.jpg
        ├── ...
        └── deep1_room_key.txt
```

The script is a single file and stands on its own. It needs only Python, Tkinter and Pillow. It reads no other files, and the only thing it saves is the `Maps` folder next to itself ("Open full size" also uses a temporary file, see Security Notes).

## Common Use Cases

### Game Master: The party walks into a building you did not plan

1. Open the window and click "Building" until one fits the scene.
2. Click "Yes" and name it.
3. Print the `_grid` picture and put it on the table.

### Game Master: Preparing a hideout for next session

1. Click "Hideout" until you like the layout.
2. Save it, then print one `_grid` page per level for the table.
3. Print the `_overview` page for yourself, to see how the levels stack.
4. Copy the seed into your notes. If the pages are lost, the seed brings the same hideout back.

### Game Master: A dungeon crawl

1. Click "Dungeon" until the size and shape suit the adventure. Most are under 30 rooms.
2. Save it, then print room 1's sheet and the rooms near it.
3. Keep the room key and the overview behind your screen. As the party goes through a doorway, find it in the key and put down the next room's sheet.

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
| The dungeon preview is too small to read | Click "Open full size" and zoom in, or open `<name>_overview.jpg` |
| "A seed is digits only" | Type digits only in the seed box, with no spaces or letters |
| The seed gives a different map than before | Click the same button as before. Seeds from v1.2 or older give different maps in v2.0 |
| "Use: [SEED] [building, hideout or dungeon]" | The script was started with a word it does not know. Use only a seed and one of those three words |
| "There is already a folder called ..." | Pick another name. A saved map is never overwritten |
| "Use a name without / \\ : * ? ..." | Take those characters out of the name, and do not start it with a dot |
| Cannot find the saved maps | Look in the `Maps` folder next to the script. The line of text in the window shows the full path after saving |

## Security Notes

- Offline: The script never uses the network.
- Writes Only To Maps: The only files it saves are JPG pictures and the dungeon room key text file, in the `Maps` folder next to the script.
- Open Full Size: "Open full size" hands a temporary copy of the dungeon overview to your picture viewer, saved in the system's temporary folder.
- Never Overwrites: Saving stops if a folder with that name already exists.
- Safe Names: Map names with path characters, or starting with a dot, are refused, so a save cannot land outside `Maps`.
- No Personal Data: The pictures and room key hold only the map, its kind, level or room, and seed.
- Standalone: One file with no installer. Deleting the script and the `Maps` folder removes everything it saved.
