#!/usr/bin/env python3
# ============================================================================
# DnD-MapBuilder-Exterior_v1.0.py
# ============================================================================

"""
.SYNOPSIS
    Tkinter window that makes random exterior area maps (lines only) and
    saves them as JPG files.

.DESCRIPTION
    Lines that cut an open area into regions, for tabletop games. The lines
    carry no meaning (no cliffs, roads or walls): this is a look at what the
    layout can be. One click makes a whole map, shows it in the window and
    asks whether to save it. A second click adds the adventure locations.

    The window:
      - Two buttons at the top. "Area map" makes a new map with no
        locations. "Adventure locations" puts new locations marked with a
        red x on the map that is showing, and can be clicked again for
        other locations on the same map
      - The seed box is under the buttons. Leave it empty for something
        new. Type a seed and click "Area map" to get that map back, or
        click "Adventure locations" to get those locations on the map that
        is showing. Type a code (map seed, dash, locations seed) and click
        either button to get that map with those locations back
      - The line of text under the seed box says what was made, with its
        seed or code. It can be selected and copied, so it can be kept
      - While a map is waiting to be saved, the question "Do you want to
        save the generated map?" shows with white "Yes" and "No" buttons
      - The window follows the Mac's light or dark look; the save buttons
        stay white either way
      - The black preview area fills the rest of the window and the map is
        fitted to it again whenever the window changes size

    Every map:
      - Each map has a seed, a string of digits, and its adventure
        locations have a seed of their own. The code joins the two with a
        dash, like 123456789012345-987654321098765. The same seed always
        makes the same map, and the same code the same map with the same
        locations, because the script uses its own whole-number dice (Dice)
        and never the standard "random" module
      - Each map is built from its seed in a fixed number of steps. When a
        map cannot be finished, it is built again from the next seed value,
        up to 9 more times. If all 10 go wrong the window says so and no
        map is made

    The Area Map and the node matrix:
      - 17 x 13 squares of 70 x 70 pixels (1190 x 910 pixels). The grid is
        not drawn
      - Each square gets 3 nodes at random pixels inside it, so a map has
        663 nodes, in new places every map. Every interior line runs from
        node to node through these
      - The Map Border sits 105 pixels in from the outer edge, which leaves
        980 x 700 pixels inside it

    TPNodes (the shape in the middle):
      - 3 or 5, 1 chance in 2 each: a triangle or a pentagon. Never 4
      - Each is a node inside the Map Border, at least 245 pixels from
        every other
      - Every TPNode is a corner of the shape, so it is a true triangle or
        pentagon. No corner is within 2 degrees of a right angle (88 to 92)
      - The shape covers 270,000 to 290,000 square pixels. TPNodes start at
        random nodes, then a random TPNode is moved to a node in its own or
        a touching square, and the move is kept when the gap still holds
        and the shape is no worse. After 300 moves without a good shape,
        the map is built again from the next seed value

    ENodes (where lines meet the edge):
      - Exactly 3, each a random pixel on a different side of the Area Map,
        never at a corner. One side, picked at random, gets none

    Lines:
      - Every line is a Rolling line: it walks node to node through the
        matrix, and from the node it is on it goes to one of the nearest
        nodes where the bend is obtuse (over 90 degrees) and that is nearer
        to the line's far end than the node it is on
      - Each step picks at random among the 3 nearest nodes that fit, so no
        line is ever straight. A line has 2 or more segments
      - Each TPNode is joined to its 2 nearest TPNodes, each pair once. If
        that leaves TPNodes cut off from the rest, the shortest line that
        joins them is added. These lines bend only at nodes inside the Map
        Border
      - Each ENode is joined to its closest TPNode. That line can bend at
        any node, outer margin included, except a node lying on the outer
        edge itself
      - No line crosses itself or another line, and none passes through a
        TPNode or ENode that is not its own end. Two lines meet only at a
        TPNode or ENode they both end on
      - If a line gets stuck (no node fits, or every one would cross a
        line), it steps back and tries the next node. It gets 6 fresh tries
        of up to 2,000 segments each

    Textures:
      - The lines and the frame cut the Area Map into areas. Three of them,
        picked at random, get one texture each: forest, sand and rock, and
        water. Every other area stays blank. Areas under 10,000 square
        pixels are never picked
      - The marks are thin and grey so they use little toner and draw fast,
        scattered on a loose grid with a random nudge, and kept clear of the
        lines:
          forest: small trees, a ring on a short trunk
          sand and rock: dots, with a small open triangle now and then
          water: small waves, two shallow arcs side by side

    Locations marked with a red x:
      - Made by "Adventure locations", from the locations seed only, so new
        locations never change the map under them
      - 7 to 29 of them, a random number each time. Each is inside the Map
        Border, never in the water or within 10 pixels of it, and at least
        40 pixels from the others
      - Each location has a number. Location 1 and the last location are
        the two farthest apart in a straight line; the others are numbered
        in order along the straight line between those two
      - Squares are named by column and row: A to Q along the top and
        bottom edges, left to right, and 1 to 13 down both sides, so a
        location can be found by its square, like C7

    Pictures:
      - The sheet is the Area Map with a 1 square (70 pixel) margin all
        round, and a header row on top: Exterior and the seed, or, with
        adventure locations, Exterior, the code and the number of
        locations marked with a red x. The column letters and row numbers
        sit in the margin
      - Interior lines are 1 pixel wide in one colour, inside a 7 pixel
        frame round the Area Map. Colour, widths, frame and showing the
        nodes are in the SETTINGS section
      - A map saves as 2 JPGs in a folder of its own: <name>.jpg with the
        lines only, and <name>_grid.jpg with a blue 70 x 70 pixel grid,
        1 pixel wide, under the lines inside the Area Map. The window shows
        the one without the grid
      - With adventure locations, saving also writes <name>_locations.txt:
        the code, the number of locations marked with a red x, then every
        location by number with its square

    Lines that start with "#" are notes for people. Python ignores them.

.NOTES
    Author : Brennon Hedman
    Version: 1.0
    Requires: Python 3.8+ and Pillow 10.1+ (python3 -m pip install pillow)
    Platform: macOS, Windows or Linux (the window uses Tkinter, which comes
              with the standard Python installer)

.EXAMPLE
    python3 DnD-MapBuilder-Exterior_v1.0.py

    Opens the window with the two buttons.

.EXAMPLE
    python3 DnD-MapBuilder-Exterior_v1.0.py 123456789012345

    Opens the window already showing the map with seed 123456789012345.

.EXAMPLE
    python3 DnD-MapBuilder-Exterior_v1.0.py 123456789012345-987654321098765

    Opens the window showing that map with the locations from seed
    987654321098765.
"""

