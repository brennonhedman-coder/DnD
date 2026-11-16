#!/usr/bin/env python3
# ============================================================================
# DnD-MapBuilder_v1.1.py
# ============================================================================

"""
.SYNOPSIS
    Tkinter window that makes a random outdoor area map with adventure
    locations, then a floor plan for every location, and saves them all as
    JPG files with a text list of the locations.

.DESCRIPTION
    The area maps come from DnD-MapBuilder-Exterior v2.0 and the floor plans
    from DnD-MapBuilder-Interior v2.1.1, both built in unchanged, so the same
    seeds make the same maps here as in those scripts.

    The area map:
      - Every button in the window is white, in Light or Dark Mode
      - "Area map" makes a new map. "Adventure locations" puts numbered
        locations marked with a red x on it, from a seed of its own. The
        seed box takes a map seed, a locations seed, or a code (map seed,
        dash, locations seed) that brings both back
      - With no locations the window asks "Do you want to save the
        generated map?"

    Floor plans for the locations:
      - With locations the window first asks "Would you like to generate
        floor plans for the locations on your adventure?" with three white
        buttons: "Yes", "No" and "Make automatically"
      - "No" goes straight to the save question
      - "Yes" switches the window to the white floor plan buttons:
        "Building", "Village", "Hideout", "Town" and "Dungeon complex". It
        shows which location is next (number and square), and the area map
        shows that location's x in red and every other x in grey. Click
        buttons until a plan suits it, then "Use for this location" moves
        on. At the last location it suggests a Dungeon complex or a Town for
        the finale. After the last one comes the save question
      - "Make automatically" picks every plan from the locations seed, so
        the same code always gets the same plans: Building 6 times in 10,
        Village 2 in 10 and Hideout 2 in 10, and for the last location a
        Town or a Dungeon complex, 1 chance in 2 each

    Saving:
      - Maps/<name>/ gets the area map with and without the grid, the
        locations text file, and every location's floor plan files, named
        <name>_location_<nn>_<kind>_..., saved the same way the floor plan
        script saves them
      - The locations text file lists every location by number and square,
        with its floor plan's kind and seed

    Lines that start with "#" are notes for people. Python ignores them.

.NOTES
    Author : Brennon Hedman
    Version: 1.1
    Requires: Python 3.8+ and Pillow 10.1+ (python3 -m pip install pillow)
    Platform: macOS, Windows or Linux (the window uses Tkinter, which comes
              with the standard Python installer)

.EXAMPLE
    python3 DnD-MapBuilder_v1.1.py

    Opens the window.

.EXAMPLE
    python3 DnD-MapBuilder_v1.1.py 123456789012345-987654321098765

    Opens the window showing that area map with those locations.
"""

import math, os, re, sys, time
from PIL import Image, ImageDraw, ImageFont


# ============================================================================
# AREA MAP SETTINGS
# ============================================================================

SQ, AW, AH, PER_SQUARE = 70, 17, 13, 3
W, H = AW * SQ, AH * SQ
INSIDE, LOOSE = (105, 105, W - 105, H - 105), (1, 1, W - 1, H - 1)
CHOICES, RESTARTS, BUDGET, REDRAWS = 3, 6, 2000, 9
TOLERANCE, GAP2, AREA_LOW, AREA_HIGH, MOVES = 2, 245 * 245, 270000, 290000, 300
BLACK, WHITE, BLUE, RED = (0, 0, 0), (255, 255, 255), (140, 190, 255), (220, 0, 0)
LINE_COLOR, LINE_WIDTH, FRAME, FRAME_WIDTH = BLACK, 1, True, 7
SHOW_NODES, NODE_COLOR, GRID_COLOR, GRID_WIDTH = False, BLUE, BLUE, 1
TEXTURES = (("forest", 34, 34), ("sand", 16, 16), ("water", 40, 26))
CELL, SMALLEST, EDGE, TEXTURE_COLOR = 5, 400, 2, (90, 90, 90)
CW, CH = W // CELL, H // CELL
X_COUNT, X_GAP2, X_SIZE, COLUMNS = (7, 29), 40 * 40, 7, "ABCDEFGHIJKLMNOPQ"
X_GREY = (165, 165, 165)
SAVE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Maps")
M64 = (1 << 64) - 1


# ============================================================================
# SEED DICE
# ============================================================================

class Dice:
    def __init__(self, seed):
        self.s = int(seed) & M64

    def below(self, n):
        self.s = (self.s + 0x9E3779B97F4A7C15) & M64
        z = ((self.s ^ (self.s >> 30)) * 0xBF58476D1CE4E5B9) & M64
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & M64
        return (z ^ (z >> 31)) % n

    def between(self, a, b):
        return a + self.below(b - a + 1)

    def pick(self, items):
        return items[self.below(len(items))]

    def shuffle(self, items):
        for i in range(len(items) - 1, 0, -1):
            j = self.below(i + 1)
            items[i], items[j] = items[j], items[i]
        return items


# ============================================================================
# GEOMETRY
# ============================================================================

def d2(p, q):
    x, y = p[0] - q[0], p[1] - q[1]
    return x * x + y * y


