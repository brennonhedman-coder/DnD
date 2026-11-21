# DnD

Dungeons & Dragons stuff to make life easier.

Click a few buttons, get a whole adventure: a map of the land, places to visit, and a floor plan for every place. Print it on normal paper and play. But in like super basic lines and it's rough.

## What's here

| File | What it is |
|---|---|
| `DnD-MapBuilder_v2.1.py` | The tool. One file, one window |
| `DnD-MapBuilder_v2.1_README_Simple.md` | The short how-to |
| `DnD-MapBuilder_v2.1_README.md` | Every detail |

All the older scripts are in the `Old-work` branch (see "Older work" below).

## What you need

- Python 3.8 or newer, on macOS, Windows or Linux
- The picture add-on Pillow. Install it once:

```bash
python3 -m pip install pillow
```

## Start it

```bash
python3 DnD-MapBuilder_v2.1.py
```

A big window opens with buttons at the top and a black area below where your maps appear.

## Make an adventure

1. Click "Area map". You get the land, with forests (green trees), water (blue waves) and sand. Click again until you like it.
2. Click "Adventure locations". Numbered red x marks appear: the places your players will visit.
3. Pick floor plans for those places:
   - "Make automatically": every place gets one at once. The easy choice.
   - "Yes": pick one place at a time, then "Use for this location".
   - "No": skip the floor plans.
4. At "Save?", click "Yes" and type a name. Everything goes into its own folder inside `Maps`, next to the script.

## The floor plans

| Button | What you get |
|---|---|
| "Building" | One house or shop, with rooms and hallways |
| "Village" | 6 to 11 buildings |
| "Hideout" | 3 or 4 floors, some up and some down, joined by stairs |
| "Town" | 12 to 29 buildings and a hideout |
| "Dungeon complex" | 15 to 99 underground rooms joined by corridors, with a room key |

## Print and play

- Every map fits one 8.5 x 11 sheet. Turn on "Fit to page" when you print.
- Pictures ending in `_grid` have blue squares for moving pieces around. The others are plain.
- `<name>_locations.txt` says which floor plan goes with which red x.
- For an online tabletop, import the pictures and set its grid to 70 pixels per square.

## Get the same map back

Every map has a number called a seed, shown under the seed box. Paste it into the seed box and click the same button to get exactly the same map. Once places are added you get two seeds joined by a dash, which brings back the land and its places together.

## If something goes wrong

| Problem | Try this |
|---|---|
| "No module named 'PIL'" | Install Pillow (see "What you need") |
| The window does not show up | Run it from the Terminal app |
| The printout is cut off | Turn on "Fit to page" in the print window |
| "There is already a folder called ..." | Pick a different name. Nothing is ever overwritten |

## Older work

Every earlier script, with its README, is kept in the `Old-work` branch: the separate area map and floor plan tools (DnD MapBuilder Exterior and Interior) and the earlier versions of DnD MapBuilder.

- On GitHub: open the branch menu (it says `main`) and pick `Old-work`.
- With git:

```bash
git checkout Old-work
```

## About this repo

I can read a Python script but I only speak English and PowerShell. AI generates, edits and reviews the code. The tool never uses the network and only saves into its `Maps` folder. It is for personal use at the table and has not been tested with any online platforms.

## License

Unlicense. See the `LICENSE` file.