import math
import os
import sys
import time
from PIL import Image, ImageDraw, ImageFont


# ============================================================================
# SETTINGS
# ============================================================================

SQ, AW, AH = 70, 17, 13
W, H = AW * SQ, AH * SQ
PER_SQUARE = 3
BORDER = 105
INSIDE = (BORDER, BORDER, W - BORDER, H - BORDER)
LOOSE = (1, 1, W - 1, H - 1)

CHOICES = 3
RESTARTS, BUDGET = 6, 2000
TOLERANCE = 2

GAP = 245
AREA_LOW, AREA_HIGH = 270000, 290000
MOVES = 300
REDRAWS = 9

BLACK, WHITE, BLUE = (0, 0, 0), (255, 255, 255), (140, 190, 255)
LINE_COLOR, LINE_WIDTH = BLACK, 1
FRAME_WIDTH = 7
FRAME = True
SHOW_NODES, NODE_COLOR = False, BLUE
GRID_COLOR, GRID_WIDTH = BLUE, 1

TEXTURES = ("forest", "sand", "water")
CELL = 5
SMALLEST = 400
EDGE = 2
TEXTURE_COLOR = (90, 90, 90)

X_COUNT = (7, 29)
X_GAP = 40
X_SIZE = 7
RED = (220, 0, 0)
COLUMNS = "ABCDEFGHIJKLMNOPQ"
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


NOTHING = frozenset()


