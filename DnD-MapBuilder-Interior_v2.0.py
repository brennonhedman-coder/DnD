#!/usr/bin/env python3
# ============================================================================
# DnD-MapBuilder-Interior_v2.0.py
# ============================================================================

"""
.SYNOPSIS
    Tkinter window that makes random floor plans (walls only) for a
    building, a hideout or a dungeon, and saves them as JPG files.

.DESCRIPTION
    Print and play floor plans for tabletop games. One click makes a whole
    map, shows it in the window and asks whether to save it.

    The window:
      - Three buttons at the top: "Building", "Hideout" and "Dungeon". Each
        click makes a new map straight away
      - The seed box is under the buttons. Leave it empty for a new map, or
        type a seed to get that map back
      - The line of text under the seed box says what was made. It can be
        selected and copied, so the seed can be kept
      - While a map is waiting to be saved, the question "Do you want to
        save the generated map?" shows with white "Yes" and "No" buttons.
        A dungeon also gets a white "Open full size" button, which opens
        the preview in your picture viewer
      - The window follows the Mac's light or dark look; the save buttons
        stay white either way
      - The black preview area fills the rest of the window and the map is
        fitted to it again whenever the window changes size

    Every map:
      - Each map has a seed, a string of digits. The same seed always makes
        the same map, because the script uses its own whole-number dice
        (Dice) and never the standard "random" module
      - Floors are cut into rectangular rooms of 3 x 3 squares or more.
        Every room can be reached: doorways join them all, and between
        rooms that are already joined, 1 wall in 6 gets a second doorway
      - Doorways are 1 square wide. Entrances and exits are never at a
        corner
      - No try-again loops: each map is built once, straight from the seed

    Building:
      - One floor with no stairs. 1 time in 10 it is a full 17 x 13 floor
        of 6 to 11 rooms; otherwise its width is 4 to 17 squares and its
        height 4 to 13, with fewer rooms on smaller floors (about 1 room
        per 20 squares, at most 11)
      - An entrance on the south, west or east wall. Half of them also get
        an exit on a different wall

    Hideout:
      - 3, 4, 5 or 6 levels, equal odds. Ground is level 1, always 17 x 13
        squares with 6 to 11 rooms, an entrance and, half the time, an exit
      - Each level after ground goes up or down on a coin flip, with at
        most 3 above ground (2, 3, 4). The rest go below: -2, -3 ... -6
      - Upper levels fit inside the level below them, and basement levels
        inside the level above them. Each is 4 x 4 squares or more
      - One 2 x 2 stairwell sits in the same spot on every level, so the
        levels line up. No wall is ever cut through it

    Dungeon:
      - 15 to 99 rooms. Each room count is weighted 1 / (rooms x rooms), so
        small dungeons are much more likely: about 6 in 10 have fewer than
        30 rooms
      - The rooms sit on an even grid of slots, 21 x 17 squares each,
        numbered in reading order (left to right, top to bottom). Each room
        is 7 x 5 to 17 x 13 squares, placed at random in its slot with at
        least 2 squares of bare rock round it
      - Rooms next to each other in the grid are joined: a random set of
        links joins every room, and 1 in 4 of the other neighbour pairs
        adds a loop
      - Each corridor is 1 square wide and bends at most twice: out of a
        doorway, along the gap between the slots, and into the next room's
        doorway. Every corridor joins exactly two rooms and none cross
      - The entrance (IN) comes in from the west edge into room 1. The exit
        (OUT) leaves the last room to the east edge
      - Every room is cut into 2 or more inner rooms (up to 11), joined by
        doorways the same way as a building

    Pictures:
      - Floor and room sheets use 70 x 70 pixel squares. Each sheet is the
        floor plus a 1 square margin all round, with a header row on top
        (kind, level or room, seed). Entrances, exits and corridor doorways
        show as a 1 x 1 bump out into the margin
      - Each sheet is saved twice: walls only, and walls with the blue grid
        inside the floor
      - The hideout overview shows every level in 2 rows, each drawn where
        it sits over the ground level: 2 across for 3 or 4 levels, 3 across
        for 5 or 6. The stairwell shows as staggered dashed tread lines
      - The dungeon overview is 20 pixels per square: white, with the blue
        grid inside rooms and corridors only, black walls, room numbers and
        the IN and OUT marks
      - A building saves 2 JPGs. A hideout saves 2 per level plus the
        overview. A dungeon saves the overview, 2 per room and a room key
        text file that lists every doorway, its corridor length and where
        it leads

    Lines that start with "#" are notes for people. Python ignores them.

.NOTES
    Author : Brennon Hedman
    Version: 2.0
    Requires: Python 3.8+ and Pillow 10.1+ (python3 -m pip install pillow)
    Platform: macOS, Windows or Linux (the window uses Tkinter, which comes
              with the standard Python installer)

.EXAMPLE
    python3 DnD-MapBuilder-Interior_v2.0.py

    Opens the window with the three buttons.

.EXAMPLE
    python3 DnD-MapBuilder-Interior_v2.0.py 123456789012345

    Opens the window already showing the hideout with seed 123456789012345.

.EXAMPLE
    python3 DnD-MapBuilder-Interior_v2.0.py 123456789012345 dungeon

    The same, for another kind: building, hideout or dungeon.
"""

