#!/usr/bin/env python3
# ============================================================================
# DnD-BuildingFloorPlans-v2.0.3.py
# ============================================================================

"""
.SYNOPSIS
    Tkinter window that makes random floor plans (walls only) for a single
    building, a bandit hideout or a dungeon, and saves them as JPG files.

.DESCRIPTION
    Print and play floor plans for tabletop games. One click makes a whole
    map, shows it in the window and asks whether to save it.

    The window:
      - Three buttons, centered at the top: "Single building", "Bandit
        hideout" and "Dungeon". Each click makes a new map straight away
      - The seed box is under the buttons. Leave it empty for a new map, or
        type a seed to get that map back
      - The line of text under the seed box says what was made. The seed
        number in it can be selected with the mouse and copied (Cmd+C on a
        Mac, Ctrl+C elsewhere). Double-click selects the whole number
      - The save question is under that, while a map is waiting to be saved
      - The preview fills the rest of the window and is fitted again
        whenever the window changes size, so it is never clipped

    Every map:
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

    Dungeon:
      - Built like a hideout, but with 4, 5 or 6 levels (equal odds), and
        every level after ground is below it: -2, -3 ... -6, each inside
        the one above

    Single building:
      - One floor only. 1 time in 10 it is a 17 x 13 ground floor; the
        other 9 times it is one of the smaller floor layouts
      - It has no stairwells. Those squares are plain floor of the room or
        hallway they would have been in
      - It always has an exterior entrance: at the end of a hallway when
        the floor has one, otherwise through the outer wall of a room,
        never at a corner. Half of them also have an exit on a different
        wall, by the same rule

    Stairwells (hideout and dungeon):
      - The main 2 x 2 stairwell sits in the same spot on every level it
        serves. It is placed first and every level is sized and placed
        around it. It links levels 1, 2 and -2, and its walls are 7 pixels
        thick, like the outer walls
      - Each level rolls 75% / 25%. On 75% the main stairwell opens straight
        onto a hallway: the hallway ends at the stairs and three rooms wrap
        round them (the "pinwheel"). On 25% the stairwell sits in a room,
        and that room has a doorway straight onto a hallway. Small levels
        with no hallway always keep the stairwell in a room
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
      - A hideout or dungeon also saves one overview sheet with every level
        on it, drawn at the same size and lined up with the ground level.
        The hideout overview is 2 floors across; the dungeon overview is
        landscape, 3 floors across and 2 down
      - On the overview, and only there, blue squares show the ground
        footprint a floor does not cover. A darker blue shows the footprint
        of the floor next to it, nearer ground, when that is not ground
      - A single building saves 2 JPGs. A hideout saves 7 or 9, a dungeon
        9, 11 or 13

    Test mode makes many maps of all three kinds and checks each one
    against the rules.

    Every number you may want to change is in the SETTINGS section.

    Lines that start with "#" are notes for people. Python ignores them.

.NOTES
    Author : Brennon Hedman
    Version: 2.0.3
    Requires: Python 3.8+ and Pillow 10.1+ (python3 -m pip install pillow)
    Platform: macOS, Windows or Linux (the window uses Tkinter, which comes
              with the standard Python installer)

.EXAMPLE
    python3 DnD-BuildingFloorPlans-v2.0.3.py

    Opens the window with the three buttons.

.EXAMPLE
    python3 DnD-BuildingFloorPlans-v2.0.3.py 123456789012345

    Opens the window already showing the hideout with seed 123456789012345.
    Add the word building or dungeon after the seed for the other two kinds.

.EXAMPLE
    python3 DnD-BuildingFloorPlans-v2.0.3.py --test 500

    No window. Makes 500 maps of each kind, checks each one against the
    rules, and prints a report with the time taken.

.EXAMPLE
    python3 DnD-BuildingFloorPlans-v2.0.3.py --save cave1 123456789012345

    No window. Makes the map with that seed and saves it in the folder
    Maps/cave1. Leave the seed off for a random map. Add the word building
    or dungeon at the end for the other two kinds (hideout if left off).
"""

import hashlib
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
DUNGEON_LEVEL_COUNTS = (4, 5, 6) # dungeon: 4 to 6 levels, equal odds of each,
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
SQUARES_PER_ROOM = 20            # other levels: at most 1 room per this many
                                 # squares, so smaller levels get fewer rooms
