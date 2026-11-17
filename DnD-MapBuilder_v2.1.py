#!/usr/bin/env python3
# ============================================================================
# DnD-MapBuilder_v2.1.py
# ============================================================================

"""
.SYNOPSIS
    Tkinter window that makes a random outdoor area map with adventure
    locations, then a floor plan for every location, and saves them all as
    JPG files with a text list of the locations.

.DESCRIPTION
    The area maps come from DnD-MapBuilder-Exterior v2.0, so the same seeds
    make the same area maps and locations as there. Buildings and hideouts
    are built and drawn by DnD-MapBuilder-Interior v1.0, so the same seed
    makes the same building or hideout as there. The dungeon complex keeps
    the even grid of rooms and short corridors, and every room inside it is
    built and drawn by the Interior v1.0 builder too.

    The area map:
      - Every button in the window is white, in Light or Dark Mode
      - Each line is drawn partly straight and partly wobbly. Which stretches
        wobble is picked at random from the map seed, so the same seed always
        draws the same lines. The wobble changes only the drawing
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

    Floor plans:
      - Building: one floor of a hideout with the stairs taken out, rooms
        and hallways, an exterior entrance and sometimes an exit
      - Village: 6 to 11 buildings. Town: 12 to 29 buildings and a hideout
      - Hideout: 3 or 4 levels, above and below ground. A main stairwell
        links levels 1, 2 and -2, and often opens straight onto a hallway;
        levels 3, 4, -3 and -4 are reached by secondary staircases
      - Dungeon complex: 15 to 99 rooms on an even grid, joined by short
        corridors that each join two rooms and never cross. Every room is
        cut into 2 to 11 inner rooms, about half of them with hallways
      - Every level and dungeon room is saved twice, walls only and with
        the grid, with a 1 square margin and a small header inside it. A
        hideout's overview shows every level over the ground footprint:
        light blue where the ground floor reaches past a level, darker blue
        for the floor next to it, nearer ground

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
    Version: 2.1
    Requires: Python 3.8+ and Pillow 10.1+ (python3 -m pip install pillow)
    Platform: macOS, Windows or Linux (the window uses Tkinter, which comes
              with the standard Python installer)

.EXAMPLE
    python3 DnD-MapBuilder_v2.1.py

    Opens the window.

.EXAMPLE
    python3 DnD-MapBuilder_v2.1.py 123456789012345-987654321098765

    Opens the window showing that area map with those locations.
"""

import math, os, random, re, sys, time
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
TEXTURES = (("forest", 54, 34), ("sand", 16, 16), ("water", 80, 26))
CELL, SMALLEST, EDGE, TEXTURE_COLOR = 5, 400, 2, (90, 90, 90)
FOREST_COLOR, WATER_COLOR = (20, 100, 40), (110, 170, 235)   # dark green trees, light blue waves
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

    def chance(self, odds):
        # True "odds[0] times in odds[1]".
        return self.below(odds[1]) < odds[0]

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


def wobble(p, q, rnd, depth=4, amp=0.22):
    # Midpoint displacement: each half of a stretch is pushed a little to one
    # side, and the pushes get smaller at every level, so the bends are
    # small at all scales. Returns the points from p up to, not including, q.
    if depth == 0:
        return [p]
    dx, dy = q[0] - p[0], q[1] - p[1]
    length = math.hypot(dx, dy) or 1
    off = rnd.uniform(-amp, amp) * length
    mid = ((p[0] + q[0]) / 2 - dy / length * off, (p[1] + q[1]) / 2 + dx / length * off)
    return wobble(p, mid, rnd, depth - 1, amp * 0.55) + wobble(mid, q, rnd, depth - 1, amp * 0.55)