import os
import sys
import time
from PIL import Image, ImageDraw, ImageFont


# ============================================================================
# SETTINGS
# ============================================================================

SQ, GW, GH = 70, 17, 13          # pixels per square on a sheet; the ground
                                 # (and largest) floor is 17 x 13 squares
SW, SH = GW + 4, GH + 4          # one dungeon slot: the largest room plus 2
                                 # squares of rock on every side
OUTER, INNER, TREAD = 7, 3, 14   # pixels: outer walls, inner walls, and the
                                 # gap between stair tread lines
BLACK, WHITE, BLUE = (0, 0, 0), (255, 255, 255), (140, 190, 255)
LABELS = {"building": "Building", "hideout": "Hideout", "dungeon": "Dungeon"}
                                 # each kind: its command-line word and the
                                 # label on its button and headers
SAVE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Maps")
                                 # saved maps go in "Maps", next to this script
STEP = {"N": (0, -1), "S": (0, 1), "W": (-1, 0), "E": (1, 0)}
                                 # one square out through each side
WALL = {"N": "north", "S": "south", "W": "west", "E": "east"}
FAR = {"N": "S", "S": "N", "W": "E", "E": "W"}
                                 # the opposite side
M64 = (1 << 64) - 1              # keeps the dice maths to 64 bits


# ============================================================================
# SEED DICE
# ============================================================================

# Our own random numbers ("splitmix64"). Only whole-number maths, so a seed
# gives the same rolls on every computer and every Python version.

class Dice:
    def __init__(self, seed):
        self.s = int(seed) & M64

    def below(self, n):
        # A whole number from 0 to n - 1.
        self.s = (self.s + 0x9E3779B97F4A7C15) & M64
        z = ((self.s ^ (self.s >> 30)) * 0xBF58476D1CE4E5B9) & M64
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & M64
        return (z ^ (z >> 31)) % n

    def between(self, a, b):
        # A whole number from a to b, both included.
        return a + self.below(b - a + 1)

    def pick(self, items):
        return items[self.below(len(items))]

    def shuffle(self, items):
        for i in range(len(items) - 1, 0, -1):
            j = self.below(i + 1)
            items[i], items[j] = items[j], items[i]
        return items


# ============================================================================
# MAP DATA
# ============================================================================

# Squares are named (x, y), counted from the top left square of the ground
# floor (or of the dungeon, or of one dungeon room). A wall piece is one
# square long and sits on a grid line:
#   ("h", x, y)  runs along the top edge of square (x, y)
#   ("v", x, y)  runs along the left edge of square (x, y)

class Floor:
    # One floor: a building, a hideout level, or the inside of a dungeon room.
    def __init__(self, number, rect, stair):
        self.number, (self.x, self.y, self.w, self.h), self.stair = number, rect, stair
        self.cell, self.doors, self.openings, self.rooms = {}, set(), [], 0
        # cell: (x, y) -> room number. doors: wall pieces left open.
        # openings: (x, y, side) of each entrance, exit or corridor doorway.


class Room:
    # One dungeon room: its place in the dungeon and its doorways, each
    # (side, x, y, the room or "IN" / "OUT" it leads to, corridor length).
    def __init__(self, number, x, y, w, h):
        self.number, self.x, self.y, self.w, self.h = number, x, y, w, h
        self.doors = []


