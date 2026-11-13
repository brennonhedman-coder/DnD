#!/usr/bin/env python3
# ============================================================================
# hideout_generator_v1.1.py
# ============================================================================

"""
.SYNOPSIS
    Tkinter window that makes random bandit hideout floor plans (walls only)
    and saves them as JPG pictures.

.DESCRIPTION
    The window has three map buttons: small, medium and large. Each click
    makes one hideout of that size: a stack of levels joined by one stairwell
    that sits in the same spot on every level.
      - Three sizes (SIZES): a small map has 2 floors, a medium map has 4,
        and a large map has 4 to 6 on a wide (landscape) footprint with
        double the area
      - Ground level: always a large floor, with 1 or 2 outside entrances
        with a bump out, kept off the corners of the building
      - Ground level position: any floor of the stack can be the ground
        level, with the other floors above it, below it or both (FLOOR_PLANS)
      - Large and small floors (LARGE_FLOOR_CHANCES): about 60% of medium
        maps have two large floors and about 40% have one. A large map can
        have any number of large floors. A large floor is always next to the
        ground level or next to another large floor
      - Stacking: above the ground no floor sticks out past the floor under
        it. Below the ground a small level may sit anywhere inside the
        hideout's footprint
      - Large levels: a main hallway along the open side of the stairwell,
        side hallways, rooms of 2 x 2 squares or more, and doorways
      - Small levels: open floor around the stairwell with a few corner rooms
      - Deep room: medium and large maps have exactly one room reached only
        by walking through 3 to 5 other rooms. Small maps have none
      - Openings never touch, the squares in front of the stairwell opening
        stay clear, and no wall piece is left attached to nothing
      - Map numbers have 15 digits. The same size and number always remake
        the same map
      - Pictures: a grid picture and a walls picture for each level, plus one
        overview sheet. The ground level is always first on the sheet (top
        left, or left on the small map, whose two levels sit side by side),
        then the levels above it going up, then the levels below it going down
      - Sheet layout (SHEET_ACROSS): small and medium maps put 2 levels
        across. The large map picks how many go across so the sheet fills
        a wide screen and shows the levels as big as it can
      - Window: opens filling the screen, with the map buttons, the map number
        and the Yes / No save question in a bar at the top
      - Test mode checks every map against every rule. Batch mode saves many
        maps without clicking

    Every number you may want to change is in the SETTINGS section. The
    script checks the settings when it starts and says which one is wrong.

    Lines that start with "#" are notes for people. Python ignores them.

.NOTES
    Author : Brennon Hedman
    Version: 1.1
    Requires: Python 3.7+ and Pillow (python3 -m pip install pillow)
    Platform: macOS, Windows or Linux (the window uses Tkinter, which comes
              with the standard Python installer)

    New in version 1.1:
      - Small map: the words in brackets after the ground level's place are
        singular, as the small map has only one other level:
        "(the other level is below it)" and "(the other level is above it)".
        Medium and large maps still say "the other levels"
      - Every map number gives the same map as in version 1.0

.EXAMPLE
    python3 hideout_generator_v1.1.py

    Opens the window with the three map buttons.

.EXAMPLE
    python3 hideout_generator_v1.1.py large 123456789012345

    Opens the window showing large map 123456789012345. Without a size word
    the medium map with that number is shown.

.EXAMPLE
    python3 hideout_generator_v1.1.py --test 200

    No window. Makes 200 maps of each size, checks each one, and prints a
    report. Add a size word to test one size: --test 200 small

.EXAMPLE
    python3 hideout_generator_v1.1.py --batch 50 maps large

    No window. Makes 50 large maps and saves them in the folder "maps".
    Without a size word the maps are medium.
"""

import os
import random
import sys

from PIL import Image, ImageDraw, ImageFont   # Pillow, the add-on that writes JPG files


# ============================================================================
# SETTINGS
# ============================================================================

# [stated]  you said it      [default] proposed earlier, in the outline
# [GUESS]   picked by Claude because nothing was decided
# Some settings depend on each other. The script checks them when it
# starts and tells you which one is wrong.

# The settings that differ by map size. There is one block per size, and the window
# has one button per block. While a map of one size is being made, checked or drawn,
# each name in its block works as a setting of that name (see use_size below).
#
#   BUTTON_TEXT          words on this size's button
#   LARGE_WIDTH          widest a large level can be, in squares. Also sets the picture size
#   LARGE_HEIGHT         tallest a large level can be. Also sets the picture size
#   LARGE_WIDTH_RANGE    large levels: the width is picked at random in this range
#   LARGE_HEIGHT_RANGE   large levels: the height is picked at random in this range
#   SMALL_WIDTH          width of the small levels
#   SMALL_HEIGHT_RANGE   small levels: the height is picked at random in this range
#   FLOOR_PLANS          the stacks a map can get: (floors above the ground level, floors
#                        below it). Each map picks one pair at random. The ground level is
#                        level 1, the floors above it are 2, 3, ... and the floors below
#                        it are -2, -3, ...
#   LARGE_FLOOR_CHANCES  how many large floors a map gets, the ground level included:
#                        {count: chance}. The chances are shares, so 40 and 60 give 40%
#                        and 60%. A count the stack has too few floors for is left out.
#                        The ground level is always large. Other large floors are next to
#                        the ground level or next to another large floor.
#   HAS_DEEP_ROOM        True = every map has exactly one deep room. False = no deep room
#   MAX_ROOMS_PER_FLOOR  no floor has more rooms than this
#   ROOM_COUNT           rooms per kind of level: (fewest, most). For the large levels the
#                        counts are for the full LARGE_WIDTH x LARGE_HEIGHT size and shrink
#                        with the footprint. The stairwell and hallways are not rooms.
#   LARGEST_ROOM         largest room per kind of level: (long side, short side) in squares
#   SIDE_HALLS           side hallways off the main hallway per kind of level: (fewest, most)
#   SHEET_ACROSS         levels side by side on the overview sheet (the window and the
#                        saved overview). A number, or "fit" = pick the number that shows the
#                        levels biggest on the screen (on the saved overview: on a screen
#                        shaped OVERVIEW_SHAPE)
#
# Kinds of level:  "ground" = the large level with the outside entrance
#                  "upper"  = a large level above the ground
#                  "lower"  = a large level below the ground
#                  "small"  = a small level: open floor around the stairwell with corner rooms
SIZES = {
    "small": {
        "BUTTON_TEXT": "Click for small map",          # [stated]
        "LARGE_WIDTH": 16,                             # [GUESS]
        "LARGE_HEIGHT": 18,                            # [GUESS]
        "LARGE_WIDTH_RANGE": (12, 16),                 # [GUESS]
        "LARGE_HEIGHT_RANGE": (14, 18),                # [GUESS]
        "SMALL_WIDTH": 9,                              # [GUESS]
        "SMALL_HEIGHT_RANGE": (10, 12),                # [GUESS]
        # [stated] two floors at most. Every level is built around the stairwell, so
        # a map with one floor only, (0, 0), would have a stairwell that leads nowhere.
        "FLOOR_PLANS": [(1, 0), (0, 1)],
        "LARGE_FLOOR_CHANCES": {1: 70, 2: 30},         # [GUESS] the second floor is usually small
        "HAS_DEEP_ROOM": False,                        # [stated]
        "MAX_ROOMS_PER_FLOOR": 10,                     # [GUESS]
        "ROOM_COUNT": {"ground": (6, 10), "upper": (6, 10), "lower": (5, 9), "small": (0, 2)},      # [GUESS]
        "LARGEST_ROOM": {"ground": (8, 6), "upper": (8, 6), "lower": (8, 6), "small": (4, 4)},      # [GUESS]
        "SIDE_HALLS": {"ground": (0, 2), "upper": (0, 1), "lower": (0, 1)},                         # [GUESS]
        "SHEET_ACROSS": 2,                             # as in version 8
    },
    "medium": {                                        # the version 7 map
        "BUTTON_TEXT": "Click for medium map",         # [stated]
        "LARGE_WIDTH": 24,                             # [estimate in outline]
        "LARGE_HEIGHT": 25,                            # [estimate in outline]
        "LARGE_WIDTH_RANGE": (18, 24),                 # [GUESS]
        "LARGE_HEIGHT_RANGE": (19, 25),                # [GUESS]
        "SMALL_WIDTH": 13,                             # [estimate in outline]
        "SMALL_HEIGHT_RANGE": (15, 18),                # [estimate in outline]
        # [stated] four floors: the ground level is the top floor, has one floor above
        # it and two below it, or is the bottom floor.
        "FLOOR_PLANS": [(0, 3), (1, 2), (3, 0)],
        "LARGE_FLOOR_CHANCES": {1: 40, 2: 60},         # [stated] about 40% one large floor, 60% two
        "HAS_DEEP_ROOM": True,                         # [stated]
        "MAX_ROOMS_PER_FLOOR": 19,                     # [stated]
        "ROOM_COUNT": {"ground": (14, 19), "upper": (10, 16), "lower": (7, 12), "small": (0, 2)},   # [GUESS]
        "LARGEST_ROOM": {"ground": (8, 6), "upper": (10, 8), "lower": (12, 10), "small": (5, 5)},   # [GUESS]
        "SIDE_HALLS": {"ground": (1, 3), "upper": (1, 2), "lower": (0, 1)},                         # [GUESS]
        "SHEET_ACROSS": 2,                             # as in version 8
    },
    "large": {
        "BUTTON_TEXT": "Click for large map",          # [stated]
        # [stated] landscape: the top edge is the long one, to suit a computer screen.
        # [GUESS] 42 x 28 = 1176 squares, about the 34 x 35 = 1190 of version 8, which
        # was double the area of the medium map.
        "LARGE_WIDTH": 42,
        "LARGE_HEIGHT": 28,
        "LARGE_WIDTH_RANGE": (32, 42),                 # [GUESS]
        "LARGE_HEIGHT_RANGE": (22, 28),                # [GUESS]
        "SMALL_WIDTH": 22,                             # [GUESS] wide and short, like the large levels
        "SMALL_HEIGHT_RANGE": (16, 20),                # [GUESS]
        # [stated] up to two more floors than the medium map: 4, 5 or 6 floors.
        # [GUESS] any floor of the stack can be the ground level.
        "FLOOR_PLANS": [(0, 3), (1, 2), (2, 1), (3, 0),
                        (0, 4), (1, 3), (2, 2), (3, 1), (4, 0),
                        (0, 5), (1, 4), (2, 3), (3, 2), (4, 1), (5, 0)],
        "LARGE_FLOOR_CHANCES": {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1},   # [stated] no cap. [GUESS] equal chances
        "HAS_DEEP_ROOM": True,                         # [GUESS] one deep room, as on the medium map
        "MAX_ROOMS_PER_FLOOR": 38,                     # [GUESS] double the medium map's 19, for double the area
        "ROOM_COUNT": {"ground": (28, 38), "upper": (20, 32), "lower": (14, 24), "small": (0, 4)},  # [GUESS]
        "LARGEST_ROOM": {"ground": (8, 6), "upper": (10, 8), "lower": (12, 10), "small": (6, 6)},   # [GUESS]
        "SIDE_HALLS": {"ground": (2, 5), "upper": (1, 4), "lower": (0, 3)},                         # [GUESS]
        "SHEET_ACROSS": "fit",                         # [stated] fill a wide screen, not a tall stack
    },
}
DEFAULT_SIZE = "medium"         # [GUESS] the size used when the command line names none
OVERVIEW_SHAPE = (16, 10)       # [GUESS] width : height of the screen a saved "fit" overview is laid out for