HALL_MIN_ROOMS = 4               # other levels get a hallway from this many rooms
SIDE_HALL_MIN_AREA = 60          # a block this big may get a side hallway
SIDE_HALL_CHANCE = (1, 2)        # 1 in 2
EXTRA_DOOR_CHANCE = (1, 6)       # chance of a second way round between two rooms

# ── Stairwells ──────────────────────────────────────────────────────────
HALL_STAIR_CHANCE = (3, 4)       # 75%: the main stairwell opens straight onto a
                                 # hallway. 25%: it sits in a room that has a
                                 # doorway straight onto a hallway. Rolled for
                                 # each level on its own
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

# ── Saving ──────────────────────────────────────────────────────────────
MAP_LABELS = {"building": "Building", "hideout": "Hideout", "dungeon": "Dungeon"}
                                 # the word for each kind in headers and messages
OVERVIEW_ACROSS = {"hideout": 2, "dungeon": 3}
                                 # floors side by side on the overview sheet
                                 # (always 2 rows): the dungeon is landscape
KINDS = ("building", "hideout", "dungeon")
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
        self.main = stairs[0] if stairs[0].kind == "main" else None
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
        self.kind = kind        # "building", "hideout" or "dungeon"
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
    """A hideout or a dungeon: the same builder with more levels,
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
    """The one way in for all three buttons."""
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
                is_ground=False, layout=None, split=None, want_exit=False):
    level = Level(number, rect, stairs)
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
    arrival_room = stairs[level.arrival].room

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
    arrival = level.stairs[level.arrival]
    start = stair_sides(arrival.pos)[arrival.open][1]
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
    A hideout is 2 floors across, a dungeon 3 (landscape); both are 2 rows.
    A single building has no overview: this gives its grid picture instead,
    which is what the window shows."""
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
# FRONT END
# ============================================================================

def run_window(first_seed=None, first_kind="hideout"):
    import tkinter as tk
    from tkinter import messagebox, simpledialog
    from PIL import ImageTk

    window = tk.Tk()
    window.title("DnD Building Floor Plans v2.0.3")
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
    #   1. the three buttons
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
                        ("dungeon", "Dungeon")):
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
        ask.pack(side="top", fill="x", before=preview)
        show_preview()
        seed_box.delete(0, "end")
        if kind == "building":
            floor = now["hideout"].levels[0]
            what = "%d x %d squares" % (floor.w, floor.h)
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

    if first_seed:
        window.update()                      # lets the window work out its size first
        show_map(first_kind, first_seed)
    window.mainloop()


# ============================================================================
# TEST MODE
# ============================================================================

def run_test(how_many):
    """All three kinds of map. Returns how many maps failed."""
    failures = run_stack_test(how_many, "hideout")
    print()
    failures += run_stack_test(how_many, "dungeon")
    print()
    failures += run_building_test(how_many)
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


def run_stack_test(how_many, kind):
    """The test for hideouts or dungeons."""
    across = OVERVIEW_ACROSS[kind]
    print("Checking %d %s maps against the rules ..."
          % (how_many, kind))
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
    args = sys.argv[1:]
    # The kind of map is the last word, if it is one of the three. Hideout if not.
    kind = "hideout"
    if args and args[-1].lower() in KINDS:
        kind = args.pop().lower()
    if args and args[0] == "--test":
        sys.exit(1 if run_test(int(args[1]) if len(args) > 1 else 200) else 0)
    if args and args[0] == "--save":
        name = clean_name(args[1] if len(args) > 1 else "")
        seed = args[2] if len(args) > 2 else new_seed()
        if not name or not seed.isdigit():
            sys.exit("Use: --save NAME [SEED] [building, hideout or dungeon]   (the seed is digits only)")
        try:
            print("Saved %s seed %s in %s" % (kind, seed, save_hideout(make_map(seed, kind), name)))
        except FileExistsError:
            sys.exit('There is already a folder called "%s" in %s.' % (name, SAVE_FOLDER))
        return
    if args and not args[0].isdigit():
        sys.exit("Use: no words, a seed (digits only), --test N, or --save NAME [SEED], "
                 "with building, hideout or dungeon as an optional last word")
    run_window(args[0] if args else None, kind)


if __name__ == "__main__":
    main()
