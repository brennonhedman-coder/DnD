# DnD
Dungeons & Dragons stuff to make life easier

# About
One tool so far has been made to make life easier: it generates maps programmatically.

The idea that sparked this repo is DnD-MapBuilder-Interior. Basically, I wanted to build a tool that generates floor plans for TTRPGs, in the form of an app you can click on like a rat clicking for food pellets, and it makes map after map as fast as you can click (maybe not literally, but it is supposed to be fast and satisfying to click and use).

The tool has gone through a few names. Hideout generator was the first iteration, it became DnD-BuildingFloorPlans for version 2.0, and the latest name is DnD-MapBuilder-Interior (starting again at v1.0). I can read a Python script but I only speak English and PowerShell. AI is generating, editing and/or reviewing the code. Each script is published with a README .md file next to it; if you don't see one for a script, it is on the way.

The goal of DnD-MapBuilder-Interior is "print and play": every map can be printed at home on 8.5 x 11 paper and you can actually play with what comes out of your printer. Every floor and every dungeon room fits on one sheet, with a 70 pixel grid. These files have not been tested with any online platforms. You get .jpg files when you hit save.

# Two versions
This repo has two versions of DnD-MapBuilder-Interior, and they are very different. Both run on their own; pick the one you like.

- v2.0 is the newest. It was rewritten from scratch to be short and simple, and its dungeons are laid out on an even grid that is easy to read and easy to lay out at the table.
- v1.0 is the bigger, more detailed version. Its floors have hallways and more kinds of stairs, and its dungeons grow into tight clusters with winding corridors.

The same seed makes a different map in each version.

| | v1.0 | v2.0 |
|---|---|---|
| Buttons | "Single building", "Bandit hideout", "Small dungeon", "Dungeon complex" | "Building", "Hideout", "Dungeon" |
| Script size | about 3,400 lines | about 730 lines |
| Floors | Rooms and hallways; the stairwell often opens straight onto a hallway | Rooms only, joined by doorways |
| Building | One floor taken from a bandit hideout, stairs removed | One floor built on its own |
| Hideout | Bandit hideout of 3 or 4 levels, or a small dungeon of 4 to 6 levels all below ground. A main stairwell links levels 1, 2 and -2; deeper levels use secondary stairwells | One button for both: 3 to 6 levels, up to 3 above ground. One stairwell runs through every level |
| Dungeon rooms | 15 to 99 rooms packed tightly into clusters | 15 to 99 rooms on an even grid, numbered left to right, top to bottom |
| Dungeon corridors | Winding, found round the rooms; they branch and meet each other | Short and simple; each joins exactly two rooms and none cross |
| Doors per dungeon room | At most 2 | Up to 4, one per wall |
| Dungeon ways out | An exit 6 times in 7, otherwise a shortcut back towards the entrance | Always an entrance on the west and an exit on the east |
| Dungeon room key | Detailed: reached from, leads on to, loops round to, every doorway | Simple: every doorway, its corridor length and where it leads |
| Dungeon overview | 2 pictures: grid on the rock, grid on the floors | 1 picture: white, grid inside rooms and corridors only |
| Command line | A seed and kind, `--save` without the window, `--test` to check many maps | A seed and kind only |
| Save buttons | Standard buttons (dark grey in Dark Mode) | White, in Light or Dark Mode |

# Files
- DnD-MapBuilder-Interior_v2.0.py: the newest version of the tool
- DnD-MapBuilder-Interior_v2.0_README.md: how to install, run and print with v2.0
- DnD-MapBuilder-Interior_v1.0.py: the bigger, more detailed version
- DnD-MapBuilder-Interior_v1.0_README.md: how to install, run and print with v1.0

Both need Python 3.8 or newer and Pillow (`python3 -m pip install pillow`). To start one:

```bash
python3 DnD-MapBuilder-Interior_v2.0.py
```

I hope you enjoy.