def use_size(size):
    """Switch the size settings to one block of SIZES: after use_size("large"),
    LARGE_WIDTH is 34, ROOM_COUNT is the large map's ROOM_COUNT, and so on.
    Every part of the script that makes, checks or draws a map calls this first."""
    globals().update(SIZES[size])
    globals()["ACTIVE_SIZE"] = size      # the name of the size now in use


use_size(DEFAULT_SIZE if DEFAULT_SIZE in SIZES else list(SIZES)[0])

# The settings below are the same for every size.

PIXELS_PER_SQUARE = 70          # [stated]

STAIR_SIZE = 4                  # [stated] 4 x 4 squares
HALL_WIDTH = 2                  # [stated] 2 squares
SMALLEST_ROOM = 2               # [stated] 2 x 2 squares

INNER_WALL_PIXELS = round(PIXELS_PER_SQUARE / 6)   # [stated] 1/6 of a square (12 pixels at 70 per square)
OUTER_WALL_PIXELS = 2 * INNER_WALL_PIXELS          # [GUESS] double the inner wall

# Step lines inside the stairwell, parallel to the open side, running wall to wall.
SHOW_STAIR_STEPS = True                              # [stated] drawn in the photo
STAIR_STEPS_PER_SQUARE = 2      # [stated] 2 = a line every half square (7 lines in a 4 x 4 stairwell)
                                # 1 = a line on each grid line only (3 lines, as in the first try)
STAIR_STEP_PIXELS = round(INNER_WALL_PIXELS / 2)    # [GUESS] half an inner wall (6 pixels at 70 per square)

DOOR_WIDTHS = (1, 2)            # [GUESS] inner doorway is 1 or 2 squares, picked at random
BUMP_WIDTH = 2                  # [default] entrance bump out, squares wide
BUMP_DEPTH = 1                  # [default] entrance bump out, squares deep
ENTRANCE_COUNT = (1, 2)         # [GUESS] entrance bump outs on the ground level: (fewest, most). Drawing 1 shows 2.
ENTRANCE_CORNER_GAP = 1         # [GUESS] squares of outer wall kept between an entrance and a corner

# Chance that two rooms that touch get an extra doorway between them      [GUESS]
EXTRA_DOOR_CHANCE = 0.10
# Chance that a hallway end stops short of the outer wall (0 = always wall to wall)   [GUESS]
HALL_STOPS_SHORT_CHANCE = 0.5

# The one deep room per map, on the sizes that have one (HAS_DEEP_ROOM in SIZES).
# (fewest, most) rooms a player must walk through to reach it.           [stated] 3 to 5
# Set to (3, 3) if no other room at all may be 3 or more rooms deep.
# On every size, with or without a deep room, no other room is as deep as the fewest.
DEEP_ROOM_WALK_THROUGH = (3, 5)
# Kinds of level that may hold the deep room. Small levels have too few rooms.   [GUESS]
# "ground" must stay in this list: it is the only large level every map has.
DEEP_ROOM_LEVEL_KINDS = ("ground", "upper", "lower")

MAP_NUMBER_DIGITS = 15          # [GUESS] map numbers run from 1 to 999,999,999,999,999
TRY_LIMIT = 20000               # [GUESS] give up with a message after this many tries for one map

MARGIN_SQUARES = 2              # [default was 1] 2 = 1 for the bump out + 1 empty square
HEADER_SQUARES = 1              # [GUESS] height of the header strip at the top
HEADER_FONT_PIXELS = 44         # [GUESS]
SHOW_MAP_NUMBER_IN_HEADER = True   # [GUESS] so a saved picture still shows its map number
GRID_OVER_WALLS = False         # [not specified] False = walls cover the grid (as in version 1).
                                # True = the grid line is drawn on top of the walls.

WALL_COLOR = (0, 0, 0)          # [stated] black
GRID_COLOR = (150, 200, 255)    # [stated] light blue
BACKGROUND_COLOR = (255, 255, 255)   # [default] white
JPG_QUALITY = 95                # [GUESS] 1-100, higher = sharper and bigger file

# The window
WINDOW_OPENS_FULL = True        # [stated] True = the window opens filling the screen.
                                # False = it opens at WINDOW_START_SIZE instead.
WINDOW_START_SIZE = (1100, 800) # [GUESS] width, height in screen points, used when WINDOW_OPENS_FULL is False
MAP_BUTTON_HINT = "Click a button again to generate a new map."    # [stated] note under the buttons
                                # The words on the buttons are BUTTON_TEXT in SIZES.

# How hard the generator tries before starting a level over (not usually worth changing).
LEVEL_TRIES = 600               # room layouts tried per level
DOOR_TRIES = 30                 # doorway layouts tried per room layout
NEW_AIM_AFTER = 150             # tries before a new room count is aimed for


# ============================================================================
# SETTINGS CHECK
# ============================================================================

SIZE_SETTING_NAMES = ("BUTTON_TEXT", "LARGE_WIDTH", "LARGE_HEIGHT", "LARGE_WIDTH_RANGE", "LARGE_HEIGHT_RANGE",
                      "SMALL_WIDTH", "SMALL_HEIGHT_RANGE", "FLOOR_PLANS", "LARGE_FLOOR_CHANCES", "HAS_DEEP_ROOM",
                      "MAX_ROOMS_PER_FLOOR", "ROOM_COUNT", "LARGEST_ROOM", "SIDE_HALLS", "SHEET_ACROSS")


def check_settings():
    """Returns a list of problems with the SETTINGS block. Empty list = fine."""
    problems = []

    def need(ok, text):
        if not ok:
            problems.append(text)

    # ── Settings that differ by size ─────────────────────────────────────
    need(DEFAULT_SIZE in SIZES, "DEFAULT_SIZE must be one of the sizes in SIZES: %s." % ", ".join(SIZES))
    need(len(OVERVIEW_SHAPE) == 2 and all(n > 0 for n in OVERVIEW_SHAPE),
         "OVERVIEW_SHAPE must be two numbers above 0: (width, height).")
    for size, block in SIZES.items():
        missing = [name for name in SIZE_SETTING_NAMES if name not in block]
        if missing:
            problems.append('SIZES["%s"] is missing: %s.' % (size, ", ".join(missing)))
            continue
        use_size(size)
        problems.extend('SIZES["%s"]: %s' % (size, text) for text in check_size_settings())
    if DEFAULT_SIZE in SIZES and all(name in SIZES[DEFAULT_SIZE] for name in SIZE_SETTING_NAMES):
        use_size(DEFAULT_SIZE)

    # ── Settings shared by every size ────────────────────────────────────
    need(BUMP_WIDTH >= 1 and BUMP_DEPTH >= 1, "BUMP_WIDTH and BUMP_DEPTH must be 1 or more.")
    need(MARGIN_SQUARES >= BUMP_DEPTH, "MARGIN_SQUARES must be at least BUMP_DEPTH, or bump outs run off the picture.")
    need(HEADER_SQUARES * PIXELS_PER_SQUARE >= HEADER_FONT_PIXELS,
         "HEADER_FONT_PIXELS is taller than the header strip (HEADER_SQUARES x PIXELS_PER_SQUARE).")
    need(1 <= ENTRANCE_COUNT[0] <= ENTRANCE_COUNT[1],
         "ENTRANCE_COUNT must go from low to high and start at 1: every map has an outside entrance.")
    need(len(DOOR_WIDTHS) > 0 and all(isinstance(w, int) and w >= 1 for w in DOOR_WIDTHS),
         "DOOR_WIDTHS must list whole numbers of 1 or more.")
    need(1 <= DEEP_ROOM_WALK_THROUGH[0] <= DEEP_ROOM_WALK_THROUGH[1],
         "DEEP_ROOM_WALK_THROUGH must go from low to high and start at 1 or more.")
    need("ground" in DEEP_ROOM_LEVEL_KINDS and "small" not in DEEP_ROOM_LEVEL_KINDS,
         'DEEP_ROOM_LEVEL_KINDS must list "ground" and must not list "small".')
    need(0 <= EXTRA_DOOR_CHANCE <= 1, "EXTRA_DOOR_CHANCE must be between 0 and 1.")
    need(0 <= HALL_STOPS_SHORT_CHANCE <= 1, "HALL_STOPS_SHORT_CHANCE must be between 0 and 1.")
    need(1 <= MAP_NUMBER_DIGITS <= 18, "MAP_NUMBER_DIGITS must be between 1 and 18.")
    need(ENTRANCE_CORNER_GAP >= 0, "ENTRANCE_CORNER_GAP cannot be negative.")
    need(isinstance(STAIR_STEPS_PER_SQUARE, int) and 1 <= STAIR_STEPS_PER_SQUARE <= 4,
         "STAIR_STEPS_PER_SQUARE must be a whole number from 1 to 4.")
    return problems


