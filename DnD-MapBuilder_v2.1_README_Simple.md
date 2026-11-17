# DnD MapBuilder v2.1 (the short version)

Click a few buttons, get a whole D&D adventure: a map of the land, places to visit, and a floor plan for every place. Print it and play.

## What you need

- A computer with Python 3 on it
- The picture add-on Pillow. Install it once by typing this in Terminal:

```bash
python3 -m pip install pillow
```

## Start it

```bash
python3 DnD-MapBuilder_v2.1.py
```

A big window opens with buttons at the top and a black area below where your maps appear.

## Make an adventure

1. Click "Area map". You get a map of the land with forests (green trees), water (blue waves) and sand. Don't like it? Click again.
2. Click "Adventure locations". Numbered red x marks appear on the map: these are the places your players will visit.
3. The window asks if you want floor plans for those places:
   - "Make automatically": every place gets one at once. The easy choice.
   - "Yes": you pick one place at a time. Click "Building", "Village", "Hideout", "Town" or "Dungeon complex" until you like it, then "Use for this location".
   - "No": skip the floor plans.
4. At "Save?", click "Yes" and type a name. Everything goes into a folder called `Maps`, next to the script.

## What the floor plans are

| Button | What you get |
|---|---|
| "Building" | One house or shop, with rooms and hallways |
| "Village" | 6 to 11 buildings |
| "Hideout" | 3 or 4 floors, some up and some down, joined by stairs |
| "Town" | 12 to 29 buildings and a hideout |
| "Dungeon complex" | 15 to 99 underground rooms joined by corridors |

## Print and play

- Open the saved folder and print the pictures on normal paper. Turn on "Fit to page" when you print.
- Pictures ending in `_grid` have blue squares for moving pieces around. The others are plain.
- Each square on the map is one 5 foot square in the game.
- The file ending in `_locations.txt` tells you which floor plan goes with which red x.
- A dungeon complex comes with a room key that says which doorway leads to which room.

## Get the same map back

Every map has a number called a seed, shown in the line of text under the seed box. Copy it into the seed box and click the same button to get exactly the same map again. Once places are added, the line shows two seeds joined by a dash: that brings back the map and its places together.

## If something goes wrong

| Problem | Try this |
|---|---|
| "No module named 'PIL'" | Install Pillow (see "What you need") |
| The window does not show up | Run it from the Terminal app |
| The printout is cut off | Turn on "Fit to page" in the print window |
| "There is already a folder called ..." | Pick a different name. Nothing is ever overwritten |
| The map buttons disappeared | You are picking floor plans. Finish every place and they come back |

For every detail, see DnD-MapBuilder_v2.1_README.md.