def area_sheet(m, grid=False, focus=None, preview=False):
    # preview=True draws only the map and its red x marks, edge to edge:
    # no frame, square names, seed or code, so the preview shows more land.
    # The saved sheets are drawn with preview=False.
    if preview:
        img = Image.new("RGB", (W, H), WHITE)
        ox, oy = 0, 0
    else:
        img = Image.new("RGB", (W + 2 * SQ, H + 3 * SQ), WHITE)
        ox, oy = SQ, 2 * SQ
    draw = ImageDraw.Draw(img)
    r, f = LINE_WIDTH // 2, FRAME_WIDTH // 2

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
    if FRAME and not preview:
        draw.rectangle((ox - f, oy - f, ox + W + f, oy + H + f), outline=LINE_COLOR, width=FRAME_WIDTH)

    # ── Texture marks, thin: dark green trees, light blue water, grey sand
    for texture, x, y in m.marks:
        x, y = ox + x, oy + y
        if texture == "forest":
            draw.ellipse((x - 5, y - 9, x + 5, y + 1), outline=FOREST_COLOR)
            draw.line((x, y + 1, x, y + 5), fill=FOREST_COLOR)
        elif texture == "water":
            draw.arc((x - 8, y - 3, x, y + 3), 180, 360, fill=WATER_COLOR)
            draw.arc((x, y - 3, x + 8, y + 3), 0, 180, fill=WATER_COLOR)
        elif (x * 7 + y * 13) % 9:
            draw.point((x, y), fill=TEXTURE_COLOR)
        else:
            draw.polygon(((x, y - 4), (x - 4, y + 3), (x + 4, y + 3)), outline=TEXTURE_COLOR)

    # ── Lines: one colour, round at every corner and end ──────────────
    # Each stretch between two nodes is straight or wobbly, chosen from the
    # map seed, so every map draws the same way each time it is shown.
    for k, path in enumerate(m.lines):
        rnd = random.Random("%s-%d" % (m.seed, k))
        nodes = [(ox + x, oy + y) for x, y in path]
        points = []
        for p, q in zip(nodes, nodes[1:]):
            points += wobble(p, q, rnd) if rnd.random() < 0.5 else [p]
        points.append(nodes[-1])
        for x, y in nodes:
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

    if preview:
        return img

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

# ── Kinds and dungeon layout ────────────────────────────────────────
GW, GH = 17, 13                  # the ground (and largest) floor is 17 x 13
                                 # squares
SW, SH = GW + 4, GH + 4          # one dungeon slot: the largest room plus 2
                                 # squares of rock on every side
LABELS = {"building": "Building", "village": "Village", "hideout": "Hideout", "town": "Town",
          "dungeon": "Dungeon complex"}
                                 # each kind and the label on its button
                                 # and headers
GROUPS = ("village", "town")     # kinds made of several maps
STEP = {"N": (0, -1), "S": (0, 1), "W": (-1, 0), "E": (1, 0)}
                                 # one square out through each side
WALL = {"N": "north", "S": "south", "W": "west", "E": "east"}

# ── The grid ────────────────────────────────────────────────────────────
SQUARE = 70                      # pixels per grid square
PLAN_GRID_COLOR = (140, 190, 255) # light blue
GRID_OVER_WALLS = False          # False = walls stay solid black where a grid
                                 # line runs along them. True = the blue line
                                 # is drawn on top, through the middle of walls

# ── Levels ──────────────────────────────────────────────────────────────
LEVEL_COUNTS = (3, 4)            # hideout: equal odds of each
BUILDING_GROUND_CHANCE = (1, 10) # building: 1 in 10 is a ground floor,
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
GROUND_FILL = PLAN_GRID_COLOR    # grid-line blue: ground footprint squares this
                                 # floor does not cover
NEXT_FLOOR_FILL = (80, 130, 225) # a darker blue: footprint of the floor next to
                                 # it, nearer ground, when that is not ground.
                                 # Squares the floor itself covers stay white,
                                 # so only the empty space around it is filled in

# ── Dungeon complex rooms ───────────────────────────────────────────
DUNGEON_INNER_ROOMS_LEAST = 2    # every dungeon room is cut into at least this
                                 # many inner rooms. Bigger rooms get more, up
                                 # to MAX_ROOMS, at 1 per SQUARES_PER_ROOM squares


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
    # A building (one level) or a hideout.
    def __init__(self, seed, stair, levels, kind="hideout"):
        self.kind = kind        # "building" or "hideout"
        self.seed = seed
        self.stair = stair
        self.levels = levels    # ground first, then 2, 3, 4, then -2, -3, -4
        self.parts = []         # a village or town has these; a building or hideout has none
        self.location = None    # the adventure location it is for


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
    dice = dice or Dice(seed)

    # ── Level count, and which side of the ground each one goes ───────────
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