def check_size_settings():
    """Problems with the size block that use_size() last switched to. Empty list = fine."""
    problems = []

    def need(ok, text):
        if not ok:
            problems.append(text)

    side = STAIR_SIZE + 4       # stairwell plus 2 clear squares on each side
    need(LARGE_WIDTH_RANGE[0] <= LARGE_WIDTH_RANGE[1] <= LARGE_WIDTH,
         "LARGE_WIDTH_RANGE must go from low to high and not above LARGE_WIDTH (%d)." % LARGE_WIDTH)
    need(LARGE_HEIGHT_RANGE[0] <= LARGE_HEIGHT_RANGE[1] <= LARGE_HEIGHT,
         "LARGE_HEIGHT_RANGE must go from low to high and not above LARGE_HEIGHT (%d)." % LARGE_HEIGHT)
    need(SMALL_WIDTH >= side, "SMALL_WIDTH must be at least %d." % side)
    need(side <= SMALL_HEIGHT_RANGE[0] <= SMALL_HEIGHT_RANGE[1],
         "SMALL_HEIGHT_RANGE must go from low to high and start at %d or more." % side)
    need(LARGE_WIDTH_RANGE[0] >= SMALL_WIDTH,
         "LARGE_WIDTH_RANGE cannot start below SMALL_WIDTH (%d): the small levels sit inside the large ones."
         % SMALL_WIDTH)
    need(LARGE_HEIGHT_RANGE[0] >= side, "LARGE_HEIGHT_RANGE must start at %d or more." % side)
    for kind in ("ground", "upper", "lower", "small"):
        need(kind in ROOM_COUNT and kind in LARGEST_ROOM and (kind == "small" or kind in SIDE_HALLS),
             'ROOM_COUNT, LARGEST_ROOM and SIDE_HALLS must each list "%s" (SIDE_HALLS has no "small").' % kind)
    for kind, (low, high) in ROOM_COUNT.items():
        need(0 <= low <= high, "ROOM_COUNT for %s must go from low to high." % kind)
        need(high <= MAX_ROOMS_PER_FLOOR,
             "ROOM_COUNT for %s goes above MAX_ROOMS_PER_FLOOR (%d)." % (kind, MAX_ROOMS_PER_FLOOR))
    for kind, (low, high) in SIDE_HALLS.items():
        need(0 <= low <= high, "SIDE_HALLS for %s must go from low to high." % kind)
    need(isinstance(HAS_DEEP_ROOM, bool), "HAS_DEEP_ROOM must be True or False.")
    need(SHEET_ACROSS == "fit" or (isinstance(SHEET_ACROSS, int) and SHEET_ACROSS >= 1),
         'SHEET_ACROSS must be a whole number of 1 or more, or "fit".')
    plans_ok = (len(FLOOR_PLANS) > 0 and
                all(len(plan) == 2 and all(isinstance(n, int) and n >= 0 for n in plan) for plan in FLOOR_PLANS))
    need(plans_ok, "FLOOR_PLANS must list pairs of whole numbers: (floors above the ground, floors below it).")
    chances_ok = (len(LARGE_FLOOR_CHANCES) > 0 and
                  all(isinstance(count, int) and count >= 1 and chance > 0
                      for count, chance in LARGE_FLOOR_CHANCES.items()))
    need(chances_ok, "LARGE_FLOOR_CHANCES must pair whole numbers of 1 or more with chances above 0.")
    if plans_ok and chances_ok:
        fewest_floors = min(1 + above + below for above, below in FLOOR_PLANS)
        need(min(LARGE_FLOOR_CHANCES) <= fewest_floors,
             "LARGE_FLOOR_CHANCES has no count small enough for a stack of %d floors." % fewest_floors)
    return problems


# ============================================================================
# DATA MODEL
# ============================================================================

# A level is a grid of squares plus a set of wall pieces on grid lines.
#
# A square is named by (x, y): x counts right, y counts down, from the
# top-left corner of the large footprint.
#
# A wall piece is one square long and sits on a grid line:
#     ("h", x, y)  horizontal piece on grid line y, from x to x+1
#     ("v", x, y)  vertical piece on grid line x, from y to y+1

class Level:
    def __init__(self):
        self.number = 0        # the level number: 1 is the ground level, 2 is above it, -2 is below it
        self.kind = ""         # "ground", "upper", "lower" or "small"
        self.size = ""         # the map size this level was made for: a name in SIZES
        self.ground_place = "" # where the ground level sits in this hideout: "top", "middle", "bottom" or "only"
        self.box = None        # (left, top, width, height) of this level's footprint
        self.frame = None      # (width, height) of this hideout's large footprint
        self.cells = {}        # square -> what it is: "S" stairwell, "H" hallway/open floor, or a room number
        self.rooms = []        # list of room rectangles (left, top, width, height)
        self.halls = []        # hallway rectangles: the main hallway first, then the side hallways
        self.walls = set()     # every wall piece to draw
        self.outer = set()     # the wall pieces that are drawn thicker
        self.stair = None      # (left, top) of the stairwell
        self.stair_side = ""   # which side of the stairwell is open: N, S, E or W
        self.route = []        # room numbers walked through to the deep room, in order; the last is the deep room


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def edge_between(a, b):
    """The wall piece that sits between two squares that touch."""
    (ax, ay), (bx, by) = a, b
    if ay == by:
        return ("v", max(ax, bx), ay)
    return ("h", ax, max(ay, by))


def piece_ends(piece):
    """The two corner points a wall piece runs between."""
    kind, x, y = piece
    return ((x, y), (x + 1, y)) if kind == "h" else ((x, y), (x, y + 1))


def squares_beside(piece):
    """The two squares a wall piece sits between."""
    kind, x, y = piece
    return ((x, y - 1), (x, y)) if kind == "h" else ((x - 1, y), (x, y))


def rect_cells(rect):
    """Every square inside a rectangle (left, top, width, height)."""
    x0, y0, w, h = rect
    return [(x, y) for y in range(y0, y0 + h) for x in range(x0, x0 + w)]


def four_neighbors(cell):
    x, y = cell
    return ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))


def shuffled(rng, items):
    """The same items in a random order."""
    items = list(items)
    order = sorted((rng.random(), i) for i in range(len(items)))
    return [items[i] for _, i in order]


# ============================================================================
# GENERATOR - WHOLE HIDEOUT
# ============================================================================

def count_try(tries):
    """Counts work done for one map and stops with a message if the settings cannot be met."""
    tries[0] += 1
    if tries[0] > TRY_LIMIT:
        raise RuntimeError(
            "No map could be made in %d tries. Some settings do not fit together. "
            "Most often this is ROOM_COUNT with LARGEST_ROOM, or DEEP_ROOM_WALK_THROUGH." % TRY_LIMIT)


def stack_of_floors(above, below, large_above, large_below):
    """The floors of one hideout as (level number, kind of level), in the order they are
    made and shown: the ground level first, then the levels above it going up, then the
    levels below it going down. The large floors are the ones nearest the ground level."""
    stack = [(1, "ground")]
    stack += [(1 + i, "upper" if i <= large_above else "small") for i in range(1, above + 1)]
    stack += [(-1 - i, "lower" if i <= large_below else "small") for i in range(1, below + 1)]
    return stack


def ground_place(above, below):
    """Where the ground level sits in a stack, in a word."""
    if above == 0 and below == 0:
        return "only"
    if above == 0:
        return "top"
    return "bottom" if below == 0 else "middle"


def pick_stack(rng):
    """Pick the floors for one hideout. Returns (ground place, stack of floors)."""
    # ── How many floors, and which one is the ground level ───────────────
    above, below = rng.choice(FLOOR_PLANS)
    floors = 1 + above + below

    # ── How many of the floors are large, the ground level included ──────
    counts = [count for count in sorted(LARGE_FLOOR_CHANCES) if count <= floors]
    large = rng.choices(counts, weights=[LARGE_FLOOR_CHANCES[count] for count in counts])[0]

    # ── Which floors are large ───────────────────────────────────────────
    # Besides the ground level, the large floors are split between the floors above
    # and the floors below. On each side they are the floors nearest the ground level.
    extra = large - 1
    large_above = rng.randint(max(0, extra - below), min(above, extra))
    return ground_place(above, below), stack_of_floors(above, below, large_above, extra - large_above)


def make_hideout(map_number, size=None):
    """Make all levels of one hideout. The same size and map number give the same map.
    The levels come back in display order: the ground level is first."""
    size = size or DEFAULT_SIZE
    use_size(size)
    rng = random.Random(map_number)      # a dice roller that repeats itself for the same number
    tries = [0]
    place, stack = pick_stack(rng)
    ground_number = stack[0][0]
    deep_choices = [number for number, kind in stack if kind in DEEP_ROOM_LEVEL_KINDS and kind != "small"]
    while True:
        count_try(tries)
        # Size of the large footprint for this hideout (the large levels share it).
        frame = (rng.randint(*LARGE_WIDTH_RANGE), rng.randint(*LARGE_HEIGHT_RANGE))
        # Stairwell spot, the same on every level. At least 2 squares from the outer wall.
        sx = rng.randint(2, frame[0] - STAIR_SIZE - 2)
        sy = rng.randint(2, frame[1] - STAIR_SIZE - 2)
        # The one deep room: which level holds it, and how many rooms are walked through to reach it.
        # On a size without a deep room, no level gets one.
        deep_level, walk = None, 0
        if HAS_DEEP_ROOM:
            deep_level = rng.choice(deep_choices)
            walk = rng.randint(*DEEP_ROOM_WALK_THROUGH)
        levels = []
        # Above the ground a small level must stay inside the floor under it, so the
        # footprint of the last level made above the ground is kept. Below the ground
        # a small level may sit anywhere inside the whole footprint.
        whole = (0, 0, frame[0], frame[1])
        box_above = whole
        for number, kind in stack:
            above = number > ground_number
            if kind == "small":
                level = make_small_level(rng, number, sx, sy, frame, box_above if above else whole, tries)
            else:
                level = make_large_level(rng, number, kind, sx, sy, frame,
                                         walk if number == deep_level else 0, tries)
            if level is None:
                break
            level.size, level.ground_place = size, place
            if above:
                box_above = level.box
            levels.append(level)
        if len(levels) == len(stack) and not check_hideout(levels):
            return levels


# ============================================================================
# GENERATOR - LARGE LEVELS
# ============================================================================

def room_count_range(kind, frame):
    """Fewest and most rooms for a level. Large levels get fewer rooms when the footprint is smaller."""
    fewest, most = ROOM_COUNT[kind]
    if kind != "small":
        share = (frame[0] * frame[1]) / (LARGE_WIDTH * LARGE_HEIGHT)
        fewest, most = max(1, round(fewest * share)), max(1, round(most * share))
    return min(fewest, MAX_ROOMS_PER_FLOOR), min(most, MAX_ROOMS_PER_FLOOR)


def short_start(rng, wall, limit):
    """Where a hallway starts: at the outer wall, or (by chance) short of it. Never 1 square short."""
    start = wall
    if limit > wall and rng.random() < HALL_STOPS_SHORT_CHANCE:
        start = rng.randint(wall, limit)
    return wall if start - wall == 1 else start


def short_end(rng, limit, wall):
    """Where a hallway ends: at the outer wall, or (by chance) short of it. Never 1 square short."""
    end = wall
    if limit < wall and rng.random() < HALL_STOPS_SHORT_CHANCE:
        end = rng.randint(limit, wall)
    return wall if wall - end == 1 else end


