#!/usr/bin/env python3
# ============================================================================
# DnD-MapBuilder-Exterior_v2.0.py
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
      - Each TPNode is joined to its 2 nearest TPNodes, each pair once,
        which always joins all of them. These lines bend only at nodes
        inside the Map Border
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
    Version: 2.0
    Requires: Python 3.8+ and Pillow 10.1+ (python3 -m pip install pillow)
    Platform: macOS, Windows or Linux (the window uses Tkinter, which comes
              with the standard Python installer)

.EXAMPLE
    python3 DnD-MapBuilder-Exterior_v2.0.py

    Opens the window with the two buttons.

.EXAMPLE
    python3 DnD-MapBuilder-Exterior_v2.0.py 123456789012345

    Opens the window already showing the map with seed 123456789012345.

.EXAMPLE
    python3 DnD-MapBuilder-Exterior_v2.0.py 123456789012345-987654321098765

    Opens the window showing that map with the locations from seed
    987654321098765.
"""

import math, os, re, sys, time
from PIL import Image, ImageDraw, ImageFont


# ============================================================================
# SETTINGS
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


def x_list(m):
    lines = ["Exterior    Code %s" % code(m), "",
             "Locations marked with a red x: %d" % len(m.xs), "",
             "Squares are 70 x 70 pixels: columns A to Q run left to right,",
             "rows 1 to 13 run top to bottom. Locations 1 and %d are the two" % len(m.xs),
             "farthest apart.", ""]
    for n, p in enumerate(m.xs, 1):
        sx, sy = square_of(p)
        lines.append("Location %-4d %s%d" % (n, COLUMNS[sx], sy + 1))
    return "\n".join(lines) + "\n"


# ============================================================================
# MAP BUILDER
# ============================================================================

class Exterior:
    def __init__(self, seed, cells, tps, lines, marks, grid, water, box, tries):
        self.seed, self.cells, self.tps, self.lines, self.marks, self.tries = seed, cells, tps, lines, marks, tries
        self.grid, self.water, self.box = grid, water, box
        self.loc_seed, self.xs = None, []


def add_locations(m, loc_seed):
    m.loc_seed = loc_seed
    m.xs = place_xs(Dice(loc_seed), m.grid, m.water, m.box)


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
        x, y = ox + x, oy + y
        draw.line((x - X_SIZE, y - X_SIZE, x + X_SIZE, y + X_SIZE), fill=RED, width=3)
        draw.line((x - X_SIZE, y + X_SIZE, x + X_SIZE, y - X_SIZE), fill=RED, width=3)
        draw.text((x + X_SIZE + 2, y - X_SIZE - 1), str(n), fill=RED, font=small, anchor="lb")

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

def run_window(first=None):
    import tkinter as tk
    from tkinter import messagebox, simpledialog
    from PIL import ImageTk

    win = tk.Tk()
    win.title("DnD MapBuilder Exterior v2.0")
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
    for text, command in (("Yes", lambda: save()), ("No", lambda: clear())):
        button = tk.Label(ask, text=text, bg="white", fg="black", padx=14, pady=3, cursor="hand2")
        button.bind("<Button-1>", lambda event, command=command: command())
        button.pack(side="left", padx=4)
    view = tk.Label(win, bg="black")
    view.pack(side="bottom", fill="both", expand=True)

    def fit(event=None):
        size = (max(200, view.winfo_width() - 10), max(200, view.winfo_height() - 10))
        if now["pic"] is None or size == now["size"]:
            return
        now["size"], pic = size, now["pic"]
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
            clear()
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
            return show()
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
    if first:
        win.update()
        show(first)
    win.mainloop()


# ============================================================================
# START
# ============================================================================

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) > 1 or (args and not all(part.isdigit() for part in args[0].split("-"))):
        sys.exit("Use: [SEED or CODE]")
    run_window(args[0] if args else None)
