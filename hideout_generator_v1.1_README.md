# Hideout Generator v1.1

Tkinter window that makes random bandit hideout floor plans (walls only) and saves them as JPG pictures.

## Requirements

- macOS, Windows or Linux
- Python 3.7+
- Pillow (the add-on that writes JPG files): `python3 -m pip install pillow`
- Tkinter (comes with the standard Python installer from python.org)

## Quick Start

1. Open Terminal and go to the folder that holds the script, for example:

```bash
cd ~/Downloads/hideout-generator
```

2. Run the script:

```bash
python3 hideout_generator_v1.1.py
```

The window opens filling the screen, with the three map buttons in a bar at the top.

## Modes / Features Walkthrough

### Making a Map

1. Click **Click for small map**, **Click for medium map** or **Click for large map**
2. The map appears below the buttons: one grid picture per level, side by side
3. The line under the buttons shows the map size, the map number and where the ground level is
4. Click the same button again to make a new map of that size

### Saving a Map

1. After a map appears, the **Do you want to save the generated map?** question shows
2. Click **Yes**, type a name and pick a folder
3. If files with that name already exist, the tool asks before replacing them
4. Click **No** to clear the map without saving

### Reopening a Map by Number

1. Note the size and map number shown under the buttons (also printed in each picture's header)
2. Run the script with the size word and the number:

```bash
python3 hideout_generator_v1.1.py large 123456789012345
```

3. The same size and number always remake the same map. Without a size word the medium map is shown

### Test Mode

1. Run with `--test` and a count, with or without a size word:

```bash
python3 hideout_generator_v1.1.py --test 200
```

2. No window opens. The tool makes that many maps of each size and checks each one against every rule
3. A report is printed per size: failures, floors, large floors, ground level place and deep room depth

### Batch Mode

1. Run with `--batch`, a count, a folder name and an optional size word:

```bash
python3 hideout_generator_v1.1.py --batch 50 maps large
```

2. No window opens. The maps are saved in the folder (it is made if it does not exist)
3. Each map is named `hideout_<size>_<map number>`. Without a size word the maps are medium

## Reference Tables

### Map Sizes

| Size   | Floors | Largest level (squares) | Large floors        | Deep room | Sheet layout                     |
|--------|--------|-------------------------|---------------------|-----------|----------------------------------|
| Small  | 2      | 16 wide x 18 tall       | 1 (70%) or 2 (30%)  | No        | 2 across, in one row             |
| Medium | 4      | 24 wide x 25 tall       | 1 (40%) or 2 (60%)  | Yes       | 2 across, 2 down                 |
| Large  | 4 to 6 | 42 wide x 28 tall       | 1 to 6, equal odds  | Yes       | Picked to fill the screen        |

### Ground Level Position Words

| Map size        | Ground level place | Line under the buttons reads                                            |
|-----------------|--------------------|-------------------------------------------------------------------------|
| Small           | Top                | `Ground level (left) is the top floor (the other level is below it)`    |
| Small           | Bottom             | `Ground level (left) is the bottom floor (the other level is above it)` |
| Medium, Large   | Top                | `Ground level (top left) is the top floor (the other levels are below it)` |
| Medium, Large   | Middle             | `Ground level (top left) is in the middle (levels above and below it)`  |
| Medium, Large   | Bottom             | `Ground level (top left) is the bottom floor (the other levels are above it)` |

### Level Kinds

| Kind     | Meaning                                                        |
|----------|----------------------------------------------------------------|
| `ground` | Large level with 1 or 2 outside entrances. Every map has one   |
| `upper`  | Large level above the ground level                             |
| `lower`  | Large level below the ground level                             |
| `small`  | Open floor around the stairwell with a few corner rooms        |

### Setting Tags

| Tag         | Meaning                                       |
|-------------|-----------------------------------------------|
| `[stated]`  | The author asked for this value               |
| `[default]` | Proposed in the outline and kept              |
| `[GUESS]`   | Picked by Claude because nothing was decided  |

### Saved Files

| File                          | Contents                                  |
|-------------------------------|-------------------------------------------|
| `<name>_level_<n>_grid.jpg`   | One level with the light blue grid        |
| `<name>_level_<n>_walls.jpg`  | One level, walls only                     |
| `<name>_overview.jpg`         | Every level's grid picture on one sheet   |

## Features

- Three map sizes, each one button in the window
- Large map is landscape (wider than tall) to suit a computer screen
- Overview sheet layout is picked to show the levels as big as the screen allows
- One stairwell, 4 x 4 squares, in the same spot on every level
- Any floor can be the ground level, with floors above it, below it or both
- One deep room per medium and large map, reached only by walking through 3 to 5 other rooms
- 15-digit map numbers: the same size and number always remake the same map
- Every number worth changing sits in the SETTINGS section, and the script checks them when it starts
- Window is resizable; the map refits after resizing stops

## Integration

```
~/Downloads/hideout-generator/
  hideout_generator_v1.1.py          <-- this tool
  hideout_generator_v1.1_README.md   <-- this file
  hideout_generator_v2.py ... v1.0   <-- earlier versions, kept unchanged
```

The folder can be anywhere. On Windows the same example is `C:\Users\<your name>\Downloads\hideout-generator\`.

The tool uses only Python's standard library plus Pillow. Tkinter draws the window, and Pillow draws and saves the JPG pictures. It needs no network connection.

## Common Use Cases

### Game Night: Need a Hideout Fast

1. Run the script and click **Click for medium map**
2. Click again until you like the layout
3. Click **Yes** and save it. Print `<name>_overview.jpg`, or the walls pictures for a battle map

### Share a Map Without Sending Files

1. Note the size and map number under the buttons
2. Send those two to the other person
3. They run `python3 hideout_generator_v1.1.py <size> <number>` and get the same map

### Build a Library of Maps

1. Run batch mode once per size, for example `--batch 50 maps large`
2. Browse the `maps` folder and keep the ones you like

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `No module named 'PIL'` | Install Pillow: `python3 -m pip install pillow` |
| `No module named 'tkinter'` | Install Python from python.org, which includes Tkinter |
| Window does not appear when run from the Claude terminal pane | Run the same command in the macOS Terminal app |
| "Settings problem" message at start | A value in SETTINGS breaks a rule. The message names the setting to fix |
| "No map was made" message | The settings could not be met within TRY_LIMIT tries. Most often ROOM_COUNT with LARGEST_ROOM, or DEEP_ROOM_WALK_THROUGH |
| A version 8 large map number gives a different map | Expected. The large map changed shape in version 9 |
| Large map levels look small | Make the window bigger or fill the screen. The layout is picked again after each resize |

## Security Notes

- **No Network**: The tool never connects to the internet. Everything runs on your computer.
- **Files Written**: Pictures are saved only to the folder you pick (or the folder named in batch mode). Existing files are replaced only after you click Yes.
- **No Data Collected**: Map numbers come from your computer's random number source. Nothing about you is stored.
- **Pillow Install**: Install Pillow with `pip` from the official Python Package Index only.