class Map:
    # A whole map. A building or hideout has floors; a dungeon has rooms,
    # corridor squares (halls), links between rooms and its IN / OUT ends.
    def __init__(self, kind, seed, floors=(), rooms=(), size=None):
        self.kind, self.seed, self.floors, self.rooms, self.size = kind, seed, list(floors), list(rooms), size
        self.halls, self.links, self.ways = set(), [], []


# ============================================================================
# FLOOR BUILDER
# ============================================================================

def room_target(d, w, h, least=1):
    # How many rooms to aim for: about 1 per 20 squares, at most 11, rolled
    # between half that and all of it.
    most = max(least, min(11, w * h // 20))
    return d.between(max(least, (most + 1) // 2), most)


def holds_stair(block, stair):
    # True if the whole 2 x 2 stairwell is inside this block.
    x, y, w, h = block
    return stair and x <= stair[0] and stair[0] + 2 <= x + w and y <= stair[1] and stair[1] + 2 <= y + h


def cuts(block, stair, axis):
    # Every line a block can be cut along (axis 0 = up and down, 1 = across)
    # that leaves both parts 3 squares or more and never splits the stairwell.
    start, size = block[axis], block[axis + 2]
    s = stair[axis] if holds_stair(block, stair) else None
    return [c for c in range(start + 3, start + size - 2) if s is None or not s < c < s + 2]


def make_floor(d, number, rect, stair, target, exits):
    f = Floor(number, rect, stair)

    # ── Cut the floor into rooms ───────────────────────────────────────
    # Bigger blocks are more likely to be picked. Each is cut across its
    # long side when it can be. Stops at the target or when nothing can
    # be cut any more.
    blocks = [rect]
    while len(blocks) < target:
        open_ = [(i, b) for i, b in enumerate(blocks) if cuts(b, stair, 0) or cuts(b, stair, 1)]
        if not open_:
            break
        roll = d.below(sum(b[2] * b[3] for _, b in open_))
        for i, b in open_:
            roll -= b[2] * b[3]
            if roll < 0:
                break
        x, y, w, h = b
        axis = 0 if w >= h else 1
        if not cuts(b, stair, axis):
            axis = 1 - axis
        c = d.pick(cuts(b, stair, axis))
        blocks[i:i + 1] = [(x, y, c - x, h), (c, y, x + w - c, h)] if axis == 0 else [(x, y, w, c - y), (x, c, w, y + h - c)]
    f.rooms = len(blocks)
    for n, (x, y, w, h) in enumerate(blocks):
        for cy in range(y, y + h):
            for cx in range(x, x + w):
                f.cell[(cx, cy)] = n

    # ── Every wall between two rooms ───────────────────────────────────
    walls = {}
    for (cx, cy), a in f.cell.items():
        for other, edge in (((cx + 1, cy), ("v", cx + 1, cy)), ((cx, cy + 1), ("h", cx, cy + 1))):
            b = f.cell.get(other)
            if b is not None and b != a:
                walls.setdefault((min(a, b), max(a, b)), []).append(edge)

    # ── Doorways ──────────────────────────────────────────────────────
    # A shared wall gets a doorway when it joins two groups of rooms that
    # are not yet joined, so every room ends up reachable. Walls between
    # rooms already joined get one 1 time in 6, for a second way round.
    group = list(range(f.rooms))

    def top(n):
        while group[n] != n:
            n = group[n]
        return n

    for pair in d.shuffle(sorted(walls)):
        a, b = top(pair[0]), top(pair[1])
        if a != b or d.below(6) == 0:
            group[a] = b
            f.doors.add(d.pick(walls[pair]))

    # ── Entrance and exit ─────────────────────────────────────────────
    # On the south, west or east wall, never at a corner or on the stairs.
    # The exit, when there is one, is on a different wall.
    if exits:
        spots = []
        for (cx, cy) in sorted(f.cell):
            if stair and stair[0] <= cx < stair[0] + 2 and stair[1] <= cy < stair[1] + 2:
                continue
            across, down = f.x < cx < f.x + f.w - 1, f.y < cy < f.y + f.h - 1
            spots += [(cx, cy, s) for s, ok in (("S", across and cy == f.y + f.h - 1),
                                                 ("W", down and cx == f.x), ("E", down and cx == f.x + f.w - 1)) if ok]
        f.openings.append(d.pick(spots))
        others = [s for s in spots if s[2] != f.openings[0][2]]
        if exits > 1 and others:
            f.openings.append(d.pick(others))
    return f


# ============================================================================
# MAP BUILDERS
# ============================================================================

def make_building(seed):
    d = Dice(seed)
    # 1 in 10: a full ground-size floor. Otherwise any size from 4 x 4 up.
    if d.below(10) == 0:
        w, h, target = GW, GH, d.between(6, 11)
    else:
        w, h = d.between(4, GW), d.between(4, GH)
        target = room_target(d, w, h)
    return Map("building", seed, [make_floor(d, 1, (0, 0, w, h), None, target, 1 + d.below(2))])


def make_hideout(seed):
    d = Dice(seed)

    # ── Level count, and which side of the ground each one goes ───────
    count = d.pick((3, 4, 5, 6))
    up = min(3, sum(d.below(2) for _ in range(count - 1)))

    # ── Stairwell first, kept off the ground floor's outer squares ─────
    stair = (d.between(1, GW - 3), d.between(1, GH - 3))
    floors = [make_floor(d, 1, (0, 0, GW, GH), stair, d.between(6, 11), 1 + d.below(2))]

    # ── Levels above, then levels below ───────────────────────────────
    # Each fits inside the one nearer ground and still holds the stairwell.
    for numbers in ([2 + i for i in range(up)], [-2 - i for i in range(count - 1 - up)]):
        x, y, w, h = 0, 0, GW, GH
        for n in numbers:
            nw, nh = d.between(4, w), d.between(4, h)
            x = d.between(max(x, stair[0] + 2 - nw), min(x + w - nw, stair[0]))
            y = d.between(max(y, stair[1] + 2 - nh), min(y + h - nh, stair[1]))
            w, h = nw, nh
            floors.append(make_floor(d, n, (x, y, w, h), stair, room_target(d, w, h), 0))
    return Map("hideout", seed, floors)


def make_dungeon(seed):
    d = Dice(seed)

    # ── Room count, weighted 1 / (rooms x rooms) ──────────────────────
    weights = [(n, 10 ** 8 // (n * n)) for n in range(15, 100)]
    roll = d.below(sum(w for _, w in weights))
    for count, w in weights:
        roll -= w
        if roll < 0:
            break

    # ── Grid of slots, about 3 wide for every 2 high ──────────────────
    cols = max(1, round((count * 1.5) ** 0.5))
    rows = -(-count // cols)
    rooms = []
    for i in range(count):
        w, h = d.between(7, GW), d.between(5, GH)
        rooms.append(Room(i + 1, i % cols * SW + 2 + d.below(GW - w + 1), i // cols * SH + 2 + d.below(GH - h + 1), w, h))
    m = Map("dungeon", seed, rooms=rooms, size=(cols * SW + 1, rows * SH + 1))

    # ── Which neighbours get a corridor ───────────────────────────────
    # Neighbour pairs in a shuffled order: a pair that joins two groups
    # not yet joined always gets one; the rest 1 time in 4 (loops).
    pairs = [(i, i + 1) for i in range(count - 1) if i % cols < cols - 1] + [(i, i + cols) for i in range(count - cols)]
    group = list(range(count))

    def top(n):
        while group[n] != n:
            n = group[n]
        return n

    chosen = []
    for a, b in d.shuffle(pairs):
        if top(a) != top(b) or d.below(4) == 0:
            group[top(a)] = top(b)
            chosen.append((a, b))

    # ── Corridors ─────────────────────────────────────────────────────
    # Side by side: out of the east wall, along the gap column between the
    # slots, into the west wall. One above the other: out of the south
    # wall, along the gap row, into the north wall. Doorways are never at
    # a corner.
    for a, b in sorted(chosen):
        A, B = rooms[a], rooms[b]
        if b == a + 1:
            ya, yb, mid = d.between(A.y + 1, A.y + A.h - 2), d.between(B.y + 1, B.y + B.h - 2), (a % cols + 1) * SW
            path = [(x, ya) for x in range(A.x + A.w, mid)] + [(mid, y) for y in range(min(ya, yb), max(ya, yb) + 1)]
            path += [(x, yb) for x in range(mid + 1, B.x)]
            A.doors.append(("E", A.x + A.w - 1, ya, b, len(path)))
            B.doors.append(("W", B.x, yb, a, len(path)))
        else:
            xa, xb, mid = d.between(A.x + 1, A.x + A.w - 2), d.between(B.x + 1, B.x + B.w - 2), (a // cols + 1) * SH
            path = [(xa, y) for y in range(A.y + A.h, mid)] + [(x, mid) for x in range(min(xa, xb), max(xa, xb) + 1)]
            path += [(xb, y) for y in range(mid + 1, B.y)]
            A.doors.append(("S", xa, A.y + A.h - 1, b, len(path)))
            B.doors.append(("N", xb, B.y, a, len(path)))
        m.halls.update(path)
        m.links.append((a, b, len(path)))

    # ── Entrance from the west edge, exit to the east edge ────────────
    first, last = rooms[0], rooms[-1]
    yi, yo = d.between(first.y + 1, first.y + first.h - 2), d.between(last.y + 1, last.y + last.h - 2)
    m.halls.update((x, yi) for x in range(0, first.x))
    m.halls.update((x, yo) for x in range(last.x + last.w, m.size[0]))
    first.doors.append(("W", first.x, yi, "IN", first.x))
    last.doors.append(("E", last.x + last.w - 1, yo, "OUT", m.size[0] - last.x - last.w))
    m.ways = [(0, yi, "IN"), (m.size[0] - 1, yo, "OUT")]

    # ── The inside of every room ──────────────────────────────────────
    # Built like a floor of its own, with each doorway as an opening.
    for r in rooms:
        r.floor = make_floor(d, 0, (0, 0, r.w, r.h), None, room_target(d, r.w, r.h, 2), 0)
        r.floor.openings = [(x - r.x, y - r.y, s) for s, x, y, _, _ in r.doors]
    return m


# ============================================================================
# DRAWING
# ============================================================================

def font_for(text, width, size=28):
    # Pillow's built-in font, shrunk until the text fits the picture.
    while size > 10 and ImageFont.load_default(size).getlength(text) > width - 40:
        size -= 2
    return ImageFont.load_default(size)


def line(draw, edge, ox, oy, thick):
    # One wall piece, centred on its grid line.
    kind, x, y = edge
    x0, y0 = ox + x * SQ, oy + y * SQ
    x1, y1 = (x0, y0 + SQ) if kind == "v" else (x0 + SQ, y0)
    draw.rectangle((x0 - thick // 2, y0 - thick // 2, x1 + thick // 2, y1 + thick // 2), fill=BLACK)


def cell_edges(x, y):
    # The four wall pieces round square (x, y).
    return {"N": ("h", x, y), "S": ("h", x, y + 1), "W": ("v", x, y), "E": ("v", x + 1, y)}


def draw_floor(img, f, ox, oy, grid, header):
    # Draws one floor with square (0, 0) at pixel (ox, oy), and the header
    # in the top row of the picture.
    draw = ImageDraw.Draw(img)
    left, top, right, bottom = ox + f.x * SQ, oy + f.y * SQ, ox + (f.x + f.w) * SQ, oy + (f.y + f.h) * SQ

    # ── Blue grid, inside the floor only ──────────────────────────────
    if grid:
        for x in range(left, right + 1, SQ):
            draw.line((x, top, x, bottom), fill=BLUE, width=2)
        for y in range(top, bottom + 1, SQ):
            draw.line((left, y, right, y), fill=BLUE, width=2)

    # ── Stairwell: staggered dashed tread lines in a thin box ─────────
    if f.stair:
        sx, sy = ox + f.stair[0] * SQ, oy + f.stair[1] * SQ
        for i, x in enumerate(range(sx + TREAD, sx + 2 * SQ, TREAD)):
            for y in range(sy + i % 2 * TREAD, sy + 2 * SQ, 2 * TREAD):
                draw.line((x, y, x, min(y + TREAD, sy + 2 * SQ)), fill=BLACK, width=3)
        draw.rectangle((sx, sy, sx + 2 * SQ, sy + 2 * SQ), outline=BLACK, width=INNER)

    # ── Inner walls, leaving the doorways open ────────────────────────
    for (cx, cy), a in f.cell.items():
        for other, edge in (((cx + 1, cy), ("v", cx + 1, cy)), ((cx, cy + 1), ("h", cx, cy + 1))):
            if f.cell.get(other, a) != a and edge not in f.doors:
                line(draw, edge, ox, oy, INNER)

    # ── Outer wall, with a 1 x 1 bump out at each opening ─────────────
    gaps = {cell_edges(x, y)[s] for x, y, s in f.openings}
    outer = [("h", x, y) for x in range(f.x, f.x + f.w) for y in (f.y, f.y + f.h)]
    outer += [("v", x, y) for y in range(f.y, f.y + f.h) for x in (f.x, f.x + f.w)]
    for x, y, s in f.openings:
        dx, dy = STEP[s]
        outer += [e for side, e in cell_edges(x + dx, y + dy).items() if side != FAR[s]]
    for edge in outer:
        if edge not in gaps:
            line(draw, edge, ox, oy, OUTER)
    draw.text((20, SQ // 2), header, fill=BLACK, font=font_for(header, img.width), anchor="lm")


def floor_header(m, f):
    if m.kind == "building":
        return "Building    Seed %s    %d x %d squares" % (m.seed, f.w, f.h)
    return "Hideout    Level %d%s    Seed %s" % (f.number, " (ground)" if f.number == 1 else "", m.seed)


def sheet(m, f, grid, header):
    # One printable sheet: a header row, then the floor with a 1 square
    # margin all round.
    img = Image.new("RGB", ((f.w + 2) * SQ, (f.h + 3) * SQ), WHITE)
    draw_floor(img, f, (1 - f.x) * SQ, (2 - f.y) * SQ, grid, header)
    return img


def hideout_overview(m):
    # Every level in 2 rows, each drawn where it sits over the ground level,
    # so the stairwells line up.
    across, cw, ch = (len(m.floors) + 1) // 2, (GW + 2) * SQ, (GH + 3) * SQ
    img = Image.new("RGB", (across * cw, 2 * ch), WHITE)
    for i, f in enumerate(m.floors):
        part = Image.new("RGB", (cw, ch), WHITE)
        draw_floor(part, f, SQ, 2 * SQ, True, floor_header(m, f))
        img.paste(part, (i % across * cw, i // across * ch))
    return img


def dungeon_overview(m):
    # The whole dungeon at 20 pixels per square, under a 60 pixel header.
    p, top = 20, 60
    img = Image.new("RGB", (m.size[0] * p, m.size[1] * p + top), WHITE)
    draw = ImageDraw.Draw(img)

    # ── Floor squares: corridors are 0, rooms their own number ────────
    floor = dict.fromkeys(m.halls, 0)
    for r in m.rooms:
        floor.update(((x, y), r.number) for x in range(r.x, r.x + r.w) for y in range(r.y, r.y + r.h))
    doors = {cell_edges(x, y)[s] for r in m.rooms for s, x, y, _, _ in r.doors}

    # ── Blue grid on the floor squares only ───────────────────────────
    for x, y in floor:
        draw.rectangle((x * p, y * p + top, x * p + p, y * p + top + p), outline=BLUE)

    # ── Black walls wherever floor meets rock or a different space ────
    # Doorways stay open, and so do the IN and OUT ends at the map edge.
    for (x, y), here in floor.items():
        for s, edge in cell_edges(x, y).items():
            dx, dy = STEP[s]
            if 0 <= x + dx < m.size[0] and 0 <= y + dy < m.size[1] and floor.get((x + dx, y + dy)) != here and edge not in doors:
                kind, ex, ey = edge
                x1, y1 = (ex, ey + 1) if kind == "v" else (ex + 1, ey)
                draw.rectangle((ex * p - 2, ey * p + top - 2, x1 * p + 2, y1 * p + top + 2), fill=BLACK)

    # ── Room numbers, IN and OUT, header ──────────────────────────────
    for r in m.rooms:
        draw.text(((r.x + r.w / 2) * p, (r.y + r.h / 2) * p + top), str(r.number), fill=BLACK,
                  font=ImageFont.load_default(28), anchor="mm")
    small = ImageFont.load_default(24)
    for x, y, word in m.ways:
        draw.text((4 if word == "IN" else img.width - 4, y * p + top - 3), word, fill=BLACK, font=small,
                  anchor="lb" if word == "IN" else "rb")
    header = "Dungeon    Seed %s    %d rooms    %d x %d squares" % (m.seed, len(m.rooms), m.size[0], m.size[1])
    draw.text((20, 30), header, fill=BLACK, font=font_for(header, img.width), anchor="lm")
    return img


def room_key(m):
    # The text file for laying the printed room sheets out at the table.
    lines = ["Dungeon    Seed %s    %d rooms" % (m.seed, len(m.rooms)), "",
             "Print the room sheets. Start with room 1, where the entrance (IN) comes in from the west edge.",
             "Squares on a wall are counted from the north or west end. Every corridor joins exactly two rooms.", ""]
    for r in m.rooms:
        lines.append("Room %d    %d x %d squares    %d inner rooms" % (r.number, r.w, r.h, r.floor.rooms))
        for s, x, y, to, length in r.doors:
            spot = y - r.y + 1 if s in "WE" else x - r.x + 1
            where = "the entrance from the west edge" if to == "IN" else "the exit to the east edge" if to == "OUT" else "room %d" % (to + 1)
            lines.append("    %s wall, square %d: corridor of %d squares to %s" % (WALL[s], spot, length, where))
        lines.append("")
    return "\n".join(lines)


def preview(m):
    # What the window shows: a building's grid sheet, or the overview.
    if m.kind == "building":
        return sheet(m, m.floors[0], True, floor_header(m, m.floors[0]))
    return hideout_overview(m) if m.kind == "hideout" else dungeon_overview(m)


# ============================================================================
# SAVING
# ============================================================================

def save_map(m, name, overview):
    # Makes Maps/<name> and writes every file into it. Stops with
    # FileExistsError if that folder is already there, so nothing is
    # ever overwritten.
    folder = os.path.join(SAVE, name)
    os.makedirs(folder)
    jpg = lambda img, part: img.save(os.path.join(folder, "%s_%s.jpg" % (name, part)), quality=95, subsampling=0)
    for f in m.floors:
        part = "" if m.kind == "building" else "level_%d_" % f.number
        for grid, word in ((False, "walls"), (True, "grid")):
            jpg(sheet(m, f, grid, floor_header(m, f)), part + word)
    for r in m.rooms:
        header = "Dungeon    Room %d of %d    Seed %s" % (r.number, len(m.rooms), m.seed)
        for grid, word in ((False, "walls"), (True, "grid")):
            jpg(sheet(m, r.floor, grid, header), "room_%02d_%s" % (r.number, word))
    if m.kind != "building":
        jpg(overview, "overview")
    if m.kind == "dungeon":
        with open(os.path.join(folder, name + "_room_key.txt"), "w") as out:
            out.write(room_key(m))
    return folder


MAKERS = {"building": make_building, "hideout": make_hideout, "dungeon": make_dungeon}


# ============================================================================
# WINDOW
# ============================================================================

def run_window(first_seed=None, first_kind="hideout"):
    import tkinter as tk
    from tkinter import messagebox, simpledialog
    from PIL import ImageTk

    win = tk.Tk()
    win.title("DnD MapBuilder Interior v2.0")
    win.geometry("%dx%d+0+0" % (win.winfo_screenwidth(), win.winfo_screenheight()))
    now = {"map": None, "pic": None, "size": None}

    # ── Top of the window: buttons, seed box, status line ─────────────
    bar = tk.Frame(win, pady=8)
    bar.pack(side="top", fill="x")
    buttons = tk.Frame(bar)
    buttons.pack()
    for kind, label in LABELS.items():
        tk.Button(buttons, text=label, command=lambda kind=kind: show(kind)).pack(side="left", padx=3)
    tk.Label(bar, text="Seed (leave empty for a new map):").pack(pady=(6, 0))
    seed_box = tk.Entry(bar, width=22, justify="center")
    seed_box.pack()
    status = tk.StringVar(value="Click a button to make a new map.")
    tk.Entry(bar, textvariable=status, state="readonly", relief="flat", justify="center",
             readonlybackground=win.cget("bg"), width=110).pack(pady=4)

    # ── Save question, with white buttons ─────────────────────────────
    # Labels that act as buttons: a Mac draws its own buttons dark grey in
    # Dark Mode, but a label keeps the colours it is given.
    ask = tk.Frame(bar)
    tk.Label(ask, text="Do you want to save the generated map?").pack(side="left", padx=4)
    def white(text, command):
        button = tk.Label(ask, text=text, bg="white", fg="black", padx=14, pady=3, cursor="hand2")
        button.bind("<Button-1>", lambda event: command())
        return button

    white("Yes", lambda: save()).pack(side="left", padx=4)
    white("No", lambda: clear()).pack(side="left", padx=4)
    full = white("Open full size", lambda: now["pic"].show())
    view = tk.Label(win, bg="black")
    view.pack(side="bottom", fill="both", expand=True)

    def fit(event=None):
        # Shrinks the map to fit the preview area, in one box shrink (each
        # preview pixel is the average of the picture pixels under it).
        size = (max(200, view.winfo_width() - 10), max(200, view.winfo_height() - 10))
        if now["pic"] is None or size == now["size"]:
            return
        now["size"] = size
        pic = now["pic"]
        scale = min(size[0] / pic.width, size[1] / pic.height, 1)
        now["photo"] = ImageTk.PhotoImage(pic.resize((max(1, round(pic.width * scale)), max(1, round(pic.height * scale))), Image.BOX))
        view.config(image=now["photo"])

    def show(kind, seed=None):
        # Makes a map from the seed box (or a new random 15 digit seed),
        # shows it and asks whether to save it.
        seed = seed or seed_box.get().strip() or str(10 ** 14 + int.from_bytes(os.urandom(8), "big") % (9 * 10 ** 14))
        if not seed.isdigit():
            messagebox.showinfo("Seed", "A seed is digits only, for example 123456789012345.")
            return
        started = time.perf_counter()
        now["map"] = MAKERS[kind](seed)
        now["pic"], now["size"] = preview(now["map"]), None
        full.pack(side="left", padx=4) if kind == "dungeon" else full.pack_forget()
        ask.pack(pady=(0, 6))
        win.update_idletasks()
        fit()
        seed_box.delete(0, "end")
        m = now["map"]
        what = ("%d rooms" % len(m.rooms) if kind == "dungeon" else
                "Levels " + ", ".join(str(f.number) for f in m.floors) if kind == "hideout" else
                "%d x %d squares" % (m.floors[0].w, m.floors[0].h))
        status.set("%s    Seed %s    %s    Made in %.2f seconds" % (LABELS[kind], seed, what, time.perf_counter() - started))

    def save():
        # Asks for a name until it is usable and not taken, or Cancel.
        while True:
            name = (simpledialog.askstring("Save map", "Type a name for this map:", parent=win) or "").strip()
            if not name:
                return
            if name.startswith(".") or any(ch in name for ch in '/\\:*?"<>|'):
                messagebox.showinfo("Save map", "Use a name without / \\ : * ? \" < > | and not starting with a dot.")
                continue
            try:
                folder = save_map(now["map"], name, now["pic"])
            except FileExistsError:
                messagebox.showinfo("Save map", "There is already a folder called \"%s\". Pick another name." % name)
                continue
            status.set("Saved in %s    (seed %s)" % (folder, now["map"].seed))
            ask.pack_forget()
            return

    def clear():
        now["map"] = now["pic"] = None
        view.config(image="")
        status.set("Not saved.")
        ask.pack_forget()

    view.bind("<Configure>", fit)
    if first_seed:
        win.update()
        show(first_kind, first_seed)
    win.mainloop()


# ============================================================================
# START
# ============================================================================

# Optional words: a seed, then building, hideout or dungeon (hideout if left
# off). Anything else stops with a short usage line.

if __name__ == "__main__":
    args = sys.argv[1:]
    kind = args.pop().lower() if args and args[-1].lower() in LABELS else "hideout"
    if args and not args[0].isdigit():
        sys.exit("Use: [SEED] [building, hideout or dungeon]")
    run_window(args[0] if args else None, kind)
