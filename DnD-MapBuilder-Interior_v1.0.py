#!/usr/bin/env python3
# ============================================================================
# DnD-MapBuilder-Interior_v1.0.py
# ============================================================================

"""
.SYNOPSIS
    Tkinter window that makes random floor plans (walls only) for a single
    building, a bandit hideout, a small dungeon or a dungeon complex,
    and saves them as JPG files.

.DESCRIPTION
    Print and play floor plans for tabletop games. One click makes a whole
    map, shows it in the window and asks whether to save it.

    The window:
      - Four buttons, centered at the top: "Single building", "Bandit
        hideout", "Small dungeon" and "Dungeon complex". Each click makes
        a new map straight away
      - The seed box is under the buttons. Leave it empty for a new map, or
        type a seed to get that map back
      - The line of text under the seed box says what was made. The seed
        number in it can be selected with the mouse and copied (Cmd+C on a
        Mac, Ctrl+C elsewhere). Double-click selects the whole number
      - The save question is under that, while a map is waiting to be saved.
        For a dungeon complex it also has "Open full size", which shows the
        overview in your picture viewer, where you can zoom in
      - The preview fills the rest of the window and is fitted again
        whenever the window changes size, so it is never clipped

    Every map made by the first three buttons:
      - The grid is always 70 x 70 pixels per square. Every wall sits on a
        grid line. Outer walls are 7 pixels thick, inner walls 3 pixels
      - Every level is cut into rectangular rooms (3 x 3 squares or more)
        and straight hallways 1 square wide. Every doorway is 1 square wide
      - The ground level is always 17 x 13 squares, and no level is bigger,
        so every level fits on one sheet of 8.5 x 11 inch paper
      - Each map has a seed, a string of digits. The same seed always makes
        the same map, on any computer and any Python version, because the
        script uses its own whole-number dice (SeedDice) and never the
        standard "random" module
      - No try-again loops: each level is built once, straight from the seed

    Bandit hideout:
      - 3 or 4 levels. Ground is level 1, the levels above it are 2, 3, 4
        and the levels below it are -2, -3, -4
      - Ground has the exterior entrance. Half of all maps also have an
        exterior exit on a different wall
      - Upper floors stack inside the floor below them, and basement floors
        inside the floor above them: 3 fits inside 2, -3 inside -2

    Small dungeon:
      - Built like a hideout, but with 4, 5 or 6 levels (equal odds), and
        every level after ground is below it: -2, -3 ... -6, each inside
        the one above

    Dungeon complex:
      - One big underground complex on a single level of 15 to 99 rooms,
        joined by corridors 1 square wide
      - Smaller complexes are much more likely. Each room count is weighted
        1 / (rooms x rooms), so 30 rooms is a quarter as likely as 15. About
        6 complexes in 10 have fewer than 30 rooms, 3 in 10 have 30 to 59,
        1 in 10 has 60 to 89, and about 1 in 50 has 90 to 99
      - Rooms are rectangles from 7 x 5 squares up to 17 x 13, every size
        equally likely. 17 x 13 is the ground level size, so every room
        prints on one sheet of 8.5 x 11 inch paper
      - Every room is built inside like a floor of the other maps: cut into
        2 or more inner rooms (3 x 3 squares or more), doorways joining
        every part, sometimes a second way round, and side hallways in the
        bigger parts. Bigger rooms get more inner rooms, up to 11. A room
        gets straight hallways 1 square wide when it rolls 4 or more inner
        rooms, which is about half of all rooms and most of the big ones
      - When a room gets a hallway and one of its doorways lines up with a
        spot where a hallway can run, the hallway is cut through that
        doorway, so the corridor from outside leads straight into it
      - Every doorway is 1 square wide and leads from a room into a
        corridor. No room has more than 2 doorways, entrance and exit
        corridors included. Corridors branch and meet each other outside
        the rooms, so the complex still joins up
      - Rooms are packed tightly into clusters, with bare rock between the
        clusters and corridors winding between the rooms
      - Every room can be reached from every other room. Some rooms are
        dead ends. Some corridors make loops
      - One entrance corridor runs from a room straight out to the edge of
        the complex. 6 complexes in 7 also have an exit on a different side.
        The complex has no stairwells
      - A complex with no exit has a shortcut instead: a corridor from the
        deepest room back to a room picked at random from those 2 to 6
        corridors from the entrance, where the normal walk is much longer.
        "Deepest" and "corridors from the entrance" count the corridors as
        they were made, room to room, not the junctions where corridors
        later meet. The shortcut mostly makes its own way: it crosses other
        corridors where it must, and now and then runs a short way along
        one where that is much shorter than going round
      - How it is made: the rooms are packed in pairs again and again
        (side by side or one above the other) aiming for a wide screen
        shape; each pairing is joined by one corridor between its two
        nearest rooms, which joins the whole complex; a few more corridors
        between near neighbours make the loops. Each corridor is found
        round the rooms, likes to follow corridors already there and keeps
        from running alongside them. Last, the inside of every room is
        built

    Single building:
      - One floor only. 1 time in 10 it is a 17 x 13 ground floor; the
        other 9 times it is one of the other floors of a hideout, which are
        usually smaller (about 1 in 100 buildings is a full 17 x 13 floor
        that is not the ground floor)
      - It has no stairwells. Those squares are plain floor of the room or
        hallway they would have been in
      - It always has an exterior entrance: at the end of a hallway when
        the floor has one, otherwise through the outer wall of a room,
        never at a corner. Half of them also have an exit on a different
        wall, by the same rule

    Stairwells (hideout and small dungeon):
      - The main 2 x 2 stairwell sits in the same spot on every level it
        serves. It is placed first and every level is sized and placed
        around it. It links levels 1, 2 and -2, and its walls are 7 pixels
        thick, like the outer walls
      - Each level rolls 75% / 25%. On 75% the main stairwell is meant to
        open straight onto a hallway: the hallway ends at the stairs and
        three blocks of rooms wrap round them (the "pinwheel"). On 25%, or
        when the level is too small or tight for the pinwheel, the
        stairwell sits in a room, and that room has a doorway straight onto
        a hallway when the level has one. The ground level almost always
        fits, so about 3 ground levels in 4 have the stairwell on a
        hallway; most other levels are too tight, so across all levels it
        is about 1 in 3
      - Levels 3, 4, -3 and deeper are reached only by secondary
        stairwells, in some room of the level next to them, never in the
        room you arrived in. Those levels have no main stairwell: rooms and
        hallways use that space
      - Every stairwell is one straight staircase: it opens at one end on
        the lower floor and the opposite end on the upper floor, so its
        tread lines run the same way on both
      - Every stairwell is planned before any level is sized

    Saved pictures:
      - Each level is saved twice: walls only, and walls with the grid.
        Each file is the level itself plus a 1 square margin all round,
        with a small header inside that margin. A ground level's entrance
        and exit bump outs reach into the margin
      - A hideout or small dungeon also saves one overview sheet with every
        level on it, drawn at the same size and lined up with the ground
        level. The hideout overview is 2 floors across; the small dungeon
        overview is landscape, 3 floors across and 2 down
      - On the overview, and only there, blue squares show the ground
        footprint a floor does not cover. A darker blue shows the footprint
        of the floor next to it, nearer ground, when that is not ground
      - A single building saves 2 JPGs. A hideout saves 7 or 9, a small
        dungeon 9, 11 or 13

    Dungeon complex pictures and room key:
      - <name>_overview.jpg and <name>_overview_grid.jpg: the whole complex
        at 20 pixels per square, with every room numbered and the entrance
        (IN) and exit (OUT) marked. Each room shows its outline only, not
        the walls inside it. The plain version has the grid on the bare rock
        round the complex only; the grid version has it on the floors only
      - <name>_room_<n>_walls.jpg and <name>_room_<n>_grid.jpg for every
        room: the room and its inside at 70 pixels per square, ready to
        print, with a 1 square margin. Outer walls are 7 pixels thick,
        inner walls 3 pixels. Each doorway is a 1 x 1 bump out into the
        margin, where the corridor starts. The header says "Room n of N"
        and the seed, which is the seed of the whole complex
      - <name>_room_key.txt: the key for laying the printed rooms out. For
        every room: its size and place, which rooms it is reached from
        (nearer the entrance), which it leads on to and which it loops
        round to, how many inner rooms it has and whether it has hallways,
        each doorway with its wall and square and whether it opens into a
        hallway or an inner room, and how long each corridor from it is
        and where it goes. A complex with no exit also says where its
        shortcut runs
      - The key lists each corridor as it was made, from one room to
        another. Corridors branch and meet outside the rooms, so a corridor
        often also reaches rooms its line in the key does not name (about
        half of all doorways). "Reached from", "leads on to" and "loops
        round to" count corridors the same way. The overview shows every
        corridor and every junction

    Test mode makes many maps of all four kinds and checks each one
    against the rules.

    Every number you may want to change is in the SETTINGS section.

    Lines that start with "#" are notes for people. Python ignores them.

.NOTES
    Author : Brennon Hedman
    Version: 1.0
    Requires: Python 3.8+ and Pillow 10.1+ (python3 -m pip install pillow)
    Platform: macOS, Windows or Linux (the window uses Tkinter, which comes
              with the standard Python installer)

.EXAMPLE
    python3 DnD-MapBuilder-Interior_v1.0.py

    Opens the window with the four buttons.

.EXAMPLE
    python3 DnD-MapBuilder-Interior_v1.0.py 123456789012345

    Opens the window already showing the hideout with seed 123456789012345.
    Add the word building, dungeon (small dungeon) or complex after the
    seed for the other kinds.

.EXAMPLE
    python3 DnD-MapBuilder-Interior_v1.0.py --test 500

    No window. Makes 500 maps of each kind, checks each one against the
    rules, and prints a report with the time taken.

.EXAMPLE
    python3 DnD-MapBuilder-Interior_v1.0.py --save cave1 123456789012345 complex

    No window. Makes the map with that seed and saves it in the folder
    Maps/cave1. Leave the seed off for a random map. The last word picks
    the kind: building, hideout, dungeon (small dungeon) or complex
    (hideout if left off).
"""

import hashlib
import heapq
import os
import sys
import time

from PIL import Image, ImageChops, ImageDraw, ImageFont   # Pillow, the add-on that writes JPG files


# ============================================================================
# SETTINGS
# ============================================================================

# ── The grid ────────────────────────────────────────────────────────────
SQUARE = 70                      # pixels per grid square
GRID_COLOR = (140, 190, 255)     # light blue
GRID_OVER_WALLS = False          # False = walls stay solid black where a grid
                                 # line runs along them. True = the blue line
                                 # is drawn on top, through the middle of walls

# ── Levels ──────────────────────────────────────────────────────────────
LEVEL_COUNTS = (3, 4)            # hideout: equal odds of each
DUNGEON_LEVEL_COUNTS = (4, 5, 6) # small dungeon: 4 to 6 levels, equal odds of each,
                                 # all of them below ground after level 1
BUILDING_GROUND_CHANCE = (1, 10) # single building: 1 in 10 is a ground floor,
                                 # the rest are one of the smaller floors
GROUND_W, GROUND_H = 17, 13      # ground footprint in squares
MIN_LEVEL = 4                    # smallest level is 4 x 4. Levels that must
                                 # hold secondary stairwells in separate rooms
                                 # are made just big enough for that

# ── Rooms and hallways ──────────────────────────────────────────────────
MIN_ROOM = 3                     # smallest room is 3 x 3
MAX_ROOMS = 11                   # most rooms on any level
GROUND_ROOMS = (6, 11)           # ground aims for this many rooms. The rules
                                 # allow 2 to 11; a low number gives a plain map
SQUARES_PER_ROOM = 20            # levels other than ground, and the rooms of a
                                 # dungeon complex: at most 1 room per this many
                                 # squares, so smaller ones get fewer rooms
HALL_MIN_ROOMS = 4               # levels other than ground, and the rooms of a
                                 # dungeon complex, get a hallway from this many
                                 # rooms
SIDE_HALL_MIN_AREA = 60          # a block this big may get a side hallway
SIDE_HALL_CHANCE = (1, 2)        # 1 in 2
EXTRA_DOOR_CHANCE = (1, 6)       # chance of a second way round between two rooms

# ── Stairwells ──────────────────────────────────────────────────────────
HALL_STAIR_CHANCE = (3, 4)       # 75%: the main stairwell opens straight onto a
                                 # hallway, when the level has room for the
                                 # pinwheel. 25%, or no room: it sits in a room
                                 # that has a doorway straight onto a hallway.
                                 # Rolled for each level on its own. Ground
                                 # nearly always has room; most other levels
                                 # do not, so about 1 level in 3 ends up with
                                 # its stairwell on a hallway
SECONDARY_FROM = 3               # levels 3, 4, -3, -4 (and further out) are
                                 # reached only by secondary stairwells
STAIR_GAP = 1                    # squares of floor kept between any two stairwells

# ── Entrance and exit ───────────────────────────────────────────────────
EXIT_CHANCE = (1, 2)             # 50%

# ── Drawing ─────────────────────────────────────────────────────────────
OUTER_WALL = 7                   # pixels
INNER_WALL = 3                   # pixels
STEP_GAP = 14                    # pixels between stair lines (10 steps)
MARGIN = 1                       # squares of white around the outermost line
HEADER_SPACE = 1                 # squares of white above the header words
HEADER_BIGGEST = 34              # header letter height in pixels, largest
HEADER_SMALLEST = 22             # and smallest. Below this the header wraps
                                 # (overview only)
MARGIN_TEXT_BIGGEST = 28         # single-level files: header letter height,
MARGIN_TEXT_SMALLEST = 8         # largest and smallest, inside the 1 square margin
MARGIN_TEXT_GAP = 6              # pixels kept clear between the header and any
                                 # wall, bump out or picture edge
JPG_QUALITY = 95                 # 1 to 95: higher is sharper, and a bigger file
MAIN_STAIR_WALL = 7              # pixels: main stairwell walls match the outer
                                 # walls. Secondary stairwells keep INNER_WALL

# ── Overview blue squares ───────────────────────────────────────────────
GROUND_FILL = GRID_COLOR         # grid-line blue: ground footprint squares this
                                 # floor does not cover
NEXT_FLOOR_FILL = (80, 130, 225) # a darker blue: footprint of the floor next to
                                 # it, nearer ground, when that is not ground.
                                 # Squares the floor itself covers stay white,
                                 # so only the empty space around it is filled in

# ── Dungeon complex: size and rooms ─────────────────────────────────────
COMPLEX_ROOM_COUNT = (15, 99)    # fewest and most rooms
COMPLEX_ROOM_FALLOFF = 2         # how fast bigger complexes get rarer: each
                                 # room count is weighted 1 / (rooms to this
                                 # power). 2 = 6 in 10 under 30 rooms and 1 in
                                 # 50 from 90 to 99. 1 = more big ones,
                                 # 3 = fewer. 0 = every count equally likely
COMPLEX_ASPECT = (3, 2)          # the whole complex is packed to roughly this
                                 # width : height
COMPLEX_ROOM_WIDTH = (7, 17)     # smallest and largest room width, in squares
COMPLEX_ROOM_HEIGHT = (5, 13)    # smallest and largest room height. Every size
                                 # in these ranges is equally likely. The largest
                                 # is the ground level size, so each room's
                                 # sheet prints on 8.5 x 11 paper
COMPLEX_MAX_DOORS = 2            # most doorways a room may have, the entrance
                                 # and exit included
COMPLEX_CLUSTER_DEPTH = 3        # the first pairings this deep leave a strip of
                                 # bare rock: 2 = a few big clusters,
                                 # 4 = many small ones
COMPLEX_CLUSTER_GAP = 5          # width of that strip, in squares
COMPLEX_INNER_ROOMS_LEAST = 2    # every room is cut into at least this many
                                 # inner rooms. Bigger rooms get more, up to
                                 # MAX_ROOMS, at 1 per SQUARES_PER_ROOM squares

# ── Dungeon complex: corridors ──────────────────────────────────────────
COMPLEX_EXTRA_LINK_CHANCE = (1, 4) # chance of a loop between two near rooms
COMPLEX_EXTRA_LINK_NEIGHBORS = 3 # each room looks at its nearest 3 neighbours
COMPLEX_EXIT_CHANCE = (6, 7)     # 6 in 7: a second way out, on a different side.
                                 # The other 1 in 7 get a shortcut instead: a
                                 # corridor from the deepest room back to a
                                 # room near the entrance
SHORTCUT_TO_STEPS = (2, 6)       # the shortcut ends at a room this many
                                 # corridors from the entrance room, fewest and
                                 # most, picked at random. It is always at least
                                 # 2 corridors nearer than the deep room
SHORTCUT_SAVING = 2              # the shortcut only goes to a room where the
                                 # normal walk is at least this many times the
                                 # straight distance between the two rooms
SHORTCUT_HALL_COST = 6.0         # the shortcut only: a square of a corridor
                                 # that is already there is dear, so the
                                 # shortcut mostly makes its own way. It still
                                 # crosses corridors, and now and then runs
                                 # along one where going round is much longer

# How corridors are found. Lower cost = more wanted.
STEP_COST = 1.0                  # a square of bare ground
HALL_COST = 0.3                  # a square of a corridor that is already there
NEAR_HALL_COST = 2.5             # a square right beside a corridor, so two
                                 # corridors do not run side by side
TURN_COST = 2.0                  # each bend. Higher gives straighter corridors

# ── Dungeon complex: the overview picture ───────────────────────────────
COMPLEX_SQUARE = 20              # pixels per grid square on the overview
COMPLEX_WALL = 4                 # pixels, every wall on the overview
COMPLEX_MARGIN = 3               # squares of white left, right and below
COMPLEX_MARGIN_TOP = 4           # squares above: the header and entrance marks
# The overview shows each room's outline only. The inside of each room
# (inner rooms, hallways and their walls) is drawn on that room's own
# sheet, which uses the 70 pixel grid and wall sizes above.

# ── Saving ──────────────────────────────────────────────────────────────
MAP_LABELS = {"building": "Building", "hideout": "Hideout", "dungeon": "Small dungeon",
              "complex": "Dungeon complex"}
                                 # the word for each kind in headers and messages
OVERVIEW_ACROSS = {"hideout": 2, "dungeon": 3}
                                 # floors side by side on the overview sheet
                                 # (always 2 rows): the small dungeon is landscape
KINDS = ("building", "hideout", "dungeon", "complex")
                                 # the words used on the command line
SEED_DIGITS = 15                 # length of a new random seed
SEED_BOX_OUTLINE = "#808080"     # color of the line round the seed box
SEED_BOX_FOCUS = "#3b82f6"       # the same line while you are typing in the box
SAVE_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Maps")
                                 # saved maps go in "Maps", next to this script

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# ── Window ──────────────────────────────────────────────────────────────
EMPTY_PREVIEW = "black"          # the preview area before a map is shown
SHOWN_PREVIEW = "black"          # the unused space around the map once one is shown