def make_large_level(rng, number, kind, sx, sy, frame, walk, tries):
    """A large level (ground, upper or lower): stairwell, main hallway, side hallways, then rooms and doorways.
    walk = how many rooms are walked through to reach the deep room (0 = no deep room on this level)."""
    W, H = frame
    fewest, most = room_count_range(kind, frame)
    if walk:
        fewest = max(fewest, walk + 1)         # the route to the deep room needs this many rooms
    if fewest > most:
        return None
    aim = rng.randint(fewest, most)            # the room count this level aims for
    for attempt in range(LEVEL_TRIES):
        count_try(tries)
        if attempt and attempt % NEW_AIM_AFTER == 0:
            aim = rng.randint(fewest, most)
        cells = {c: None for c in rect_cells((0, 0, W, H))}
        for c in rect_cells((sx, sy, STAIR_SIZE, STAIR_SIZE)):
            cells[c] = "S"

        # ── Main hallway ─────────────────────────────────────────────────
        # Straight, along the open side of the stairwell. It always covers
        # the stairwell opening. Each end reaches the outer wall or stops short of it.
        side = rng.choice("NSEW")
        main_runs_left_right = side in "NS"
        if main_runs_left_right:
            a = short_start(rng, 0, sx)
            b = short_end(rng, sx + STAIR_SIZE, W)
            main = (a, sy - HALL_WIDTH if side == "N" else sy + STAIR_SIZE, b - a, HALL_WIDTH)
        else:
            a = short_start(rng, 0, sy)
            b = short_end(rng, sy + STAIR_SIZE, H)
            main = (sx - HALL_WIDTH if side == "W" else sx + STAIR_SIZE, a, HALL_WIDTH, b - a)
        halls = [main]

        # ── Side hallways ────────────────────────────────────────────────
        # Straight, branching off the main hallway toward the outer wall.
        used = []
        for _ in range(rng.randint(*SIDE_HALLS[kind])):
            for _ in range(20):
                p = rng.randint(a, b - HALL_WIDTH)
                if any(abs(p - q) < HALL_WIDTH + SMALLEST_ROOM for q in used):
                    continue                   # too close to another side hallway
                part = rng.choice(("before", "after", "both"))
                rects = []
                near = main[1] if main_runs_left_right else main[0]     # main hallway's near edge
                far = near + HALL_WIDTH                                  # and its far edge
                wall = H if main_runs_left_right else W
                if part != "after" and near >= SMALLEST_ROOM:
                    start = short_start(rng, 0, near - SMALLEST_ROOM)
                    rects.append((p, start, HALL_WIDTH, near - start) if main_runs_left_right
                                 else (start, p, near - start, HALL_WIDTH))
                if part != "before" and wall - far >= SMALLEST_ROOM:
                    end = short_end(rng, far + SMALLEST_ROOM, wall)
                    rects.append((p, far, HALL_WIDTH, end - far) if main_runs_left_right
                                 else (far, p, end - far, HALL_WIDTH))
                if not rects:
                    continue
                if any(cells[c] == "S" for r in rects for c in rect_cells(r)):
                    continue                   # would run through the stairwell
                halls.extend(rects)
                used.append(p)
                break
        for r in halls:
            for c in rect_cells(r):
                cells[c] = "H"

        # ── Rooms ────────────────────────────────────────────────────────
        # Everything left over becomes blocks, and blocks get cut into rooms.
        free = [c for c, v in cells.items() if v is None]
        blocks = cut_into_rectangles(rng, free)
        if any(min(w, h) < SMALLEST_ROOM for (_, _, w, h) in blocks):
            continue                           # a leftover strip narrower than 2 squares
        # A low room count needs large rooms; a high one can use any mix of sizes.
        place = (aim - fewest) / (most - fewest) if most > fewest else 0.5    # 0 = fewest, 1 = most
        thrift = 1 - place * rng.random()
        rooms = split_into_rooms(rng, blocks, kind, aim, thrift)
        if rooms is None:
            continue
        for i, r in enumerate(rooms):
            for c in rect_cells(r):
                cells[c] = i

        # ── Entrances and doorways ───────────────────────────────────────
        box = (0, 0, W, H)
        spots = entrance_spots(cells, box) if kind == "ground" else None
        if kind == "ground" and not (spots[0] or spots[1]):
            continue                           # no hallway reaches the outer wall away from a corner
        plan = wall_plan(cells)
        for _ in range(DOOR_TRIES):
            level = finish_level(rng, number, kind, box, cells, rooms, halls, sx, sy, side, frame,
                                 plan, spots, walk)
            if level is not None and not check_level(level):
                return level
    return None


# ============================================================================
# GENERATOR - SMALL LEVELS
# ============================================================================

def stair_front(sx, sy, side):
    """The squares directly in front of the stairwell opening."""
    n = range(STAIR_SIZE)
    if side == "N":
        return [(sx + i, sy - 1) for i in n]
    if side == "S":
        return [(sx + i, sy + STAIR_SIZE) for i in n]
    if side == "W":
        return [(sx - 1, sy + i) for i in n]
    return [(sx + STAIR_SIZE, sy + i) for i in n]


def make_small_level(rng, number, sx, sy, frame, inside, tries):
    """A small level: open floor around the stairwell, with 0 to 2 corner rooms.
    inside = the footprint (left, top, width, height) this level must stay inside:
    above the ground, the floor under it; below the ground, the whole hideout footprint."""
    in_x, in_y, in_w, in_h = inside
    aim = rng.randint(*ROOM_COUNT["small"])    # the room count this level aims for
    for attempt in range(LEVEL_TRIES):
        count_try(tries)
        if attempt and attempt % NEW_AIM_AFTER == 0:
            aim = rng.randint(*ROOM_COUNT["small"])
        w = SMALL_WIDTH
        h = min(rng.randint(*SMALL_HEIGHT_RANGE), in_h)
        # Slide the small footprint so it holds the stairwell (2 squares clear on
        # every side) and stays inside the footprint it was given.
        ax = rng.randint(max(in_x, sx + STAIR_SIZE + 2 - w), min(in_x + in_w - w, sx - 2))
        ay = rng.randint(max(in_y, sy + STAIR_SIZE + 2 - h), min(in_y + in_h - h, sy - 2))
        box = (ax, ay, w, h)
        cells = {c: "H" for c in rect_cells(box)}
        for c in rect_cells((sx, sy, STAIR_SIZE, STAIR_SIZE)):
            cells[c] = "S"
        side = rng.choice("NSEW")
        keep_clear = set(stair_front(sx, sy, side))    # nothing may stand in front of the stairwell opening

        rooms = []
        ok = True
        biggest = LARGEST_ROOM["small"][0]
        for _ in range(aim):
            rw = rng.randint(SMALLEST_ROOM, biggest)
            rh = rng.randint(SMALLEST_ROOM, biggest)
            rx = rng.choice((ax, ax + w - rw))         # left or right corner
            ry = rng.choice((ay, ay + h - rh))         # top or bottom corner
            room = (rx, ry, rw, rh)
            if any(cells[c] != "H" or c in keep_clear for c in rect_cells(room)):
                ok = False                             # on the stairwell, another room, or the opening
                break
            for c in rect_cells(room):
                cells[c] = len(rooms)
            rooms.append(room)
        if not ok:
            continue

        plan = wall_plan(cells)
        for _ in range(DOOR_TRIES):
            level = finish_level(rng, number, "small", box, cells, rooms, [], sx, sy, side, frame,
                                 plan, None, 0)
            if level is not None and not check_level(level):
                return level
    return None


# ============================================================================
# GENERATOR - ROOMS AND WALLS
# ============================================================================

def cut_into_rectangles(rng, free):
    """Cut a patch of free squares into rectangles. A random flip/turn varies the result."""
    flip_x, flip_y, turn = rng.random() < 0.5, rng.random() < 0.5, rng.random() < 0.5

    def there(c):
        x, y = c
        x, y = (-x if flip_x else x), (-y if flip_y else y)
        return (y, x) if turn else (x, y)

    def back(c):
        x, y = (c[1], c[0]) if turn else c
        return (-x if flip_x else x), (-y if flip_y else y)

    left = {there(c) for c in free}
    rects = []
    while left:
        x, y = min(left, key=lambda c: (c[1], c[0]))      # top-left free square
        w = 1
        while (x + w, y) in left:
            w += 1
        h = 1
        while all((x + i, y + h) in left for i in range(w)):
            h += 1
        for c in rect_cells((x, y, w, h)):
            left.discard(c)
        (ax, ay), (bx, by) = back((x, y)), back((x + w - 1, y + h - 1))
        rects.append((min(ax, bx), min(ay, by), abs(ax - bx) + 1, abs(ay - by) + 1))
    return rects


