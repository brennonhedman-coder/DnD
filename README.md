# DnD
Dungeons & Dragons stuff to make life easier

# About
One tool so far has been made to make life easier: it generates maps programmatically.

The idea that sparked this repo is DnD-MapBuilder-Interior. Basically, I wanted to build a tool that generates floor plans for TTRPGs, in the form of an app you can click on like a rat clicking for food pellets, and it makes map after map as fast as you can click (maybe not literally, but it is supposed to be fast and satisfying to click and use).

The tool has gone through a few names. Hideout generator was the first iteration, it became DnD-BuildingFloorPlans for version 2.0, and the latest name is DnD-MapBuilder-Interior (starting again at v1.0). I can read a Python script but I only speak English and PowerShell. AI is generating, editing and/or reviewing the code. Each script is published with a README .md file next to it; if you don't see one for a script, it is on the way.

The reason everything was renamed and all the code rewritten and redesigned for 2.0 was to make these maps usable if someone prints them on a full sheet of paper. You could use these maps a lot of different ways, but the goal is "print and play": every map can be printed at home on 8.5 x 11 paper and you can actually play with what comes out of your printer. There are four buttons: "Single building", "Bandit hideout", "Small dungeon" and "Dungeon complex". Other compatibility features include a 70 pixel grid, but these files have not been tested with any online platforms. You get .jpg files when you hit save.

# Files
- DnD-MapBuilder-Interior_v1.0.py: the latest version of the tool
- DnD-MapBuilder-Interior_v1.0_README.md: how to install, run and print with it
- hideout_generator: the original iteration. I plan to keep working on it as well; it makes much larger maps if you just count the grid squares (each square represents 5' x 5').

I hope you enjoy.