def check_settings():
    """Stops with a message if two dungeon complex settings cannot work together."""
    problems = []
    if not 1 <= COMPLEX_ROOM_WIDTH[0] <= COMPLEX_ROOM_WIDTH[1] or not 1 <= COMPLEX_ROOM_HEIGHT[0] <= COMPLEX_ROOM_HEIGHT[1]:
        problems.append("COMPLEX_ROOM_WIDTH and COMPLEX_ROOM_HEIGHT must each go from low to high.")
    if min(COMPLEX_ROOM_WIDTH[0], COMPLEX_ROOM_HEIGHT[0]) < MIN_ROOM:
        problems.append("The smallest dungeon complex room must be at least MIN_ROOM across.")
    if not 2 <= COMPLEX_ROOM_COUNT[0] <= COMPLEX_ROOM_COUNT[1]:
        problems.append("COMPLEX_ROOM_COUNT must go from low to high.")
    if COMPLEX_ROOM_FALLOFF < 0 or COMPLEX_ROOM_FALLOFF != int(COMPLEX_ROOM_FALLOFF):
        problems.append("COMPLEX_ROOM_FALLOFF must be a whole number, 0 or more.")
    if COMPLEX_MAX_DOORS < 1:
        problems.append("COMPLEX_MAX_DOORS must be 1 or more.")
    if problems:
        sys.exit("Settings problem:\n  " + "\n  ".join(problems))


# ============================================================================
# SEED DICE
# ============================================================================

# Our own random numbers. Only whole-number maths, so a seed
# gives the same rolls on every computer and every Python version.

BITS_64 = (1 << 64) - 1


class SeedDice:
    def __init__(self, seed_text):
        self.state = int(seed_text) & BITS_64

    def roll(self):
        """One big whole number (the "splitmix64" recipe)."""
        self.state = (self.state + 0x9E3779B97F4A7C15) & BITS_64
        z = self.state
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & BITS_64
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & BITS_64
        return z ^ (z >> 31)

    def below(self, n):
        """A whole number from 0 to n - 1."""
        return self.roll() % n

    def between(self, low, high):
        """A whole number from low to high, both included."""
        return low + self.below(high - low + 1)

    def chance(self, odds):
        """True "odds[0] times in odds[1]"."""
        return self.below(odds[1]) < odds[0]

    def pick(self, items):
        return items[self.below(len(items))]

    def shuffle(self, items):
        for i in range(len(items) - 1, 0, -1):
            j = self.below(i + 1)
            items[i], items[j] = items[j], items[i]


def new_seed():
    """A fresh seed for a new map. This is the only place real randomness is used."""
    number = int.from_bytes(os.urandom(8), "big") % (9 * 10 ** (SEED_DIGITS - 1))
    return str(number + 10 ** (SEED_DIGITS - 1))


# ============================================================================
# FLOOR DATA MODEL
# ============================================================================

# Squares are named by (x, y), counted from the top left square of the
# ground level, which is (0, 0). Every level uses the same numbering, which
# is what lines the stairwells up.
#
# A wall piece is one square long and sits on a grid line:
#   ("h", x, y)  runs along the top edge of square (x, y)
#   ("v", x, y)  runs along the left edge of square (x, y)

HALL = -1      # what a hallway square holds; a room square holds its room number
ALCOVE = -2    # a stairwell square in a hallway alcove (it belongs to no room)


class Stair:
    """One 2 x 2 stairwell on one level."""

    def __init__(self, pos, kind, link=None):
        self.pos = pos              # top left square
        self.kind = kind            # "main" or "secondary"
        self.link = link            # secondary only: (level nearer ground, level further out)
        self.open = None            # the side you step on: N, E, S or W
        self.alcove = False         # True = it sits in a hallway alcove, not in a room
        self.room = None            # the room it sits in, when it is in one


class Level:
    def __init__(self, number, rect, stairs):
        self.number = number                  # 1, 2, 3 ... or -2, -3 ...
        self.x, self.y, self.w, self.h = rect
        self.stairs = stairs                  # main stairwell first (if any), then secondaries
        self.main = stairs[0] if stairs and stairs[0].kind == "main" else None
                                              # None on levels 3, 4, -3, -4
        self.stair = self.main.pos if self.main else None
        self.arrival = 0                      # which stairwell players arrive by
        self.hall_roll = False                # did this level roll the 75% hallway result?
        self.rooms = []                       # (x, y, w, h) of each room
        self.cell = {}                        # (x, y) -> room number, HALL or ALCOVE
        self.doors = set()                    # wall pieces left open
        self.inner = set()                    # 3 pixel wall pieces
        self.outer = set()                    # 7 pixel wall pieces
        self.openings = []                    # ("entrance" or "exit", x, y, side)
        self.start = None                     # a level with no stairwell: the square
                                              # the walk to every square starts from

    def extent(self):
        """Left, top, right and bottom grid lines, bump outs included."""
        sides = [side for _, _, _, side in self.openings]
        return (self.x - ("W" in sides), self.y - ("N" in sides),
                self.x + self.w + ("E" in sides), self.y + self.h + ("S" in sides))

    def all_steps(self):
        """Every square covered by a stairwell."""
        cells = set()
        for stair in self.stairs:
            cells |= stair_cells(stair.pos)
        return cells


class Hideout:
    def __init__(self, seed, stair, levels, kind="hideout"):
        self.kind = kind        # "building", "hideout" or "dungeon" (small dungeon)
        self.seed = seed
        self.stair = stair
        self.levels = levels    # ground first, then 2, 3, 4, then -2, -3, -4


def edge_between(a, b):
    """The wall piece between two squares that touch."""
    if a[1] == b[1]:
        return ("v", max(a[0], b[0]), a[1])
    return ("h", a[0], max(a[1], b[1]))


def edge_ends(edge):
    """The two grid corners a wall piece runs between."""
    kind, x, y = edge
    return ((x, y), (x + 1, y)) if kind == "h" else ((x, y), (x, y + 1))


def stair_cells(stair):
    sx, sy = stair
    return {(sx, sy), (sx + 1, sy), (sx, sy + 1), (sx + 1, sy + 1)}


def stair_sides(stair):
    """For each side of the stairwell: its 2 wall pieces and the 2 squares in front."""
    sx, sy = stair
    return {
        "N": ([("h", sx, sy), ("h", sx + 1, sy)], [(sx, sy - 1), (sx + 1, sy - 1)]),
        "E": ([("v", sx + 2, sy), ("v", sx + 2, sy + 1)], [(sx + 2, sy), (sx + 2, sy + 1)]),
        "S": ([("h", sx, sy + 2), ("h", sx + 1, sy + 2)], [(sx, sy + 2), (sx + 1, sy + 2)]),
        "W": ([("v", sx, sy), ("v", sx, sy + 1)], [(sx - 1, sy), (sx - 1, sy + 1)]),
    }


def stairs_clear(a, b):
    """True if two stairwells keep STAIR_GAP squares of floor between them."""
    return abs(a[0] - b[0]) >= 2 + STAIR_GAP or abs(a[1] - b[1]) >= 2 + STAIR_GAP


def rect_holds(rect, pos):
    """True if the whole 2 x 2 stairwell at pos is inside rect."""
    x, y, w, h = rect
    return x <= pos[0] and pos[0] + 2 <= x + w and y <= pos[1] and pos[1] + 2 <= y + h


# A stairwell that links two floors is one straight staircase: you step on
# at one end on the lower floor and step off at the other end on the upper
# floor. So its open side on one floor is the opposite of the other, and its
# tread lines run the same way on both.
OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}


def footprint(pos, side):
    """(left, top, right, bottom) of a stairwell plus the 2 landing squares
    in front of its open side. No wall, hallway or level edge may cross it."""
    x, y = pos
    return {"N": (x, y - 1, x + 2, y + 2), "S": (x, y, x + 2, y + 3),
            "W": (x - 1, y, x + 2, y + 2), "E": (x, y, x + 3, y + 2)}[side]


def box_holds(rect, box):
    """True if rect (x, y, w, h) holds the whole box (left, top, right, bottom)."""
    x, y, w, h = rect
    return x <= box[0] and box[2] <= x + w and y <= box[1] and box[3] <= y + h


# ============================================================================
# PINWHEEL (the 75% hallway stairwell)
# ============================================================================

# A 2 x 2 hole cannot be cut out of one room and leave rectangles of 3 x 3 or
# more, so a hallway stairwell uses this layout. The hallway runs in from the
# outer wall and ends at the stairs; its last 2 squares run along the open
# side. Three blocks wrap round the other sides, and each block is then cut
# into rooms in the usual way.
#
#     +-----------+--------+
#     |  block A  |        |
#     |           |block B |
#     |..hall.....|        |        .... = hallway
#     |      |####|        |        #### = stairwell
#     |blk D |####|        |
#     |      +----+--------+
#     |      |   block C   |
#     +------+-------------+
#
# It is drawn here with the stairs opening north and the hallway coming in
# from the west. The other 7 ways round are the same drawing, turned and
# mirrored. Each way is a whole-number matrix (a, b, c, d):
#     new x = a * x + b * y        new y = c * x + d * y

TURNS = ((1, 0, 0, 1), (-1, 0, 0, 1), (1, 0, 0, -1), (-1, 0, 0, -1),
         (0, 1, 1, 0), (0, -1, 1, 0), (0, 1, -1, 0), (0, -1, -1, 0))
SIDE_STEP = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}
STEP_SIDE = {step: side for side, step in SIDE_STEP.items()}


def turn_rect(m, rect):
    a, b, c, d = m
    x, y, w, h = rect
    xs = (a * x + b * y, a * (x + w) + b * (y + h))
    ys = (c * x + d * y, c * (x + w) + d * (y + h))
    return (min(xs), min(ys), abs(xs[1] - xs[0]), abs(ys[1] - ys[0]))


def turn_side(m, side):
    a, b, c, d = m
    dx, dy = SIDE_STEP[side]
    return STEP_SIDE[(a * dx + b * dy, c * dx + d * dy)]


def pinwheel_fits(rect, pos):
    """Quick test: 3 squares or more on every side of the stairs, 4 on one."""
    x, y, w, h = rect
    gaps = (pos[0] - x, x + w - pos[0] - 2, pos[1] - y, y + h - pos[1] - 2)
    return min(gaps) >= MIN_ROOM and max(gaps) >= MIN_ROOM + 1


def pinwheel_layouts(rect, pos, others=(), need_exit=False, need_side=None):
    """
    Every way the pinwheel fits round the stairwell at pos inside rect.
    others: footprints of other stairwells; each must sit wholly inside one block.
    need_exit: block A must be wide enough to hold a side hallway, so the
               ground level always has a second wall for the exit.
    need_side: the side the stairwell must open on, or None for any.
    Each layout is (blocks, hallway, open side). A block is (rect, hall sides).
    """
    found = []
    if not pinwheel_fits(rect, pos):
        return found
    for m in TURNS:
        X0, Y0, W, H = turn_rect(m, rect)
        X1, Y1 = X0 + W, Y0 + H
        a, y, _, _ = turn_rect(m, (pos[0], pos[1], 2, 2))
        if (y - 1 - Y0 < MIN_ROOM or Y1 - y - 2 < MIN_ROOM
                or a - X0 < MIN_ROOM or X1 - a - 2 < MIN_ROOM):
            continue
        if need_exit and a + 2 - X0 < 2 * MIN_ROOM + 1:
            continue
        back = (m[0], m[2], m[1], m[3])          # turning back the other way
        if need_side and turn_side(back, "N") != need_side:
            continue
        parts =(((X0, Y0, a + 2 - X0, y - 1 - Y0), "S"),     # block A
                 ((a + 2, Y0, X1 - a - 2, y + 2 - Y0), ""),   # block B
                 ((a, y + 2, X1 - a, Y1 - y - 2), ""),        # block C
                 ((X0, y, a - X0, Y1 - y), "N"))              # block D
        blocks = tuple((turn_rect(back, part), frozenset(turn_side(back, s) for s in sides))
                       for part, sides in parts)
        if not all(any(box_holds(block, other) for block, _ in blocks) for other in others):
            continue
        hall = turn_rect(back, (X0, y - 1, a + 2 - X0, 1))
        found.append((blocks, hall, turn_side(back, "N")))
    return found


_ground_spots = {}


def ground_pinwheel_spots(need_exit):
    """Every stairwell spot on the ground level that has room for a pinwheel.
    Worked out once, then kept, because the ground level never changes size."""
    if need_exit not in _ground_spots:
        found = []
        for sy in range(GROUND_H - 1):
            for sx in range(GROUND_W - 1):
                layouts = pinwheel_layouts((0, 0, GROUND_W, GROUND_H), (sx, sy), need_exit=need_exit)
                if layouts:
                    found.append(((sx, sy), layouts))
        _ground_spots[need_exit] = found
    return _ground_spots[need_exit]


# ============================================================================
# GENERATOR
# ============================================================================

# Everything that could make a level fail is decided first, so each level
# is still built only once:
#   1. Roll the level count, the ground level's 75 / 25 and the exit.
#   2. Place the main stairwell. On a hallway roll, only spots where the
#      pinwheel fits are allowed.
#   3. For each run of levels going up (or down), place every secondary
#      stairwell, each with one straight wall (or hallway) line that will
#      keep it in a different room from the stairwell players arrive by.
#   4. Size each level so that it holds its stairwells and that line.
#   5. Build each level: the pinwheel or the planned first cut, then cut
#      the blocks into rooms, add doorways, outer wall, entrance and exit.

def make_hideout(seed, kind="hideout", dice=None):
    """A hideout or a small dungeon: the same builder with more levels,
    all of them below ground."""
    dice = dice or SeedDice(seed)

    # ── Level count, and which side of the ground each one goes ───────────
    if kind == "dungeon":
        count = dice.pick(DUNGEON_LEVEL_COUNTS)
        above = 0
    else:
        count = dice.pick(LEVEL_COUNTS)
        above = sum(dice.below(2) for _ in range(count - 1))
    below = count - 1 - above

    # ── Ground rolls, made before anything is placed ──────────────────────
    ground_hall = dice.chance(HALL_STAIR_CHANCE)
    want_exit = dice.chance(EXIT_CHANCE)

    # ── Main stairwell first ──────────────────────────────────────────────
    # Its open side on ground is fixed now too. Levels 2 and -2 open on the
    # opposite side, so the landing squares on BOTH sides must be on the
    # ground footprint (they always are for a pinwheel spot).
    ground_rect = (0, 0, GROUND_W, GROUND_H)
    layout = None
    if ground_hall:
        stair, layouts = dice.pick(ground_pinwheel_spots(want_exit))
        layout = dice.pick(layouts)
        ground_open = layout[2]
    else:
        stair = dice.pick(GROUND_ROOM_SPOTS)
        ground_open = dice.pick([side for side in "NESW"
                                 if box_holds(ground_rect, footprint(stair, side))
                                 and box_holds(ground_rect, footprint(stair, OPPOSITE[side]))])
    main = Stair(stair, "main")
    main.open = ground_open

    # ── Ground level ──────────────────────────────────────────────────────
    ground = build_level(dice, 1, ground_rect, [main],
                         dice.between(GROUND_ROOMS[0], GROUND_ROOMS[1]), True,
                         is_ground=True, layout=layout, want_exit=want_exit)
    ground.hall_roll = ground_hall
    levels = [ground]

    # ── Levels above, then levels below ───────────────────────────────────
    levels += build_run(dice, 1, above, stair, ground_open, len(ground.rooms))
    levels += build_run(dice, -1, below, stair, ground_open, len(ground.rooms))
    return Hideout(seed, stair, levels, kind)


# ── Single building ─────────────────────────────────────────────────────
# A single building is one floor of a hideout with the stairs taken out.
# The whole hideout is built first, exactly as the Bandit hideout button
# would build it from the same seed, so every floor shape the hideout can
# make is a shape a building can have. Then one floor is picked, its
# stairwells are removed, and it gets an entrance if it has none.

def edge_cells(edge):
    """The two squares a wall piece sits between."""
    kind, x, y = edge
    return (x, y), ((x - 1, y) if kind == "v" else (x, y - 1))


def strip_stairs(level):
    """Remove every stairwell: no tread lines and no stairwell walls. The
    squares become plain floor of the room or hallway they sat in."""
    for s in level.stairs:
        if s.alcove:
            for c in stair_cells(s.pos):
                level.cell[c] = HALL
    for s in level.stairs:
        for edges, _ in stair_sides(s.pos).values():
            for edge in edges:
                a, b = edge_cells(edge)
                # Keep it only where it is also a real wall between two rooms
                # (or a room and a hallway). The outer wall is drawn on its own.
                if None in (level.cell.get(a), level.cell.get(b)) or level.cell[a] == level.cell[b]:
                    level.inner.discard(edge)
    level.stairs = []
    level.main = level.stair = None


def wall_spots(level, hallway):
    """Every (x, y, side) on the outer wall where an entrance or exit could
    go, never at a corner: hallway ends, or (hallway=False) room squares."""
    spots = []
    for (cx, cy), what in sorted(level.cell.items()):
        if (what == HALL) != hallway:
            continue
        across = 0 < cx - level.x < level.w - 1      # not in a corner column
        down = 0 < cy - level.y < level.h - 1        # not in a corner row
        if cy == level.y and across:
            spots.append((cx, cy, "N"))
        if cy == level.y + level.h - 1 and across:
            spots.append((cx, cy, "S"))
        if cx == level.x and down:
            spots.append((cx, cy, "W"))
        if cx == level.x + level.w - 1 and down:
            spots.append((cx, cy, "E"))
    return spots


def make_building(seed):
    dice = SeedDice(seed)
    source = make_hideout(seed, "hideout", dice)

    # ── Which floor: ground 1 time in 10, else one of the others ──────────
    if dice.chance(BUILDING_GROUND_CHANCE):
        level = source.levels[0]
    else:
        level = dice.pick(source.levels[1:])
    want_exit = dice.chance(EXIT_CHANCE)
    strip_stairs(level)

    # ── Entrance and exit: a hallway end, else a room on the outer wall ───
    # A ground floor already has its own and keeps them.
    if not level.openings:
        halls, rooms = wall_spots(level, True), wall_spots(level, False)
        entrance = dice.pick(halls or rooms)
        level.openings.append(("entrance",) + entrance)
        if want_exit:
            others = ([spot for spot in halls if spot[2] != entrance[2]]
                      or [spot for spot in rooms if spot[2] != entrance[2]])
            level.openings.append(("exit",) + dice.pick(others))
        bump_outs(level)
    level.number = 1             # the only floor is the ground floor
    return Hideout(seed, None, [level], "building")


def make_map(seed, kind):
    """The one way in for all four buttons."""
    if kind == "complex":
        return make_dungeon_complex(seed)
    return make_building(seed) if kind == "building" else make_hideout(seed, kind)


# Ground spots for a 25% room stairwell: anywhere, except the 4 corner spots
# where neither direction has floor at both ends.
GROUND_ROOM_SPOTS = [(sx, sy) for sy in range(GROUND_H - 1) for sx in range(GROUND_W - 1)
                     if 1 <= sx <= GROUND_W - 3 or 1 <= sy <= GROUND_H - 3]