def split_into_rooms(rng, blocks, kind, aim, thrift):
    """Cut blocks into rooms until none is too big and there are exactly `aim` rooms.
    Returns None when this layout cannot give that count.
    thrift (0 to 1) = how often a forced cut makes the largest piece allowed. A high value
    gives fewer, larger rooms, which is what a low room count needs."""
    long_max, short_max = LARGEST_ROOM[kind]

    def too_big(r):
        return max(r[2], r[3]) > long_max or min(r[2], r[3]) > short_max

    def can_split(r):
        return max(r[2], r[3]) >= 2 * SMALLEST_ROOM

    def split(r, forced=False):
        x, y, w, h = r
        along_width = w >= h if rng.random() < 0.8 else w < h    # usually cut the long side
        if along_width and w < 2 * SMALLEST_ROOM:
            along_width = False
        if not along_width and h < 2 * SMALLEST_ROOM:
            along_width = True
        size, other = (w, h) if along_width else (h, w)
        edge = max(SMALLEST_ROOM, min(size // 2, short_max - 2)) # keep cuts away from the ends
        if forced and rng.random() < thrift:
            longest = long_max if other <= short_max else short_max
            cut = max(edge, min(longest, size - edge))
            if rng.random() < 0.5:
                cut = size - cut
        else:
            cut = rng.randint(edge, size - edge)
        if along_width:
            return (x, y, cut, h), (x + cut, y, w - cut, h)
        return (x, y, w, cut), (x, y + cut, w, h - cut)

    rooms = list(blocks)
    while True:                              # first: cut anything larger than the largest room
        big = [r for r in rooms if too_big(r) and can_split(r)]
        if not big:
            break
        if len(rooms) >= aim:
            return None                      # already at the count, and still too big
        rooms.remove(big[0])
        rooms.extend(split(big[0], forced=True))
    if len(rooms) > aim or any(too_big(r) for r in rooms):
        return None
    while len(rooms) < aim:                  # then: keep cutting the biggest room up to the count
        choices = [r for r in rooms if can_split(r)]
        if not choices:
            return None
        biggest = max(choices, key=lambda r: r[2] * r[3])
        rooms.remove(biggest)
        rooms.extend(split(biggest))
    return rooms


def wall_plan(cells):
    """Where walls go before any doorway is opened.
    Returns (all wall pieces, the outer ones, wall pieces between each pair of things that touch)."""
    walls, outer, shared = set(), set(), {}
    for c, a in cells.items():
        for n in four_neighbors(c):
            b = cells.get(n, "outside")
            if b == a:
                continue
            e = edge_between(c, n)
            walls.add(e)
            if b == "outside":
                outer.add(e)
            elif n > c:                      # count each wall piece once
                pieces = shared.setdefault((a, b), shared.setdefault((b, a), []))
                pieces.append(e)
    return walls, outer, shared


def finish_level(rng, number, kind, box, cells, rooms, halls, sx, sy, side, frame, plan, spots, walk):
    """Open the stairwell side, the entrances and the doorways. Returns None if it cannot be done."""
    base_walls, outer, shared = plan
    level = Level()
    level.size = ACTIVE_SIZE
    level.number, level.kind, level.box, level.frame = number, kind, box, frame
    level.cells, level.rooms, level.halls = cells, rooms, halls
    level.stair, level.stair_side = (sx, sy), side
    level.walls, level.outer = set(base_walls), set(outer)

    # Openings are gaps: wall pieces taken back out. Nothing is ever drawn across them.
    opened = list(stair_side_edges(sx, sy, side))
    if kind == "ground":
        for where in pick_entrances(rng, spots[0], spots[1]):
            gap, bump = entrance_pieces(box, where[0], where[1])
            opened.extend(gap)
            level.walls.update(bump)
            level.outer.update(bump)
    result = make_doors(rng, cells, len(rooms), halls, shared, opened, walk)
    if result is None:
        return None
    doors, level.route = result
    level.walls.difference_update(opened)
    for door in doors:
        level.walls.difference_update(door)
    return level


# ============================================================================
# GENERATOR - OPENINGS AND DOORWAYS
# ============================================================================

def stair_side_edges(sx, sy, side):
    """The four wall pieces on one side of the stairwell."""
    n = range(STAIR_SIZE)
    if side == "N":
        return [("h", sx + i, sy) for i in n]
    if side == "S":
        return [("h", sx + i, sy + STAIR_SIZE) for i in n]
    if side == "W":
        return [("v", sx, sy + i) for i in n]
    return [("v", sx + STAIR_SIZE, sy + i) for i in n]


def straight_runs(edges):
    """Group wall pieces into straight unbroken runs."""
    lines = {}
    for kind, x, y in edges:
        line, pos = (y, x) if kind == "h" else (x, y)
        lines.setdefault((kind, line), []).append(pos)
    runs = []
    for (kind, line), spots in lines.items():
        spots.sort()
        run = [spots[0]]
        for p in spots[1:]:
            if p == run[-1] + 1:
                run.append(p)
            else:
                runs.append((kind, line, run))
                run = [p]
        runs.append((kind, line, run))
    return runs


def pick_door(rng, pieces, open_points):
    """Pick a doorway 1 or 2 squares wide somewhere along these wall pieces.
    A doorway may not touch any opening that already exists (open_points)."""
    want = rng.choice(DOOR_WIDTHS)
    options = []
    for kind, line, run in straight_runs(pieces):
        width = want
        if len(run) < width + 2:              # short wall: use the narrowest doorway so wall is left
            width = min(min(DOOR_WIDTHS), len(run))
        for start in range(len(run) - width + 1):
            door = [(kind, p, line) if kind == "h" else (kind, line, p) for p in run[start:start + width]]
            if not any(end in open_points for piece in door for end in piece_ends(piece)):
                options.append(door)
    return rng.choice(options) if options else None


def find_route(rng, neighbors, starts, length):
    """A chain of `length` rooms: it starts at a room on a hallway and each next room touches the one before."""
    steps = [0]

    def grow(route):
        if len(route) == length:
            return True
        steps[0] += 1
        if steps[0] > 2000:
            return False
        for nxt in shuffled(rng, neighbors[route[-1]]):
            if nxt in route:
                continue
            route.append(nxt)
            if grow(route):
                return True
            route.pop()
        return False

    for start in shuffled(rng, starts):
        route = [start]
        if grow(route):
            return route
    return None


def make_doors(rng, cells, room_count, halls, shared, opened, walk):
    """Give every room a doorway. Returns (doorways, route to the deep room) or None.

    Rules built in here:
      - a doorway never touches another opening;
      - every side hallway gets a doorway (unless an entrance already opens onto it);
      - the rooms on the route to the deep room open only onto the route;
      - every other room is at most (fewest walk-through) - 1 rooms from a hallway."""
    open_points = {end for piece in opened for end in piece_ends(piece)}
    doors = []

    def try_door(pieces):
        door = pick_door(rng, pieces, open_points)
        if door is None:
            return False
        doors.append(door)
        for piece in door:
            open_points.update(piece_ends(piece))
        return True

    neighbors = {i: [j for j in range(room_count) if (i, j) in shared] for i in range(room_count)}
    on_hall = [i for i in range(room_count) if (i, "H") in shared]
    joined = set()

    # ── Step 1: The route to the deep room ───────────────────────────────
    # Its rooms after the first open only onto the route.
    route = []
    if walk:
        route = find_route(rng, neighbors, on_hall, walk + 1)
        if route is None:
            return None
        for a, b in zip(route, route[1:]):
            if not try_door(shared[(a, b)]):
                return None
            joined.add((min(a, b), max(a, b)))
    closed = set(route[1:])

    # ── Step 2: Hallway doorways ─────────────────────────────────────────
    # Side hallways first: each needs at least one opening.
    hall_of = {c: i for i, rect in enumerate(halls) for c in rect_cells(rect)}

    def hall_number(piece):
        for c in squares_beside(piece):
            if cells.get(c) == "H":
                return hall_of.get(c)
        return None

    has_opening = {hall_number(piece) for piece in opened
                   if any(c not in cells for c in squares_beside(piece))}     # entrances
    depth = {}
    for side_hall in shuffled(rng, range(1, len(halls))):
        if side_hall in has_opening:
            continue
        for room in shuffled(rng, [i for i in on_hall if i not in closed]):
            pieces = [p for p in shared[(room, "H")] if hall_number(p) == side_hall]
            if pieces and try_door(pieces):
                depth[room] = 0
                break
        else:
            return None                       # no room can open onto this side hallway
    for room in on_hall:
        if room not in closed and room not in depth and try_door(shared[(room, "H")]):
            depth[room] = 0
    if route and route[0] not in depth:
        return None

    # ── Step 3: Rooms off the hallway ────────────────────────────────────
    # Each opens onto a neighbor that is closer to the hallway.
    limit = DEEP_ROOM_WALK_THROUGH[0] - 1     # deepest any other room may be
    now = 0
    while True:
        added = {}
        waiting = [i for i in range(room_count) if i not in depth and i not in closed]
        for room in shuffled(rng, waiting):
            for other in shuffled(rng, [j for j in neighbors[room] if depth.get(j) == now and j not in closed]):
                if try_door(shared[(room, other)]):
                    added[room] = now + 1
                    joined.add((min(room, other), max(room, other)))
                    break
        if not added:
            break
        depth.update(added)
        now += 1
    if any(i not in depth and i not in closed for i in range(room_count)):
        return None                           # a room could not be reached
    if depth and max(depth.values()) > limit:
        return None                           # a second deep room would appear

    # ── Step 4: Extra doorways ───────────────────────────────────────────
    # A few, between neighbors (never into the route).
    for i in range(room_count):
        for j in range(i + 1, room_count):
            if i in closed or j in closed:
                continue
            if (i, j) in shared and (i, j) not in joined and rng.random() < EXTRA_DOOR_CHANCE:
                try_door(shared[(i, j)])
    return doors, route


# ============================================================================
# GENERATOR - ENTRANCES
# ============================================================================

def entrance_spots(cells, box):
    """Places where a hallway meets the outer wall and an entrance fits, away from the corners.
    Returns (spots at the end of a hallway, spots along the side of a hallway)."""
    x0, y0, w, h = box
    hall_ends, other_spots = [], []
    for side in "NSWE":
        if side in "NS":
            y = y0 if side == "N" else y0 + h - 1
            line = [cells[(x, y)] == "H" for x in range(x0, x0 + w)]
        else:
            x = x0 if side == "W" else x0 + w - 1
            line = [cells[(x, y)] == "H" for y in range(y0, y0 + h)]

        def off_corner(s):
            return s >= ENTRANCE_CORNER_GAP and s + BUMP_WIDTH <= len(line) - ENTRANCE_CORNER_GAP

        i = 0
        while i < len(line):
            if not line[i]:
                i += 1
                continue
            j = i
            while j < len(line) and line[j]:
                j += 1
            if j - i == BUMP_WIDTH:
                if off_corner(i):
                    hall_ends.append((side, i))
            elif j - i > BUMP_WIDTH:
                other_spots.extend((side, s) for s in range(i, j - BUMP_WIDTH + 1) if off_corner(s))
            i = j
    return hall_ends, other_spots


def pick_entrances(rng, hall_ends, other_spots):
    """Choose 1 or 2 entrance spots. Hallway ends are used first."""
    pool = hall_ends or other_spots
    chosen = []
    for _ in range(rng.randint(*ENTRANCE_COUNT)):
        # A new entrance stays clear of the ones already placed on the same wall.
        pool = [(sd, s) for (sd, s) in pool
                if all(sd != cs or abs(s - c) >= BUMP_WIDTH + 2 for (cs, c) in chosen)]
        if not pool:
            break
        chosen.append(rng.choice(pool))
        pool = hall_ends + other_spots         # later entrances may use any hallway spot
    return chosen


def entrance_pieces(box, side, s):
    """The wall pieces to take out (gap) and to add (bump out) for one entrance."""
    x0, y0, w, h = box
    wide, deep = range(BUMP_WIDTH), range(BUMP_DEPTH)
    if side == "N":
        gx = x0 + s
        gap = [("h", gx + i, y0) for i in wide]
        bump = [("v", gx + k, y0 - 1 - d) for d in deep for k in (0, BUMP_WIDTH)]
    elif side == "S":
        gx, yb = x0 + s, y0 + h
        gap = [("h", gx + i, yb) for i in wide]
        bump = [("v", gx + k, yb + d) for d in deep for k in (0, BUMP_WIDTH)]
    elif side == "W":
        gy = y0 + s
        gap = [("v", x0, gy + i) for i in wide]
        bump = [("h", x0 - 1 - d, gy + k) for d in deep for k in (0, BUMP_WIDTH)]
    else:
        gy, xb = y0 + s, x0 + w
        gap = [("v", xb, gy + i) for i in wide]
        bump = [("h", xb + d, gy + k) for d in deep for k in (0, BUMP_WIDTH)]
    return gap, bump


# ============================================================================
# CHECKER
# ============================================================================

# Looks only at the finished level (squares + walls) and returns a list
# of problems. An empty list means the level passes.

def room_depths(level):
    """For each room: how many other rooms must be walked through to reach it from a hallway
    (or from the open floor on a small level). 0 = the room opens straight onto the hallway."""
    cells, walls = level.cells, level.walls
    links = {}
    for c, a in cells.items():
        for n in ((c[0] + 1, c[1]), (c[0], c[1] + 1)):
            b = cells.get(n)
            if b is None or b == a or edge_between(c, n) in walls:
                continue
            links.setdefault(a, set()).add(b)
            links.setdefault(b, set()).add(a)
    steps = {"H": 0, "S": 0}
    todo = ["H", "S"]
    while todo:
        nxt = []
        for a in todo:
            for b in links.get(a, ()):
                if b not in steps:
                    steps[b] = steps[a] + 1
                    nxt.append(b)
        todo = nxt
    return {thing: steps[thing] - 1 for thing in steps if isinstance(thing, int)}


def deep_room_depths(level):
    """The depths of the rooms that are as deep as a deep room (sorted). Empty on most levels."""
    return sorted(d for d in room_depths(level).values() if d >= DEEP_ROOM_WALK_THROUGH[0])


def check_level(level):
    use_size(level.size)                       # check against the settings of this level's map size
    problems = []
    cells, walls = level.cells, level.walls
    sx, sy = level.stair

    # ── Stairwell ────────────────────────────────────────────────────────
    # 4 x 4, in its spot, exactly one side open, nothing in front of the opening.
    if any(cells.get(c) != "S" for c in rect_cells((sx, sy, STAIR_SIZE, STAIR_SIZE))):
        problems.append("stairwell is not where it should be")
    if sum(1 for v in cells.values() if v == "S") != STAIR_SIZE * STAIR_SIZE:
        problems.append("stairwell is not 4 x 4")
    open_sides = []
    for side in "NSEW":
        closed = sum(1 for e in stair_side_edges(sx, sy, side) if e in walls)
        if closed == 0:
            open_sides.append(side)
        elif closed != STAIR_SIZE:
            problems.append("stairwell side %s is partly open" % side)
    if open_sides != [level.stair_side]:
        problems.append("stairwell must have exactly one open side")
    if any(cells.get(c) != "H" for c in stair_front(sx, sy, level.stair_side)):
        problems.append("something stands in front of the stairwell opening")

    # ── Rooms ────────────────────────────────────────────────────────────
    # Rectangles, at least 2 x 2, not too big, and not too many or too few.
    room_cells = {}
    for c, v in cells.items():
        if isinstance(v, int):
            room_cells.setdefault(v, []).append(c)
    long_max, short_max = LARGEST_ROOM[level.kind]
    for i, cs in room_cells.items():
        xs, ys = [c[0] for c in cs], [c[1] for c in cs]
        w, h = max(xs) - min(xs) + 1, max(ys) - min(ys) + 1
        if w * h != len(cs):
            problems.append("room %d is not a rectangle" % i)
        if min(w, h) < SMALLEST_ROOM:
            problems.append("room %d is smaller than 2 x 2" % i)
        if max(w, h) > long_max or min(w, h) > short_max:
            problems.append("room %d is too big" % i)
    fewest, most = room_count_range(level.kind, level.frame)
    if not fewest <= len(room_cells) <= most:
        problems.append("room count %d is out of range" % len(room_cells))
    if len(room_cells) > MAX_ROOMS_PER_FLOOR:
        problems.append("more than %d rooms on one floor" % MAX_ROOMS_PER_FLOOR)

    # ── Hallways and open floor ──────────────────────────────────────────
    # Never narrower than 2 squares.
    for (x, y), v in cells.items():
        if v != "H":
            continue
        if not any(all(cells.get((bx + i, by + j)) == "H" for i in (0, 1) for j in (0, 1))
                   for bx in (x - 1, x) for by in (y - 1, y)):
            problems.append("floor narrower than 2 squares at %d,%d" % (x, y))
            break

    # ── Every square can be reached ──────────────────────────────────────
    # From the stairwell, without crossing a wall.
    seen, todo = {(sx, sy)}, [(sx, sy)]
    while todo:
        c = todo.pop()
        for n in four_neighbors(c):
            if n in cells and n not in seen and edge_between(c, n) not in walls:
                seen.add(n)
                todo.append(n)
    if len(seen) != len(cells):
        problems.append("%d squares cannot be reached" % (len(cells) - len(seen)))

    # ── Walls and openings ───────────────────────────────────────────────
    # Walls sit between two different things (never through the middle of a room).
    # Openings: every place where a wall piece is missing between two different things.
    gaps = {}                                  # missing wall piece -> (the two things it joins, the two squares)
    for c, label in cells.items():
        for n in four_neighbors(c):
            e = edge_between(c, n)
            other = cells.get(n, "outside")
            if other == label:
                if e in walls:
                    problems.append("a wall runs through the middle of a space")
            elif e not in walls:
                gaps[e] = (frozenset((label, other)), (c, n))

    # Group the missing pieces into openings: straight, unbroken, joining the same two things.
    openings = []
    for kind, line, run in straight_runs(list(gaps)):
        current = []
        for p in run:
            piece = (kind, p, line) if kind == "h" else (kind, line, p)
            if current and gaps[piece][0] != gaps[current[-1]][0]:
                openings.append(current)
                current = []
            current.append(piece)
        openings.append(current)
    touching = {}
    entrances = 0
    for index, opening in enumerate(openings):
        things = gaps[opening[0]][0]
        if "outside" in things:
            entrances += 1
            if level.kind != "ground":
                problems.append("an opening in the outer wall on a level other than the ground level")
            if len(opening) != BUMP_WIDTH or things != frozenset(("H", "outside")):
                problems.append("an entrance is the wrong width or does not open onto a hallway")
        elif "S" in things:
            if things != frozenset(("S", "H")):
                problems.append("a room opens straight onto the stairwell")
        elif len(opening) > max(DOOR_WIDTHS):
            problems.append("a doorway is wider than allowed")
        for piece in opening:
            for point in piece_ends(piece):
                touching.setdefault(point, set()).add(index)
    if any(len(found) > 1 for found in touching.values()):
        problems.append("two openings touch")
    if level.kind == "ground" and not ENTRANCE_COUNT[0] <= entrances <= ENTRANCE_COUNT[1]:
        problems.append("the ground level has %d entrances" % entrances)

    # ── Entrances stay off the corners ───────────────────────────────────
    x0, y0, w, h = level.box
    for piece, (things, (c, n)) in gaps.items():
        if "outside" in things:
            inside = c if c in cells else n
            along, length = ((inside[0] - x0, w) if piece[0] == "h" else (inside[1] - y0, h))
            if along < ENTRANCE_CORNER_GAP or along > length - 1 - ENTRANCE_CORNER_GAP:
                problems.append("an entrance is against a corner")

    # ── Every room has a doorway ─────────────────────────────────────────
    for i in room_cells:
        if not any(i in things for things, _ in gaps.values()):
            problems.append("room %d has no doorway" % i)

    # ── No loose wall pieces ─────────────────────────────────────────────
    # A loose piece is a straight wall with both ends attached to nothing.
    at_point = {}
    for e in walls:
        for point in piece_ends(e):
            at_point.setdefault(point, []).append(e)
    seen_walls = set()
    for e in walls:
        if e in seen_walls:
            continue
        group = [e]
        seen_walls.add(e)
        i = 0
        while i < len(group):
            for point in piece_ends(group[i]):
                for other in at_point[point]:
                    if other not in seen_walls:
                        seen_walls.add(other)
                        group.append(other)
            i += 1
        if len({piece[0] for piece in group}) == 1:
            problems.append("a wall piece is attached to nothing")

    # ── Side hallways ────────────────────────────────────────────────────
    # Hallways are where the level says they are, and every side hallway has an opening.
    for index, rect in enumerate(level.halls):
        squares = set(rect_cells(rect))
        if any(cells.get(c) != "H" for c in squares):
            problems.append("a hallway is not where it should be")
        if index > 0 and not any((c in squares and cells.get(n) != "H") or (n in squares and cells.get(c) != "H")
                                 for _, (c, n) in gaps.values()):
            problems.append("a side hallway has no doorway on it")

    # ── Deep room ────────────────────────────────────────────────────────
    # Rooms behind rooms: only the route to the deep room may be deep.
    depths = room_depths(level)
    low, high = DEEP_ROOM_WALK_THROUGH
    deep = sorted(d for d in depths.values() if d >= low)
    if level.route:
        walk = len(level.route) - 1
        if deep != list(range(low, walk + 1)) or not low <= walk <= high:
            problems.append("the deep room is not reached by walking through %d to %d rooms" % (low, high))
        if [depths.get(room) for room in level.route] != list(range(walk + 1)):
            problems.append("the route to the deep room has a shortcut")
    elif deep:
        problems.append("a room is %d rooms deep on a level with no deep room" % deep[-1])
    return problems


def check_hideout(levels):
    """Checks one whole map: every level, the stairwell spot, the deep room, and the stack of floors."""
    problems = ["level %d: %s" % (lv.number, p) for lv in levels for p in check_level(lv)]
    use_size(levels[0].size)                   # check against the settings of this map's size
    if len({lv.size for lv in levels}) != 1:
        problems.append("the levels are not all of one map size")
    if len({lv.stair for lv in levels}) != 1:
        problems.append("the stairwell is not in the same spot on every level")
    if len({lv.frame for lv in levels}) != 1:
        problems.append("the levels do not share one footprint")

    # ── Deep room ────────────────────────────────────────────────────────
    # Exactly one on a size that has a deep room, none on a size that does not.
    with_deep_room = [lv.number for lv in levels if deep_room_depths(lv)]
    wanted = 1 if HAS_DEEP_ROOM else 0
    if len(with_deep_room) != wanted:
        problems.append("the map must have %d deep room(s); %d levels have one" % (wanted, len(with_deep_room)))

    # ── Stack of floors ──────────────────────────────────────────────────
    # One ground level, it is shown first, every level is inside the
    # hideout's footprint, and above the ground no floor sticks out past the floor under it.
    stack = sorted(levels, key=lambda lv: -lv.number)          # top floor first
    if len({lv.number for lv in levels}) != len(levels):
        problems.append("two levels have the same number")
    grounds = [i for i, lv in enumerate(stack) if lv.kind == "ground"]
    if len(grounds) != 1:
        problems.append("the map must have exactly one ground level; it has %d" % len(grounds))
    else:
        if levels[0].kind != "ground":
            problems.append("the ground level is not the first level shown")
        for i, lv in enumerate(stack):
            x, y, w, h = lv.box
            if x < 0 or y < 0 or x + w > lv.frame[0] or y + h > lv.frame[1]:
                problems.append("level %d sticks out past the hideout's footprint" % lv.number)
            if i < grounds[0]:                                 # above the ground
                under = stack[i + 1]
                ux, uy, uw, uh = under.box
                if x < ux or y < uy or x + w > ux + uw or y + h > uy + uh:
                    problems.append("level %d sticks out past level %d under it" % (lv.number, under.number))

        # The stack is one of FLOOR_PLANS, numbered 1, then 2, 3, ... going up and -2, -3, ... going down.
        going_up = stack[:grounds[0]][::-1]
        going_down = stack[grounds[0] + 1:]
        if (len(going_up), len(going_down)) not in [tuple(plan) for plan in FLOOR_PLANS]:
            problems.append("%d floors above the ground and %d below is not one of FLOOR_PLANS"
                            % (len(going_up), len(going_down)))
        if ([lv.number for lv in going_up] != list(range(2, 2 + len(going_up)))
                or [lv.number for lv in going_down] != list(range(-2, -2 - len(going_down), -1))
                or stack[grounds[0]].number != 1):
            problems.append("the levels are not numbered 1, then 2, 3, ... above and -2, -3, ... below")

        # Large floors: an allowed count, each next to the ground level or another large floor.
        large = sum(1 for lv in levels if lv.kind != "small")
        if LARGE_FLOOR_CHANCES.get(large, 0) <= 0:
            problems.append("%d large floors is not a count in LARGE_FLOOR_CHANCES" % large)
        for floors, large_kind in ((going_up, "upper"), (going_down, "lower")):
            kinds = [lv.kind for lv in floors]
            count = sum(1 for kind in kinds if kind == large_kind)
            if kinds != [large_kind] * count + ["small"] * (len(kinds) - count):
                problems.append("a large floor is not next to the ground level or another large floor")
    return problems


# ============================================================================
# RENDERER
# ============================================================================

# Every picture of one map is the same size, and the stairwell lands on the
# same pixels in every picture. The picture size depends on the map size
# (LARGE_WIDTH and LARGE_HEIGHT in SIZES).

def get_font(size):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:                     # older Pillow
        pass
    for path in ("/System/Library/Fonts/Helvetica.ttc", "/Library/Fonts/Arial.ttf"):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()


def header_text(level, map_number):
    text = "Level %d" % level.number
    if level.kind == "ground":
        text += " - ground level - has the exterior entrance"
    if SHOW_MAP_NUMBER_IN_HEADER:
        # The size is shown with the number: the two together remake the map.
        text += "     %s map %d" % (level.size.capitalize(), map_number)
    return text


def render_level(level, map_number, with_grid, grid_over_walls=None):
    use_size(level.size)                       # draw with the settings of this level's map size
    if grid_over_walls is None:
        grid_over_walls = GRID_OVER_WALLS
    S = PIXELS_PER_SQUARE
    columns = LARGE_WIDTH + 2 * MARGIN_SQUARES
    rows = HEADER_SQUARES + LARGE_HEIGHT + 2 * MARGIN_SQUARES
    image = Image.new("RGB", (columns * S, rows * S), BACKGROUND_COLOR)    # a whole number of squares
    draw = ImageDraw.Draw(image)
    # A footprint smaller than LARGE_WIDTH x LARGE_HEIGHT is centered in the picture.
    shift_x = (LARGE_WIDTH - level.frame[0]) // 2
    shift_y = (LARGE_HEIGHT - level.frame[1]) // 2
    left = (MARGIN_SQUARES + shift_x) * S                       # pixel where square x=0 starts
    top = (HEADER_SQUARES + MARGIN_SQUARES + shift_y) * S       # pixel where square y=0 starts

    def draw_grid():
        for x in range(0, image.width, S):
            draw.line([(x, 0), (x, image.height - 1)], fill=GRID_COLOR, width=1)
        for y in range(0, image.height, S):
            draw.line([(0, y), (image.width - 1, y)], fill=GRID_COLOR, width=1)

    if with_grid and not grid_over_walls:
        draw_grid()

    # ── Walls ────────────────────────────────────────────────────────────
    # A black bar centered on the grid line for each wall piece.
    across_at, down_at = {}, {}       # corner point -> thickness of walls meeting there
    for e in level.walls:
        kind, x, y = e
        t = OUTER_WALL_PIXELS if e in level.outer else INNER_WALL_PIXELS
        lo, hi = t // 2, t - t // 2 - 1
        if kind == "h":
            py = top + y * S
            draw.rectangle([left + x * S, py - lo, left + (x + 1) * S, py + hi], fill=WALL_COLOR)
            for corner in ((x, y), (x + 1, y)):
                across_at[corner] = max(across_at.get(corner, 0), t)
        else:
            px = left + x * S
            draw.rectangle([px - lo, top + y * S, px + hi, top + (y + 1) * S], fill=WALL_COLOR)
            for corner in ((x, y), (x, y + 1)):
                down_at[corner] = max(down_at.get(corner, 0), t)
    # Square off the corners where an up-down wall meets a left-right wall.
    for corner, tv in down_at.items():
        th = across_at.get(corner)
        if th:
            px, py = left + corner[0] * S, top + corner[1] * S
            draw.rectangle([px - tv // 2, py - th // 2,
                            px + tv - tv // 2 - 1, py + th - th // 2 - 1], fill=WALL_COLOR)

    # ── Stair step lines ─────────────────────────────────────────────────
    # Thin lines parallel to the open side, STAIR_STEPS_PER_SQUARE of them per square.
    if SHOW_STAIR_STEPS and level.stair:
        sx, sy = level.stair
        t = STAIR_STEP_PIXELS
        lo, hi = t // 2, t - t // 2 - 1
        n = STAIR_STEPS_PER_SQUARE
        for i in range(1, STAIR_SIZE * n):
            step = (i * S) // n                      # pixels from the stairwell's edge to this line
            if level.stair_side in ("W", "E"):       # opening on the left or right: up-down lines
                px = left + sx * S + step
                draw.rectangle([px - lo, top + sy * S, px + hi, top + (sy + STAIR_SIZE) * S], fill=WALL_COLOR)
            else:                                    # opening on the top or bottom: left-right lines
                py = top + sy * S + step
                draw.rectangle([left + sx * S, py - lo, left + (sx + STAIR_SIZE) * S, py + hi], fill=WALL_COLOR)

    if with_grid and grid_over_walls:
        draw_grid()

    # ── Header text ──────────────────────────────────────────────────────
    # The font shrinks when the text is wider than the picture (the small map's pictures are narrow).
    text = header_text(level, map_number)
    font_pixels = HEADER_FONT_PIXELS
    font = get_font(font_pixels)
    while font_pixels > 12 and draw.textlength(text, font=font) > image.width - S:
        font_pixels -= 2
        font = get_font(font_pixels)
    draw.text((S // 2, (HEADER_SQUARES * S - font_pixels) // 2), text, fill=WALL_COLOR, font=font)
    return image


def render_hideout(levels, map_number):
    """Returns {level number: {"grid": picture, "walls": picture}}.
    The pictures keep the order of the levels: the ground level is first."""
    return {lv.number: {"grid": render_level(lv, map_number, True),
                        "walls": render_level(lv, map_number, False)} for lv in levels}


def sheet_across(count, w, h, space_width, space_height):
    """How many pictures go side by side on the sheet (SHEET_ACROSS of the size in use).
    count = how many pictures, w x h = the size of one picture,
    space_width x space_height = the space the sheet must fit in."""
    if SHEET_ACROSS != "fit":
        return min(SHEET_ACROSS, count)
    # ── "fit": try every number across, keep the one that shows them biggest ──
    best, best_scale = 1, 0
    for across in range(1, count + 1):
        down = (count + across - 1) // across
        scale = min(space_width / (w * across), space_height / (h * down))
        if scale > best_scale:
            best, best_scale = across, scale
    return best


def make_preview(pictures, size, max_width=None, max_height=None):
    """All grid pictures on one sheet, shrunk to fit max_width x max_height.
    Without a max size the sheet is full size (for the saved overview).
    The pictures go left to right, then down. The first picture goes top-left,
    and the first picture is always the ground level."""
    use_size(size)                             # SHEET_ACROSS of this map size
    grids = [both["grid"] for both in pictures.values()]
    w, h = grids[0].size
    if max_width is None:
        across = sheet_across(len(grids), w, h, *OVERVIEW_SHAPE)
    else:
        across = sheet_across(len(grids), w, h, max_width, max_height)
    down = (len(grids) + across - 1) // across
    sheet = Image.new("RGB", (w * across, h * down), BACKGROUND_COLOR)
    for i, g in enumerate(grids):
        sheet.paste(g, ((i % across) * w, (i // across) * h))
    if max_width is not None:
        sheet.thumbnail((max_width, max_height))
    return sheet


# ============================================================================
# SAVING FILES
# ============================================================================

def file_names(folder, name, numbers):
    """The file paths for one map: name + level number + grid or walls, plus one overview.
    numbers = the level numbers of this map (they differ with where the ground level sits)."""
    names = {(number, style): os.path.join(folder, "%s_level_%d_%s.jpg" % (name, number, style))
             for number in numbers for style in ("walls", "grid")}
    names["overview"] = os.path.join(folder, "%s_overview.jpg" % name)
    return names


def save_hideout(pictures, size, folder, name):
    """Saves a grid and a walls picture per level, plus the overview. Returns how many files were saved."""
    names = file_names(folder, name, list(pictures))
    for key, path in names.items():
        if key == "overview":
            # All the grid pictures on one sheet, as the window shows them, at full size.
            picture = make_preview(pictures, size)
        else:
            number, style = key
            picture = pictures[number][style]
        # subsampling=0 keeps thin colored lines (the grid) their true color in the JPG
        picture.save(path, "JPEG", quality=JPG_QUALITY, subsampling=0)
    return len(names)


# Words for the window and the test report.
GROUND_PLACE_WORDS = {"top": "the top floor (the other levels are below it)",
                      "middle": "in the middle (levels above and below it)",
                      "bottom": "the bottom floor (the other levels are above it)",
                      "only": "the only floor"}
# The same words for a map with just one other level (the small map: 2 floors).
GROUND_PLACE_WORDS_ONE_OTHER = {"top": "the top floor (the other level is below it)",
                                "bottom": "the bottom floor (the other level is above it)"}


def new_map_number():
    return random.SystemRandom().randint(1, 10 ** MAP_NUMBER_DIGITS - 1)


# ============================================================================
# FRONT END (THE WINDOW)
# ============================================================================

def run_window(first_map_number=None, first_size=None):
    """Opens the window. With a map number or a size, that map is shown as the window opens."""
    import tkinter as tk                      # Tkinter, comes with the standard Python installer
    from tkinter import filedialog, messagebox
    from PIL import ImageTk

    root = tk.Tk()
    root.title("Hideout map generator - version 1.1")
    wrong = check_settings()
    if wrong:
        messagebox.showerror("Settings problem", "\n".join(wrong))
        root.destroy()
        return
    state = {"number": None, "size": None, "pictures": None, "sheet": None, "refit": None}

    # ── Window size ──────────────────────────────────────────────────────
    # Fill the screen, or use the size set in SETTINGS.
    root.minsize(700, 450)
    if WINDOW_OPENS_FULL:
        try:
            root.state("zoomed")              # maximized on Mac and Windows
        except tk.TclError:                   # some systems have no "zoomed"; fill the screen by hand
            root.geometry("%dx%d+0+0" % (root.winfo_screenwidth(), root.winfo_screenheight() - 80))
    else:
        root.geometry("%dx%d" % WINDOW_START_SIZE)

    # ── Top bar ──────────────────────────────────────────────────────────
    # Row 1: one map button per size. Row 2: the save question and the map number.
    # Always on screen.
    bar = tk.Frame(root)
    bar.pack(side="top", fill="x", padx=8, pady=6)
    button_row = tk.Frame(bar)
    button_row.pack(side="top", fill="x")
    size_buttons = {}
    for size in SIZES:
        size_buttons[size] = tk.Button(button_row, text=SIZES[size]["BUTTON_TEXT"], font=("Helvetica", 18))
        size_buttons[size].pack(side="left", padx=(0, 10))
    info_row = tk.Frame(bar)
    info_row.pack(side="top", fill="x", pady=(6, 0))
    info = tk.Label(info_row, text=MAP_BUTTON_HINT)
    info.pack(side="left")
    question = tk.Frame(info_row)             # shown only while there is a map to save
    tk.Label(question, text="Do you want to save the generated map?").pack(side="left", padx=6)
    yes_button = tk.Button(question, text="Yes")
    yes_button.pack(side="left")
    no_button = tk.Button(question, text="No")
    no_button.pack(side="left")

    # ── Preview area ─────────────────────────────────────────────────────
    # The preview fills the rest of the window. The picture is centered in it with
    # place(), so a new picture never changes the size of the area it sits in.
    area = tk.Frame(root)
    area.pack(side="top", fill="both", expand=True, padx=8, pady=(0, 8))
    preview = tk.Label(area)
    preview.place(relx=0.5, rely=0.5, anchor="center")

    # ── Preview helpers ──────────────────────────────────────────────────
    def show_question(on):
        if on:
            # Placed before the map number, so a narrow window never cuts the Yes / No buttons off.
            question.pack(side="left", padx=(0, 12), before=info)
        else:
            question.pack_forget()

    def clear_preview():
        preview.config(image="")
        preview.image = None
        state["sheet"] = None

    def fit_preview():
        """Lay out the sheet and shrink it to fit the preview area right now."""
        state["refit"] = None
        if state["sheet"] is None:
            return
        width, height = area.winfo_width(), area.winfo_height()
        if width < 50 or height < 50:         # the window is not laid out yet
            return
        # Laid out again on every resize: on a "fit" size the number across depends on the space.
        shown = make_preview(state["sheet"], state["size"], width, height)
        photo = ImageTk.PhotoImage(shown)
        preview.config(image=photo)
        preview.image = photo                 # keeps the picture from being thrown away

    def on_resize(event):
        # Wait until the resizing pauses, then refit once.
        if state["refit"] is not None:
            root.after_cancel(state["refit"])
        state["refit"] = root.after(150, fit_preview)

    # ── Button actions ───────────────────────────────────────────────────
    def map_name():
        """The map on screen, in words: its size and number."""
        return "%s map number: %d" % (state["size"].capitalize(), state["number"])

    def on_go(size, number=None):
        """Make and show a map of one size. Without a number, a new map number is picked."""
        number = number or new_map_number()
        try:
            levels = make_hideout(number, size)
            pictures = render_hideout(levels, number)
        except RuntimeError as problem:       # the settings could not be met
            messagebox.showerror("No map was made", str(problem))
            show_question(False)              # nothing is left on screen to save
            clear_preview()
            state["number"], state["size"], state["pictures"] = None, None, None
            info.config(text="No map was made. See the message.")
            return
        state["number"], state["size"], state["pictures"] = number, size, pictures
        state["sheet"] = pictures             # fit_preview lays these out for the space there is
        root.update_idletasks()               # make sure the window size is known
        fit_preview()
        place = levels[0].ground_place
        # Where the ground level sits on the sheet. When every level fits in one row
        # (the small map: 2 levels, 2 across) nothing is below it, so "top" is left out.
        use_size(size)
        one_row = SHEET_ACROSS != "fit" and len(levels) <= SHEET_ACROSS
        corner = "left" if one_row else "top left"
        # Two floors in all = one other level, so the words in brackets are singular.
        words = GROUND_PLACE_WORDS_ONE_OTHER if len(levels) == 2 else GROUND_PLACE_WORDS
        info.config(text="%s     Ground level (%s) is %s"
                         % (map_name(), corner, words.get(place, GROUND_PLACE_WORDS.get(place, place))))
        show_question(True)

    def on_yes():
        path = filedialog.asksaveasfilename(title="Type a name for this map and pick a folder")
        if not path:
            return                            # the user pressed Cancel
        folder, name = os.path.split(path)
        if name.lower().endswith((".jpg", ".jpeg")):
            name = name.rsplit(".", 1)[0]     # drop a typed picture ending; other periods stay
        already = [p for p in file_names(folder, name, list(state["pictures"])).values() if os.path.exists(p)]
        if already and not messagebox.askyesno(
                "Replace files?", "%d files with this name already exist. Replace them?" % len(already)):
            return
        try:
            saved = save_hideout(state["pictures"], state["size"], folder, name)
        except OSError as problem:            # for example: the folder cannot be written to
            messagebox.showerror("The map was not saved", str(problem))
            info.config(text="%s - NOT saved. See the message." % map_name())
            return
        info.config(text="%s - saved %d files in %s" % (map_name(), saved, folder))
        show_question(False)

    def on_no():
        show_question(False)
        clear_preview()
        info.config(text="Not saved. " + MAP_BUTTON_HINT)

    # ── Connect the buttons and start ────────────────────────────────────
    for size, button in size_buttons.items():
        button.config(command=lambda size=size: on_go(size))       # each button makes its own size
    yes_button.config(command=on_yes)
    no_button.config(command=on_no)
    area.bind("<Configure>", on_resize)
    if first_map_number or first_size:
        # A map was asked for on the command line: show it once the window is up.
        root.after(200, lambda: on_go(first_size or DEFAULT_SIZE, first_map_number))
    root.mainloop()


# ============================================================================
# TEST AND BATCH
# ============================================================================

def run_test(how_many, sizes):
    """Make a batch of maps of each size in `sizes` and check each one against every rule
    in the checker. Returns how many maps failed."""
    return sum(test_one_size(how_many, size) for size in sizes)


def test_one_size(how_many, size):
    """Make and check `how_many` maps of one size, and print a report. Returns how many failed."""
    from PIL import ImageChops
    failed = 0
    layouts = set()
    walks, deep_on, places, larges, floors = {}, {}, {}, {}, {}
    most_tries, total_tries = 0, 0
    for number in range(1, how_many + 1):
        levels = make_hideout(number, size)
        problems = check_hideout(levels)
        if any(lv.size != size for lv in levels):
            problems.append("the map is not the size that was asked for")
        if [(lv.number, lv.kind) for lv in make_hideout(number, size)] != [(lv.number, lv.kind) for lv in levels]:
            problems.append("the same size and number did not give the same floors")
        place = levels[0].ground_place
        places[place] = places.get(place, 0) + 1
        large = sum(1 for lv in levels if lv.kind != "small")
        larges[large] = larges.get(large, 0) + 1
        floors[len(levels)] = floors.get(len(levels), 0) + 1
        for lv in levels:
            if lv.route:
                walks[len(lv.route) - 1] = walks.get(len(lv.route) - 1, 0) + 1
                deep_on[lv.number] = deep_on.get(lv.number, 0) + 1
        if number <= 3:      # compare the two pictures of each level, pixel by pixel
            for lv in levels:
                black = [render_level(lv, number, g, False).convert("L").point(lambda v: 255 if v == 0 else 0)
                         for g in (True, False)]
                if ImageChops.difference(black[0], black[1]).getbbox() is not None:
                    problems.append("walls picture and grid picture do not line up")
        if problems:
            failed += 1
            print("%s map %d FAILED: %s" % (size.capitalize(), number, "; ".join(sorted(set(problems)))))
        layouts.add(tuple(tuple(sorted(lv.walls)) for lv in levels))
    print("%s: %d maps made. %d failed the checks. %d different layouts."
          % (size.upper(), how_many, failed, len(layouts)))
    print("    Floors -> maps: %s." % dict(sorted(floors.items())))
    print("    Large floors -> maps: %s." % dict(sorted(larges.items())))
    print("    Ground level place -> maps: %s." % dict(sorted(places.items())))
    if walks:
        print("    Deep room: rooms walked through -> maps: %s. Level it is on -> maps: %s."
              % (dict(sorted(walks.items())), dict(sorted(deep_on.items()))))
    else:
        print("    Deep room: none (HAS_DEEP_ROOM is off for this size).")
    return failed


def run_batch(how_many, folder, size):
    """Make and save many maps of one size without the window.
    Each map is named hideout_<size>_<map number>."""
    os.makedirs(folder, exist_ok=True)
    used = set()
    files = 0
    for count in range(1, how_many + 1):
        number = new_map_number()
        while number in used:
            number = new_map_number()
        used.add(number)
        files += save_hideout(render_hideout(make_hideout(number, size), number), size,
                              folder, "hideout_%s_%d" % (size, number))
        print("%d of %d saved: %s map %d" % (count, how_many, size, number))
    print("Done. %d maps (%d files) are in %s" % (how_many, files, os.path.abspath(folder)))


# ============================================================================
# COMMAND LINE AND START
# ============================================================================

HOW_TO = """How to run (a size word is small, medium or large):
    python3 hideout_generator_v1.1.py                        window with the three map buttons
    python3 hideout_generator_v1.1.py large 123456789012345  window showing that map (no size word = medium)
    python3 hideout_generator_v1.1.py --test 200             no window; make 200 maps of each size and check them
    python3 hideout_generator_v1.1.py --test 200 small       the same for one size
    python3 hideout_generator_v1.1.py --batch 50 maps large  no window; save 50 large maps in the folder "maps"
                                                             (no size word = medium) """


def main(arguments):
    # ── Step 1: Work out what was asked for ──────────────────────────────
    # A size word may stand anywhere on the line. It is taken out first.
    size = None
    words = []
    for word in arguments:
        if size is None and word.lower() in SIZES:
            size = word.lower()
        else:
            words.append(word)
    mode, number, folder = "window", None, None
    try:
        if words and words[0] == "--test":
            if len(words) > 2:
                raise ValueError
            mode, number = "test", (int(words[1]) if len(words) > 1 else 100)
        elif words and words[0] == "--batch":
            if len(words) != 3:
                raise ValueError
            mode, number, folder = "batch", int(words[1]), words[2]
        elif words:
            number = int(words[0])
            if number < 1 or len(words) != 1:
                raise ValueError
    except ValueError:
        print(HOW_TO)
        return 1

    # ── Step 2: Check the SETTINGS before doing any work ─────────────────
    wrong = check_settings()
    if wrong:
        print("Settings problem:\n  " + "\n  ".join(wrong))
        if mode != "window":
            return 1                          # (the window shows the same message in a box)

    # ── Step 3: Do it ────────────────────────────────────────────────────
    try:
        if mode == "test":
            if run_test(number, [size] if size else list(SIZES)):
                return 1
        elif mode == "batch":
            run_batch(number, folder, size or DEFAULT_SIZE)
        else:
            run_window(number, size)
    except RuntimeError as problem:           # no map could be made with these settings
        print(problem)
        return 1
    except OSError as problem:                # for example: the folder cannot be written to
        print("Files could not be saved: %s" % problem)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