def side(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def on_segment(n, p, q):
    return (side(p, q, n) == 0 and min(p[0], q[0]) <= n[0] <= max(p[0], q[0])
            and min(p[1], q[1]) <= n[1] <= max(p[1], q[1]))


def clash(p, q, r, s, ok):
    if (max(p[0], q[0]) < min(r[0], s[0]) or max(r[0], s[0]) < min(p[0], q[0])
            or max(p[1], q[1]) < min(r[1], s[1]) or max(r[1], s[1]) < min(p[1], q[1])):
        return False
    d1, d2_, d3, d4 = side(r, s, p), side(r, s, q), side(p, q, r), side(p, q, s)
    if d1 * d2_ > 0 or d3 * d4 > 0:
        return False
    shared = [e for e in (p, q) if e == r or e == s]
    if len(shared) != 1:
        return True
    e = shared[0]
    if d1 == 0 and d2_ == 0:
        a, b = (q if e == p else p), (s if e == r else r)
        if (a[0] - e[0]) * (b[0] - e[0]) + (a[1] - e[1]) * (b[1] - e[1]) > 0:
            return True
    return e not in ok


def d2(p, q):
    return (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2


def inside(p, box):
    return box[0] <= p[0] <= box[2] and box[1] <= p[1] <= box[3]


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


# ============================================================================
# BENDS
# ============================================================================


def obtuse(u, v):
    dot, cross = -u[0] * v[0] - u[1] * v[1], u[0] * v[1] - u[1] * v[0]
    return cross != 0 and dot < 0


# ============================================================================
# NODE MATRIX
# ============================================================================

def square_of(p):
    return min(p[0] // SQ, AW - 1), min(p[1] // SQ, AH - 1)


def make_matrix(d):
    cells = {}
    for sy in range(AH):
        for sx in range(AW):
            spots = [(sx * SQ + d.below(SQ), sy * SQ + d.below(SQ)) for _ in range(PER_SQUARE)]
            cells[(sx, sy)] = list(dict.fromkeys(spots))
    return cells


def make_ring(cells):
    return {(sx, sy): [q for x in range(sx - 1, sx + 2) for y in range(sy - 1, sy + 2) for q in cells.get((x, y), ())]
            for sx, sy in cells}


def around(ring, p):
    return ring[square_of(p)]


# ============================================================================
# TPNODES
# ============================================================================

def shape_cost(points):
    corners = hull(points)
    faults, twice = len(points) - len(corners), 0
    if len(corners) >= 3:
        for i, q in enumerate(corners):
            p, r = corners[i - 1], corners[(i + 1) % len(corners)]
            u, v = (p[0] - q[0], p[1] - q[1]), (r[0] - q[0], r[1] - q[1])
            angle = math.degrees(math.atan2(abs(u[0] * v[1] - u[1] * v[0]), u[0] * v[0] + u[1] * v[1]))
            if abs(angle - 90) <= TOLERANCE:
                faults += 1
            twice += q[0] * r[1] - r[0] * q[1]
    twice = abs(twice)
    return faults, max(2 * AREA_LOW - twice, twice - 2 * AREA_HIGH, 0)


def place_tps(d, count, cells, ring):
    spots = [p for ps in cells.values() for p in ps if inside(p, INSIDE)]
    pts = []
    for _ in range(count):
        free = [s for s in spots if all(d2(s, p) >= GAP * GAP for p in pts)]
        if not free:
            return None
        pts.append(d.pick(free))
    cost = shape_cost(pts)
    for _ in range(MOVES):
        if cost == (0, 0):
            break
        i = d.below(count)
        near = [q for q in around(ring, pts[i]) if inside(q, INSIDE) and q not in pts]
        if not near:
            continue
        q = d.pick(near)
        if any(d2(q, p) < GAP * GAP for j, p in enumerate(pts) if j != i):
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
        if n == skip:
            continue
        if s in "NS":
            found.append((d.between(1, W - 1), 0 if s == "N" else H))
        else:
            found.append((0 if s == "W" else W, d.between(1, H - 1)))
    return found


# ============================================================================
# LINES
# ============================================================================

def squares_under(p, q):
    (x0, y0), (x1, y1) = square_of((min(p[0], q[0]), min(p[1], q[1]))), square_of((max(p[0], q[0]), max(p[1], q[1])))
    return [(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)]


def blocked(p, q, mine, foreign, drawn, ends):
    if any(on_segment(n, p, q) for n in foreign):
        return True
    if any(clash(p, q, r, s, NOTHING) for r, s in mine):
        return True
    near = {seg for c in squares_under(p, q) for seg in drawn.get(c, ())}
    return any(clash(p, q, r, s, ends) for r, s in near)


def route(d, a, b, box, ring, ends, drawn):
    foreign = [n for n in ends if n != a and n != b]

    def extend(p, prev):
        fits = []
        for q in around(ring, p):
            if q == p or q in path or (q != b and (q in ends or not inside(q, box))):
                continue
            if q == b and len(path) < 2:
                continue
            if d2(q, b) >= d2(p, b):
                continue
            if prev is not None and not obtuse((p[0] - prev[0], p[1] - prev[1]), (q[0] - p[0], q[1] - p[1])):
                continue
            fits.append((d2(p, q), q))
        fits = [q for _, q in sorted(fits)]
        for q in d.shuffle(fits[:CHOICES]) + fits[CHOICES:]:
            if tried[0] >= BUDGET:
                return False
            tried[0] += 1
            if blocked(p, q, zip(path, path[1:-1]), foreign, drawn, ends):
                continue
            path.append(q)
            if q == b or extend(q, p):
                return True
            path.pop()
        return False

    for _ in range(RESTARTS):
        tried, path = [0], [a]
        if extend(a, None):
            return path
    return None


# ============================================================================
# TEXTURES
# ============================================================================


def find_areas(lines):
    cw, ch = W // CELL, H // CELL
    small = Image.new("L", (cw, ch), 0)
    draw = ImageDraw.Draw(small)
    draw.rectangle((0, 0, cw - 1, ch - 1), outline=255)
    for path in lines:
        draw.line([(min(x // CELL, cw - 1), min(y // CELL, ch - 1)) for x, y in path], fill=255)
    wall = small.load()
    area_of, areas = {}, []
    for y in range(ch):
        for x in range(cw):
            if wall[x, y] or (x, y) in area_of:
                continue
            group, todo = [], [(x, y)]
            area_of[(x, y)] = len(areas)
            while todo:
                cx, cy = todo.pop()
                group.append((cx, cy))
                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if 0 <= nx < cw and 0 <= ny < ch and not wall[nx, ny] and (nx, ny) not in area_of:
                        area_of[(nx, ny)] = len(areas)
                        todo.append((nx, ny))
            areas.append(group)
    return areas, area_of


def place_textures(d, lines):
    areas, area_of = find_areas(lines)
    big = d.shuffle([n for n, cells in enumerate(areas) if len(cells) >= SMALLEST])
    spacing = {"forest": (34, 34), "sand": (16, 16), "water": (40, 26)}
    marks, water = [], None
    for texture, n in zip(TEXTURES, big):
        if texture == "water":
            water = n
        sx, sy = spacing[texture]
        xs, ys = [c[0] for c in areas[n]], [c[1] for c in areas[n]]
        for y in range(min(ys) * CELL, (max(ys) + 1) * CELL, sy):
            for x in range(min(xs) * CELL, (max(xs) + 1) * CELL, sx):
                px, py = x + d.below(sx // 2 + 1), y + d.below(sy // 2 + 1)
                cx, cy = px // CELL, py // CELL
                if all(area_of.get((cx + i, cy + j)) == n for i in range(-EDGE, EDGE + 1) for j in range(-EDGE, EDGE + 1)):
                    marks.append((texture, px, py))
    return marks, area_of, water


# ============================================================================
# LOCATIONS MARKED WITH A RED X
# ============================================================================

def square_name(p):
    sx, sy = square_of(p)
    return "%s%d" % (COLUMNS[sx], sy + 1)


def place_xs(d, area_of, water):
    x0, y0, x1, y1 = INSIDE
    span = range(-EDGE, EDGE + 1)
    free = [(x, y) for y in range(y0, y1 + 1, 10) for x in range(x0, x1 + 1, 10)
            if water is None or all(area_of.get((x // CELL + i, y // CELL + j)) != water for i in span for j in span)]
    xs = []
    for _ in range(d.between(*X_COUNT)):
        if not free:
            break
        p = d.pick(free)
        xs.append(p)
        free = [q for q in free if d2(p, q) >= X_GAP * X_GAP]
    if len(xs) < 2:
        return xs
    _, i, j = max((d2(p, q), i, j) for i, p in enumerate(xs) for j, q in enumerate(xs) if i < j)
    a, b = xs[i], xs[j]
    along = lambda q: (q[0] - a[0]) * (b[0] - a[0]) + (q[1] - a[1]) * (b[1] - a[1])
    return [a] + sorted((q for k, q in enumerate(xs) if k not in (i, j)), key=lambda q: (along(q), q)) + [b]


def x_list(m):
    lines = ["Exterior    Code %s" % code(m), "",
             "Locations marked with a red x: %d" % len(m.xs), "",
             "Squares are 70 x 70 pixels: columns A to Q run left to right,",
             "rows 1 to 13 run top to bottom. Locations 1 and %d are the two" % len(m.xs),
             "farthest apart.", ""]
    lines += ["Location %-4d %s" % (n, square_name(p)) for n, p in enumerate(m.xs, 1)]
    return "\n".join(lines) + "\n"


# ============================================================================
# MAP BUILDER
# ============================================================================

class Exterior:
    def __init__(self, seed, cells, tps, enodes, lines, marks, area_of, water, tries):
        self.seed, self.cells, self.tps, self.enodes, self.lines, self.tries = seed, cells, tps, enodes, lines, tries
        self.marks, self.area_of, self.water = marks, area_of, water
        self.loc_seed, self.xs = None, []


def add_locations(m, loc_seed):
    m.loc_seed = loc_seed
    m.xs = place_xs(Dice(loc_seed), m.area_of, m.water)


def code(m):
    return "%s-%s" % (m.seed, m.loc_seed) if m.loc_seed else m.seed


def near_pairs(tps):
    pairs, group = set(), list(range(len(tps)))
    for i, a in enumerate(tps):
        for _, j in sorted((d2(a, b), j) for j, b in enumerate(tps) if j != i)[:2]:
            pairs.add((min(i, j), max(i, j)))

    def top(n):
        while group[n] != n:
            n = group[n]
        return n

    for i, j in pairs:
        group[top(i)] = top(j)
    while len({top(n) for n in group}) > 1:
        _, i, j = min((d2(tps[i], tps[j]), i, j) for i in range(len(tps)) for j in range(i + 1, len(tps)) if top(i) != top(j))
        pairs.add((i, j))
        group[top(i)] = top(j)
    return sorted(pairs)


def draw_once(value):
    d = Dice(value)

    # ── Node matrix, TPNodes and ENodes ───────────────────────────────
    cells = make_matrix(d)
    ring = make_ring(cells)
    tps = place_tps(d, d.pick((3, 5)), cells, ring)
    if tps is None:
        return None
    enodes = place_enodes(d)
    ends = frozenset(tps) | frozenset(enodes)

    # ── Which points get a line ───────────────────────────────────────
    jobs = [(tps[i], tps[j], INSIDE) for i, j in near_pairs(tps)]
    jobs += [(e, min(tps, key=lambda p: d2(e, p)), LOOSE) for e in enodes]

    # ── Draw each line ────────────────────────────────────────────────
    drawn, lines = {}, []
    for a, b, box in jobs:
        path = route(d, a, b, box, ring, ends, drawn)
        if not path:
            return None
        lines.append(path)
        for p, q in zip(path, path[1:]):
            for c in squares_under(p, q):
                drawn.setdefault(c, []).append((p, q))
    marks, area_of, water = place_textures(d, lines)
    return cells, tps, enodes, lines, marks, area_of, water


def make_exterior(seed):
    for tries in range(1, REDRAWS + 2):
        got = draw_once(int(seed) + tries - 1)
        if got:
            return Exterior(seed, *got, tries)
    return None


# ============================================================================
# DRAWING
# ============================================================================

def font_for(text, width, size=28):
    while size > 10 and ImageFont.load_default(size).getlength(text) > width - 40:
        size -= 2
    return ImageFont.load_default(size)


def sheet(m, grid=False):
    img = Image.new("RGB", (W + 2 * SQ, H + 3 * SQ), WHITE)
    draw = ImageDraw.Draw(img)
    ox, oy, r, f = SQ, 2 * SQ, LINE_WIDTH // 2, FRAME_WIDTH // 2
    at = lambda p: (ox + p[0], oy + p[1])

    # ── Blue grid, inside the Area Map only ───────────────────────────
    if grid:
        for x in range(ox, ox + W + 1, SQ):
            draw.line((x, oy, x, oy + H), fill=GRID_COLOR, width=GRID_WIDTH)
        for y in range(oy, oy + H + 1, SQ):
            draw.line((ox, y, ox + W, y), fill=GRID_COLOR, width=GRID_WIDTH)

    # ── Node matrix ───────────────────────────────────────────────────
    if SHOW_NODES:
        for ps in m.cells.values():
            for p in ps:
                cx, cy = at(p)
                draw.ellipse((cx - 2, cy - 2, cx + 2, cy + 2), fill=NODE_COLOR)

    # ── Frame round the Area Map ──────────────────────────────────────
    if FRAME:
        draw.rectangle((ox - f, oy - f, ox + W + f, oy + H + f), outline=LINE_COLOR, width=FRAME_WIDTH)

    # ── Texture marks, thin and grey ──────────────────────────────────
    for texture, x, y in m.marks:
        x, y = ox + x, oy + y
        if texture == "forest":
            draw.ellipse((x - 5, y - 9, x + 5, y + 1), outline=TEXTURE_COLOR)
            draw.line((x, y + 1, x, y + 5), fill=TEXTURE_COLOR)
        elif texture == "sand":
            if (x * 7 + y * 13) % 9:
                draw.point((x, y), fill=TEXTURE_COLOR)
            else:
                draw.polygon(((x, y - 4), (x - 4, y + 3), (x + 4, y + 3)), outline=TEXTURE_COLOR)
        else:
            draw.arc((x - 8, y - 3, x, y + 3), 180, 360, fill=TEXTURE_COLOR)
            draw.arc((x, y - 3, x + 8, y + 3), 0, 180, fill=TEXTURE_COLOR)

    # ── Lines: one colour, round at every corner and end ──────────────
    for path in m.lines:
        for p in path:
            cx, cy = at(p)
            draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=LINE_COLOR)
        for p, q in zip(path, path[1:]):
            draw.line((at(p), at(q)), fill=LINE_COLOR, width=LINE_WIDTH)
    # ── Locations marked with a red x, and their numbers ──────────────
    small = ImageFont.load_default(16)
    for n, p in enumerate(m.xs, 1):
        cx, cy = at(p)
        draw.line((cx - X_SIZE, cy - X_SIZE, cx + X_SIZE, cy + X_SIZE), fill=RED, width=3)
        draw.line((cx - X_SIZE, cy + X_SIZE, cx + X_SIZE, cy - X_SIZE), fill=RED, width=3)
        draw.text((cx + X_SIZE + 2, cy - X_SIZE - 1), str(n), fill=RED, font=small, anchor="lb")

    # ── Square names round the edge: A to Q across, 1 to 13 down ──────
    label = ImageFont.load_default(22)
    for i, letter in enumerate(COLUMNS[:AW]):
        x = ox + i * SQ + SQ // 2
        draw.text((x, oy - SQ // 2), letter, fill=BLACK, font=label, anchor="mm")
        draw.text((x, oy + H + SQ // 2), letter, fill=BLACK, font=label, anchor="mm")
    for j in range(AH):
        y = oy + j * SQ + SQ // 2
        draw.text((ox - SQ // 2, y), str(j + 1), fill=BLACK, font=label, anchor="mm")
        draw.text((ox + W + SQ // 2, y), str(j + 1), fill=BLACK, font=label, anchor="mm")
    header = "Exterior    Seed %s" % m.seed
    if m.loc_seed:
        header = "Exterior    Code %s    Locations marked with a red x: %d" % (code(m), len(m.xs))
    draw.text((20, SQ // 2), header, fill=BLACK, font=font_for(header, img.width), anchor="lm")
    return img


# ============================================================================
# SAVING
# ============================================================================

def save_map(m, name):
    folder = os.path.join(SAVE, name)
    os.makedirs(folder)
    sheet(m).save(os.path.join(folder, name + ".jpg"), quality=95, subsampling=0)
    sheet(m, grid=True).save(os.path.join(folder, name + "_grid.jpg"), quality=95, subsampling=0)
    if m.loc_seed:
        with open(os.path.join(folder, name + "_locations.txt"), "w") as out:
            out.write(x_list(m))
    return folder


# ============================================================================
# WINDOW
# ============================================================================

def run_window(first_seed=None):
    import tkinter as tk
    from tkinter import messagebox, simpledialog
    from PIL import ImageTk

    win = tk.Tk()
    win.title("DnD MapBuilder Exterior v1.0")
    win.geometry("%dx%d+0+0" % (win.winfo_screenwidth(), win.winfo_screenheight()))
    now = {"map": None, "pic": None, "size": None}

    # ── Top of the window: buttons, seed box, status line ─────────────
    bar = tk.Frame(win, pady=8)
    bar.pack(side="top", fill="x")
    buttons = tk.Frame(bar)
    buttons.pack()
    tk.Button(buttons, text="Area map", command=lambda: show()).pack(side="left", padx=3)
    tk.Button(buttons, text="Adventure locations", command=lambda: locate()).pack(side="left", padx=3)
    tk.Label(bar, text="Seed or code (leave empty for something new):").pack(pady=(6, 0))
    seed_box = tk.Entry(bar, width=36, justify="center")
    seed_box.pack()
    status = tk.StringVar(value="Click \"Area map\" to make a new map.")
    tk.Entry(bar, textvariable=status, state="readonly", relief="flat", justify="center",
             readonlybackground=win.cget("bg"), width=110).pack(pady=4)

    # ── Save question, with white buttons ─────────────────────────────
    ask = tk.Frame(bar)
    tk.Label(ask, text="Do you want to save the generated map?").pack(side="left", padx=4)

    def white(text, command):
        button = tk.Label(ask, text=text, bg="white", fg="black", padx=14, pady=3, cursor="hand2")
        button.bind("<Button-1>", lambda event: command())
        return button

    white("Yes", lambda: save()).pack(side="left", padx=4)
    white("No", lambda: clear()).pack(side="left", padx=4)
    view = tk.Label(win, bg="black")
    view.pack(side="bottom", fill="both", expand=True)

    def fit(event=None):
        size = (max(200, view.winfo_width() - 10), max(200, view.winfo_height() - 10))
        if now["pic"] is None or size == now["size"]:
            return
        now["size"] = size
        pic = now["pic"]
        scale = min(size[0] / pic.width, size[1] / pic.height, 1)
        now["photo"] = ImageTk.PhotoImage(pic.resize((max(1, round(pic.width * scale)), max(1, round(pic.height * scale))), Image.BOX))
        view.config(image=now["photo"])

    def new_seed():
        return str(10 ** 14 + int.from_bytes(os.urandom(8), "big") % (9 * 10 ** 14))

    def read_box(typed=None):
        typed = (typed or seed_box.get()).strip()
        parts = typed.split("-")
        if typed and (len(parts) > 2 or not all(part.isdigit() for part in parts)):
            messagebox.showinfo("Seed", "A seed is digits only, like 123456789012345. A code is two seeds "
                                "joined by a dash, like 123456789012345-987654321098765.")
            return None
        return parts if typed else []

    def display(m, what, started):
        now["map"], now["pic"], now["size"] = m, sheet(m), None
        ask.pack(pady=(0, 6))
        win.update_idletasks()
        fit()
        seed_box.delete(0, "end")
        status.set("%s    %s    Made in %.2f seconds" % (("Code " if m.loc_seed else "Seed ") + code(m), what,
                                                       time.perf_counter() - started))

    def show(typed=None):
        parts = read_box(typed)
        if parts is None:
            return
        started = time.perf_counter()
        seed = parts[0] if parts else new_seed()
        m = make_exterior(seed)
        if m is None:
            now["map"] = now["pic"] = None
            view.config(image="")
            ask.pack_forget()
            seed_box.delete(0, "end")
            status.set("Seed %s    No map could be made from this seed. Click again for a new map." % seed)
            return
        what = "Area map    %s%s" % ("Triangle" if len(m.tps) == 3 else "Pentagon", "" if m.tries == 1 else "    Try %d" % m.tries)
        if len(parts) == 2:
            add_locations(m, parts[1])
            what += "    Locations marked with a red x: %d" % len(m.xs)
        display(m, what, started)

    def locate():
        parts = read_box()
        if parts is None:
            return
        if len(parts) == 2:
            show()
            return
        if now["map"] is None:
            messagebox.showinfo("Adventure locations", "Make a map first with the \"Area map\" button.")
            return
        started = time.perf_counter()
        add_locations(now["map"], parts[0] if parts else new_seed())
        display(now["map"], "Adventure locations    Locations marked with a red x: %d" % len(now["map"].xs), started)

    def save():
        while True:
            name = (simpledialog.askstring("Save map", "Type a name for this map:", parent=win) or "").strip()
            if not name:
                return
            if name.startswith(".") or any(ch in name for ch in '/\\:*?"<>|'):
                messagebox.showinfo("Save map", "Use a name without / \\ : * ? \" < > | and not starting with a dot.")
                continue
            try:
                folder = save_map(now["map"], name)
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
    if first_seed:
        win.update()
        show(first_seed)
    win.mainloop()


# ============================================================================
# START
# ============================================================================


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) > 1 or (args and not all(part.isdigit() for part in args[0].split("-"))):
        sys.exit("Use: [SEED or CODE]")
    run_window(args[0] if args else None)