def plan_split(dice, limit, first, keep_clear):
    """
    Pick a spot and a facing for a secondary stairwell inside "limit", plus
    one straight line that will keep it in a different room from the
    stairwell "first" (the one players arrive by on this floor).
    first and keep_clear are (spot, open side) on this floor. The line never
    crosses any of their footprints, and the new spot keeps STAIR_GAP
    squares clear of them all.
    Returns (axis, line, spot, open side on this floor). The floor it leads
    to opens on the opposite side. Axis 0 = the line runs top to bottom at
    x = line; axis 1 = it runs left to right at y = line. The floor is later
    made wide enough for 3 squares on each side of the line, plus 1 more in
    case the line becomes a hallway.
    """
    lx, ly, lw, lh = limit
    span = {0: (lx, lx + lw), 1: (ly, ly + lh)}
    feet = [footprint(spot, side) for spot, side in keep_clear + [first]]
    lines = []
    for axis in (0, 1):
        lo, hi = span[axis]
        for line in range(lo + MIN_ROOM, hi - MIN_ROOM):
            # Every footprint wholly before the line, or wholly past the
            # hallway square the line may become.
            if all(f[axis + 2] <= line or f[axis] >= line + 1 for f in feet):
                lines.append((axis, line))
    dice.shuffle(lines)
    first_foot = feet[-1]
    for axis, line in lines:
        before = first_foot[axis + 2] <= line
        spots = []
        for y in range(ly, ly + lh - 1):
            for x in range(lx, lx + lw - 1):
                if not all(stairs_clear((x, y), spot) for spot, _ in keep_clear + [first]):
                    continue
                for side in "NESW":
                    here = footprint((x, y), side)
                    if not (box_holds(limit, here) and box_holds(limit, footprint((x, y), OPPOSITE[side]))):
                        continue
                    if (here[axis] >= line + 1) if before else (here[axis + 2] <= line):
                        spots.append(((x, y), side))
        if spots:
            spot, side = dice.pick(spots)
            return axis, line, spot, side
    raise RuntimeError("no room for a secondary stairwell")   # the ground is too small


def needed_box(boxes, split):
    """The smallest (left, top, right, bottom) a level can be: it must hold
    these boxes (stairwell footprints), and leave room on both sides of its
    planned line."""
    left = min(b[0] for b in boxes)
    top = min(b[1] for b in boxes)
    right = max(b[2] for b in boxes)
    bottom = max(b[3] for b in boxes)
    if split:
        axis, line = split
        if axis == 0:
            left, right = min(left, line - MIN_ROOM), max(right, line + 1 + MIN_ROOM)
        else:
            top, bottom = min(top, line - MIN_ROOM), max(bottom, line + 1 + MIN_ROOM)
    return (left, top, right, bottom)


def join_boxes(a, b):
    return (min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3]))