def side(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def inside(p, box):
    return box[0] <= p[0] <= box[2] and box[1] <= p[1] <= box[3]


def square_of(p):
    return min(p[0] // SQ, AW - 1), min(p[1] // SQ, AH - 1)


def hull(points):
    pts = sorted(set(points))
    if len(pts) < 3:
        return pts
    half = []
    for run in (pts, pts[::-1]):
        part = []
        for p in run:
            while len(part) >= 2 and side(part[-2], part[-1], p) <= 0:
                part.pop()
            part.append(p)
        half += part[:-1]
    return half


def shape_cost(points):
    corners = hull(points)
    faults, twice = len(points) - len(corners), 0
    if len(corners) >= 3:
        for i, q in enumerate(corners):
            p, r = corners[i - 1], corners[(i + 1) % len(corners)]
            u, v = (p[0] - q[0], p[1] - q[1]), (r[0] - q[0], r[1] - q[1])
            if abs(math.degrees(math.atan2(abs(u[0] * v[1] - u[1] * v[0]), u[0] * v[0] + u[1] * v[1])) - 90) <= TOLERANCE:
                faults += 1
            twice += q[0] * r[1] - r[0] * q[1]
    twice = abs(twice)
    return faults, max(2 * AREA_LOW - twice, twice - 2 * AREA_HIGH, 0)


# ============================================================================
# NODE MATRIX
# ============================================================================

def make_matrix(d):
    cells = {}
    for sy in range(AH):
        for sx in range(AW):
            cells[(sx, sy)] = list(dict.fromkeys([(sx * SQ + d.below(SQ), sy * SQ + d.below(SQ)) for _ in range(PER_SQUARE)]))
    ring = {(sx, sy): [q for x in range(sx - 1, sx + 2) for y in range(sy - 1, sy + 2) for q in cells.get((x, y), ())]
            for sx, sy in cells}
    return cells, ring


# ============================================================================
# TPNODES
# ============================================================================

def place_tps(d, count, cells, ring):
    spots = [p for ps in cells.values() for p in ps if inside(p, INSIDE)]
    pts = []
    for _ in range(count):
        free = [s for s in spots if all(d2(s, p) >= GAP2 for p in pts)]
        if not free:
            return None
        pts.append(d.pick(free))
    cost = shape_cost(pts)
    for _ in range(MOVES):
        if cost == (0, 0):
            break
        i = d.below(count)
        near = [q for q in ring[square_of(pts[i])] if inside(q, INSIDE) and q not in pts]
        if not near:
            continue
        q = d.pick(near)
        if any(d2(q, p) < GAP2 for j, p in enumerate(pts) if j != i):
            continue
        trial = pts[:i] + [q] + pts[i + 1:]
        better = shape_cost(trial)
        if better <= cost:
            pts, cost = trial, better
    return pts if cost == (0, 0) else None


# ============================================================================
# ENODES
# ============================================================================

def place_enodes(d):
    skip, found = d.below(4), []
    for n, s in enumerate("NSWE"):
        if n != skip:
            found.append((d.between(1, W - 1), 0 if s == "N" else H) if s in "NS" else (0 if s == "W" else W, d.between(1, H - 1)))
    return found


# ============================================================================
# LINES
# ============================================================================

def hits(p, q, segs, ok):
    px, py = p
    qx, qy = q
    lox, hix = (px, qx) if px < qx else (qx, px)
    loy, hiy = (py, qy) if py < qy else (qy, py)
    for r, s in segs:
        rx, ry = r
        sx, sy = s
        if (rx if rx > sx else sx) < lox or (rx if rx < sx else sx) > hix or (ry if ry > sy else sy) < loy or (ry if ry < sy else sy) > hiy:
            continue
        a = (sx - rx) * (py - ry) - (sy - ry) * (px - rx)
        b = (sx - rx) * (qy - ry) - (sy - ry) * (qx - rx)
        if a * b > 0:
            continue
        c = (qx - px) * (ry - py) - (qy - py) * (rx - px)
        e = (qx - px) * (sy - py) - (qy - py) * (sx - px)
        if c * e > 0:
            continue
        shared = [t for t in (p, q) if t == r or t == s]
        if len(shared) != 1:
            return True
        t = shared[0]
        if a == 0 and b == 0:
            u, v = (q if t == p else p), (s if t == r else r)
            if (u[0] - t[0]) * (v[0] - t[0]) + (u[1] - t[1]) * (v[1] - t[1]) > 0:
                return True
        if t not in ok:
            return True
    return False


def under(p, q):
    x0, y0 = square_of((min(p[0], q[0]), min(p[1], q[1])))
    x1, y1 = square_of((max(p[0], q[0]), max(p[1], q[1])))
    return [(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)]


def route(d, a, b, box, ring, ends, drawn):
    foreign = [n for n in ends if n != a and n != b]
    bx, by = b
    x0, y0, x1, y1 = box
    none = frozenset()

    def blocked(p, q):
        lox, hix, loy, hiy = min(p[0], q[0]), max(p[0], q[0]), min(p[1], q[1]), max(p[1], q[1])
        for n in foreign:
            if lox <= n[0] <= hix and loy <= n[1] <= hiy and side(p, q, n) == 0:
                return True
        if hits(p, q, zip(path, path[1:-1]), none):
            return True
        for x in range(min(lox // SQ, AW - 1), min(hix // SQ, AW - 1) + 1):
            for y in range(min(loy // SQ, AH - 1), min(hiy // SQ, AH - 1) + 1):
                segs = drawn.get((x, y))
                if segs and hits(p, q, segs, ends):
                    return True
        return False

    def extend(p, prev):
        px, py = p
        far = (px - bx) ** 2 + (py - by) ** 2
        fits = []
        for q in ring[square_of(p)]:
            if q == p or q in seen:
                continue
            qx, qy = q
            if q != b:
                if q in ends or not (x0 <= qx <= x1 and y0 <= qy <= y1):
                    continue
            elif len(path) < 2:
                continue
            if (qx - bx) ** 2 + (qy - by) ** 2 >= far:
                continue
            if prev is not None:
                ux, uy, vx, vy = px - prev[0], py - prev[1], qx - px, qy - py
                if ux * vy == uy * vx or ux * vx + uy * vy <= 0:
                    continue
            fits.append(((qx - px) ** 2 + (qy - py) ** 2, q))
        fits = [q for _, q in sorted(fits)]
        for q in d.shuffle(fits[:CHOICES]) + fits[CHOICES:]:
            if tried[0] >= BUDGET:
                return False
            tried[0] += 1
            if blocked(p, q):
                continue
            path.append(q)
            seen.add(q)
            if q == b or extend(q, p):
                return True
            path.pop()
            seen.discard(q)
        return False

    for _ in range(RESTARTS):
        tried, path, seen = [0], [a], {a}
        if extend(a, None):
            return path
    return None


# ============================================================================
# TEXTURES
# ============================================================================

def find_areas(lines):
    small = Image.new("L", (CW, CH), 0)
    draw = ImageDraw.Draw(small)
    draw.rectangle((0, 0, CW - 1, CH - 1), outline=255)
    for path in lines:
        draw.line([(min(x // CELL, CW - 1), min(y // CELL, CH - 1)) for x, y in path], fill=255)
    wall = small.tobytes()
    runs, top, above = [], [], []

    def root(k):
        while top[k] != k:
            top[k] = top[top[k]]
            k = top[k]
        return k

    for y in range(CH):
        here = []
        for found in re.finditer(b"\x00+", wall[y * CW:(y + 1) * CW]):
            k, a, b = len(runs), found.start(), found.end()
            runs.append((y, a, b))
            top.append(k)
            for o in above:
                if runs[o][1] < b and a < runs[o][2]:
                    top[root(o)] = root(k)
            here.append(k)
        above = here
    grid, number, areas = [-1] * (CW * CH), {}, []
    for k, (y, a, b) in enumerate(runs):
        r = root(k)
        if r not in number:
            number[r] = len(areas)
            areas.append([0, a, b - 1, y, y])
        n = number[r]
        area = areas[n]
        area[0] += b - a
        area[1], area[2], area[4] = min(area[1], a), max(area[2], b - 1), y
        grid[y * CW + a:y * CW + b] = [n] * (b - a)
    return areas, grid


def clear_of(grid, cx, cy, n):
    if not (EDGE <= cx < CW - EDGE and EDGE <= cy < CH - EDGE):
        return False
    return all(grid[(cy + j) * CW + cx + i] == n for j in range(-EDGE, EDGE + 1) for i in range(-EDGE, EDGE + 1))


def place_textures(d, lines):
    areas, grid = find_areas(lines)
    big = d.shuffle([n for n, area in enumerate(areas) if area[0] >= SMALLEST])
    marks, water = [], None
    for (texture, sx, sy), n in zip(TEXTURES, big):
        if texture == "water":
            water = n
        _, ax0, ax1, ay0, ay1 = areas[n]
        for y in range(ay0 * CELL, (ay1 + 1) * CELL, sy):
            for x in range(ax0 * CELL, (ax1 + 1) * CELL, sx):
                px, py = x + d.below(sx // 2 + 1), y + d.below(sy // 2 + 1)
                if clear_of(grid, px // CELL, py // CELL, n):
                    marks.append((texture, px, py))
    box = None
    if water is not None:
        _, ax0, ax1, ay0, ay1 = areas[water]
        box = (ax0 - EDGE, ay0 - EDGE, ax1 + EDGE, ay1 + EDGE)
    return marks, grid, water, box


# ============================================================================
# LOCATIONS MARKED WITH A RED X
# ============================================================================

def place_xs(d, grid, water, box):
    x0, y0, x1, y1 = INSIDE
    span = range(-EDGE, EDGE + 1)

    def dry(x, y):
        cx, cy = x // CELL, y // CELL
        if water is None or not (box[0] <= cx <= box[2] and box[1] <= cy <= box[3]):
            return True
        return all(grid[(cy + j) * CW + cx + i] != water for j in span for i in span)

    free = [(x, y) for y in range(y0, y1 + 1, 10) for x in range(x0, x1 + 1, 10) if dry(x, y)]
    xs = []
    for _ in range(d.between(*X_COUNT)):
        if not free:
            break
        px, py = p = d.pick(free)
        xs.append(p)
        free = [q for q in free if (q[0] - px) ** 2 + (q[1] - py) ** 2 >= X_GAP2]
    if len(xs) < 2:
        return xs
    _, i, j = max((d2(p, q), i, j) for i, p in enumerate(xs) for j, q in enumerate(xs) if i < j)
    a, b = xs[i], xs[j]
    rest = sorted((q for k, q in enumerate(xs) if k not in (i, j)),
                  key=lambda q: ((q[0] - a[0]) * (b[0] - a[0]) + (q[1] - a[1]) * (b[1] - a[1]), q))
    return [a] + rest + [b]


# ============================================================================
# AREA MAP BUILDER
# ============================================================================

class Exterior:
    def __init__(self, seed, cells, tps, lines, marks, grid, water, box, tries):
        self.seed, self.cells, self.tps, self.lines, self.marks, self.tries = seed, cells, tps, lines, marks, tries
        self.grid, self.water, self.box = grid, water, box
        self.loc_seed, self.xs, self.plans = None, [], []


def add_locations(m, loc_seed):
    m.loc_seed = loc_seed
    m.xs = place_xs(Dice(loc_seed), m.grid, m.water, m.box)
    m.plans = [None] * len(m.xs)


def code(m):
    return "%s-%s" % (m.seed, m.loc_seed) if m.loc_seed else m.seed


def draw_once(value):
    d = Dice(value)

    # ── Node matrix, TPNodes and ENodes ───────────────────────────────
    cells, ring = make_matrix(d)
    tps = place_tps(d, d.pick((3, 5)), cells, ring)
    if tps is None:
        return None
    enodes = place_enodes(d)
    ends = frozenset(tps) | frozenset(enodes)

    # ── Which points get a line ───────────────────────────────────────
    pairs = {tuple(sorted((i, j))) for i, a in enumerate(tps)
             for _, j in sorted((d2(a, b), j) for j, b in enumerate(tps) if j != i)[:2]}
    jobs = [(tps[i], tps[j], INSIDE) for i, j in sorted(pairs)]
    jobs += [(e, min(tps, key=lambda p: d2(e, p)), LOOSE) for e in enodes]

    # ── Draw each line ────────────────────────────────────────────────
    drawn, lines = {}, []
    for a, b, box in jobs:
        path = route(d, a, b, box, ring, ends, drawn)
        if not path:
            return None
        lines.append(path)
        for p, q in zip(path, path[1:]):
            for c in under(p, q):
                drawn.setdefault(c, []).append((p, q))
    return (cells, tps, lines) + place_textures(d, lines)


def make_exterior(seed):
    for tries in range(1, REDRAWS + 2):
        got = draw_once(int(seed) + tries - 1)
        if got:
            return Exterior(seed, *got, tries)
    return None


# ============================================================================
# AREA MAP DRAWING
# ============================================================================

def font_for(text, width, size=28):
    while size > 10 and ImageFont.load_default(size).getlength(text) > width - 40:
        size -= 2
    return ImageFont.load_default(size)


def area_sheet(m, grid=False, focus=None):
    img = Image.new("RGB", (W + 2 * SQ, H + 3 * SQ), WHITE)
    draw = ImageDraw.Draw(img)
    ox, oy, r, f = SQ, 2 * SQ, LINE_WIDTH // 2, FRAME_WIDTH // 2

    # ── Blue grid, inside the Area Map only ───────────────────────────
    if grid:
        for x in range(ox, ox + W + 1, SQ):
            draw.line((x, oy, x, oy + H), fill=GRID_COLOR, width=GRID_WIDTH)
        for y in range(oy, oy + H + 1, SQ):
            draw.line((ox, y, ox + W, y), fill=GRID_COLOR, width=GRID_WIDTH)

    # ── Node matrix ───────────────────────────────────────────────────
    if SHOW_NODES:
        for ps in m.cells.values():
            for x, y in ps:
                draw.ellipse((ox + x - 2, oy + y - 2, ox + x + 2, oy + y + 2), fill=NODE_COLOR)

    # ── Frame round the Area Map ──────────────────────────────────────
    if FRAME:
        draw.rectangle((ox - f, oy - f, ox + W + f, oy + H + f), outline=LINE_COLOR, width=FRAME_WIDTH)

    # ── Texture marks, thin and grey ──────────────────────────────────
    for texture, x, y in m.marks:
        x, y = ox + x, oy + y
        if texture == "forest":
            draw.ellipse((x - 5, y - 9, x + 5, y + 1), outline=TEXTURE_COLOR)
            draw.line((x, y + 1, x, y + 5), fill=TEXTURE_COLOR)
        elif texture == "water":
            draw.arc((x - 8, y - 3, x, y + 3), 180, 360, fill=TEXTURE_COLOR)
            draw.arc((x, y - 3, x + 8, y + 3), 0, 180, fill=TEXTURE_COLOR)
        elif (x * 7 + y * 13) % 9:
            draw.point((x, y), fill=TEXTURE_COLOR)
        else:
            draw.polygon(((x, y - 4), (x - 4, y + 3), (x + 4, y + 3)), outline=TEXTURE_COLOR)

    # ── Lines: one colour, round at every corner and end ──────────────
    for path in m.lines:
        points = [(ox + x, oy + y) for x, y in path]
        for x, y in points:
            draw.ellipse((x - r, y - r, x + r, y + r), fill=LINE_COLOR)
        draw.line(points, fill=LINE_COLOR, width=LINE_WIDTH)

    # ── Locations marked with a red x, and their numbers ──────────────
    small = ImageFont.load_default(16)
    for n, (x, y) in enumerate(m.xs, 1):
        mark = RED if focus is None or n == focus else X_GREY
        x, y = ox + x, oy + y
        draw.line((x - X_SIZE, y - X_SIZE, x + X_SIZE, y + X_SIZE), fill=mark, width=3)
        draw.line((x - X_SIZE, y + X_SIZE, x + X_SIZE, y - X_SIZE), fill=mark, width=3)
        draw.text((x + X_SIZE + 2, y - X_SIZE - 1), str(n), fill=mark, font=small, anchor="lb")

    # ── Square names round the edge: A to Q across, 1 to 13 down ──────
    label = ImageFont.load_default(22)
    for i, letter in enumerate(COLUMNS[:AW]):
        for y in (oy - SQ // 2, oy + H + SQ // 2):
            draw.text((ox + i * SQ + SQ // 2, y), letter, fill=BLACK, font=label, anchor="mm")
    for j in range(AH):
        for x in (ox - SQ // 2, ox + W + SQ // 2):
            draw.text((x, oy + j * SQ + SQ // 2), str(j + 1), fill=BLACK, font=label, anchor="mm")
    header = "Exterior    Seed %s" % m.seed
    if m.loc_seed:
        header = "Exterior    Code %s    Locations marked with a red x: %d" % (code(m), len(m.xs))
    draw.text((20, SQ // 2), header, fill=BLACK, font=font_for(header, img.width), anchor="lm")
    return img


# ============================================================================
# FLOOR PLAN SETTINGS
# ============================================================================

SQ, GW, GH = 70, 17, 13          # pixels per square on a sheet; the ground
                                 # (and largest) floor is 17 x 13 squares
SW, SH = GW + 4, GH + 4          # one dungeon slot: the largest room plus 2
                                 # squares of rock on every side
OUTER, INNER, TREAD = 7, 3, 14   # pixels: outer walls, inner walls, and the
                                 # gap between stair tread lines
LABELS = {"building": "Building", "village": "Village", "hideout": "Hideout", "town": "Town",
          "dungeon": "Dungeon complex"}
                                 # each kind: its command-line word and the
                                 # label on its button and headers
GROUPS = ("village", "town")     # kinds made of several maps
STEP = {"N": (0, -1), "S": (0, 1), "W": (-1, 0), "E": (1, 0)}
                                 # one square out through each side
WALL = {"N": "north", "S": "south", "W": "west", "E": "east"}
FAR = {"N": "S", "S": "N", "W": "E", "E": "W"}
                                 # the opposite side


# ============================================================================
# FLOOR PLAN DATA
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
    # A whole map. A building or hideout has floors; a
    # dungeon complex has rooms, corridor squares (halls), links between
    # rooms and its IN / OUT ends; a village or town has parts, its maps.
    def __init__(self, kind, seed, floors=(), rooms=(), size=None, parts=()):
        self.kind, self.seed, self.floors, self.rooms, self.size = kind, seed, list(floors), list(rooms), size
        self.halls, self.links, self.ways = set(), [], []
        self.parts = list(parts)         # a village's or town's own maps
        self.location = None             # the adventure location it is for


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
# FLOOR PLAN MAKERS
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


def part_seed(d):
    # A 15 digit seed for one map in a village or town.
    return str(10 ** 14 + d.below(9 * 10 ** 14))


def make_village(seed):
    d = Dice(seed)
    return Map("village", seed, parts=[make_building(part_seed(d)) for _ in range(d.between(6, 11))])


def make_town(seed):
    # 12 to 29 buildings and a hideout.
    d = Dice(seed)
    parts = [make_building(part_seed(d)) for _ in range(d.between(12, 29))]
    return Map("town", seed, parts=parts + [make_hideout(part_seed(d))])


# ============================================================================
# FLOOR PLAN DRAWING
# ============================================================================

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


def at_location(m):
    # "Location n    " for a floor plan made for an adventure location.
    return "Location %d    " % m.location if m.location else ""


def floor_header(m, f):
    if m.kind == "building":
        return "%sBuilding    Seed %s    %d x %d squares" % (at_location(m), m.seed, f.w, f.h)
    return "%s%s    Level %d%s    Seed %s" % (at_location(m), LABELS[m.kind], f.number, " (ground)" if f.number == 1 else "", m.seed)


def floor_sheet(m, f, grid, header):
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
    header = "%sDungeon complex    Seed %s    %d rooms    %d x %d squares" % (at_location(m), m.seed, len(m.rooms), m.size[0], m.size[1])
    draw.text((20, 30), header, fill=BLACK, font=font_for(header, img.width), anchor="lm")
    return img


def room_key(m):
    # The text file for laying the printed room sheets out at the table.
    lines = ["Dungeon complex    Seed %s    %d rooms" % (m.seed, len(m.rooms)), "",
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


def what_it_is(m):
    # A village's or town's contents, in words.
    houses = sum(p.kind == "building" for p in m.parts)
    extra = "".join(", a %s" % LABELS[p.kind].lower() for p in m.parts if p.kind != "building")
    return "%d buildings%s" % (houses, extra)


def group_overview(m):
    # 3 across and 2 down, each on its grid sheet: a village's six buildings
    # with the lowest seeds, or a town's five, with the town's hideout
    # overview, shrunk to fit, in the sixth spot. A header row runs across
    # the top with the number of buildings.
    cw, ch = (GW + 2) * SQ, (GH + 3) * SQ
    hideouts = [p for p in m.parts if p.kind == "hideout"]
    houses = sorted((p for p in m.parts if p.kind == "building"), key=lambda p: int(p.seed))[:6 - len(hideouts)]
    img = Image.new("RGB", (3 * cw, SQ + 2 * ch), WHITE)
    for i, b in enumerate(houses):
        img.paste(floor_sheet(b, b.floors[0], True, floor_header(b, b.floors[0])), (i % 3 * cw, SQ + i // 3 * ch))
    for h in hideouts:
        pic = hideout_overview(h)
        scale = min(cw / pic.width, ch / pic.height)
        pic = pic.resize((round(pic.width * scale), round(pic.height * scale)), Image.LANCZOS)
        img.paste(pic, (2 * cw + (cw - pic.width) // 2, SQ + ch + (ch - pic.height) // 2))
    shown = "five buildings with the lowest seeds and the hideout" if hideouts else "six buildings with the lowest seeds"
    total = "%d buildings in total%s" % (sum(p.kind == "building" for p in m.parts), " and a hideout" if hideouts else "")
    header = "%s%s    Seed %s    %s    (%s shown)" % (at_location(m), LABELS[m.kind], m.seed, total, shown)
    ImageDraw.Draw(img).text((20, SQ // 2), header, fill=BLACK, font=font_for(header, img.width, 40), anchor="lm")
    return img


def building_list(m, name):
    # The text file saved with a village or town: every map in it, with its
    # seed and the start of its file names.
    lines = ["%s    Seed %s    %s" % (LABELS[m.kind], m.seed, what_it_is(m)), "",
             "To get one of these maps back on its own, type its seed into the seed box",
             "and click the button named at the start of its line.", ""]
    for p, part in zip(m.parts, part_names(m)):
        if p.kind == "building":
            f = p.floors[0]
            lines.append("Building %-4s Seed %s    %d x %d squares    %d room%s    %s_%s..." % (part[9:11].lstrip("0"), p.seed, f.w, f.h, f.rooms, "" if f.rooms == 1 else "s", name, part))
        else:
            levels = ", ".join(str(f.number) for f in p.floors)
            lines.append("%s    Seed %s    Levels %s    %s_%s..." % (LABELS[p.kind], p.seed, levels, name, part))
    return "\n".join(lines) + "\n"


def part_names(m):
    # The file name part for each map in a village or town.
    names, n = [], 0
    for p in m.parts:
        if p.kind == "building":
            n += 1
            names.append("building_%02d_" % n)
        else:
            names.append(p.kind + "_")
    return names


def plan_preview(m):
    # What the window shows: a building's grid sheet, a village's or town's
    # buildings, or the overview.
    if m.kind == "building":
        return floor_sheet(m, m.floors[0], True, floor_header(m, m.floors[0]))
    if m.kind in GROUPS:
        return group_overview(m)
    return dungeon_overview(m) if m.kind == "dungeon" else hideout_overview(m)


# ============================================================================
# FLOOR PLAN SAVING
# ============================================================================

def save_part(m, folder, name, front, overview):
    # Writes one map's files, each named <name>_<front><part>.jpg. front is
    # empty for a map saved on its own.
    jpg = lambda img, part: img.save(os.path.join(folder, "%s_%s%s.jpg" % (name, front, part)), quality=95, subsampling=0)
    for f in m.floors:
        part = "" if m.kind == "building" else "level_%d_" % f.number
        for grid, word in ((False, "walls"), (True, "grid")):
            jpg(floor_sheet(m, f, grid, floor_header(m, f)), part + word)
    for r in m.rooms:
        header = "%sDungeon complex    Room %d of %d    Seed %s" % (at_location(m), r.number, len(m.rooms), m.seed)
        for grid, word in ((False, "walls"), (True, "grid")):
            jpg(floor_sheet(m, r.floor, grid, header), "room_%02d_%s" % (r.number, word))
    if m.kind != "building":
        jpg(overview or hideout_overview(m), "overview")
    if m.kind == "dungeon":
        with open(os.path.join(folder, "%s_%sroom_key.txt" % (name, front)), "w") as out:
            out.write(room_key(m))


def save_plan_map(m, name, overview):
    # Makes Maps/<name> and writes every file into it. Stops with
    # FileExistsError if that folder is already there, so nothing is
    # ever overwritten.
    folder = os.path.join(SAVE, name)
    os.makedirs(folder)
    if m.kind not in GROUPS:
        save_part(m, folder, name, "", overview)
        return folder

    # ── Village or town: every map in it, the preview and the list ────
    for p, front in zip(m.parts, part_names(m)):
        save_part(p, folder, name, front, None)
    overview.save(os.path.join(folder, name + "_overview.jpg"), quality=95, subsampling=0)
    with open(os.path.join(folder, name + "_buildings.txt"), "w") as out:
        out.write(building_list(m, name))
    return folder


PLAN_MAKERS = {"building": make_building, "village": make_village, "hideout": make_hideout, "town": make_town,
          "dungeon": make_dungeon}

# ============================================================================
# ADVENTURE FLOOR PLANS
# ============================================================================

PLAN_KINDS = ("building", "village", "hideout", "town", "dungeon")


def auto_plans(m):
    # Every location's floor plan, picked from the locations seed (the dice
    # carry on from where the locations were placed).
    d = Dice(m.loc_seed)
    place_xs(d, m.grid, m.water, m.box)
    plans = []
    for n in range(len(m.xs)):
        if n == len(m.xs) - 1:
            kind = "town" if d.below(2) == 0 else "dungeon"
        else:
            roll = d.below(10)
            kind = "building" if roll < 6 else "village" if roll < 8 else "hideout"
        plans.append((kind, part_seed(d)))
    return plans


def for_location(m, n):
    # Marks a floor plan, and every map inside a village or town, as made
    # for location n, so their headers say so.
    m.location = n
    for p in m.parts:
        p.location = n
    return m


def plan_front(n, kind):
    # The file name part for location n's floor plan.
    return "location_%02d_%s_" % (n, kind)


def x_list(m, name):
    # The text file saved with the map: every location, its square and its
    # floor plan.
    lines = ["Area map    Code %s" % code(m), "",
             "Locations marked with a red x: %d" % len(m.xs), "",
             "Squares are 70 x 70 pixels: columns A to Q run left to right,",
             "rows 1 to 13 run top to bottom. Locations 1 and %d are the two" % len(m.xs),
             "farthest apart.", "",
             "A floor plan's seed, typed into the seed box while choosing floor plans",
             "with the same button, makes that floor plan again.", ""]
    for n, (p, plan) in enumerate(zip(m.xs, m.plans), 1):
        sx, sy = square_of(p)
        line = "Location %-4d %-5s" % (n, "%s%d" % (COLUMNS[sx], sy + 1))
        if plan:
            line += " %-16s Seed %s    %s_%s..." % (LABELS[plan[0]], plan[1], name, plan_front(n, plan[0]))
        lines.append(line.rstrip())
    return "\n".join(lines) + "\n"


def save_plan(m, folder, name, front):
    # One floor plan's files, named <name>_<front>..., the same way the
    # floor plan buttons save them on their own.
    if m.kind not in GROUPS:
        save_part(m, folder, name, front, None if m.kind == "building" else plan_preview(m))
        return
    for p, part in zip(m.parts, part_names(m)):
        save_part(p, folder, name, front + part, None)
    plan_preview(m).save(os.path.join(folder, "%s_%soverview.jpg" % (name, front)), quality=95, subsampling=0)
    with open(os.path.join(folder, "%s_%sbuildings.txt" % (name, front)), "w") as out:
        out.write(building_list(m, "%s_%s" % (name, front[:-1])))


# ============================================================================
# SAVING
# ============================================================================

def save_area(m, name):
    # Makes Maps/<name> and writes every file into it. Stops with
    # FileExistsError if that folder is already there, so nothing is
    # ever overwritten.
    folder = os.path.join(SAVE, name)
    os.makedirs(folder)
    area_sheet(m).save(os.path.join(folder, name + ".jpg"), quality=95, subsampling=0)
    area_sheet(m, grid=True).save(os.path.join(folder, name + "_grid.jpg"), quality=95, subsampling=0)
    if m.loc_seed:
        with open(os.path.join(folder, name + "_locations.txt"), "w") as out:
            out.write(x_list(m, name))
    for n, plan in enumerate(m.plans, 1):
        if plan:
            save_plan(for_location(PLAN_MAKERS[plan[0]](plan[1]), n), folder, name, plan_front(n, plan[0]))
    return folder


# ============================================================================
# WINDOW
# ============================================================================

def run_window(first=None):
    import tkinter as tk
    from tkinter import font as tkfont, messagebox, simpledialog
    from PIL import ImageTk

    win = tk.Tk()
    win.title("DnD MapBuilder v1.1")
    win.geometry("%dx%d+0+0" % (win.winfo_screenwidth(), win.winfo_screenheight()))
    now = {"map": None, "pic": None, "size": None, "plan": None, "at": 0}

    def white(parent, text, action):
        # A white button: a label, because a Mac draws its own buttons dark
        # grey in Dark Mode but a label keeps the colours it is given. The
        # colours swap only while it is pressed; letting go runs the action.
        button = tk.Label(parent, text=text, bg="white", fg="black", padx=14, pady=3)

        def release(event):
            button.config(bg="white", fg="black")
            action()

        button.bind("<ButtonPress-1>", lambda event: button.config(bg="black", fg="white"))
        button.bind("<ButtonRelease-1>", release)
        return button

    # ── Top of the window: buttons, seed box, status line ─────────────
    # The area buttons and the floor plan buttons share the top spot; only
    # one set shows at a time.
    bar = tk.Frame(win, pady=8)
    bar.pack(side="top", fill="x")
    top = tk.Frame(bar)
    top.pack()
    area_buttons, plan_buttons = tk.Frame(top), tk.Frame(top)
    area_buttons.pack()
    white(area_buttons, "Area map", lambda: show()).pack(side="left", padx=3)
    white(area_buttons, "Adventure locations", lambda: locate()).pack(side="left", padx=3)
    where = tk.StringVar()
    tk.Label(plan_buttons, textvariable=where).pack(pady=(0, 4))
    row = tk.Frame(plan_buttons)
    row.pack()
    for kind in PLAN_KINDS:
        white(row, LABELS[kind], lambda kind=kind: make_plan(kind)).pack(side="left", padx=3)
    box_label = tk.StringVar(value="Seed or code (leave empty for something new):")
    tk.Label(bar, textvariable=box_label).pack(pady=(6, 0))
    seed_box = tk.Entry(bar, width=36, justify="center")
    seed_box.pack()
    status = tk.StringVar(value="Click \"Area map\" to make a new map.")
    bold = tkfont.nametofont("TkDefaultFont").copy()
    bold.configure(weight="bold")
    tk.Entry(bar, textvariable=status, state="readonly", relief="flat", justify="center", font=bold,
             readonlybackground=win.cget("bg"), width=130).pack(pady=4)

    # ── Question row, with white buttons ──────────────────────────────
    ask = tk.Frame(bar)
    question = tk.StringVar()
    view = tk.Label(win, bg="black")
    view.pack(side="bottom", fill="both", expand=True)

    def offer(text, choices):
        # Shows a question with one white button per (label, action).
        for child in ask.winfo_children():
            child.destroy()
        tk.Label(ask, textvariable=question).pack(side="left", padx=4)
        question.set(text)
        for label, action in choices:
            white(ask, label, action).pack(side="left", padx=4)
        ask.pack(pady=(10, 6))

    def fit(event=None):
        size = (max(200, view.winfo_width() - 10), max(200, view.winfo_height() - 10))
        if now["pic"] is None or size == now["size"]:
            return
        now["size"], pic = size, now["pic"]
        scale = min(size[0] / pic.width, size[1] / pic.height, 1)
        now["photo"] = ImageTk.PhotoImage(pic.resize((max(1, round(pic.width * scale)), max(1, round(pic.height * scale))), Image.BOX))
        view.config(image=now["photo"])

    def picture(pic):
        now["pic"], now["size"] = pic, None
        win.update_idletasks()
        fit()

    def new_seed():
        return str(10 ** 14 + int.from_bytes(os.urandom(8), "big") % (9 * 10 ** 14))

    def read_box(typed=None, codes=True):
        typed = (typed or seed_box.get()).strip()
        parts = typed.split("-")
        if typed and (len(parts) > (2 if codes else 1) or not all(part.isdigit() for part in parts)):
            messagebox.showinfo("Seed", "A seed is digits only, like 123456789012345. A code is two seeds "
                                "joined by a dash, like 123456789012345-987654321098765.")
            return None
        seed_box.delete(0, "end")
        return parts if typed else []

    # ── Area map and its locations ────────────────────────────────────
    def area_shown(m, what, started):
        now["map"] = m
        picture(area_sheet(m))
        status.set("%s    %s    Made in %.2f seconds" % (("Code " if m.loc_seed else "Seed ") + code(m), what,
                                                       time.perf_counter() - started))
        if m.xs:
            offer("Would you like to generate floor plans for the locations on your adventure?",
                  [("Yes", start_plans), ("No", ask_save), ("Make automatically", automatic)])
        else:
            offer("Do you want to save the generated map?", [("Yes", save), ("No", clear)])

    def show(typed=None):
        parts = read_box(typed)
        if parts is None:
            return
        started = time.perf_counter()
        seed = parts[0] if parts else new_seed()
        m = make_exterior(seed)
        if m is None:
            clear()
            status.set("Seed %s    No map could be made from this seed. Click again for a new map." % seed)
            return
        what = "Area map" + ("" if m.tries == 1 else "    Try %d" % m.tries)
        if len(parts) == 2:
            add_locations(m, parts[1])
            what += "    Locations marked with a red x: %d" % len(m.xs)
        area_shown(m, what, started)

    def locate():
        parts = read_box()
        if parts is None:
            return
        if len(parts) == 2:
            return show("-".join(parts))
        if now["map"] is None:
            messagebox.showinfo("Adventure locations", "Make a map first with the \"Area map\" button.")
            return
        started = time.perf_counter()
        add_locations(now["map"], parts[0] if parts else new_seed())
        area_shown(now["map"], "Adventure locations    Locations marked with a red x: %d" % len(now["map"].xs), started)

    def ask_save():
        offer("Save?", [("Yes", save), ("No", clear)])

    def automatic():
        m = now["map"]
        m.plans = auto_plans(m)
        kinds = [LABELS[kind] for kind, _ in m.plans]
        status.set("Code %s    Floor plans made: %s" % (code(m), ", ".join(
            "%d %s" % (kinds.count(k), k) for k in dict.fromkeys(kinds))))
        ask_save()

    # ── Floor plans, one location at a time ───────────────────────────
    def start_plans():
        now["at"] = 0
        area_buttons.pack_forget()
        plan_buttons.pack()
        box_label.set("Floor plan seed (leave empty for a new one):")
        next_location()

    def next_location():
        m, n = now["map"], now["at"]
        sx, sy = square_of(m.xs[n])
        text = "Location %d of %d, square %s%d: click a button to make its floor plan." % (n + 1, len(m.xs), COLUMNS[sx], sy + 1)
        if n == len(m.xs) - 1:
            text += "  Last location: a \"Dungeon complex\" or a \"Town\" makes a good finale."
        where.set(text)
        now["plan"] = None
        picture(area_sheet(m, focus=n + 1))
        ask.pack_forget()

    def make_plan(kind):
        parts = read_box(codes=False)
        if parts is None:
            return
        started = time.perf_counter()
        seed = parts[0] if parts else new_seed()
        plan = for_location(PLAN_MAKERS[kind](seed), now["at"] + 1)
        now["plan"] = (kind, seed)
        picture(plan_preview(plan))
        houses = sum(p.kind == "building" for p in plan.parts)
        status.set("Location %d    %s%s    Seed %s    Made in %.2f seconds" % (
            now["at"] + 1, LABELS[kind], "    %d Buildings" % houses if houses else "", seed, time.perf_counter() - started))
        choices = [("Use for this location", use_plan)]
        if kind in ("dungeon",) + GROUPS:
            choices.append(("Open full size", lambda: now["pic"].show()))
        offer("Use this floor plan for location %d?" % (now["at"] + 1), choices)

    def use_plan():
        m = now["map"]
        m.plans[now["at"]] = now["plan"]
        now["at"] += 1
        if now["at"] < len(m.xs):
            return next_location()
        plan_buttons.pack_forget()
        area_buttons.pack()
        box_label.set("Seed or code (leave empty for something new):")
        picture(area_sheet(m))
        status.set("Code %s    Every location has a floor plan." % code(m))
        ask_save()

    # ── Saving ────────────────────────────────────────────────────────
    def save():
        while True:
            name = (simpledialog.askstring("Save map", "Type a name for this map:", parent=win) or "").strip()
            if not name:
                return
            if name.startswith(".") or any(ch in name for ch in '/\\:*?"<>|'):
                messagebox.showinfo("Save map", "Use a name without / \\ : * ? \" < > | and not starting with a dot.")
                continue
            try:
                folder = save_area(now["map"], name)
            except FileExistsError:
                messagebox.showinfo("Save map", "There is already a folder called \"%s\". Pick another name." % name)
                continue
            status.set("Saved in %s    (%s)" % (folder, code(now["map"])))
            ask.pack_forget()
            return

    def clear():
        now["map"] = now["pic"] = None
        view.config(image="")
        status.set("Not saved.")
        ask.pack_forget()

    view.bind("<Configure>", fit)
    if first:
        win.update()
        show(first)
    win.mainloop()


# ============================================================================
# START
# ============================================================================

# An optional seed or code. Anything else stops with a short usage line.

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) > 1 or (args and not all(part.isdigit() for part in args[0].split("-"))):
        sys.exit("Use: [SEED or CODE]")
    run_window(args[0] if args else None)