# ── Building ────────────────────────────────────────────────────────────
# A building is one floor of a hideout with the stairs taken out.
# The whole hideout is built first, exactly as the Hideout button
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
    dice = Dice(seed)
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

# repair_level runs on every level as it is built, as a safety net.

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


# ============================================================================
# DUNGEON COMPLEX, VILLAGE AND TOWN
# ============================================================================

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
    for r in rooms:
        r.floor = make_chamber(d, r)
    return m


# Each room of the dungeon complex is built as a one-floor level by the
# same builder as a building or a hideout floor: cut into rooms of 3 x 3 or
# more and hallways 1 square wide, with doorways joining every part,
# sometimes a second way round, and side hallways in bigger blocks.
#
# When the room gets a hallway and one of its doorways lines up with a
# spot where a hallway can run, the first hallway is cut through that
# doorway, so the corridor from outside leads straight into it.
#
# Each doorway to a corridor is an opening in the outer wall with a 1 x 1
# bump out, where the corridor starts.

def make_chamber(d, room):
    rect = (room.x, room.y, room.w, room.h)

    # ── How many inner rooms: fewer in smaller rooms, never fewer than 2 ──
    most = min(MAX_ROOMS, max(DUNGEON_INNER_ROOMS_LEAST, room.w * room.h // SQUARES_PER_ROOM))
    target = d.between(max(DUNGEON_INNER_ROOMS_LEAST, (most + 1) // 2), most)
    want_halls = target >= HALL_MIN_ROOMS

    # ── The first hallway: through a doorway when one lines up ────────────
    split = None
    if want_halls:
        lines = []
        for side, x, y, _, _ in room.doors:
            # A doorway in the north or south wall: a hallway top to bottom.
            axis = 0 if side in "NS" else 1
            line = (x, y)[axis]
            start, length = (room.x, room.w) if axis == 0 else (room.y, room.h)
            if MIN_ROOM <= line - start < length - MIN_ROOM:
                lines.append((axis, line))
        if lines:
            split = d.pick(lines)

    # ── Rooms, hallways, doorways and walls, as on every other floor ──────
    chamber = build_level(d, room.number, rect, [], target, want_halls,
                          split=split, start=room.doors[0][1:3])

    # ── Doorways to the corridors: openings in the outer wall ─────────────
    for side, x, y, to, _ in room.doors:
        kind = "entrance" if to == "IN" else "exit" if to == "OUT" else "doorway"
        chamber.openings.append((kind, x, y, side))
    bump_outs(chamber)
    return chamber


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
    # "Location n" comes first on a floor plan made for an adventure location.
    front = ["Location %d" % hideout.location] if hideout.location else []
    if hideout.kind == "dungeon":
        # One room's sheet. The seed is the seed of the whole complex.
        where = "Room %d of %d" % (level.number, len(hideout.rooms))
        return front + [LABELS[hideout.kind], where, "Seed " + hideout.seed]
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
    return front + [LABELS[hideout.kind], where, "Seed " + hideout.seed]


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
        draw.line([(x, 0), (x, height - 1)], fill=PLAN_GRID_COLOR, width=1)
    for y in range(0, height, SQUARE):
        draw.line([(0, y), (width - 1, y)], fill=PLAN_GRID_COLOR, width=1)


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
            None       = no header.
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
    """All levels on one sheet, grid version, ground at the top left,
    2 floors across and 2 rows. A building has no overview: this gives its
    grid picture instead, which is what the window shows."""
    ground = hideout.levels[0]
    if hideout.kind == "building":
        return render_level(hideout, ground, True, tight_frame(ground), header="margin")
    across = 2
    frame = own_frame(hideout, ground)
    width, height = frame[0] * SQUARE, frame[1] * SQUARE
    sheet = Image.new("RGB", (across * width, 2 * height), WHITE)
    for index, level in enumerate(hideout.levels):
        picture = render_level(hideout, level, True, frame, blue_squares=True)
        sheet.paste(picture, ((index % across) * width, (index // across) * height))
    return sheet


# ============================================================================
# DUNGEON COMPLEX, VILLAGE AND TOWN DRAWING
# ============================================================================

def cell_edges(x, y):
    # The four wall pieces round square (x, y).
    return {"N": ("h", x, y), "S": ("h", x, y + 1), "W": ("v", x, y), "E": ("v", x + 1, y)}


def at_location(m):
    # "Location n    " for a floor plan made for an adventure location.
    return "Location %d    " % m.location if m.location else ""


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
        lines.append("Room %d    %d x %d squares    %d inner rooms%s" % (r.number, r.w, r.h, len(r.floor.rooms),
                     "    with hallways" if HALL in r.floor.cell.values() else ""))
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
        img.paste(render_overview(b), (i % 3 * cw, SQ + i // 3 * ch))
    for h in hideouts:
        pic = render_overview(h)
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
            f = p.levels[0]
            lines.append("Building %-4s Seed %s    %d x %d squares    %d room%s    %s_%s..." % (part[9:11].lstrip("0"), p.seed, f.w, f.h, len(f.rooms), "" if len(f.rooms) == 1 else "s", name, part))
        else:
            levels = ", ".join(str(f.number) for f in p.levels)
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
    if m.kind in GROUPS:
        return group_overview(m)
    return dungeon_overview(m) if m.kind == "dungeon" else render_overview(m)


# ============================================================================
# FLOOR PLAN SAVING
# ============================================================================

def save_part(m, folder, name, front, overview):
    # Writes one map's files, each named <name>_<front><part>.jpg. front is
    # empty for a map saved on its own. Every level and every dungeon room
    # is saved twice, walls only and with the grid, cropped to a 1 square
    # margin with the small header in it.
    jpg = lambda img, part: img.save(os.path.join(folder, "%s_%s%s.jpg" % (name, front, part)), quality=JPG_QUALITY, subsampling=0)
    if m.kind == "dungeon":
        for r in m.rooms:
            frame = tight_frame(r.floor)
            for grid, word in ((False, "walls"), (True, "grid")):
                jpg(render_level(m, r.floor, grid, frame, header="margin"), "room_%02d_%s" % (r.number, word))
        jpg(overview or dungeon_overview(m), "overview")
        with open(os.path.join(folder, "%s_%sroom_key.txt" % (name, front)), "w") as out:
            out.write(room_key(m))
        return
    for level in m.levels:
        part = "" if m.kind == "building" else "level_%d_" % level.number
        frame = tight_frame(level)
        for grid, word in ((False, "walls"), (True, "grid")):
            jpg(render_level(m, level, grid, frame, header="margin"), part + word)
    if m.kind == "hideout":
        jpg(overview or render_overview(m), "overview")


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
             "rows 1 to 13 run top to bottom."]
    if len(m.xs) > 1:
        lines.append("Locations 1 and %d are the two farthest apart." % len(m.xs))
    lines += ["",
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
    win.title("DnD MapBuilder v2.1")
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
    bar = tk.Frame(win, pady=3)
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
    # The label and the seed box share one row, with the box to the right of the words.
    seed_row = tk.Frame(bar)
    seed_row.pack(pady=(6, 0))
    box_label = tk.StringVar(value="Seed or code (leave empty for something new):")
    tk.Label(seed_row, textvariable=box_label).pack(side="left", padx=(0, 8))
    # A white outline that stays on whether or not the box has focus.
    seed_box = tk.Entry(seed_row, width=36, justify="center", highlightthickness=1,
                        highlightbackground="white", highlightcolor="white", relief="flat", bd=0)
    seed_box.pack(side="left")
    status = tk.StringVar(value="Click \"Area map\" to make a new map.")
    bold = tkfont.nametofont("TkDefaultFont").copy()
    bold.configure(weight="bold")
    # takefocus=0 and no highlight: the status line never takes focus, so
    # selecting its text does not draw a border round it.
    tk.Entry(bar, textvariable=status, state="readonly", relief="flat", justify="center", font=bold,
             readonlybackground=win.cget("bg"), width=130, takefocus=0, highlightthickness=0,
             borderwidth=0).pack(pady=2)

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
        picture(area_sheet(m, preview=True))
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
        picture(area_sheet(m, focus=n + 1, preview=True))
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
        picture(area_sheet(m, preview=True))
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