def build_run(dice, direction, how_many, stair, ground_open, ground_rooms):
    """Every level going up (direction 1) or down (direction -1) from ground."""
    numbers = [direction * (2 + i) for i in range(how_many)]
    if not numbers:
        return []
    ground_rect = (0, 0, GROUND_W, GROUND_H)

    # ── 1. Plan every stairwell on every level of this run ────────────────
    # plan[n] is a list of (spot, kind, link, open side). Levels 2 and -2
    # start with the main stairwell, opening opposite its ground side;
    # levels further out have none, only secondaries.
    plan = {n: [(stair, "main", None, OPPOSITE[ground_open])] if abs(n) < SECONDARY_FROM else []
            for n in numbers}
    splits = {}
    for here, further in zip(numbers, numbers[1:]):
        if abs(further) < SECONDARY_FROM:
            continue
        arrival = plan[here][-1]                  # the stairwell players arrive by
        keep_clear = [(spot, side) for spot, _, _, side in plan[here][:-1]]
        axis, line, spot, side = plan_split(dice, ground_rect, (arrival[0], arrival[3]), keep_clear)
        splits[here] = (axis, line)
        plan[here].append((spot, "secondary", (here, further), side))
        plan[further].append((spot, "secondary", (here, further), OPPOSITE[side]))

    # ── 2. The smallest box each level may be ─────────────────────────────
    # Each level fits inside the one next to it, nearer ground (above AND
    # below ground), so a level must also be big enough for every level
    # further out. Every level still sits over the main stairwell spot.
    boxes = {}
    for n in numbers:
        feet = [footprint(spot, side) for spot, _, _, side in plan[n]]
        boxes[n] = needed_box(feet + [(stair[0], stair[1], stair[0] + 2, stair[1] + 2)], splits.get(n))
    for here, further in reversed(list(zip(numbers, numbers[1:]))):
        boxes[here] = join_boxes(boxes[here], boxes[further])

    # ── 3. Size, place and build each level ───────────────────────────────
    levels = []
    limit = ground_rect
    for n in numbers:
        # Only levels with a main stairwell roll 75 / 25.
        near = abs(n) < SECONDARY_FROM
        hall_roll = near and dice.chance(HALL_STAIR_CHANCE)
        lx, ly, lw, lh = limit
        bx0, by0, bx1, by1 = boxes[n]
        w = dice.between(max(MIN_LEVEL, bx1 - bx0), lw)
        h = dice.between(max(MIN_LEVEL, by1 - by0), lh)
        xs = range(max(lx, bx1 - w), min(lx + lw - w, bx0) + 1)
        ys = range(max(ly, by1 - h), min(ly + lh - h, by0) + 1)

        # Fewer rooms on smaller levels, and always fewer than the ground level.
        most = min(MAX_ROOMS, max(1, w * h // SQUARES_PER_ROOM), max(1, ground_rooms - 1))
        target = dice.between((most + 1) // 2, most)
        if n in splits:
            target = max(target, 2)              # the stairwells need 2 rooms or more
        want_halls = target >= HALL_MIN_ROOMS

        stairs = []
        for spot, kind, link, side in plan[n]:
            stairs.append(Stair(spot, kind, link))
            stairs[-1].open = side
        others = [footprint(s.pos, s.open) for s in stairs[1:]]

        # ── The 75% hallway roll: find a spot where the pinwheel fits ─────
        layout = rect = None
        if hall_roll and want_halls:
            spots = [(x, y) for y in ys for x in xs if pinwheel_fits((x, y, w, h), stair)]
            dice.shuffle(spots)
            for x, y in spots:
                layouts = pinwheel_layouts((x, y, w, h), stair, others, need_side=stairs[0].open)
                if layouts:
                    rect, layout = (x, y, w, h), dice.pick(layouts)
                    break
        if rect is None:
            rect = (dice.pick(xs), dice.pick(ys), w, h)

        level = build_level(dice, n, rect, stairs, target, want_halls,
                            layout=layout, split=None if layout else splits.get(n))
        level.hall_roll = hall_roll
        levels.append(level)
        limit = rect                             # the next level fits inside this one
    return levels


def cut_spots(block, stairs, want_halls, hall_need):
    """
    Every spot where a block can be cut. Returns four lists of offsets:
    ("V", False) plain wall top to bottom,  ("V", True) hallway top to bottom,
    ("H", False) plain wall left to right,  ("H", True) hallway left to right.
    stairs: footprints (stairwell plus landing squares) of the stairwells
    that sit in rooms.
    hall_need: the footprint of a stairwell whose room must end up beside a
    hallway (the 25% room stairwell), or None.
    """
    x, y, w, h, hall_sides, is_root, big = block
    inside = [f for f in stairs if box_holds((x, y, w, h), f)]
    need = hall_need if hall_need in inside else None
    big_enough = is_root or big or w * h >= SIDE_HALL_MIN_AREA
    spots = {}
    for way, start, length, axis, ends, lose in (("V", x, w, 0, "NS", ("E", "W")),
                                                 ("H", y, h, 1, "WE", ("S", "N"))):
        plain = []
        for k in range(MIN_ROOM, length - MIN_ROOM + 1):
            line = start + k
            # A plain wall must not cut a stairwell or shut off its landing.
            if any(f[axis] < line < f[axis + 2] for f in inside):
                continue
            # The half that holds the 25% room stairwell must keep a hallway side.
            if need:
                keep = hall_sides - {lose[0]} if need[axis + 2] <= line else hall_sides - {lose[1]}
                if not keep:
                    continue
            plain.append(k)
        spots[(way, False)] = plain
        # A hallway must not run through a stairwell or its landing, and one
        # end of it must meet a hallway that is already there (the first one
        # is free).
        joins = is_root or ends[0] in hall_sides or ends[1] in hall_sides
        spots[(way, True)] = [k for k in range(MIN_ROOM, length - MIN_ROOM)
                              if not any(f[axis] <= start + k < f[axis + 2] for f in inside)
                              ] if want_halls and joins and big_enough else []
    return spots


def cut_block(blocks, index, way, k, with_hall, hall_strips):
    """Cut blocks[index] in two at offset k, with a hallway or a plain wall."""
    x, y, w, h, sides, _, _ = blocks[index]
    gap = 1 if with_hall else 0
    if way == "V":
        first = (x, y, k, h, (sides | {"E"}) if with_hall else (sides - {"E"}), False, False)
        second = (x + k + gap, y, w - k - gap, h,
                  (sides | {"W"}) if with_hall else (sides - {"W"}), False, False)
        if with_hall:
            hall_strips.append((x + k, y, 1, h))
    else:
        first = (x, y, w, k, (sides | {"S"}) if with_hall else (sides - {"S"}), False, False)
        second = (x, y + k + gap, w, h - k - gap,
                  (sides | {"N"}) if with_hall else (sides - {"N"}), False, False)
        if with_hall:
            hall_strips.append((x, y + k, w, 1))
    blocks[index:index + 1] = [first, second]


def middle_pick(dice, choices, length):
    """Roll twice and keep the spot nearer the middle: fewer sliver rooms."""
    return min(dice.pick(choices), dice.pick(choices), key=lambda k: abs(2 * k - length))


def build_level(dice, number, rect, stairs, room_target, want_halls,
                is_ground=False, layout=None, split=None, want_exit=False, start=None):
    level = Level(number, rect, stairs)
    level.start = start          # only used when the level has no stairwell
    level.arrival = 0            # the main stairwell, or on levels 3, 4, -3, -4
                                 # the secondary that leads in from nearer ground
    main = level.main            # None on levels 3, 4, -3, -4
    # Footprints: each stairwell plus its landing squares, kept whole while
    # cutting. (A pinwheel stairwell's footprint is never inside a block, so
    # it is simply skipped.) Every open side was fixed during planning.
    stair_spots = [footprint(s.pos, s.open) for s in stairs]
    hall_strips = []

    # ── Start: the pinwheel (75% roll) or the whole level as one block ────
    # A block is (x, y, w, h, sides that run along a hallway, whole level?,
    # may hold a hallway whatever its size?).
    if layout:
        parts, hall, open_side = layout
        blocks = [part + (sides, False, False) for part, sides in parts]
        hall_strips.append(hall)
        main.alcove = True
        main.open = open_side                    # the same side planning asked for
        hall_need = None
    else:
        blocks = [(rect[0], rect[1], rect[2], rect[3], frozenset(), True, False)]
        if want_halls:
            root = cut_spots(blocks[0], stair_spots, True, None)
            want_halls = bool(root[("V", True)] or root[("H", True)])
        # 25% roll: the main stairwell's room must touch a hallway.
        hall_need = stair_spots[0] if want_halls and main else None

    # ── Planned first cut: keeps the secondary stairwell apart ────────────
    if split:
        axis, line = split
        way = "V" if axis == 0 else "H"
        cut_block(blocks, 0, way, line - (rect[0] if axis == 0 else rect[1]), want_halls, hall_strips)

    # ── Ground pinwheel with an exit: a side hallway to a second wall ─────
    if layout and is_ground and want_exit:
        way = "V" if hall[3] == 1 else "H"
        choices = []
        for index in (0, 3):                     # blocks A and D touch the hallway
            block = blocks[index][:6] + (True,)
            spots = cut_spots(block, stair_spots, True, None)[(way, True)]
            if spots:
                choices.append((index, spots))
        index, spots = dice.pick(choices)
        block = blocks[index]
        cut_block(blocks, index, way, middle_pick(dice, spots, block[2] if way == "V" else block[3]),
                  True, hall_strips)

    # ── Cut the blocks into rooms and hallways ────────────────────────────
    while len(blocks) < room_target:
        # Which blocks can still be cut? Bigger blocks are more likely to be picked.
        open_blocks = []
        for index, block in enumerate(blocks):
            spots = cut_spots(block, stair_spots, want_halls, hall_need)
            if any(spots.values()):
                open_blocks.append((index, spots))
        if not open_blocks:
            break
        roll = dice.below(sum(blocks[i][2] * blocks[i][3] for i, _ in open_blocks))
        for index, spots in open_blocks:
            roll -= blocks[index][2] * blocks[index][3]
            if roll < 0:
                break
        x, y, w, h, sides, is_root, _ = blocks[index]

        # Cut across the long way. A near-square block rolls for it.
        if 2 * w > 3 * h:
            way = "V"
        elif 2 * h > 3 * w:
            way = "H"
        else:
            way = dice.pick("VH")
        if not (spots[(way, False)] or spots[(way, True)]):
            way = "H" if way == "V" else "V"

        with_hall = bool(spots[(way, True)]) and (
            is_root or not spots[(way, False)] or dice.chance(SIDE_HALL_CHANCE))
        cut_block(blocks, index, way, middle_pick(dice, spots[(way, with_hall)], w if way == "V" else h),
                  with_hall, hall_strips)

    # ── Fill in the grid of squares ───────────────────────────────────────
    for room_number, block in enumerate(blocks):
        x, y, w, h = block[:4]
        level.rooms.append((x, y, w, h))
        for cy in range(y, y + h):
            for cx in range(x, x + w):
                level.cell[(cx, cy)] = room_number
    for x, y, w, h in hall_strips:
        for cy in range(y, y + h):
            for cx in range(x, x + w):
                level.cell[(cx, cy)] = HALL
    if main and main.alcove:
        for c in stair_cells(main.pos):
            level.cell[c] = ALCOVE

    # ── Stairwells: closed on three sides, open on one ────────────────────
    # The open side was fixed during planning, and no cut was allowed to
    # cross a stairwell's landing, so a stairwell in a room always opens onto
    # two squares of floor in its own room.
    steps = level.all_steps()
    for s in stairs:
        if not s.alcove:
            s.room = level.cell[s.pos]

    # ── Find every wall between two different rooms (or room and hall) ────
    walls = set()
    door_spots = {}     # (room, other room or hall) -> wall pieces that could be a doorway
    hall_node = len(level.rooms)
    for cy in range(level.y, level.y + level.h):
        for cx in range(level.x, level.x + level.w):
            here = level.cell[(cx, cy)]
            for other in ((cx + 1, cy), (cx, cy + 1)):
                there = level.cell.get(other)
                if there is None or there == here:
                    continue
                edge = edge_between((cx, cy), other)
                walls.add(edge)
                # No doorway straight onto the side of the stairs.
                if (cx, cy) in steps or other in steps:
                    continue
                a = hall_node if here == HALL else here
                b = hall_node if there == HALL else there
                door_spots.setdefault((min(a, b), max(a, b)), []).append(edge)

    # A hallway stairwell has no wall on its open side.
    if main and main.alcove:
        walls -= set(stair_sides(main.pos)[main.open][0])

    # ── Doorways ──────────────────────────────────────────────────────────
    # Join everything into one connected house. Hallway doors come first,
    # then room to room, and the arrival stairwell's room last, so rooms do
    # not all open off the stairwell room. Every room beside a hallway gets
    # a hallway door, which is what gives the 25% stairwell room its door.
    arrival_room = stairs[level.arrival].room if stairs else None

    def rank(pair):
        if pair[1] == hall_node:
            return 0
        return 2 if arrival_room in pair else 1

    pairs = []
    for wanted in (0, 1, 2):
        group = [pair for pair in sorted(door_spots) if rank(pair) == wanted]
        dice.shuffle(group)
        pairs += group

    group_of = list(range(hall_node + 1))      # which connected group each room is in

    def find(n):
        while group_of[n] != n:
            n = group_of[n]
        return n

    used_corners = set()

    def add_door(pair):
        # Prefer a spot that does not touch a doorway that is already there.
        apart = [e for e in door_spots[pair]
                 if not (edge_ends(e)[0] in used_corners or edge_ends(e)[1] in used_corners)]
        edge = dice.pick(apart or door_spots[pair])
        level.doors.add(edge)
        used_corners.update(edge_ends(edge))

    spare = []
    for pair in pairs:
        a, b = find(pair[0]), find(pair[1])
        if a != b:
            group_of[a] = b
            add_door(pair)
        elif rank(pair) == 1:
            spare.append(pair)
    for pair in spare:
        if dice.chance(EXTRA_DOOR_CHANCE):
            add_door(pair)

    # ── Inner walls ───────────────────────────────────────────────────────
    level.inner = walls - level.doors
    for s in stairs:
        if s.open and not s.alcove:
            for side, (edges, _) in stair_sides(s.pos).items():
                if side != s.open:
                    level.inner.update(edges)

    # ── Entrance and exit: ground only, at the end of a hallway ───────────
    # Hallways are always 3 squares or more from a corner, so these are too.
    if is_ground:
        ends = []
        for (cx, cy), what in sorted(level.cell.items()):
            if what != HALL:
                continue
            if cy == level.y:
                ends.append((cx, cy, "N"))
            if cy == level.y + level.h - 1:
                ends.append((cx, cy, "S"))
            if cx == level.x:
                ends.append((cx, cy, "W"))
            if cx == level.x + level.w - 1:
                ends.append((cx, cy, "E"))
        entrance = dice.pick(ends)
        level.openings.append(("entrance",) + entrance)
        if want_exit:
            others = [end for end in ends if end[2] != entrance[2]]
            if others:
                level.openings.append(("exit",) + dice.pick(others))

    # ── Outer wall, with a 1 x 1 bump out at each opening ─────────────────
    left, top, right, bottom = level.x, level.y, level.x + level.w, level.y + level.h
    for cx in range(left, right):
        level.outer.update([("h", cx, top), ("h", cx, bottom)])
    for cy in range(top, bottom):
        level.outer.update([("v", left, cy), ("v", right, cy)])
    bump_outs(level)

    repair_level(level)
    return level


def bump_outs(level):
    """Open the outer wall at each entrance and exit, with a 1 x 1 bump out."""
    left, top, right, bottom = level.x, level.y, level.x + level.w, level.y + level.h
    for _, cx, cy, side in level.openings:
        if side == "N":
            level.outer.discard(("h", cx, top))
            level.outer.update([("v", cx, top - 1), ("v", cx + 1, top - 1)])
        elif side == "S":
            level.outer.discard(("h", cx, bottom))
            level.outer.update([("v", cx, bottom), ("v", cx + 1, bottom)])
        elif side == "W":
            level.outer.discard(("v", left, cy))
            level.outer.update([("h", left - 1, cy), ("h", left - 1, cy + 1)])
        else:
            level.outer.discard(("v", right, cy))
            level.outer.update([("h", right, cy), ("h", right, cy + 1)])


# ============================================================================
# CHECKER
# ============================================================================

# repair_level runs on every level as it is built. check_hideout is the full
# rule check that test mode uses.

def reached_cells(level):
    """Every square you can walk to from the stairwell players arrive by."""
    steps = level.all_steps()
    if level.stairs:
        arrival = level.stairs[level.arrival]
        start = stair_sides(arrival.pos)[arrival.open][1]
    else:
        start = [level.start]
    seen = set(start)
    todo = list(start)
    while todo:
        here = todo.pop()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            there = (here[0] + dx, here[1] + dy)
            if there in seen or there in steps or there not in level.cell:
                continue
            if level.cell[there] != level.cell[here] and edge_between(here, there) not in level.doors:
                continue
            seen.add(there)
            todo.append(there)
    return seen


def repair_level(level):
    """
    Safety net. If any square cannot be reached from the stairwell, open one
    doorway into it. One pass per room at most, so it can never loop for long.
    Returns how many doorways it had to add (the builder should leave it 0).
    """
    steps = level.all_steps()
    added = 0
    for _ in range(len(level.rooms) + 1):
        seen = reached_cells(level)
        fix = None
        for here in sorted(level.cell):
            if here in seen or here in steps:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                there = (here[0] + dx, here[1] + dy)
                if there in seen:
                    fix = edge_between(here, there)
                    break
            if fix:
                break
        if not fix:
            break
        level.doors.add(fix)
        level.inner.discard(fix)
        added += 1
    return added


def has_hall_door(level, room):
    """True if the room has a doorway straight onto a hallway."""
    for kind, x, y in level.doors:
        a = level.cell.get((x, y))
        b = level.cell.get((x - 1, y) if kind == "v" else (x, y - 1))
        if {a, b} == {room, HALL}:
            return True
    return False


def check_hideout(hideout):
    """Returns a list of broken rules. An empty list means the map is good."""
    bad = []
    ground = hideout.levels[0]
    by_number = {level.number: level for level in hideout.levels}

    # ── The stack of levels ───────────────────────────────────────────────
    numbers = [level.number for level in hideout.levels]
    ups = [n for n in numbers if n > 1]
    downs = [n for n in numbers if n < 0]
    counts = DUNGEON_LEVEL_COUNTS if hideout.kind == "dungeon" else LEVEL_COUNTS
    if len(numbers) not in counts or numbers[0] != 1:
        bad.append("level count or ground level is wrong")
    if hideout.kind == "dungeon" and ups:
        bad.append("a dungeon has a level above ground")
    if ups != list(range(2, 2 + len(ups))) or downs != list(range(-2, -2 - len(downs), -1)):
        bad.append("level numbers have a gap: %s" % numbers)
    if numbers != [1] + ups + downs:
        bad.append("levels are not in overview order")
    if (ground.x, ground.y, ground.w, ground.h) != (0, 0, GROUND_W, GROUND_H):
        bad.append("ground is not %d x %d" % (GROUND_W, GROUND_H))
    if not ground.openings or ground.openings[0][0] != "entrance":
        bad.append("ground has no entrance")

    for level in hideout.levels:
        name = "level %d: " % level.number
        # Every level fits inside the next level nearer ground, above AND below.
        if level is ground:
            inside = ground
        else:
            inside = by_number.get(level.number - (1 if level.number > 0 else -1), ground)
        if level.w < MIN_LEVEL or level.h < MIN_LEVEL:
            bad.append(name + "smaller than 4 x 4")
        if (level.x < inside.x or level.y < inside.y or level.x + level.w > inside.x + inside.w
                or level.y + level.h > inside.y + inside.h):
            bad.append(name + "sticks out past the floor it must fit inside")

        # One staircase: opposite open ends on the two floors it links.
        for s in level.stairs:
            if s.kind == "main" and level is not ground:
                if s.open != OPPOSITE[ground.main.open]:
                    bad.append(name + "main stairwell does not open opposite its ground end")
            if s.kind == "secondary" and s.link[1] == level.number:
                other = by_number.get(s.link[0])
                twin = [t for t in (other.stairs if other else []) if t.link == s.link]
                if not twin or twin[0].open != OPPOSITE[s.open]:
                    bad.append(name + "secondary stairwell does not open opposite its other end")
        if level is not ground and level.openings:
            bad.append(name + "has an entrance or exit")
        if level is not ground and len(level.rooms) > len(ground.rooms):
            bad.append(name + "has more rooms than ground")

        # ── Stairwells ────────────────────────────────────────────────────
        steps = level.all_steps()
        main = level.main
        far = abs(level.number) >= SECONDARY_FROM
        if far:
            if main or any(s.kind == "main" for s in level.stairs):
                bad.append(name + "has a main stairwell, but it should be left off")
            if not rect_holds((level.x, level.y, level.w, level.h), hideout.stair):
                bad.append(name + "does not sit over the main stairwell spot")
        elif main is None or main.pos != hideout.stair or level.stair != hideout.stair:
            bad.append(name + "main stairwell is missing or in a different spot")
        for i, a in enumerate(level.stairs):
            for b in level.stairs[i + 1:]:
                if not stairs_clear(a.pos, b.pos):
                    bad.append(name + "two stairwells touch")
        for s in level.stairs:
            cells = stair_cells(s.pos)
            values = {level.cell.get(c) for c in cells}
            if s.alcove:
                if values != {ALCOVE}:
                    bad.append(name + "hallway stairwell squares are wrong")
                if s.kind == "secondary":
                    bad.append(name + "secondary stairwell is not in a room")
            elif len(values) != 1 or level.cell.get(s.pos) in (None, HALL, ALCOVE):
                bad.append(name + "stairwell is not inside one room")
            if s.open is None:
                bad.append(name + "stairwell has no open side")
                continue
            front = stair_sides(s.pos)[s.open][1]
            want = HALL if s.alcove else s.room
            if any(level.cell.get(c) != want or c in steps for c in front):
                bad.append(name + "stairwell does not open onto floor")
            closed = [e for side, (edges, _) in stair_sides(s.pos).items()
                      if side != s.open for e in edges]
            if any(e not in level.inner and e not in level.outer for e in closed):
                bad.append(name + "stairwell has a gap in a closed side")
            if any(e in level.inner or e in level.outer for e in stair_sides(s.pos)[s.open][0]):
                bad.append(name + "a wall is drawn across a stairwell's open side")

        # 75 / 25: hallway alcove, or a room with a doorway onto a hallway.
        has_halls = any(what == HALL for what in level.cell.values())
        if main and main.alcove and not has_halls:
            bad.append(name + "hallway stairwell but no hallway")
        if main and not main.alcove and has_halls and not has_hall_door(level, main.room):
            bad.append(name + "main stairwell room has no doorway onto a hallway")

        # Secondary stairwells link the right levels, at the same spot on both.
        secondaries = [s for s in level.stairs if s.kind == "secondary"]
        step = 1 if level.number > 0 else -1
        nearer, further = level.number - step, level.number + step
        expected = []
        if far:
            expected.append((nearer, level.number))
        if level is not ground and abs(further) >= SECONDARY_FROM and further in by_number:
            expected.append((level.number, further))
        if sorted(s.link for s in secondaries) != sorted(expected):
            bad.append(name + "secondary stairwells are %s, should be %s"
                       % (sorted(s.link for s in secondaries), sorted(expected)))
        for s in secondaries:
            other = by_number.get(s.link[0] if s.link[1] == level.number else s.link[1])
            if other is None or not any(t.kind == "secondary" and t.pos == s.pos and t.link == s.link
                                        for t in other.stairs):
                bad.append(name + "secondary stairwell is not on the level it leads to")
        arrival = level.stairs[level.arrival]
        if arrival.kind != "main" and not (far and arrival.link == (nearer, level.number)):
            bad.append(name + "players arrive by the wrong stairwell")
        for s in secondaries:
            if s is not arrival and arrival.room is not None and s.room == arrival.room:
                bad.append(name + "departing stairwell is in the arrival room")

        # ── Rooms and hallways ────────────────────────────────────────────
        low = 2 if level is ground else 1
        if not low <= len(level.rooms) <= MAX_ROOMS:
            bad.append(name + "%d rooms" % len(level.rooms))
        covered = 0
        for index, (x, y, w, h) in enumerate(level.rooms):
            covered += w * h
            if w < MIN_ROOM or h < MIN_ROOM:
                bad.append(name + "room smaller than 3 x 3")
            if any(level.cell.get((cx, cy)) != index
                   for cy in range(y, y + h) for cx in range(x, x + w)):
                bad.append(name + "room %d is not a clean rectangle" % index)
        halls = [c for c, what in level.cell.items() if what == HALL]
        alcove = [c for c, what in level.cell.items() if what == ALCOVE]
        if (covered + len(halls) + len(alcove) != level.w * level.h
                or len(level.cell) != level.w * level.h):
            bad.append(name + "has leftover space")
        for cx, cy in halls:
            across = (level.cell.get((cx - 1, cy)) == HALL or level.cell.get((cx + 1, cy)) == HALL)
            along = (level.cell.get((cx, cy - 1)) == HALL or level.cell.get((cx, cy + 1)) == HALL)
            if across and along:
                # Fine at a junction, but never a 2 x 2 patch of hallway.
                for dx, dy in ((0, 0), (-1, 0), (0, -1), (-1, -1)):
                    if all(level.cell.get((cx + dx + i, cy + dy + j)) == HALL
                           for i in (0, 1) for j in (0, 1)):
                        bad.append(name + "hallway wider than 1 square")
        if len(level.rooms) > 1:
            doored = set()
            for kind, x, y in level.doors:
                a = (x, y)
                b = (x - 1, y) if kind == "v" else (x, y - 1)
                doored.update([level.cell.get(a), level.cell.get(b)])
            if any(index not in doored for index in range(len(level.rooms))):
                bad.append(name + "a room has no doorway")
        if level.doors & level.inner or level.doors & level.outer:
            bad.append(name + "a line is drawn across a doorway")
        if len(reached_cells(level)) != level.w * level.h - len(steps):
            bad.append(name + "part of the level cannot be reached from the stairwell")

        # ── Entrance and exit ─────────────────────────────────────────────
        for kind, cx, cy, side in level.openings:
            on_wall = {"N": cy == level.y, "S": cy == level.y + level.h - 1,
                       "W": cx == level.x, "E": cx == level.x + level.w - 1}[side]
            run = cx - level.x if side in "NS" else cy - level.y
            length = level.w if side in "NS" else level.h
            if level.cell.get((cx, cy)) != HALL or not on_wall or run in (0, length - 1):
                bad.append(name + kind + " is at a corner or not lined up with a hallway")
        if len(level.openings) == 2 and level.openings[0][3] == level.openings[1][3]:
            bad.append(name + "entrance and exit share a wall")
    return bad


def check_building(building):
    """The rules for a single building. An empty list means it is good."""
    bad = []
    if len(building.levels) != 1:
        return ["a single building must have exactly 1 floor"]
    level = building.levels[0]
    if level.stairs or level.main or ALCOVE in level.cell.values():
        bad.append("a stairwell is left")
    if level.w < MIN_LEVEL or level.h < MIN_LEVEL or level.w > GROUND_W or level.h > GROUND_H:
        bad.append("floor size is wrong: %d x %d" % (level.w, level.h))

    # ── Rooms: clean rectangles that, with the hallways, fill the floor ───
    covered = 0
    for index, (x, y, w, h) in enumerate(level.rooms):
        covered += w * h
        if w < MIN_ROOM or h < MIN_ROOM:
            bad.append("room smaller than 3 x 3")
        if any(level.cell.get((cx, cy)) != index for cy in range(y, y + h) for cx in range(x, x + w)):
            bad.append("room %d is not a clean rectangle" % index)
    halls = [c for c, what in level.cell.items() if what == HALL]
    if covered + len(halls) != level.w * level.h or len(level.cell) != level.w * level.h:
        bad.append("has leftover space")

    # ── No stairwell wall left: every inner wall is between two different
    # rooms, or a room and a hallway
    for edge in level.inner:
        a, b = edge_cells(edge)
        if level.cell.get(a) is None or level.cell.get(b) is None or level.cell[a] == level.cell[b]:
            bad.append("a wall is left standing inside a room or hallway")
            break
    if level.doors & level.inner or level.doors & level.outer:
        bad.append("a line is drawn across a doorway")

    # ── Entrance and exit ─────────────────────────────────────────────────
    kinds = [opening[0] for opening in level.openings]
    if kinds not in (["entrance"], ["entrance", "exit"]):
        bad.append("openings are %s" % kinds)
        return bad
    hall_ends = wall_spots(level, True)
    for index, (kind, cx, cy, side) in enumerate(level.openings):
        on_wall = {"N": cy == level.y, "S": cy == level.y + level.h - 1,
                   "W": cx == level.x, "E": cx == level.x + level.w - 1}[side]
        run = cx - level.x if side in "NS" else cy - level.y
        length = level.w if side in "NS" else level.h
        if not on_wall or run in (0, length - 1):
            bad.append(kind + " is at a corner or not on the outer wall")
        # A hallway end must be used when there is one (for the exit: one on
        # a different wall from the entrance).
        free = [spot for spot in hall_ends if index == 0 or spot[2] != level.openings[0][3]]
        if free and level.cell.get((cx, cy)) != HALL:
            bad.append(kind + " is in a room, but a hallway end was free")
    if len(level.openings) == 2 and level.openings[0][3] == level.openings[1][3]:
        bad.append("entrance and exit share a wall")

    # ── Every square can be walked to from the entrance, going only where
    # no wall line is drawn
    start = level.openings[0][1:3]
    seen, todo = {start}, [start]
    while todo:
        here = todo.pop()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            there = (here[0] + dx, here[1] + dy)
            if there in seen or there not in level.cell or edge_between(here, there) in level.inner:
                continue
            seen.add(there)
            todo.append(there)
    if len(seen) != level.w * level.h:
        bad.append("part of the building cannot be reached from the entrance")
    return bad


def fingerprint(hideout):
    """A short code that changes if anything about the map changes."""
    parts = [hideout.seed, hideout.stair]
    if hideout.kind != "hideout":            # a hideout's code has no kind in it
        parts.append(hideout.kind)
    for level in hideout.levels:
        parts += [level.number, (level.x, level.y, level.w, level.h), level.rooms,
                  sorted(level.cell.items()), sorted(level.doors), sorted(level.inner),
                  sorted(level.outer), level.openings,
                  [(s.pos, s.kind, s.link, s.open, s.alcove) for s in level.stairs]]
    return hashlib.sha256(repr(parts).encode()).hexdigest()[:16]


# ============================================================================
# RENDERER
# ============================================================================

# A "frame" says how big the picture is and where the ground level's top
# left corner goes on it: (columns, rows, x offset, y offset, header rows),
# all in whole squares. A level's own JPGs use a frame sized for that level.
# On the overview every level uses the ground level's frame, which is what
# keeps the stairwells lined up.

_fonts = {}


def get_font(size):
    # Pillow's built-in font, so the header looks the same on every computer.
    if size not in _fonts:
        _fonts[size] = ImageFont.load_default(size)
    return _fonts[size]


def header_parts(hideout, level):
    if hideout.kind == "complex":
        # One room's sheet. The seed is the seed of the whole complex.
        where = "Room %d of %d" % (level.number, len(hideout.rooms))
        return [MAP_LABELS[hideout.kind], where, "Seed " + hideout.seed]
    if hideout.kind == "building":
        where = "%d x %d squares: exterior entrance" % (level.w, level.h)
        if len(level.openings) > 1:
            where += " and an exit"
    elif level.number == 1:
        has = "has the exterior entrance"
        if len(level.openings) > 1:
            has += " and an exit"
        where = "Level 1 (ground): " + has
    else:
        where = "Level %d" % level.number
        notes = []
        ways = []
        for s in level.stairs:
            if s.kind != "secondary":
                continue
            other = s.link[0] if s.link[1] == level.number else s.link[1]
            ways.append("%s to level %d" % ("up" if other > level.number else "down", other))
        if ways:
            notes.append("secondary stairs " + " and ".join(ways))
        if notes:
            where += ": " + "; ".join(notes)
    return [MAP_LABELS[hideout.kind], where, "Seed " + hideout.seed]


def fit_header(parts, width):
    """Pick the header size for a picture this many pixels wide.
    Returns (font, lines of text, line height, rows of squares it needs)."""
    room = width - 2 * 20
    one_line = "     ".join(parts)
    size = HEADER_BIGGEST
    while size > HEADER_SMALLEST and get_font(size).getlength(one_line) > room:
        size -= 2
    font = get_font(size)
    if font.getlength(one_line) <= room:
        lines = [one_line]
    else:
        # Too wide even at the smallest size: wrap, and let the top margin grow.
        lines = [parts[0]]
        for part in parts[1:]:
            if font.getlength(lines[-1] + "     " + part) <= room:
                lines[-1] += "     " + part
            else:
                lines.append(part)
        # A part that is still too wide on its own is broken between words.
        broken = []
        for line in lines:
            words = line.split(" ")
            current = words[0]
            for word in words[1:]:
                if font.getlength(current + " " + word) <= room:
                    current += " " + word
                else:
                    broken.append(current)
                    current = word
            broken.append(current)
        lines = broken
    line_height = size * 13 // 10
    # HEADER_SPACE squares of white above the words, then enough whole squares
    # for the words plus a wall's thickness. The 1 square MARGIN below the
    # header then keeps the words more than 1 square from any line.
    rows = HEADER_SPACE + -(-(len(lines) * line_height + OUTER_WALL) // SQUARE)   # rounded up
    return font, lines, line_height, rows


def own_frame(hideout, level):
    """
    Every floor uses the ground level's frame, so every picture is the same
    size as the ground picture and every floor sits where it really is over
    the ground footprint. The header rows fit the longest header of any
    level (the top margin grows in whole squares). "level" is not used:
    every level gets the same frame.
    """
    left, top, right, bottom = hideout.levels[0].extent()
    columns = (right - left) + 2 * MARGIN
    header_rows = max(fit_header(header_parts(hideout, one), columns * SQUARE)[3]
                      for one in hideout.levels)
    rows = header_rows + (bottom - top) + 2 * MARGIN
    return (columns, rows, MARGIN - left, header_rows + MARGIN - top, header_rows)


def draw_grid(draw, width, height):
    for x in range(0, width, SQUARE):
        draw.line([(x, 0), (x, height - 1)], fill=GRID_COLOR, width=1)
    for y in range(0, height, SQUARE):
        draw.line([(0, y), (width - 1, y)], fill=GRID_COLOR, width=1)


def draw_walls(draw, edges, thickness, ox, oy, corner_count, color=BLACK):
    """Bars centered on grid lines, with square joints where walls meet."""
    r = thickness // 2
    for kind, x, y in edges:
        px, py = (x + ox) * SQUARE, (y + oy) * SQUARE
        if kind == "h":
            draw.rectangle([px, py - r, px + SQUARE, py + r], fill=color)
        else:
            draw.rectangle([px - r, py, px + r, py + SQUARE], fill=color)
    # A free wall end (the side of a doorway) is left flat, exactly on its
    # grid line. Everywhere two or more pieces meet, the joint is filled in.
    for (x, y), count in corner_count.items():
        if count >= 2:
            px, py = (x + ox) * SQUARE, (y + oy) * SQUARE
            draw.rectangle([px - r, py - r, px + r, py + r], fill=color)


def count_corners(edges):
    """How many wall pieces meet at each grid corner."""
    corners = {}
    for edge in edges:
        for corner in edge_ends(edge):
            corners[corner] = corners.get(corner, 0) + 1
    return corners


def next_floor_in(hideout, level):
    """The floor next to this one, nearer ground (ground itself for 2 and -2)."""
    step = 1 if level.number > 0 else -1
    nearer = level.number - step
    if nearer in (0, -1):
        nearer = 1
    return next(one for one in hideout.levels if one.number == nearer)


def fill_squares(draw, level, near, ox, oy):
    """
    Blue squares (overview only). Inside each grid square, leaving the grid
    line itself alone: the next floor's footprint in darker blue when that
    floor is not ground, the rest of the ground footprint in grid-line blue.
    Squares this floor covers stay white.
    """
    def covers(one, cx, cy):
        return one.x <= cx < one.x + one.w and one.y <= cy < one.y + one.h

    for cy in range(0, GROUND_H):
        for cx in range(0, GROUND_W):
            if covers(level, cx, cy):
                continue
            color = NEXT_FLOOR_FILL if near.number != 1 and covers(near, cx, cy) else GROUND_FILL
            px, py = (cx + ox) * SQUARE, (cy + oy) * SQUARE
            draw.rectangle([px + 1, py + 1, px + SQUARE - 1, py + SQUARE - 1], fill=color)


def tight_frame(level):
    """
    The frame for a saved single-level file: the level itself plus
    a 1 square margin all round, measured from its outer wall. A ground
    level's entrance and exit bump outs reach into that margin. No header
    rows: the header is shrunk to fit inside the margin.
    """
    columns = level.w + 2 * MARGIN
    rows = level.h + 2 * MARGIN
    return (columns, rows, MARGIN - level.x, MARGIN - level.y, 0)


def wrap_parts(parts, font, room):
    """Wrap the header parts into lines no wider than room pixels. Parts are
    kept apart by a wide gap on one line; a long part breaks between words."""
    lines = [""]
    for part in parts:
        for i, word in enumerate(part.split(" ")):
            gap = "     " if i == 0 else " "
            trial = lines[-1] + gap + word if lines[-1] else word
            if font.getlength(trial) <= room:
                lines[-1] = trial
            elif not lines[-1]:
                lines[-1] = word                 # one word wider than the room
            else:
                lines.append(word)
    return lines


def margin_header(hideout, level, frame):
    """
    Where the header goes on a single-level file: inside the top or bottom
    margin row, clear of the outer wall, of any entrance or exit bump out on
    that side, and of the picture edge. Tries every free stretch and keeps
    the one that allows the biggest letters (the top wins a tie).
    Returns (font, lines, line height, left x, top y).
    """
    columns, rows, ox, oy, _ = frame
    width, height = columns * SQUARE, rows * SQUARE
    gap = MARGIN_TEXT_GAP
    wall = OUTER_WALL // 2 + 1
    bands = (("N", gap, SQUARE - wall - gap),                       # top margin row
             ("S", height - SQUARE + wall + gap, height - gap))    # bottom margin row
    parts = header_parts(hideout, level)
    best = None
    for side, top, bottom in bands:
        # Free stretches of this margin row, between any bump outs on this side.
        blocked = sorted(((cx + ox) * SQUARE - wall - gap, (cx + 1 + ox) * SQUARE + wall + gap)
                         for _, cx, cy, at in level.openings if at == side)
        stretches, start = [], gap
        for left, right in blocked:
            stretches.append((start, left))
            start = right
        stretches.append((start, width - gap))
        for left, right in stretches:
            room = right - left
            for size in range(MARGIN_TEXT_BIGGEST, MARGIN_TEXT_SMALLEST - 1, -1):
                if best and size <= best[0]:
                    break
                font = get_font(size)
                lines = wrap_parts(parts, font, room)
                line_height = size * 12 // 10
                if (len(lines) * line_height <= bottom - top
                        and max(font.getlength(line) for line in lines) <= room):
                    best = (size, font, lines, line_height, left,
                            top + (bottom - top - len(lines) * line_height) // 2)
                    break
    if best is None:                             # nothing fits: smallest letters, top left
        font = get_font(MARGIN_TEXT_SMALLEST)
        lines = wrap_parts(parts, font, width - 2 * gap)
        best = (MARGIN_TEXT_SMALLEST, font, lines, MARGIN_TEXT_SMALLEST * 12 // 10, gap, gap)
    return best[1:]


def render_level(hideout, level, with_grid, frame=None, blue_squares=False, header="overview"):
    """
    One picture of one level. blue_squares is only ever True on the overview.
    header: "overview" = the full-size header in its own rows (ground frame),
            "margin"   = the small header inside the 1 square margin (saved
                         single-level files, with tight_frame),
            None       = no header (used by test mode).
    """
    columns, rows, ox, oy, header_rows = frame or own_frame(hideout, level)
    width, height = columns * SQUARE, rows * SQUARE
    image = Image.new("RGB", (width, height), WHITE)
    draw = ImageDraw.Draw(image)

    if with_grid and not GRID_OVER_WALLS:
        draw_grid(draw, width, height)

    # ── Blue squares: where this floor sits over the floors below it ──────
    if blue_squares and level.number != 1:
        fill_squares(draw, level, next_floor_in(hideout, level), ox, oy)

    # ── Inner walls ───────────────────────────────────────────────────────
    all_corners = count_corners(level.inner | level.outer)
    outer_corners = count_corners(level.outer)
    draw_walls(draw, level.inner, INNER_WALL, ox, oy, all_corners)

    # ── Main stairwell walls, as thick as the outer walls ─────────────────
    # (Secondary stairwells keep their 3 pixel inner walls, drawn above.)
    main = level.main
    if main:
        heavy = {edge for side, (edges, _) in stair_sides(main.pos).items()
                 if side != main.open for edge in edges}
        draw_walls(draw, heavy, MAIN_STAIR_WALL, ox, oy, count_corners(heavy))

    # ── Stairwells: tread lines across the direction of travel ────────────
    for s in level.stairs:
        left, top = (s.pos[0] + ox) * SQUARE, (s.pos[1] + oy) * SQUARE
        for offset in range(STEP_GAP, 2 * SQUARE, STEP_GAP):
            if s.open in "NS":
                draw.line([(left, top + offset), (left + 2 * SQUARE, top + offset)], fill=BLACK, width=1)
            else:
                draw.line([(left + offset, top), (left + offset, top + 2 * SQUARE)], fill=BLACK, width=1)

    # ── Outer wall, drawn last so it covers the ends of inner walls ───────
    draw_walls(draw, level.outer, OUTER_WALL, ox, oy, outer_corners)

    if with_grid and GRID_OVER_WALLS:
        draw_grid(draw, width, height)

    # ── Header ────────────────────────────────────────────────────────────
    if header == "overview":
        # 1 square of white above it, 1 square clear of any line.
        font, lines, line_height, _ = fit_header(header_parts(hideout, level), width)
        left, text_top = 20, HEADER_SPACE * SQUARE
    elif header == "margin":
        # Small, inside the 1 square margin of a saved single-level file.
        font, lines, line_height, left, text_top = margin_header(
            hideout, level, (columns, rows, ox, oy, header_rows))
    else:
        return image
    for i, line in enumerate(lines):
        draw.text((left, text_top + i * line_height), line, fill=BLACK, font=font)
    return image


def render_overview(hideout):
    """All levels on one sheet, grid version, ground at the top left.
    A hideout is 2 floors across, a small dungeon 3 (landscape); both are
    2 rows. A single building has no overview: this gives its grid picture
    instead, which is what the window shows. A dungeon complex gives its own
    overview of the whole complex."""
    if hideout.kind == "complex":
        return render_complex_overview(hideout, rock_grid=True)
    ground = hideout.levels[0]
    if hideout.kind == "building":
        return render_level(hideout, ground, True, tight_frame(ground), header="margin")
    across = OVERVIEW_ACROSS[hideout.kind]
    frame = own_frame(hideout, ground)
    width, height = frame[0] * SQUARE, frame[1] * SQUARE
    sheet = Image.new("RGB", (across * width, 2 * height), WHITE)
    for index, level in enumerate(hideout.levels):
        picture = render_level(hideout, level, True, frame, blue_squares=True)
        sheet.paste(picture, ((index % across) * width, (index // across) * height))
    return sheet


def save_jpg(image, path):
    image.save(path, "JPEG", quality=JPG_QUALITY, subsampling=0)


def clean_name(name):
    """Returns the name if it can be a folder name, or "" if it cannot."""
    name = (name or "").strip()
    if not name or name.startswith(".") or any(ch in name for ch in '/\\:*?"<>|'):
        return ""
    return name


def save_hideout(hideout, name, overview=None):
    """Makes the folder and writes every JPG into it. Returns the folder."""
    if hideout.kind == "complex":
        return save_dungeon_complex(hideout, name, overview)
    folder = os.path.join(SAVE_FOLDER, name)
    os.makedirs(folder)          # stops with FileExistsError if the name is taken
    if hideout.kind == "building":
        # One floor: 2 files, no level number in the name and no overview.
        level = hideout.levels[0]
        for with_grid, word in ((False, "walls"), (True, "grid")):
            picture = render_level(hideout, level, with_grid, tight_frame(level), header="margin")
            save_jpg(picture, os.path.join(folder, "%s_%s.jpg" % (name, word)))
        return folder
    for level in hideout.levels:
        # Single-level files: cropped to a 1 square margin, small header.
        frame = tight_frame(level)
        for with_grid, word in ((False, "walls"), (True, "grid")):
            picture = render_level(hideout, level, with_grid, frame, header="margin")
            save_jpg(picture, os.path.join(folder, "%s_level_%d_%s.jpg" % (name, level.number, word)))
    save_jpg(overview or render_overview(hideout), os.path.join(folder, name + "_overview.jpg"))
    return folder


# ============================================================================
# DUNGEON COMPLEX: DATA MODEL
# ============================================================================

# One big complex on a single level. Squares are named by (x, y), counted
# from the top left square of the complex, which is (0, 0). Wall pieces are
# named the same way as on the other maps.

FOUR_WAYS = ((1, 0), (-1, 0), (0, 1), (0, -1))
SIDE_WORDS = {"N": "north", "E": "east", "S": "south", "W": "west"}


class ComplexRoom:
    def __init__(self, number, w, h):
        self.number = number     # 1, 2, 3 ...
        self.x = self.y = 0      # top left square, filled in once the rooms are packed
        self.w, self.h = w, h
        self.doors = 0           # how many doorways it has
        self.door_list = []      # (square inside, square outside, wall piece) of each doorway

    def cells(self):
        return [(cx, cy) for cy in range(self.y, self.y + self.h)
                for cx in range(self.x, self.x + self.w)]

    def centre2(self):
        """The centre, doubled so it stays a whole number."""
        return 2 * self.x + self.w, 2 * self.y + self.h


class DungeonComplex:
    def __init__(self, seed, width, height):
        self.kind = "complex"
        self.seed = seed
        self.W, self.H = width, height
        self.rooms = []          # ComplexRoom objects; room number n is rooms[n - 1]
        self.room_at = {}        # square -> room number, for every room square
        self.hall = set()        # corridor squares
        self.doors = set()       # wall pieces left open as doorways
        self.walls = set()       # wall pieces to draw
        self.links = []          # every corridor made between two rooms:
                                 # (room, other room, its doorway, the other's doorway,
                                 #  squares of corridor between them)
        self.openings = []       # ("entrance" or "exit", x, y, side)
        self.opening_doors = {}  # "entrance" or "exit" -> (room, doorway, squares of corridor)
        self.shortcut = None     # a complex with no exit: (deep room, its doorway,
                                 #  room it leads back to, that room's doorway,
                                 #  squares of corridor)
        self.chambers = []       # one Level per room: what that room's printed sheet shows


# ============================================================================
# DUNGEON COMPLEX: GENERATOR
# ============================================================================

# How a complex is made, straight from the seed with no try-again loops:
#   1. Roll the room count (smaller counts are likelier), then the size
#      of every room.
#   2. Pack the rooms. Each room is put in a box with 1 free square all
#      round it, and the boxes are paired up again and again, side by side
#      or one above the other, aiming for a wide screen shape. The first few
#      pairings leave a strip of bare rock, which gathers the rooms into
#      clusters.
#   3. Cut the entrance (and maybe an exit).
#   4. Join the rooms: every pairing gets one corridor between the two
#      nearest rooms on either side of it, which joins the whole complex.
#      A few more corridors between near neighbours make loops.
#   5. No exit: cut the shortcut.
#   6. Draw the walls, then build the inside of every room.

class PackBox:
    """A box holding one room (with 1 free square all round it), or two
    smaller boxes packed together."""

    def __init__(self, w, h, room=None):
        self.w, self.h = w, h
        self.x = self.y = 0      # top left corner, filled in once everything is packed
        self.kids = None         # the two boxes packed together
        self.offsets = None      # where each of them sits inside this box
        self.room = room         # the room, for a box that holds one


def pack_boxes(dice, boxes, shape=None, depth=0):
    """Pack a list of boxes into one box that is near `shape` (width, height).
    The list is split in two near the middle, and the two halves are packed
    and put side by side (a wide shape) or one above the other (a tall
    shape). Each half is aimed at the shape that makes the pair come out
    right: half as wide when side by side, half as tall when stacked."""
    if len(boxes) == 1:
        return boxes[0]
    shape = shape or COMPLEX_ASPECT
    n = len(boxes)
    low = max(1, n * 2 // 5)
    cut = dice.between(low, min(n - 1, max(low, (n * 3 + 4) // 5)))
    wide, tall = shape
    # A shape that is clearly wide goes side by side and one that is clearly
    # tall is stacked. A near-square shape rolls for it.
    if 4 * wide > 5 * tall:
        across = True
    elif 4 * tall > 5 * wide:
        across = False
    else:
        across = dice.chance((1, 2))
    half = (wide, 2 * tall) if across else (2 * wide, tall)
    a = pack_boxes(dice, boxes[:cut], half, depth + 1)
    b = pack_boxes(dice, boxes[cut:], half, depth + 1)
    # The first few pairings leave a strip of bare rock between the halves.
    gap = COMPLEX_CLUSTER_GAP if depth < COMPLEX_CLUSTER_DEPTH else 0
    if across:
        box = PackBox(a.w + gap + b.w, max(a.h, b.h))
        box.offsets = ((0, dice.between(0, box.h - a.h)), (a.w + gap, dice.between(0, box.h - b.h)))
    else:
        box = PackBox(max(a.w, b.w), a.h + gap + b.h)
        box.offsets = ((dice.between(0, box.w - a.w), 0), (dice.between(0, box.w - b.w), a.h + gap))
    box.kids = (a, b)
    return box


def place_boxes(box, x, y):
    """Fix the position of every box and every room inside this one."""
    box.x, box.y = x, y
    if box.kids is None:
        box.room.x, box.room.y = x + 1, y + 1
        return
    for kid, (ox, oy) in zip(box.kids, box.offsets):
        place_boxes(kid, x + ox, y + oy)


def rooms_under(box):
    if box.kids is None:
        return [box.room]
    return rooms_under(box.kids[0]) + rooms_under(box.kids[1])


def room_distance(a, b):
    (ax, ay), (bx, by) = a.centre2(), b.centre2()
    return abs(ax - bx) + abs(ay - by)


def tree_links(box, links):
    """One corridor for every pairing: between the two nearest rooms on either side."""
    if box.kids is None:
        return
    for kid in box.kids:
        tree_links(kid, links)
    best = min(((room_distance(a, b), a.number, b.number)
                for a in rooms_under(box.kids[0]) for b in rooms_under(box.kids[1])))
    links.append((best[1], best[2]))


def pick_door(dice, room, other):
    """A doorway on the side of `room` that faces `other`. Returns the square
    inside, the corridor square outside, and the wall piece between them."""
    gap_x = max(other.x - (room.x + room.w), room.x - (other.x + other.w))
    gap_y = max(other.y - (room.y + room.h), room.y - (other.y + other.h))
    (rx, ry), (ox, oy) = room.centre2(), other.centre2()
    if gap_x >= gap_y:
        side = "E" if ox > rx else "W"
    else:
        side = "S" if oy > ry else "N"
    if side in "EW":
        x = room.x + room.w - 1 if side == "E" else room.x
        spots = [(x, y) for y in range(room.y, room.y + room.h)]
        near = lambda c: abs(2 * c[1] + 1 - oy)
    else:
        y = room.y + room.h - 1 if side == "S" else room.y
        spots = [(x, y) for x in range(room.x, room.x + room.w)]
        near = lambda c: abs(2 * c[0] + 1 - ox)
    inside = min(dice.pick(spots), dice.pick(spots), key=near)
    dx, dy = SIDE_STEP[side]
    outside = (inside[0] + dx, inside[1] + dy)
    return inside, outside, edge_between(inside, outside)


def door_for(dice, room, other):
    """The doorway room uses for a corridor to `other`. A room that has
    COMPLEX_MAX_DOORS doorways already uses the one nearest to `other`: its
    corridor then branches off from the corridors outside that doorway."""
    if len(room.door_list) >= COMPLEX_MAX_DOORS:
        ox, oy = other.centre2()
        return min(room.door_list, key=lambda d: abs(2 * d[1][0] + 1 - ox) + abs(2 * d[1][1] + 1 - oy))
    door = pick_door(dice, room, other)
    if door not in room.door_list:
        room.door_list.append(door)
    return door


def route_corridor(dungeon, start, goal, hall_cost=HALL_COST):
    """The cheapest lane of squares from start to goal that goes round every
    room (A* search). Bends cost extra, corridors that are already there are
    cheap (unless hall_cost says otherwise), and squares right beside one
    are dear."""
    width, height = dungeon.W, dungeon.H
    hall, room_at = dungeon.hall, dungeon.room_at
    queue = [(0.0, 0.0, start, -1)]
    best = {(start, -1): 0.0}
    came = {}
    while queue:
        _, g, cell, way = heapq.heappop(queue)
        if g > best.get((cell, way), 1e18):
            continue
        if cell == goal:
            lane = [cell]
            key = (cell, way)
            while key in came:
                key = came[key]
                lane.append(key[0])
            return lane
        for next_way, (dx, dy) in enumerate(FOUR_WAYS):
            n = (cell[0] + dx, cell[1] + dy)
            if not (0 <= n[0] < width and 0 <= n[1] < height) or n in room_at:
                continue
            if n in hall:
                step = hall_cost
            elif any((n[0] + ex, n[1] + ey) in hall for ex, ey in FOUR_WAYS):
                step = NEAR_HALL_COST
            else:
                step = STEP_COST
            if way != -1 and next_way != way:
                step += TURN_COST
            new_g = g + step
            key = (n, next_way)
            if new_g < best.get(key, 1e18):
                best[key] = new_g
                came[key] = (cell, way)
                heapq.heappush(queue, (new_g + abs(n[0] - goal[0]) + abs(n[1] - goal[1]),
                                       new_g, n, next_way))
    raise RuntimeError("no corridor could be found")      # cannot happen: every room has a ring of free squares


def join_rooms(dice, dungeon, a, b):
    """A corridor from a doorway in room a to a doorway in room b."""
    inside_a, outside_a, door_a = door_for(dice, a, b)
    inside_b, outside_b, door_b = door_for(dice, b, a)
    lane = route_corridor(dungeon, outside_a, outside_b)
    dungeon.hall.update(lane)
    dungeon.doors.update((door_a, door_b))
    dungeon.links.append((a.number, b.number, door_a, door_b, len(lane)))


def make_dungeon_complex(seed):
    dice = SeedDice(seed)
    count = roll_room_count(dice)

    # ── Every room's size: any width and height in the ranges ─────────────
    rooms = [ComplexRoom(number, dice.between(*COMPLEX_ROOM_WIDTH), dice.between(*COMPLEX_ROOM_HEIGHT))
             for number in range(1, count + 1)]

    # ── Pack the rooms, each in a box 1 square bigger on every side ───────
    root = pack_boxes(dice, [PackBox(r.w + 2, r.h + 2, r) for r in rooms])
    place_boxes(root, 0, 0)
    dungeon = DungeonComplex(seed, root.w, root.h)
    dungeon.rooms = rooms
    for room in rooms:
        for c in room.cells():
            dungeon.room_at[c] = room.number

    # ── Entrance, and maybe an exit, on different sides. These come first, so
    # their doorways count towards each room's COMPLEX_MAX_DOORS ──────────
    sides = ["N", "E", "S", "W"]
    dice.shuffle(sides)
    cut_opening(dice, dungeon, "entrance", sides[0])
    if dice.chance(COMPLEX_EXIT_CHANCE):
        cut_opening(dice, dungeon, "exit", sides[1])

    # ── Corridors: every pairing first, then a few loops ──────────────────
    links = []
    tree_links(root, links)
    for a, b in links:
        join_rooms(dice, dungeon, dungeon.rooms[a - 1], dungeon.rooms[b - 1])
    joined = {(min(a, b), max(a, b)) for a, b in links}
    for room in dungeon.rooms:
        near = sorted((r for r in dungeon.rooms if r is not room),
                      key=lambda r: (room_distance(room, r), r.number))[:COMPLEX_EXTRA_LINK_NEIGHBORS]
        for other in near:
            pair = (min(room.number, other.number), max(room.number, other.number))
            if pair not in joined and dice.chance(COMPLEX_EXTRA_LINK_CHANCE):
                joined.add(pair)
                join_rooms(dice, dungeon, dungeon.rooms[pair[0] - 1], dungeon.rooms[pair[1] - 1])

    # ── No exit: a shortcut from deep inside back near the entrance ──────
    if "exit" not in dungeon.opening_doors:
        cut_shortcut(dice, dungeon)

    build_complex_walls(dungeon)
    count_complex_doors(dungeon)
    dungeon.chambers = [make_chamber(dice, dungeon, room) for room in dungeon.rooms]
    return dungeon


def room_count_weights():
    """(room count, weight) for every count allowed. Each weight is
    1 / (count to the COMPLEX_ROOM_FALLOFF power), kept as a whole number so
    a seed rolls the same count on every computer."""
    low, high = COMPLEX_ROOM_COUNT
    return [(n, 10 ** 15 // n ** int(COMPLEX_ROOM_FALLOFF)) for n in range(low, high + 1)]


def roll_room_count(dice):
    """One room count, smaller counts likelier (one roll of the dice)."""
    weights = room_count_weights()
    roll = dice.below(sum(w for _, w in weights))
    for n, w in weights:
        roll -= w
        if roll < 0:
            return n
    return weights[-1][0]


def cut_opening(dice, dungeon, kind, side):
    """A straight corridor from the room nearest one side of the complex out
    to that side. The room nearest a side always has a clear lane, because
    no other room is further out."""
    if side in "EW":
        pick = (min if side == "W" else max)(dungeon.rooms, key=lambda r: (r.x if side == "W" else r.x + r.w, r.number))
        y = dice.between(pick.y, pick.y + pick.h - 1)
        x = pick.x if side == "W" else pick.x + pick.w - 1
        inside = (x, y)
        lane = ([(cx, y) for cx in range(0, pick.x)] if side == "W"
                else [(cx, y) for cx in range(pick.x + pick.w, dungeon.W)])
        spot = (0, y) if side == "W" else (dungeon.W - 1, y)
    else:
        pick = (min if side == "N" else max)(dungeon.rooms, key=lambda r: (r.y if side == "N" else r.y + r.h, r.number))
        x = dice.between(pick.x, pick.x + pick.w - 1)
        y = pick.y if side == "N" else pick.y + pick.h - 1
        inside = (x, y)
        lane = ([(x, cy) for cy in range(0, pick.y)] if side == "N"
                else [(x, cy) for cy in range(pick.y + pick.h, dungeon.H)])
        spot = (x, 0) if side == "N" else (x, dungeon.H - 1)
    dx, dy = SIDE_STEP[side]
    dungeon.hall.update(lane)
    outside = (inside[0] + dx, inside[1] + dy)
    door = edge_between(inside, outside)
    dungeon.doors.add(door)
    pick.door_list.append((inside, outside, door))
    dungeon.openings.append((kind, spot[0], spot[1], side))
    dungeon.opening_doors[kind] = (pick.number, door, len(lane))


def cut_shortcut(dice, dungeon):
    """A corridor from the deepest room (the most corridors away from the
    entrance room; the furthest away of those if there is a tie) back to a
    room picked at random from those SHORTCUT_TO_STEPS corridors from the
    entrance room, and at least 2 corridors nearer than the deep room.
    Each end uses a new doorway if its room has fewer than
    COMPLEX_MAX_DOORS, else the doorway nearest the other room. Existing
    corridors are dear for it, so it mostly makes its own way back.
    "Corridors from the entrance" counts corridors as they were made
    (room_steps), not the junctions where corridors later meet."""
    steps, _ = room_steps(dungeon)
    entrance_room = dungeon.rooms[dungeon.opening_doors["entrance"][0] - 1]
    deep = max(dungeon.rooms, key=lambda r: (steps.get(r.number, 0),
                                             room_distance(r, entrance_room), -r.number))
    depth = steps[deep.number]
    low, high = SHORTCUT_TO_STEPS
    choices = [r for r in dungeon.rooms if low <= steps.get(r.number, 0) <= min(high, depth - 2)]
    # A complex too shallow for that (none was found in test runs) takes
    # the rooms between the entrance and the deep room instead.
    choices = choices or [r for r in dungeon.rooms if 1 <= steps.get(r.number, 0) < depth]
    # Keep the rooms where the shortcut really saves walking: the normal
    # way there from the deep room is at least SHORTCUT_SAVING times the
    # straight distance across the gap between the two rooms.
    walked = walk_from(dungeon, deep)
    worth = [r for r in choices
             if min(walked.get(c, 1 << 30) for c in r.cells()) >= SHORTCUT_SAVING * (rooms_gap(deep, r) + 2)]
    target = dice.pick(worth or choices)
    inside, outside, door = door_for(dice, deep, target)
    target_inside, target_outside, target_door = door_for(dice, target, deep)
    lane = route_corridor(dungeon, outside, target_outside, hall_cost=SHORTCUT_HALL_COST)
    dungeon.hall.update(lane)
    dungeon.doors.update((door, target_door))
    dungeon.shortcut = (deep.number, door, target.number, target_door, len(lane))


def rooms_gap(a, b):
    """Squares across the gap between two rooms, straight across and down."""
    gap_x = max(0, b.x - (a.x + a.w), a.x - (b.x + b.w))
    gap_y = max(0, b.y - (a.y + a.h), a.y - (b.y + b.h))
    return gap_x + gap_y


def walk_from(dungeon, room):
    """How many squares it takes to walk from the room to every square of the
    complex, through doorways and corridors only."""
    far = {c: 0 for c in room.cells()}
    todo = list(far)
    room_at, hall, doors = dungeon.room_at, dungeon.hall, dungeon.doors
    for here in todo:
        for dx, dy in FOUR_WAYS:
            there = (here[0] + dx, here[1] + dy)
            if there in far or (there not in room_at and there not in hall):
                continue
            if (here in room_at) != (there in room_at) and edge_between(here, there) not in doors:
                continue
            far[there] = far[here] + 1
            todo.append(there)
    return far


def opening_edge(dungeon, spot, side):
    """The wall piece on the outside of the complex at an entrance or exit."""
    x, y = spot
    return {"N": ("h", x, 0), "S": ("h", x, dungeon.H),
            "W": ("v", 0, y), "E": ("v", dungeon.W, y)}[side]


def build_complex_walls(dungeon):
    """Every wall piece: round every room and corridor, except doorways."""
    floor = set(dungeon.room_at) | dungeon.hall
    for cell in floor:
        for dx, dy in FOUR_WAYS:
            n = (cell[0] + dx, cell[1] + dy)
            if n not in floor:
                dungeon.walls.add(edge_between(cell, n))
            elif (cell in dungeon.hall) != (n in dungeon.hall):
                dungeon.walls.add(edge_between(cell, n))
    dungeon.walls -= dungeon.doors
    for _, x, y, side in dungeon.openings:
        dungeon.walls.discard(opening_edge(dungeon, (x, y), side))


def count_complex_doors(dungeon):
    for kind, x, y in dungeon.doors:
        for cell in ((x, y), (x - 1, y) if kind == "v" else (x, y - 1)):
            if cell in dungeon.room_at:
                dungeon.rooms[dungeon.room_at[cell] - 1].doors += 1


# ── The inside of every room, and its sheet ─────────────────────────────
# Each room of the complex is built as a one-floor level by the same
# builder as every other map: cut into rooms of 3 x 3 or more and
# hallways 1 square wide, with doorways joining every part, sometimes a
# second way round, and side hallways in bigger blocks.
#
# When the room gets a hallway and one of its doorways lines up with a
# spot where a hallway can run, the first hallway is cut through that
# doorway, so the corridor from outside leads straight into it.
#
# Each doorway to a corridor is an opening in the outer wall with a 1 x 1
# bump out, where the corridor starts. The sheet is drawn by the same
# renderer as every other map: a 7 pixel outer wall, 3 pixel inner walls,
# and a 1 square margin with the small header in it.

def make_chamber(dice, dungeon, room):
    rect = (room.x, room.y, room.w, room.h)

    # ── How many inner rooms: fewer in smaller rooms, never fewer than 2 ──
    most = min(MAX_ROOMS, max(COMPLEX_INNER_ROOMS_LEAST, room.w * room.h // SQUARES_PER_ROOM))
    target = dice.between(max(COMPLEX_INNER_ROOMS_LEAST, (most + 1) // 2), most)
    want_halls = target >= HALL_MIN_ROOMS

    # ── The first hallway: through a doorway when one lines up ────────────
    split = None
    if want_halls:
        lines = []
        for inside, outside, _ in room.door_list:
            # A doorway in the north or south wall: a hallway top to bottom.
            axis = 0 if inside[0] == outside[0] else 1
            line = inside[axis]
            start, length = (room.x, room.w) if axis == 0 else (room.y, room.h)
            if MIN_ROOM <= line - start < length - MIN_ROOM:
                lines.append((axis, line))
        if lines:
            split = dice.pick(lines)

    # ── Rooms, hallways, doorways and walls, as on every other map ────────
    first_door = room.door_list[0][0]
    chamber = build_level(dice, room.number, rect, [], target, want_halls,
                          split=split, start=first_door)
    chamber.hall_through_door = split is not None

    # ── Doorways to the corridors: openings in the outer wall ─────────────
    kinds = {door: kind for kind, (number, door, _) in dungeon.opening_doors.items()
             if number == room.number}
    for inside, outside, door in room.door_list:
        side = STEP_SIDE[(outside[0] - inside[0], outside[1] - inside[1])]
        chamber.openings.append((kinds.get(door, "doorway"), inside[0], inside[1], side))
    bump_outs(chamber)
    return chamber


# ============================================================================
# DUNGEON COMPLEX: CHECKER
# ============================================================================

def check_dungeon_complex(dungeon):
    """Returns a list of broken rules. An empty list means the complex is good."""
    bad = []
    low, high = COMPLEX_ROOM_COUNT
    rooms = dungeon.rooms
    if not low <= len(rooms) <= high:
        bad.append("room count %d is outside %d to %d" % (len(rooms), low, high))
    if sum(r.w * r.h for r in rooms) != len(dungeon.room_at):
        bad.append("two rooms overlap")
    for r in rooms:
        if r.x < 1 or r.y < 1 or r.x + r.w > dungeon.W - 1 or r.y + r.h > dungeon.H - 1:
            bad.append("room %d is not 1 square clear of the edge" % r.number)
        if not (COMPLEX_ROOM_WIDTH[0] <= r.w <= COMPLEX_ROOM_WIDTH[1] and COMPLEX_ROOM_HEIGHT[0] <= r.h <= COMPLEX_ROOM_HEIGHT[1]):
            bad.append("room %d is outside the room size ranges" % r.number)
        if r.doors == 0:
            bad.append("room %d has no doorway" % r.number)
        if r.doors > COMPLEX_MAX_DOORS:
            bad.append("room %d has %d doorways" % (r.number, r.doors))
    for c in dungeon.hall:
        if c in dungeon.room_at:
            bad.append("a corridor runs through room %d" % dungeon.room_at[c])
            break

    # ── Each room's sheet matches the room ────────────────────────────────
    if len(dungeon.chambers) != len(rooms):
        bad.append("there is not one sheet for every room")
    for r, chamber in zip(rooms, dungeon.chambers):
        if (chamber.x, chamber.y, chamber.w, chamber.h) != (r.x, r.y, r.w, r.h):
            bad.append("room %d sheet is the wrong size" % r.number)
        if len(chamber.openings) != r.doors:
            bad.append("room %d sheet shows %d doorways, the room has %d"
                       % (r.number, len(chamber.openings), r.doors))
        for _, cx, cy, side in chamber.openings:
            dx, dy = SIDE_STEP[side]
            door = edge_between((cx, cy), (cx + dx, cy + dy))
            if door not in dungeon.doors or door in chamber.outer:
                bad.append("room %d sheet has a doorway that is not in the complex" % r.number)
        if chamber.stairs:
            bad.append("room %d has a stairwell" % r.number)
        bad += ["room %d: %s" % (r.number, text) for text in check_chamber(chamber)]

    if not dungeon.openings or dungeon.openings[0][0] != "entrance":
        bad.append("no entrance")
        return bad
    # Walk from the entrance through every gap in the walls.
    floor = set(dungeon.room_at) | dungeon.hall
    start = (dungeon.openings[0][1], dungeon.openings[0][2])
    seen, todo = {start}, [start]
    while todo:
        here = todo.pop()
        for dx, dy in FOUR_WAYS:
            there = (here[0] + dx, here[1] + dy)
            if there in seen or there not in floor:
                continue
            edge = edge_between(here, there)
            if edge in dungeon.walls:
                continue
            seen.add(there)
            todo.append(there)
    if len(seen) != len(floor):
        bad.append("%d squares cannot be reached from the entrance" % (len(floor) - len(seen)))
    steps, _ = room_steps(dungeon)
    if len(steps) != len(rooms):
        bad.append("the room key cannot reach every room from the entrance")

    # ── An exit or a shortcut, never both and never neither ───────────────
    has_exit = "exit" in dungeon.opening_doors
    if has_exit == bool(dungeon.shortcut):
        bad.append("has %s" % ("an exit and a shortcut" if has_exit else "no exit and no shortcut"))
    if dungeon.shortcut:
        deep, deep_door, target, target_door, length = dungeon.shortcut
        if steps.get(deep, 0) != max(steps.values()):
            bad.append("the shortcut does not start from the deepest room")
        low, high = SHORTCUT_TO_STEPS
        if not low <= steps.get(target, 0) <= high:
            bad.append("the shortcut ends %d corridors from the entrance" % steps.get(target, 0))
        if steps.get(target, 0) > steps.get(deep, 0) - 2:
            bad.append("the shortcut does not skip at least one room")
        if deep_door not in dungeon.doors or target_door not in dungeon.doors:
            bad.append("the shortcut doorways are wrong")
        # Walk the corridors from outside the deep room's doorway: the
        # other room's doorway is reached in no more squares than the shortcut.
        room = rooms[deep - 1]
        begin = next(o for i, o, d in room.door_list if d == deep_door)
        goal = next(o for i, o, d in rooms[target - 1].door_list if d == target_door)
        far, todo = {begin: 1}, [begin]
        for here in todo:
            for dx, dy in FOUR_WAYS:
                there = (here[0] + dx, here[1] + dy)
                if there in dungeon.hall and there not in far:
                    far[there] = far[here] + 1
                    todo.append(there)
        if far.get(goal, length + 1) > length:
            bad.append("the shortcut does not reach the room it leads back to")
    return bad


def check_chamber(chamber):
    """The rules for the inside of one room of the complex."""
    bad = []

    # ── Inner rooms: clean rectangles that, with the hallways, fill it ────
    covered = 0
    for index, (x, y, w, h) in enumerate(chamber.rooms):
        covered += w * h
        if w < MIN_ROOM or h < MIN_ROOM:
            bad.append("inner room smaller than 3 x 3")
        if any(chamber.cell.get((cx, cy)) != index for cy in range(y, y + h) for cx in range(x, x + w)):
            bad.append("inner room %d is not a clean rectangle" % index)
    halls = [c for c, what in chamber.cell.items() if what == HALL]
    if covered + len(halls) != chamber.w * chamber.h or len(chamber.cell) != chamber.w * chamber.h:
        bad.append("has leftover space")
    for cx, cy in halls:
        for dx, dy in ((0, 0), (-1, 0), (0, -1), (-1, -1)):
            if all(chamber.cell.get((cx + dx + i, cy + dy + j)) == HALL for i in (0, 1) for j in (0, 1)):
                bad.append("hallway wider than 1 square")
    if len(chamber.rooms) > MAX_ROOMS:
        bad.append("%d inner rooms" % len(chamber.rooms))

    # ── Doorways: every inner room has one, and no line is drawn across one
    if len(chamber.rooms) > 1:
        doored = set()
        for edge in chamber.doors:
            doored.update(chamber.cell.get(c) for c in edge_cells(edge))
        if any(index not in doored for index in range(len(chamber.rooms))):
            bad.append("an inner room has no doorway")
    if chamber.doors & chamber.inner or chamber.doors & chamber.outer:
        bad.append("a line is drawn across a doorway")
    for kind, cx, cy, side in chamber.openings:
        if (cx, cy) not in chamber.cell:
            bad.append("a doorway to a corridor does not open into the room")

    # ── Every square can be walked to ─────────────────────────────────────
    if len(reached_cells(chamber)) != chamber.w * chamber.h:
        bad.append("part of the room cannot be reached")
    return bad


def complex_fingerprint(dungeon):
    """A short code that changes if anything about the complex changes."""
    parts = [dungeon.seed, dungeon.kind, dungeon.W, dungeon.H,
             [(r.x, r.y, r.w, r.h, r.door_list) for r in dungeon.rooms],
             sorted(dungeon.hall), sorted(dungeon.doors), sorted(dungeon.walls),
             dungeon.links, dungeon.openings,
             [(c.rooms, sorted(c.cell.items()), sorted(c.doors), sorted(c.inner), sorted(c.outer),
               c.openings) for c in dungeon.chambers]]
    return hashlib.sha256(repr(parts).encode()).hexdigest()[:16]


# ============================================================================
# DUNGEON COMPLEX: OVERVIEW, SHEETS AND ROOM KEY
# ============================================================================

def render_complex_overview(dungeon, with_grid=False, rock_grid=False):
    """The whole complex on one picture: white paper, black walls, every
    room numbered. with_grid adds the grid, on the floors only.
    rock_grid puts the grid on the bare rock round the complex instead,
    and keeps every room and corridor plain white (the window preview and
    the saved <name>_overview.jpg)."""
    px = COMPLEX_SQUARE
    left, top = COMPLEX_MARGIN * px, COMPLEX_MARGIN_TOP * px
    width = (dungeon.W + 2 * COMPLEX_MARGIN) * px
    height = (dungeon.H + COMPLEX_MARGIN_TOP + COMPLEX_MARGIN) * px
    image = Image.new("RGB", (width, height), WHITE)
    draw = ImageDraw.Draw(image)

    def box(x, y, w=1, h=1):
        return [left + x * px, top + y * px, left + (x + w) * px - 1, top + (y + h) * px - 1]

    # ── Grid, on the floors only ──────────────────────────────────────────
    if with_grid:
        mask = Image.new("L", (width, height), 0)        # where the floor is
        mask_draw = ImageDraw.Draw(mask)
        for cell in dungeon.hall:
            mask_draw.rectangle(box(*cell), fill=255)
        for r in dungeon.rooms:
            mask_draw.rectangle(box(r.x, r.y, r.w, r.h), fill=255)
        lined = image.copy()
        lined_draw = ImageDraw.Draw(lined)
        for gx in range(dungeon.W + 1):
            lined_draw.line([left + gx * px, top, left + gx * px, top + dungeon.H * px], fill=GRID_COLOR)
        for gy in range(dungeon.H + 1):
            lined_draw.line([left, top + gy * px, left + dungeon.W * px, top + gy * px], fill=GRID_COLOR)
        image.paste(lined, mask=mask)

    # ── Grid, on the bare rock only ───────────────────────────────────────
    # The grid runs across the whole picture, lined up with the complex's
    # squares, then every room and corridor is painted white over it.
    if rock_grid:
        for gx in range(0, width, px):
            draw.line([gx, 0, gx, height - 1], fill=GRID_COLOR)
        for gy in range(0, height, px):
            draw.line([0, gy, width - 1, gy], fill=GRID_COLOR)
        for cell in dungeon.hall:
            draw.rectangle(box(*cell), fill=WHITE)
        for r in dungeon.rooms:
            draw.rectangle(box(r.x, r.y, r.w, r.h), fill=WHITE)

    # ── Walls. A doorway is a gap in the wall ─────────────────────────────
    half = COMPLEX_WALL // 2
    for kind, x, y in dungeon.walls:
        gx, gy = left + x * px, top + y * px
        if kind == "h":
            draw.rectangle([gx - half, gy - half, gx + px + half, gy - half + COMPLEX_WALL - 1], fill=BLACK)
        else:
            draw.rectangle([gx - half, gy - half, gx - half + COMPLEX_WALL - 1, gy + px + half], fill=BLACK)

    # ── Room numbers ──────────────────────────────────────────────────────
    for r in dungeon.rooms:
        cx2, cy2 = r.centre2()
        mx, my = left + cx2 * px / 2, top + cy2 * px / 2
        size = int(max(px * 0.7, min(min(r.w, r.h) * px * 0.45, px * 1.7)))
        draw.text((mx, my), str(r.number), font=get_font(size), fill=BLACK, anchor="mm",
                  stroke_width=3, stroke_fill=WHITE)

    # ── Entrance and exit arrows, outside the complex ─────────────────────
    for kind, x, y, side in dungeon.openings:
        dx, dy = SIDE_STEP[side]
        cxp, cyp = left + (x + 0.5) * px + dx * px, top + (y + 0.5) * px + dy * px
        # The arrow points into the complex for an entrance, out for an exit.
        pointing = (-dx, -dy) if kind == "entrance" else (dx, dy)
        tip = (cxp + pointing[0] * px * 0.4, cyp + pointing[1] * px * 0.4)
        base = (cxp - pointing[0] * px * 0.4, cyp - pointing[1] * px * 0.4)
        side_x, side_y = -pointing[1] * px * 0.4, pointing[0] * px * 0.4
        draw.polygon([tip, (base[0] + side_x, base[1] + side_y), (base[0] - side_x, base[1] - side_y)],
                     fill=BLACK)
        draw.text((cxp + dx * px * 1.2, cyp + dy * px * 1.2), "IN" if kind == "entrance" else "OUT",
                  font=get_font(int(px * 0.9)), fill=BLACK, anchor="mm", stroke_width=2, stroke_fill=WHITE)

    # ── Header ────────────────────────────────────────────────────────────
    draw.text((left, px * 0.9), "%s    Seed %s    %d rooms    %d x %d squares"
              % (MAP_LABELS[dungeon.kind], dungeon.seed, len(dungeon.rooms), dungeon.W, dungeon.H),
              font=get_font(int(px * 0.95)), fill=BLACK, anchor="lm", stroke_width=3, stroke_fill=WHITE)
    return image


def ordinal(n):
    """1st, 2nd, 3rd, 4th ... 11th, 12th, 13th ... 21st."""
    suffix = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return "%d%s" % (n, suffix)


def squares(n):
    return "1 square" if n == 1 else "%d squares" % n


def room_file(dungeon, name, number, word):
    """The file name of one room's sheet. Numbers are padded so the files sort in order."""
    return "%s_room_%0*d_%s.jpg" % (name, len(str(len(dungeon.rooms))), number, word)


def room_steps(dungeon):
    """How many corridors each room is from the entrance room (which is 0),
    and which rooms each room's corridors lead to. Both count each corridor
    as it was made, from one room to another, not the junctions where
    corridors later meet."""
    leads = {r.number: set() for r in dungeon.rooms}
    for a, b, _, _, _ in dungeon.links:
        leads[a].add(b)
        leads[b].add(a)
    start = dungeon.opening_doors["entrance"][0] if "entrance" in dungeon.opening_doors else 1
    steps, todo = {start: 0}, [start]
    for here in todo:                    # todo grows as rooms are found
        for there in sorted(leads[here]):
            if there not in steps:
                steps[there] = steps[here] + 1
                todo.append(there)
    return steps, leads


def room_list(numbers):
    numbers = sorted(numbers)
    return ("room " if len(numbers) == 1 else "rooms ") + ", ".join(str(n) for n in numbers)


def complex_room_key(dungeon, name=None):
    """The room key as plain text: how the printed rooms fit together."""
    count = len(dungeon.rooms)
    lines = ["%s   Seed %s   %d rooms   %d x %d squares"
             % (MAP_LABELS[dungeon.kind], dungeon.seed, count, dungeon.W, dungeon.H), "",
             "How to lay it out: print every room's sheet. Each sheet shows one room,",
             "with each doorway as a small bump out in the margin, and \"Room n of %d\"" % count,
             "and the seed in its header. Start at the entrance room and follow the",
             "doorways listed below. The overview picture shows the whole complex.",
             "Squares are counted from the top left square of the complex, (0, 0).", ""]
    opening_side = {kind: side for kind, _, _, side in dungeon.openings}
    for kind, x, y, side in dungeon.openings:
        number, _, length = dungeon.opening_doors[kind]
        lines.append("%s: on the %s side, at square (%d, %d), a corridor of %s from room %d"
                     % (kind.capitalize(), SIDE_WORDS[side], x, y, squares(length), number))
    if dungeon.shortcut:
        deep, _, target, _, length = dungeon.shortcut
        steps, _ = room_steps(dungeon)
        lines.append("No exit. Shortcut: from room %d, deep in the complex (%d corridors from the entrance),"
                     % (deep, steps[deep]))
        lines.append("    a corridor of %s back to room %d (%d corridors from the entrance)"
                     % (squares(length), target, steps[target]))
    lines.append("")

    steps, leads = room_steps(dungeon)
    entrance_room = dungeon.opening_doors["entrance"][0]
    for r in dungeon.rooms:
        notes = []
        shortcut_here = dungeon.shortcut and dungeon.shortcut[0] == r.number
        shortcut_end = dungeon.shortcut and dungeon.shortcut[2] == r.number
        if len(leads[r.number]) == 1 and not (shortcut_here or shortcut_end):
            notes.append("dead end")
        if shortcut_here:
            notes.append("shortcut back to room %d" % dungeon.shortcut[2])
        if shortcut_end:
            notes.append("end of the shortcut from room %d" % dungeon.shortcut[0])
        lines.append("Room %d: %d x %d squares, top left at (%d, %d), %d doorway%s, corridors run on to rooms %s%s"
                     % (r.number, r.w, r.h, r.x, r.y, r.doors, "" if r.doors == 1 else "s",
                        ", ".join(str(n) for n in sorted(leads[r.number])),
                        ("   [" + ", ".join(notes) + "]") if notes else ""))

        # ── Which sheet, and how it fits with the rooms round it ──────────
        if name:
            lines.append("    Sheets       : %s and %s" % (room_file(dungeon, name, r.number, "walls"),
                                                         room_file(dungeon, name, r.number, "grid")))
        lines.append("    Sheet header : \"Room %d of %d\", seed %s" % (r.number, count, dungeon.seed))
        here = steps.get(r.number, 0)
        nearer = [n for n in leads[r.number] if steps.get(n, 0) < here]
        further = [n for n in leads[r.number] if steps.get(n, 0) > here]
        level = [n for n in leads[r.number] if steps.get(n, 0) == here]
        if r.number == entrance_room:
            lines.append("    Reached from : the entrance")
        if nearer:
            lines.append("    Reached from : %s (nearer the entrance)" % room_list(nearer))
        if further:
            lines.append("    Leads on to  : %s" % room_list(further))
        if level:
            lines.append("    Loops round  : %s (as far from the entrance as this room)" % room_list(level))

        # ── What is inside it ─────────────────────────────────────────────
        chamber = dungeon.chambers[r.number - 1]
        inner = len(chamber.rooms)
        has_halls = HALL in chamber.cell.values()
        lines.append("    Inside       : %d inner room%s%s" % (inner, "" if inner == 1 else "s",
                                                           ", joined by hallways" if has_halls else ", no hallway"))

        # ── Each doorway: where it is on the wall, and where it goes ──────
        for index, (inside, outside, door) in enumerate(r.door_list, 1):
            side = STEP_SIDE[(outside[0] - inside[0], outside[1] - inside[1])]
            if side in "NS":
                where = "%s wall, %s square from the west end" % (SIDE_WORDS[side], ordinal(inside[0] - r.x + 1))
            else:
                where = "%s wall, %s square from the north end" % (SIDE_WORDS[side], ordinal(inside[1] - r.y + 1))
            ways = []
            for kind, (number, opening_door, length) in sorted(dungeon.opening_doors.items()):
                if number == r.number and opening_door == door:
                    ways.append("the %s corridor, %s out to the %s side of the complex"
                                % (kind, squares(length), SIDE_WORDS[opening_side[kind]]))
            for a, b, door_a, door_b, length in dungeon.links:
                if a == r.number and door_a == door:
                    ways.append("a corridor of %s to room %d" % (squares(length), b))
                if b == r.number and door_b == door:
                    ways.append("a corridor of %s to room %d" % (squares(length), a))
            if dungeon.shortcut:
                deep, deep_door, target, target_door, length = dungeon.shortcut
                if deep == r.number and deep_door == door:
                    ways.append("the shortcut, %s back to room %d" % (squares(length), target))
                if target == r.number and target_door == door:
                    ways.append("the shortcut, %s from room %d deep in the complex"
                                % (squares(length), deep))
            opens_into = "a hallway" if chamber.cell.get(inside) == HALL else "an inner room"
            lines.append("    Doorway %d    : %s, opening into %s. Leads to %s"
                         % (index, where, opens_into, "; ".join(ways)))
        lines.append("")
    return "\n".join(lines)


def save_dungeon_complex(dungeon, name, overview=None):
    """Saves into Maps/<name>: the overview twice, every room's sheet twice,
    and the room key. Raises FileExistsError if that folder exists."""
    folder = os.path.join(SAVE_FOLDER, name)
    os.makedirs(folder)
    save_jpg(overview or render_complex_overview(dungeon, rock_grid=True), os.path.join(folder, name + "_overview.jpg"))
    save_jpg(render_complex_overview(dungeon, with_grid=True), os.path.join(folder, name + "_overview_grid.jpg"))
    for chamber in dungeon.chambers:
        frame = tight_frame(chamber)
        for with_grid, word in ((False, "walls"), (True, "grid")):
            picture = render_level(dungeon, chamber, with_grid, frame, header="margin")
            save_jpg(picture, os.path.join(folder, room_file(dungeon, name, chamber.number, word)))
    with open(os.path.join(folder, name + "_room_key.txt"), "w", encoding="utf-8") as key_file:
        key_file.write(complex_room_key(dungeon, name))
    return folder


# ============================================================================
# FRONT END
# ============================================================================

def run_window(first_seed=None, first_kind="hideout"):
    import tkinter as tk
    from tkinter import messagebox, simpledialog
    from PIL import ImageTk

    window = tk.Tk()
    window.title("DnD MapBuilder Interior v1.0")
    # ── Open full size: fill the whole screen, then ask for "zoomed" ──────
    # (the green maximise button). Not every system knows "zoomed", so the
    # screen-sized geometry is the fallback.
    window.geometry("%dx%d+0+0" % (window.winfo_screenwidth(), window.winfo_screenheight()))
    try:
        window.state("zoomed")
    except tk.TclError:
        pass
    now = {"hideout": None, "overview": None, "photo": None}

    # ── Top of the window: four centred lines, one under the other ───────────
    #   1. the four buttons
    #   2. the seed box
    #   3. the line of text about the map (kind, seed, levels)
    #   4. the save question (only there while a map is waiting to be saved)
    # A frame packed at the top with no "fill" sits in the middle of its
    # line, which is what centres each of these.
    bar = tk.Frame(window, pady=8)
    bar.pack(side="top", fill="x")

    button_row = tk.Frame(bar)
    button_row.pack(side="top")
    buttons = {}
    for kind, words in (("building", "Single building"), ("hideout", "Bandit hideout"),
                        ("dungeon", "Small dungeon"), ("complex", "Dungeon complex")):
        buttons[kind] = tk.Button(button_row, text=words)
        buttons[kind].pack(side="left", padx=3)

    seed_row = tk.Frame(bar)
    seed_row.pack(side="top", pady=(6, 0))
    tk.Label(seed_row, text="Click a button to make a new map.").pack(side="left", padx=(0, 12))
    tk.Label(seed_row, text="Seed (leave empty for a new map):").pack(side="left")
    # A 1 pixel line all the way round, so the box shows on any background.
    # It turns blue while the box is being typed in.
    seed_box = tk.Entry(seed_row, width=22, relief="flat", bd=2, highlightthickness=1,
                        highlightbackground=SEED_BOX_OUTLINE, highlightcolor=SEED_BOX_FOCUS)
    seed_box.pack(side="left", padx=(4, 0))

    # The line of text about the map is three pieces side by side:
    # words, the seed number, more words. A Label cannot be selected with the
    # mouse, so the seed is a read-only Entry made to look like plain text:
    # no border, the window's own background, and exactly as wide as the
    # number (width 0 means "fit the text").
    status_row = tk.Frame(bar)
    status_row.pack(side="top", pady=(6, 0))
    status_before = tk.Label(status_row, text="")
    status_before.pack(side="left")
    seed_text = tk.StringVar()
    seed_shown = tk.Entry(status_row, textvariable=seed_text, width=0, state="readonly",
                          relief="flat", bd=0, highlightthickness=0, justify="center",
                          font=status_before.cget("font"), fg=status_before.cget("fg"),
                          readonlybackground=window.cget("bg"))
    seed_shown.pack(side="left")
    status_after = tk.Label(status_row, text="")
    status_after.pack(side="left")

    def set_status(before, seed="", after=""):
        status_before.config(text=before)
        seed_text.set(seed)
        seed_shown.selection_clear()
        status_after.config(text=after)

    ask = tk.Frame(window)
    ask_row = tk.Frame(ask)
    ask_row.pack(side="top", pady=(0, 8))
    question = tk.Label(ask_row, text="Do you want to save the generated map?")
    yes_button = tk.Button(ask_row, text="Yes")
    no_button = tk.Button(ask_row, text="No")
    for widget in (question, yes_button, no_button):
        widget.pack(side="left", padx=4)
    # Dungeon complex only: the overview is big, so it can be opened full size
    # in the picture viewer, where you can zoom in.
    full_button = tk.Button(ask_row, text="Open full size")

    # The preview area is black until a map is made and shown.
    preview = tk.Label(window, bg=EMPTY_PREVIEW)
    preview.pack(side="bottom", fill="both", expand=True)

    def show_preview():
        if now["overview"] is None:
            preview.config(image="", bg=EMPTY_PREVIEW)
            return
        preview.config(bg=SHOWN_PREVIEW)
        # Shrink the overview to fit the space the preview really has right
        # now, so no part of it (header or bottom floors) is cut off.
        window.update_idletasks()
        size = (max(200, preview.winfo_width() - 10), max(200, preview.winfo_height() - 10))
        now["shown_at"] = size
        small = now["overview"].copy()
        small.thumbnail(size)
        now["photo"] = ImageTk.PhotoImage(small)     # kept in "now" so it is not thrown away
        preview.config(image=now["photo"])

    def preview_resized(event):
        # The window changed size: fit the preview again (only if it really changed).
        if now["overview"] is not None and now.get("shown_at") != (max(200, event.width - 10),
                                                                    max(200, event.height - 10)):
            show_preview()

    preview.bind("<Configure>", preview_resized)

    def show_map(kind, seed=None):
        seed = seed or seed_box.get().strip() or new_seed()
        if not seed.isdigit():
            messagebox.showinfo("Seed", "A seed is digits only, for example 123456789012345.")
            return
        started = time.perf_counter()
        now["hideout"] = make_map(seed, kind)
        now["overview"] = render_overview(now["hideout"])
        # The save question goes in first, so the preview is sized to the
        # space left below it and the picture is never clipped.
        if kind == "complex":
            full_button.pack(side="left", padx=4)
        else:
            full_button.pack_forget()
        ask.pack(side="top", fill="x", before=preview)
        show_preview()
        seed_box.delete(0, "end")
        if kind == "building":
            floor = now["hideout"].levels[0]
            what = "%d x %d squares" % (floor.w, floor.h)
        elif kind == "complex":
            dc = now["hideout"]
            what = "%d rooms    %d x %d squares" % (len(dc.rooms), dc.W, dc.H)
        else:
            what = "Levels " + ", ".join(str(level.number) for level in now["hideout"].levels)
        set_status("%s    Seed " % MAP_LABELS[kind], seed,
                   "    %s    Made in %.2f seconds" % (what, time.perf_counter() - started))

    def save_map():
        while True:
            typed = simpledialog.askstring("Save map", "Type a name for this map:", parent=window)
            if typed is None:
                return                       # Cancel was pressed; the map stays on screen
            name = clean_name(typed)
            if not name:
                messagebox.showinfo("Save map", "Use a name without / \\ : * ? \" < > | and not starting with a dot.")
                continue
            try:
                folder = save_hideout(now["hideout"], name, now["overview"])
            except FileExistsError:
                messagebox.showinfo("Save map", "There is already a folder called \"%s\". Pick another name." % name)
                continue
            except OSError as problem:
                messagebox.showerror("Save map", "Could not save:\n%s" % problem)
                return
            set_status("Saved in %s    (seed " % folder, now["hideout"].seed, ")")
            ask.pack_forget()
            return

    def discard_map():
        now["hideout"] = now["overview"] = None
        show_preview()
        set_status("Not saved.")
        ask.pack_forget()

    for kind, button in buttons.items():
        button.config(command=lambda kind=kind: show_map(kind))
    yes_button.config(command=save_map)
    no_button.config(command=discard_map)
    full_button.config(command=lambda: now["overview"] and now["overview"].show())

    if first_seed:
        window.update()                      # lets the window work out its size first
        show_map(first_kind, first_seed)
    window.mainloop()


# ============================================================================
# TEST MODE
# ============================================================================

def run_test(how_many):
    """All four kinds of map. Returns how many maps failed."""
    failures = run_stack_test(how_many, "hideout")
    print()
    failures += run_stack_test(how_many, "dungeon")
    print()
    failures += run_building_test(how_many)
    print()
    failures += run_complex_test(how_many)
    print()
    print("OVERALL: %s" % ("all maps passed" if not failures else "%d maps FAILED" % failures))
    return failures


def run_building_test(how_many):
    print("Checking %d single buildings against the rules ..." % how_many)
    failures = 0
    ground_floors = hall_doors = room_doors = exits = 0
    sizes = {}
    started = time.perf_counter()
    buildings = [make_building(str(1000 + n)) for n in range(how_many)]
    build_time = time.perf_counter() - started
    for index, building in enumerate(buildings):
        problems = check_building(building)
        if fingerprint(make_building(building.seed)) != fingerprint(building):
            problems.append("the same seed made a different map")
        level = building.levels[0]
        ground_floors += (level.w, level.h) == (GROUND_W, GROUND_H)
        exits += len(level.openings) > 1
        in_hall = level.cell.get(level.openings[0][1:3]) == HALL if level.openings else False
        hall_doors += in_hall
        room_doors += not in_hall
        sizes[len(level.rooms)] = sizes.get(len(level.rooms), 0) + 1

        # ── Pictures, first 25: the floor plus a 1 square margin, a header,
        # and nothing drawn inside any room (so no tread lines are left)
        if index < 25:
            frame = tight_frame(level)
            walls = render_level(building, level, False, frame, header="margin")
            bare = render_level(building, level, False, frame, header=None)
            if walls.size != ((level.w + 2) * SQUARE, (level.h + 2) * SQUARE):
                problems.append("saved picture is not the floor plus a 1 square margin")
            if render_overview(building).size != walls.size:
                problems.append("preview is not the grid picture")
            if ImageChops.difference(walls, bare).getbbox() is None:
                problems.append("saved picture has no header")
            for x, y, w, h in level.rooms:
                inside = bare.crop(((x + frame[2]) * SQUARE + 4, (y + frame[3]) * SQUARE + 4,
                                    (x + w + frame[2]) * SQUARE - 4, (y + h + frame[3]) * SQUARE - 4))
                if inside.getextrema() != ((255, 255),) * 3:
                    problems.append("something is drawn inside a room")
                    break
        if problems:
            failures += 1
            print("  seed %s: %s" % (building.seed, "; ".join(sorted(set(problems)))))
    print("Ground floors  : %d of %d  (%.0f%%, aim is 10%%)"
          % (ground_floors, how_many, 100.0 * ground_floors / max(1, how_many)))
    print("Rooms          : %s" % ", ".join("%d rooms x %d" % item for item in sorted(sizes.items())))
    print("Entrance       : %d at a hallway end, %d through a room wall" % (hall_doors, room_doors))
    print("With an exit   : %d of %d  (%.0f%%)" % (exits, how_many, 100.0 * exits / max(1, how_many)))
    print("Build time     : %.2f ms per map" % (1000 * build_time / max(1, how_many)))
    print("RESULT: %s" % ("all buildings passed" if not failures else "%d buildings FAILED" % failures))
    return failures


def run_complex_test(how_many):
    """The test for dungeon complexes."""
    print("Checking %d dungeon complexes against the rules ..." % how_many)
    failures = 0
    counts, exits, dead_ends = [], 0, 0
    inner_rooms, with_halls, hall_doors, all_doors, uncut = {}, 0, 0, 0, 0
    shortcuts, shortcut_depth, shortcut_length, shortcut_ends = 0, 0, 0, {}
    started = time.perf_counter()
    dungeons = [make_dungeon_complex(str(100000000000000 + n * 7919)) for n in range(how_many)]
    build_time = time.perf_counter() - started
    slowest = 0.0
    for dungeon in dungeons:
        problems = check_dungeon_complex(dungeon)
        one = time.perf_counter()
        again = make_dungeon_complex(dungeon.seed)
        slowest = max(slowest, time.perf_counter() - one)
        if complex_fingerprint(again) != complex_fingerprint(dungeon):
            problems.append("the same seed made a different map")
        key = complex_room_key(dungeon, "test")
        if any(("Room %d:" % r.number) not in key for r in dungeon.rooms):
            problems.append("a room is missing from the room key")
        counts.append(len(dungeon.rooms))
        exits += len(dungeon.openings) > 1
        _, leads = room_steps(dungeon)
        dead_ends += sum(1 for r in dungeon.rooms if len(leads[r.number]) == 1)
        if dungeon.shortcut:
            shortcuts += 1
            steps_now = room_steps(dungeon)[0]
            shortcut_depth += steps_now[dungeon.shortcut[0]]
            shortcut_length += dungeon.shortcut[4]
            end = steps_now[dungeon.shortcut[2]]
            shortcut_ends[end] = shortcut_ends.get(end, 0) + 1
        for chamber in dungeon.chambers:
            inner_rooms[len(chamber.rooms)] = inner_rooms.get(len(chamber.rooms), 0) + 1
            uncut += len(chamber.rooms) == 1
            with_halls += HALL in chamber.cell.values()
            for _, cx, cy, _ in chamber.openings:
                all_doors += 1
                hall_doors += chamber.cell.get((cx, cy)) == HALL
        if problems:
            failures += 1
            print("  seed %s: %s" % (dungeon.seed, "; ".join(sorted(set(problems)))))

    # ── Pictures, first 3 complexes: the overview, and every room's sheet
    # is the room plus a 1 square margin, with its header inside the margin
    started = time.perf_counter()
    pictured = dungeons[:3]
    for dungeon in pictured:
        problems = []
        walls = render_complex_overview(dungeon)
        grid = render_complex_overview(dungeon, with_grid=True)
        if walls.size != ((dungeon.W + 2 * COMPLEX_MARGIN) * COMPLEX_SQUARE,
                          (dungeon.H + COMPLEX_MARGIN_TOP + COMPLEX_MARGIN) * COMPLEX_SQUARE) or grid.size != walls.size:
            problems.append("overview is the wrong size")
        for chamber in dungeon.chambers:
            frame = tight_frame(chamber)
            sheet = render_level(dungeon, chamber, True, frame, header="margin")
            bare = render_level(dungeon, chamber, False, frame, header=None)
            if sheet.size != ((chamber.w + 2) * SQUARE, (chamber.h + 2) * SQUARE):
                problems.append("room %d sheet is not the room plus a 1 square margin" % chamber.number)
            changed = ImageChops.difference(render_level(dungeon, chamber, False, frame, header="margin"),
                                            bare).getbbox()
            if changed is None:
                problems.append("room %d sheet has no header" % chamber.number)
            elif not (changed[3] <= SQUARE - OUTER_WALL // 2
                      or changed[1] >= sheet.size[1] - SQUARE + OUTER_WALL // 2 + 1):
                problems.append("room %d sheet header is outside the margin" % chamber.number)
        if problems:
            failures += 1
            print("  seed %s: %s" % (dungeon.seed, "; ".join(problems)))
    draw_time = time.perf_counter() - started

    print("Rooms          : %d to %d per complex" % (min(counts), max(counts)))
    weights = room_count_weights()
    whole = sum(w for _, w in weights)
    for lo, hi in ((15, 29), (30, 59), (60, 89), (90, 99)):
        got = sum(1 for c in counts if lo <= c <= hi)
        aim = sum(w for n, w in weights if lo <= n <= hi) / whole
        print("  %2d to %2d rooms: %5d of %d  (%4.1f%%, aim is %4.1f%%)"
              % (lo, hi, got, how_many, 100.0 * got / max(1, how_many), 100.0 * aim))
    print("Dead ends      : %.1f per complex on average" % (dead_ends / max(1, how_many)))
    print("With an exit   : %d of %d  (%.0f%%, aim is 86%%)" % (exits, how_many, 100.0 * exits / max(1, how_many)))
    print("With a shortcut: %d of %d, from a room %.1f corridors deep, %.0f squares long on average"
          % (shortcuts, how_many, shortcut_depth / max(1, shortcuts), shortcut_length / max(1, shortcuts)))
    print("Shortcut ends  : %s" % ", ".join("%d corridors from the entrance x %d" % item
                                            for item in sorted(shortcut_ends.items())))
    print("Inner rooms    : %s" % ", ".join("%d x %d" % item for item in sorted(inner_rooms.items())))
    print("Left uncut     : %d rooms of %d (no room for 2 inner rooms)"
          % (uncut, sum(counts)))
    print("With a hallway : %d rooms of %d  (%.0f%%)" % (with_halls, sum(counts), 100.0 * with_halls / max(1, sum(counts))))
    print("Doorways       : %d of %d open straight into a hallway" % (hall_doors, all_doors))
    print("Build time     : %.2f ms per map, slowest %.2f ms"
          % (1000 * build_time / max(1, how_many), 1000 * slowest))
    print("Draw time      : %.0f ms per map (overview twice plus every room's sheet, before saving)"
          % (1000 * draw_time / max(1, len(pictured))))
    print("Seed check     : seed 123456789012345 has fingerprint %s on this computer"
          % complex_fingerprint(make_dungeon_complex("123456789012345")))
    print("RESULT: %s" % ("all dungeon complexes passed" if not failures else "%d dungeon complexes FAILED" % failures))
    return failures


def run_stack_test(how_many, kind):
    """The test for hideouts or small dungeons."""
    across = OVERVIEW_ACROSS[kind]
    print("Checking %d %s maps against the rules ..."
          % (how_many, "small dungeon" if kind == "dungeon" else kind))
    failures = 0
    repairs = 0
    level_counts = {}
    room_counts = {}
    hall_stairs = {"ground": [0, 0], "other levels with a hallway": [0, 0], "levels with main stairs": [0, 0]}
    rolled_but_room = 0
    secondaries = 0

    # ── Rules of the layout, every map ────────────────────────────────────
    started = time.perf_counter()
    hideouts = [make_hideout(str(1000 + n), kind) for n in range(how_many)]
    build_time = time.perf_counter() - started
    for hideout in hideouts:
        problems = check_hideout(hideout)
        if fingerprint(make_hideout(hideout.seed, kind)) != fingerprint(hideout):
            problems.append("the same seed made a different map")
        for level in hideout.levels:
            repairs += repair_level(level)
            room_counts[len(level.rooms)] = room_counts.get(len(level.rooms), 0) + 1
            if level.main is None:              # levels 3, 4, -3, -4: no main stairwell
                secondaries += len(level.stairs)
                continue
            alcove = level.main.alcove
            has_halls = HALL in level.cell.values()
            keys = ["levels with main stairs"]
            if level.number == 1:
                keys.append("ground")
            elif has_halls:
                keys.append("other levels with a hallway")
            for key in keys:
                hall_stairs[key][0] += alcove
                hall_stairs[key][1] += 1
            if level.hall_roll and not alcove and level.number != 1:
                rolled_but_room += 1
            secondaries += sum(s.kind == "secondary" for s in level.stairs)
        level_counts[len(hideout.levels)] = level_counts.get(len(hideout.levels), 0) + 1
        if problems:
            failures += 1
            print("  seed %s: %s" % (hideout.seed, "; ".join(sorted(set(problems)))))

    # ── Rules of the pictures, first 25 maps ──────────────────────────────
    started = time.perf_counter()
    pictured = hideouts[:25]
    for hideout in pictured:
        problems = []
        ground_size = None
        for level in hideout.levels:
            name = "level %d " % level.number

            # ── Saved single-level files: 1 square margin, small header
            tight = tight_frame(level)
            walls = render_level(hideout, level, False, tight, header="margin")
            grid = render_level(hideout, level, True, tight, header="margin")
            bare_walls = render_level(hideout, level, False, tight, header=None)
            bare_grid = render_level(hideout, level, True, tight, header=None)
            if walls.size != grid.size or walls.size != ((level.w + 2) * SQUARE, (level.h + 2) * SQUARE):
                problems.append(name + "saved pictures are not the level plus a 1 square margin")
            # Walls and grid versions line up: black sits on the same pixels in both.
            if not GRID_OVER_WALLS:
                dark = lambda value: 255 if value < 60 else 0
                if (bare_walls.convert("L").point(dark).tobytes()
                        != bare_grid.convert("L").point(dark).tobytes()):
                    problems.append(name + "walls and grid pictures do not line up")
            # The grid is 70 pixels: a pixel on a grid line, away from walls, is blue.
            low = walls.size[1] - 35          # in the bottom margin, clear of walls
            if (bare_grid.getpixel((SQUARE * (tight[0] - 1), low)) != GRID_COLOR
                    or bare_grid.getpixel((35, walls.size[1] - SQUARE)) != GRID_COLOR
                    or bare_grid.getpixel((35, low)) != WHITE):
                problems.append(name + "grid is off")
            # Single-level pictures never have blue squares.
            if NEXT_FLOOR_FILL in [color for _, color in (grid.getcolors(1 << 16) or [])]:
                problems.append(name + "picture has blue squares")
            # The small header: inside the top or bottom margin row, and sitting
            # on plain white (or plain grid) only, never on a wall or bump out.
            changed = ImageChops.difference(walls, bare_walls).getbbox()
            if changed is None:
                problems.append(name + "saved picture has no header")
            else:
                in_top = changed[3] <= SQUARE - OUTER_WALL // 2
                in_bottom = changed[1] >= walls.size[1] - SQUARE + OUTER_WALL // 2 + 1
                if not (in_top or in_bottom) or changed[0] < 0 or changed[2] > walls.size[0]:
                    problems.append(name + "saved header is outside the margin: %s" % (changed,))
                clear = bare_walls.crop((max(0, changed[0] - 1), max(0, changed[1] - 1),
                                         changed[2] + 1, changed[3] + 1)).getextrema()
                if clear != ((255, 255),) * 3:
                    problems.append(name + "saved header touches a wall line")

            # ── Overview quadrant: ground frame, full header ───────────────
            frame = own_frame(hideout, level)
            walls = render_level(hideout, level, False, frame)
            if level.number == 1:
                ground_size = walls.size
            # Header: measured on the real pixels of the walls picture.
            # 1 square of white above the words, and 1 square or more between
            # the words and the highest line below them.
            font, lines, line_height, _ = fit_header(header_parts(hideout, level), walls.size[0])
            ink = walls.convert("L").point(lambda value: 255 if value < 200 else 0)
            split = frame[4] * SQUARE
            words = ink.crop((0, 0, walls.size[0], split)).getbbox()
            below = ink.crop((0, split, walls.size[0], walls.size[1])).getbbox()
            if words is None or words[1] < HEADER_SPACE * SQUARE:
                problems.append("level %d header has %s pixels of white above it"
                                % (level.number, words and words[1]))
            elif below is None or split + below[1] - words[3] < SQUARE:
                problems.append("level %d header is %s pixels from a line"
                                % (level.number, below and split + below[1] - words[3]))
            if max(font.getlength(line) for line in lines) > walls.size[0] - 20:
                problems.append("level %d header runs off the picture" % level.number)
        sheet = render_overview(hideout)
        if sheet.size != (across * ground_size[0], 2 * ground_size[1]):
            problems.append("overview is not %d x 2 ground pictures" % across)
        if sheet.size[0] <= sheet.size[1] and kind == "dungeon":
            problems.append("dungeon overview is not landscape")
        # Every unused place on the sheet is plain white.
        for place in range(len(hideout.levels), across * 2):
            corner = ((place % across) * ground_size[0], (place // across) * ground_size[1])
            box = corner + (corner[0] + ground_size[0], corner[1] + ground_size[1])
            if sheet.crop(box).getextrema() != ((255, 255),) * 3:
                problems.append("unused overview place is not plain white")
        if problems:
            failures += 1
            print("  seed %s: %s" % (hideout.seed, "; ".join(problems)))
    draw_time = time.perf_counter() - started

    print("Levels per map : %s" % ", ".join("%d levels x %d" % item for item in sorted(level_counts.items())))
    print("Rooms per level: %s" % ", ".join("%d rooms x %d" % item for item in sorted(room_counts.items())))
    for key, (hits, total) in hall_stairs.items():
        print("Hallway stairs : %-28s %4d of %4d  (%.0f%%)" % (key, hits, total, 100.0 * hits / max(1, total)))
    print("Rolled hallway but too tight, so used a room: %d levels" % rolled_but_room)
    print("Secondary stairs: %d (each one counted on both levels it links)" % secondaries)
    print("Repairs needed : %d" % repairs)
    print("Build time     : %.2f ms per map" % (1000 * build_time / how_many))
    print("Draw time      : %.0f ms per map (every JPG picture plus the overview, before saving)"
          % (1000 * draw_time / max(1, len(pictured))))
    print("Seed check     : seed 123456789012345 has fingerprint %s on this computer"
          % fingerprint(make_hideout("123456789012345", kind)))
    print("RESULT: %s" % ("all maps passed" if not failures else "%d maps FAILED" % failures))
    return failures


# ============================================================================
# START
# ============================================================================

def main():
    check_settings()
    args = sys.argv[1:]
    # The kind of map is the last word, if it is one of the four. Hideout if not.
    kind = "hideout"
    if args and args[-1].lower() in KINDS:
        kind = args.pop().lower()
    if args and args[0] == "--test":
        sys.exit(1 if run_test(int(args[1]) if len(args) > 1 else 200) else 0)
    if args and args[0] == "--save":
        name = clean_name(args[1] if len(args) > 1 else "")
        seed = args[2] if len(args) > 2 else new_seed()
        if not name or not seed.isdigit():
            sys.exit("Use: --save NAME [SEED] [building, hideout, dungeon or complex]   (the seed is digits only)")
        try:
            print("Saved %s seed %s in %s" % (kind, seed, save_hideout(make_map(seed, kind), name)))
        except FileExistsError:
            sys.exit('There is already a folder called "%s" in %s.' % (name, SAVE_FOLDER))
        return
    if args and not args[0].isdigit():
        sys.exit("Use: no words, a seed (digits only), --test N, or --save NAME [SEED], "
                 "with building, hideout, dungeon or complex as an optional last word")
    run_window(args[0] if args else None, kind)


if __name__ == "__main__":
    main()
