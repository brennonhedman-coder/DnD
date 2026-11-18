#!/usr/bin/env python3
# ============================================================================
# DnD-DiceAdventure_v2.1.py
# ============================================================================

"""
.SYNOPSIS
    Tkinter dice game: cross a DnD MapBuilder area map from one adventure
    location to the next, rolling black or white dice to travel and to
    fight what you meet on the road.

.DESCRIPTION
    The game, step by step:
      - "Play", then choose your land just like DnD MapBuilder: click "Area
        map" until you like the map, then "Use this map"
      - Click "Adventure locations" to scatter 29 red x's on the map, again
        until you like them, then "Use these locations". Never in the water,
        and every one can be reached without crossing water. START and
        FINISH are the two farthest apart in a straight line
      - Flip a coin or pick black or white dice. Your enemies roll the other
        colour
      - Roll 3 dice: the total (3 to 18) is how many stops your route makes,
        START and FINISH included. The route runs from START to FINISH round
        the water, keeping as close to the shortest way as it can while it
        strays to pick up exactly that many red x's. Its stops are numbered
        in order; the other red x's turn grey
      - Roll 1 die for your travel speed. 1 = a slow walk with frequent,
        weak encounters; 6 = a reckless gallop with rare, deadly ones
      - "Get ready for your adventure", then "Start". You begin at location
        1 with 12 health and travel to each location in turn
      - Each leg is as long as its route on the map, round any water: one
        map square is 6 miles. Each travel roll is 2 dice, and you go as
        many miles as you roll (the last roll of a leg stops at the location)
      - Each leg rolls 1 to 4 encounters for every 30 miles (or part of
        30 miles), spread along the way, so long legs are more dangerous.
        Slow travel meets more of them
      - Each encounter is a hazard or an enemy. Fast travel meets fewer
        hazards: (6 - your speed) in 6 are hazards, the rest enemies
      - You see it coming: roll 1 die, 4 or more and you avoid it
        altogether. The die and its result stay on the table for a moment
        before the game moves on
      - If not, roll 2 dice. A hazard (a well, a pit of spikes, a twig to
        trip over, ice to slip on and more) needs more than 7, or you lose
        2 health. An enemy (Ravens, a Fox, Raccoons, an Old woman, an Old
        man, Wild dogs, Wolves, Rabid monkeys, a Cougar, a Bear or a Lion)
        needs more than twice your travel speed, at least 7, or you lose 4
        health. Against an enemy, double six always wins
      - You start with 12 health
      - At travel speed 6 you may roll 1 die each for a companion fox and
        companion ravens: 5 or 6 joins you. Each adds 2 to every fight roll,
        but the fox lets you down 1 attack in 4 and the ravens 1 in 8, and
        the story says when. With both, every attack gets +4, no fails
      - Reach the last location to win. Run out of health and you lose

    The dice are real random rolls. Each throw tumbles in from the left and
    settles on the green table.

    Lines that start with "#" are notes for people. Python ignores them.

.NOTES
    Author : Brennon Hedman
    Version: 2.1
    Requires: Python 3.8+ and Pillow 10.1+ (python3 -m pip install pillow)
    Platform: macOS, Windows or Linux (the window uses Tkinter, which comes
              with the standard Python installer)

.EXAMPLE
    python3 DnD-DiceAdventure_v2.1.py

    Opens the game window.
"""

import heapq, itertools, math, random, re, time
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
TEXTURES = (("forest", 54, 34), ("sand", 16, 16), ("water", 80, 26), ("red sand", 16, 16))
                                 # red sand only goes on a 4th big area, if the map has one free
CELL, SMALLEST, EDGE, TEXTURE_COLOR = 5, 400, 2, (90, 90, 90)
FOREST_COLOR, WATER_COLOR, RED_SAND_COLOR = (20, 100, 40), (110, 170, 235), (185, 95, 35)
                                 # dark green trees, light blue waves, brown-orange red sand
CW, CH = W // CELL, H // CELL
X_GAP2, X_SIZE, COLUMNS = 40 * 40, 7, "ABCDEFGHIJKLMNOPQ"
X_GREY = (165, 165, 165)
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

def place_xs(d, grid, water, box, count):
    x0, y0, x1, y1 = INSIDE
    span = range(-EDGE, EDGE + 1)

    def dry(x, y):
        cx, cy = x // CELL, y // CELL
        if water is None or not (box[0] <= cx <= box[2] and box[1] <= cy <= box[3]):
            return True
        return all(grid[(cy + j) * CW + cx + i] != water for j in span for i in span)

    free = [(x, y) for y in range(y0, y1 + 1, 10) for x in range(x0, x1 + 1, 10) if dry(x, y)]
    xs = []
    for _ in range(count):
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

    # ── Texture marks, thin: dark green trees, light blue water, grey sand,
    # and brown-orange red sand
    for texture, x, y in m.marks:
        x, y = ox + x, oy + y
        if texture == "forest":
            draw.ellipse((x - 5, y - 9, x + 5, y + 1), outline=FOREST_COLOR)
            draw.line((x, y + 1, x, y + 5), fill=FOREST_COLOR)
        elif texture == "water":
            draw.arc((x - 8, y - 3, x, y + 3), 180, 360, fill=WATER_COLOR)
            draw.arc((x, y - 3, x + 8, y + 3), 0, 180, fill=WATER_COLOR)
        else:
            color = RED_SAND_COLOR if texture == "red sand" else TEXTURE_COLOR
            if (x * 7 + y * 13) % 9:
                draw.point((x, y), fill=color)
            else:
                draw.polygon(((x, y - 4), (x - 4, y + 3), (x + 4, y + 3)), outline=color)

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
# GAME SETTINGS
# ============================================================================

START_HEALTH = 12                # health at the start of an adventure
MILES_PER_SQUARE = 6            # one 70 pixel map square is 6 miles: each leg is as
                                 # long as its route on the map, round any water
LOCATIONS = 29                   # red x's on the map, as many as DnD MapBuilder's most
ENCOUNTER_MILES = 30            # a leg rolls 1 to 4 encounters for every 30 miles
                                 # or part of 30 miles
FELT = "#1f5c36"                 # the green table the dice land on
DIE_SIZE = 70                    # pixels across one die
ROLL_FRAMES, FRAME_MS = 16, 45   # how long a throw tumbles: frames and pause
RESULT_PAUSE_MS = 1800           # how long the avoid die stays on the table, with
                                 # its result, before the game moves on

# Each creature: name, and what you see (one is picked).
CREATURES = [
    ("Ravens", ["A flock of ravens dives out of the trees at you."]),
    ("Fox", ["A fox darts out of the brush and snaps at your heels."]),
    ("Raccoons", ["A pack of raccoons swarms out of a hollow log."]),
    ("Old woman", ["An old woman steps into the road and mutters a curse."]),
    ("Old man", ["An old man with a crooked staff bars the way.",
                 "An old man chases you around, screaming.",
                 "An old man runs after you, crying."]),
    ("Wild dogs", ["A pack of wild dogs comes snarling down the road."]),
    ("Wolves", ["A pack of wolves circles you, teeth bared."]),
    ("Rabid monkeys", ["A rabid monkey lab test family escapes its cages and comes for you."]),
    ("Cougar", ["A cougar drops from a rock ledge in front of you."]),
    ("Bear", ["A bear rears up on its hind legs in front of you."]),
    ("Lion", ["A lion steps out of the tall grass and roars."]),
]

# Which creature you meet, by travel speed: one weight per creature above,
# in the same order. Slow travel meets weak creatures, fast travel the
# strong ones.
CREATURE_ODDS = {
    1: (4, 3, 3, 3, 3, 1, 1, 1, 0, 0, 0),
    2: (3, 3, 3, 3, 3, 2, 1, 1, 1, 0, 0),
    3: (2, 2, 2, 2, 2, 2, 2, 2, 1, 1, 0),
    4: (1, 1, 2, 2, 2, 3, 2, 2, 2, 2, 1),
    5: (1, 1, 1, 1, 1, 3, 2, 2, 3, 3, 2),
    6: (1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 3),
}

# Each hazard: what you see ahead, and what happens if it gets you.
HAZARDS = [
    ("a well", "You fall into the well."),
    ("a pit of spikes", "You fall into the pit of spikes."),
    ("an open mine shaft", "You fall into the mine shaft."),
    ("a sink hole", "You fall into the sink hole."),
    ("a pot hole", "You fall into the pot hole."),
    ("a mud hole", "You fall into the mud hole."),
    ("a fast river", "You fall into the river."),
    ("a crevice", "You fall into the crevice."),
    ("the ocean of sadness", "You fall into the ocean of sadness."),
    ("a twig", "You trip over the twig."),
    ("a tree branch on the ground", "You trip over the tree branch."),
    ("a dead deer", "You trip over the dead deer."),
    ("an old shoe", "You trip over the old shoe."),
    ("a rock", "You trip over the rock."),
    ("a squirrel", "You trip over the squirrel."),
    ("a sleeping hippy", "You trip over the sleeping hippy."),
    ("a low tree branch", "You hit your head on the tree branch."),
    ("spilled beans", "You slip on the beans."),
    ("wet moss", "You slip on the wet moss."),
    ("ice", "You slip on the ice."),
]
AVOID_AT = 4                     # first, 1 die: this or more and you avoid the
                                 # hazard or enemy altogether
HAZARD_NUMBER = 7                # not avoided: 2 dice must beat this to get past a hazard
HAZARD_DAMAGE = 2                # health lost when a hazard gets you
ENEMY_DAMAGE = 4                 # health lost when an enemy gets you
                                 # (an enemy's number is twice your speed, at least 7)
ENEMY_LEAST = 7                  # an enemy's number is twice your travel speed,
                                 # but never less than this

# Companions, only at travel speed 6: roll 1 die each, 5 or 6 joins you.
# Each adds 2 to every fight roll, but the fox lets you down 1 attack in 4
# and the ravens 1 in 8. With both, 4 is added to every attack, no fails.
COMPANION_JOINS = 5              # this or more on 1 die
COMPANION_BONUS = 2
COMPANION_FAILS = {"fox": 4, "ravens": 8}   # 1 attack in this many

# How many encounters on the way to each location, by travel speed (weights
# for 1, 2, 3 and 4 encounters). Slow travel meets creatures often, fast
# travel rarely.
ENCOUNTER_ODDS = {
    1: (1, 2, 3, 4),
    2: (2, 3, 3, 2),
    3: (3, 3, 2, 2),
    4: (4, 3, 2, 1),
    5: (6, 3, 1, 0),
    6: (8, 2, 0, 0),
}

SPEED_WORDS = {
    1: "A slow, careful walk. You meet trouble often, but most of it is hazards (2 damage).",
    2: "An easy pace. Trouble often, mostly hazards.",
    3: "A steady march. Hazards and enemies, half and half.",
    4: "A brisk pace. Less trouble, but more of it is enemies (4 damage), and they are tougher.",
    5: "A fast ride. Trouble is rare, nearly all of it enemies.",
    6: "A reckless gallop. Trouble is rare, but every bit of it is a tough enemy.",
}

PIPS = {1: [(0, 0)], 2: [(-1, -1), (1, 1)], 3: [(-1, -1), (0, 0), (1, 1)],
        4: [(-1, -1), (1, -1), (-1, 1), (1, 1)], 5: [(-1, -1), (1, -1), (0, 0), (-1, 1), (1, 1)],
        6: [(-1, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (1, 1)]}

RNG = random.SystemRandom()      # real randomness for the dice; the map has its own seeds


# ============================================================================
# GAME RULES
# ============================================================================

# Kept apart from the window, so the rules can be tried on their own.

def roll(count):
    return [RNG.randint(1, 6) for _ in range(count)]


def weighted(weights):
    # A position in the list, picked with these weights.
    pick = RNG.randrange(sum(weights))
    for i, w in enumerate(weights):
        pick -= w
        if pick < 0:
            return i


def encounters_for(speed):
    return 1 + weighted(ENCOUNTER_ODDS[speed])


def encounter_for(speed):
    # Fast travel meets fewer hazards and more enemies: (6 - speed) in 6
    # encounters are hazards, the rest enemies. Returns (kind, name, what
    # you see, number to beat, health lost, what happens).
    if RNG.randrange(6) >= speed:
        thing, fall = RNG.choice(HAZARDS)
        return ("hazard", thing, "Watch out: %s!" % thing, HAZARD_NUMBER, HAZARD_DAMAGE, fall)
    name, sights = CREATURES[weighted(CREATURE_ODDS[speed])]
    return ("creature", name, RNG.choice(sights), enemy_number(speed), ENEMY_DAMAGE, None)


def enemy_number(speed):
    return max(ENEMY_LEAST, 2 * speed)


def enemy_faces(speed):
    # The enemy's two dice: one shows your travel speed, the other makes up
    # the enemy's number.
    return [speed, enemy_number(speed) - speed]


def companion_help(fox, ravens):
    # (points added, the story of it) for one attack.
    if fox and ravens:
        return 2 * COMPANION_BONUS, "Your fox and your ravens fight beside you (+%d)." % (2 * COMPANION_BONUS)
    if fox:
        if RNG.randrange(COMPANION_FAILS["fox"]) == 0:
            return 0, "Your fox hangs back this time and does not help."
        return COMPANION_BONUS, "Your fox bites at the enemy (+%d)." % COMPANION_BONUS
    if ravens:
        if RNG.randrange(COMPANION_FAILS["ravens"]) == 0:
            return 0, "Your ravens circle overhead but do not dive in."
        return COMPANION_BONUS, "Your ravens dive at the enemy (+%d)." % COMPANION_BONUS
    return 0, ""


def beats(total, need, dice, creature):
    # Beat the number to avoid harm. Against a creature, double six always
    # wins, so even an enemy number of 12 can be beaten.
    return total > need or (creature and dice == [6, 6])


def route_miles(points):
    # How far a route on the map is, in miles (never less than 1).
    pixels = sum(math.hypot(q[0] - p[0], q[1] - p[1]) for p, q in zip(points, points[1:]))
    return max(1, round(pixels / SQ * MILES_PER_SQUARE))


def encounters_on_leg(speed, miles):
    # 1 to 4 encounters (by travel speed) for every ENCOUNTER_MILES started.
    return sum(encounters_for(speed) for _ in range(-(-miles // ENCOUNTER_MILES)))


def stops_on_leg(miles, count):
    # Where on the way the encounters happen: spread evenly along the leg.
    return [round(miles * k / (count + 1)) for k in range(1, count + 1)]


def new_seed():
    return str(10 ** 14 + RNG.randrange(9 * 10 ** 14))


def new_area_map():
    # A new area map, the same way DnD MapBuilder's "Area map" button makes one.
    while True:
        m = make_exterior(new_seed())
        if m is not None:
            return m


def place_locations(m, count):
    # Exactly "count" locations marked with a red x, the same way DnD
    # MapBuilder's "Adventure locations" button places them, from a new
    # locations seed each time. Never in the water, and every location can
    # be reached from the start without crossing water. Location 1 (the
    # start) and the last location (the finish) are the two farthest apart
    # in a straight line.
    while True:
        m.loc_seed = new_seed()
        m.xs = place_xs(Dice(m.loc_seed), m.grid, m.water, m.box, count)
        if len(m.xs) != count:
            continue
        reach = dry_land(m, m.xs[0])
        if all(cell_of(p) in reach for p in m.xs):
            return


def cell_of(p):
    # The map cell (CELL x CELL pixels) a pixel point is in, as one number.
    return min(p[1] // CELL, CH - 1) * CW + min(p[0] // CELL, CW - 1)


def is_water(m, k):
    return m.water is not None and m.grid[k] == m.water


def dry_land(m, start):
    # Every map cell you can walk to from "start" without stepping in water.
    first = cell_of(start)
    seen, todo = {first}, [first]
    while todo:
        k = todo.pop()
        x, y = k % CW, k // CW
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            n = ny * CW + nx
            if 0 <= nx < CW and 0 <= ny < CH and n not in seen and not is_water(m, n):
                seen.add(n)
                todo.append(n)
    return seen


def land_route(m, a, b):
    # The shortest way from a to b that never enters the water, as pixel
    # points: straight across land, round the shore where water is in the way.
    if dry_line(m, a, b):
        return [a, b]                    # nothing in the way: straight there
    start, goal = cell_of(a), cell_of(b)
    gx, gy = goal % CW, goal // CW
    guess = lambda k: max(abs(k % CW - gx), abs(k // CW - gy)) + 0.414 * min(abs(k % CW - gx), abs(k // CW - gy))
    best, came, todo = {start: 0.0}, {}, [(guess(start), start)]
    while todo:
        _, k = heapq.heappop(todo)
        if k == goal:
            break
        x, y = k % CW, k // CW
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            nx, ny = x + dx, y + dy
            n = ny * CW + nx
            if not (0 <= nx < CW and 0 <= ny < CH) or is_water(m, n):
                continue
            if dx and dy and (is_water(m, y * CW + nx) or is_water(m, ny * CW + x)):
                continue                     # no cutting a corner of the water
            cost = best[k] + (1.414 if dx and dy else 1.0)
            if cost < best.get(n, 1e18):
                best[n], came[n] = cost, k
                heapq.heappush(todo, (cost + guess(n), n))
    cells = [goal]
    while cells[-1] != start:
        cells.append(came[cells[-1]])
    cells.reverse()
    points = [a] + [((k % CW) * CELL + CELL // 2, (k // CW) * CELL + CELL // 2) for k in cells[1:-1]] + [b]

    # ── Straighten it: from each point, go straight to the farthest point
    # further on that can be reached without touching water ──────────────
    kept, i = [points[0]], 0
    while i < len(points) - 1:
        j = i + 1
        while j + 1 < len(points) and dry_line(m, points[i], points[j + 1]):
            j += 1
        kept.append(points[j])
        i = j
    return kept


def dry_line(m, p, q):
    # True if the straight line from p to q never touches water.
    steps = max(1, int(math.hypot(q[0] - p[0], q[1] - p[1]) // 2))
    return not any(is_water(m, cell_of((int(p[0] + (q[0] - p[0]) * i / steps), int(p[1] + (q[1] - p[1]) * i / steps))))
                   for i in range(steps + 1))


def route_length(points):
    return sum(math.hypot(q[0] - p[0], q[1] - p[1]) for p, q in zip(points, points[1:]))


def plan_route(m, count):
    # A trip from START (location 1) to FINISH (the last location) that
    # stops at exactly "count" red x's, START and FINISH included. It keeps
    # as close to the shortest way as it can, straying only as far as it
    # must to pick up enough stops. The stops are renumbered 1 to count in
    # the order they are visited; the other red x's become spares. Returns
    # the route of each leg, round the water.
    xs, n = m.xs, len(m.xs)
    far = land_distances(m, xs)
    trip = [0] + pick_stops(far, n, count) + [n - 1]
    m.spare = [xs[i] for i in range(n) if i not in trip]
    m.xs = [xs[i] for i in trip]
    return [land_route(m, a, b) for a, b in zip(m.xs, m.xs[1:])]


def land_distances(m, xs):
    # How far apart every two red x's are over land, in pixels. Straight
    # where nothing is in the way. Where water is, the way round is measured
    # on a coarser grid (2 x 2 map cells), which is quick and close enough
    # to choose stops by; the legs actually used are then found exactly.
    n, far, wet = len(xs), {}, set()
    for i in range(n):
        for j in range(i + 1, n):
            if dry_line(m, xs[i], xs[j]):
                far[i, j] = far[j, i] = math.hypot(xs[i][0] - xs[j][0], xs[i][1] - xs[j][1])
            else:
                wet.update((i, j))
    if not wet:
        return far
    cw, ch, big = (CW + 1) // 2, (CH + 1) // 2, 2 * CELL
    water = [any(is_water(m, min(2 * y + b, CH - 1) * CW + min(2 * x + a, CW - 1)) for a in (0, 1) for b in (0, 1))
             for y in range(ch) for x in range(cw)]
    spot = {i: min(xs[i][1] // big, ch - 1) * cw + min(xs[i][0] // big, cw - 1) for i in range(n)}
    for i in sorted(wet):
        wanted = {j for j in range(n) if j != i and (i, j) not in far}
        if not wanted:
            continue
        best, todo, found = {spot[i]: 0.0}, [(0.0, spot[i])], {}
        targets = {spot[j]: j for j in wanted}
        while todo and len(found) < len(targets):
            cost, k = heapq.heappop(todo)
            if cost > best.get(k, 1e18):
                continue
            if k in targets:
                found[k] = cost
            x, y = k % cw, k // cw
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                nx, ny = x + dx, y + dy
                q = ny * cw + nx
                if 0 <= nx < cw and 0 <= ny < ch and not water[q]:
                    c = cost + (1.414 if dx and dy else 1.0)
                    if c < best.get(q, 1e18):
                        best[q] = c
                        heapq.heappush(todo, (c, q))
        for j in wanted:
            d = found.get(spot[j])
            far[i, j] = far[j, i] = d * big if d is not None else route_length(land_route(m, xs[i], xs[j]))
    return far


def pick_stops(far, n, count):
    # The stops between START (0) and FINISH (n - 1).
    # ── Up to 3 stops between: try every choice and order, keep the best ─
    if count - 2 <= 3:
        return list(min(itertools.permutations(range(1, n - 1), count - 2),
                        key=lambda t: sum(far[a, b] for a, b in zip((0,) + t, t + (n - 1,)))))

    # ── More: add stops one at a time, each where it lengthens the trip least
    trip, spare = [0, n - 1], set(range(1, n - 1))
    while len(trip) < count:
        _, c, i = min((far[trip[i], c] + far[c, trip[i + 1]] - far[trip[i], trip[i + 1]], c, i)
                      for c in sorted(spare) for i in range(len(trip) - 1))
        trip.insert(i + 1, c)
        spare.discard(c)

    # ── Then keep trying small changes while any makes it shorter ────────
    # Reverse a stretch, move one stop, or swap a stop for a spare red x.
    length = lambda t: sum(far[a, b] for a, b in zip(t, t[1:]))
    best, better = length(trip), True
    while better:
        better = False
        tries = []
        for i in range(1, len(trip) - 1):
            for j in range(i + 1, len(trip) - 1):
                tries.append(trip[:i] + trip[i:j + 1][::-1] + trip[j + 1:])
            rest = trip[:i] + trip[i + 1:]
            tries += [rest[:k] + [trip[i]] + rest[k:] for k in range(1, len(rest))]
            tries += [trip[:i] + [c] + trip[i + 1:] for c in sorted(spare)]
        for t in tries:
            if length(t) < best - 1e-9:
                spare = set(range(1, n - 1)) - set(t)
                trip, best, better = t, length(t), True
                break
    return trip[1:-1]


def point_along(points, part):
    # The point "part" of the way along a line through these points (0 to 1).
    lengths = [math.hypot(q[0] - p[0], q[1] - p[1]) for p, q in zip(points, points[1:])]
    left = sum(lengths) * min(1, max(0, part))
    for (p, q), d in zip(zip(points, points[1:]), lengths):
        if left <= d and d:
            return p[0] + (q[0] - p[0]) * left / d, p[1] + (q[1] - p[1]) * left / d
        left -= d
    return points[-1]


# ============================================================================
# DICE AND COIN DRAWING
# ============================================================================

def die_colors(color):
    # (body, outline, pips) for a black or a white die.
    return ("#111111", "#777777", "#ffffff") if color == "black" else ("#ffffff", "#000000", "#000000")


def draw_die(canvas, cx, cy, value, color, angle=0.0, size=DIE_SIZE):
    body, edge, pip = die_colors(color)
    c, s = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    turn = lambda x, y: (cx + x * c - y * s, cy + x * s + y * c)
    h = size / 2
    corners = []
    for x, y in ((-h, -h), (h, -h), (h, h), (-h, h)):
        corners += turn(x, y)
    canvas.create_polygon(corners, fill=body, outline=edge, width=3, joinstyle="round")
    r, step = size * 0.09, size * 0.27
    for px, py in PIPS[value]:
        x, y = turn(px * step, py * step)
        canvas.create_oval(x - r, y - r, x + r, y + r, fill=pip, outline=pip)


def draw_coin(canvas, cx, cy, squash, color, radius=55):
    body, edge, _ = die_colors(color)
    w = max(2, radius * abs(squash))
    canvas.create_oval(cx - w, cy - radius, cx + w, cy + radius, fill=body, outline=edge, width=3)


# ============================================================================
# WINDOW
# ============================================================================

def run_game():
    import tkinter as tk
    from tkinter import font as tkfont
    from PIL import ImageTk

    win = tk.Tk()
    win.title("DnD Dice Adventure v2.1")
    win.geometry("%dx%d+0+0" % (win.winfo_screenwidth(), win.winfo_screenheight()))
    g = {"busy": False, "pic": None, "size": None}

    def white(parent, text, action):
        # A white button: a label, because a Mac draws its own buttons dark
        # grey in Dark Mode but a label keeps the colours it is given.
        button = tk.Label(parent, text=text, bg="white", fg="black", padx=16, pady=5)

        def release(event):
            button.config(bg="white", fg="black")
            if not g["busy"]:
                action()

        button.bind("<ButtonPress-1>", lambda event: button.config(bg="black", fg="white"))
        button.bind("<ButtonRelease-1>", release)
        return button

    # ── Layout: message, dice table, buttons, then the map ────────────
    big = tkfont.nametofont("TkDefaultFont").copy()
    big.configure(size=18, weight="bold")
    title = tk.StringVar(value="Dice Adventure")
    message = tk.StringVar()
    tk.Label(win, textvariable=title, font=big).pack(pady=(10, 2))
    tk.Label(win, textvariable=message, wraplength=1000, justify="center").pack(pady=(0, 6))
    table = tk.Canvas(win, width=1000, height=190, bg=FELT, highlightthickness=0)
    table.pack()
    buttons = tk.Frame(win)
    buttons.pack(pady=8)
    view = tk.Label(win, bg="black")
    view.pack(side="bottom", fill="both", expand=True)

    def offer(*choices):
        for child in buttons.winfo_children():
            child.destroy()
        for text, action in choices:
            white(buttons, text, action).pack(side="left", padx=6)

    def say(head, text=""):
        title.set(head)
        message.set(text)

    # ── Health bar, top right of the table ────────────────────────────
    def health_bar():
        table.delete("health")
        if "health" not in g:
            return
        x0, y0 = 760, 18
        table.create_text(x0, y0, text="Health %d / %d" % (g["health"], START_HEALTH), anchor="nw",
                          fill="white", font=("TkDefaultFont", 14, "bold"), tags="health")
        part = max(0, g["health"]) / START_HEALTH
        table.create_rectangle(x0, y0 + 26, x0 + 220, y0 + 42, outline="white", tags="health")
        table.create_rectangle(x0, y0 + 26, x0 + 220 * part, y0 + 42, outline="",
                               fill="#3fbf5f" if part > 0.5 else "#e0b030" if part > 0.25 else "#d03030", tags="health")
        friends = [n for n in ("fox", "ravens") if g.get(n)]
        if friends:
            table.create_text(x0, y0 + 52, text="Companions: " + " and ".join(friends), anchor="nw",
                              fill="white", font=("TkDefaultFont", 13), tags="health")

    def clear_table():
        table.delete("all")
        health_bar()

    # ── Throwing dice: they tumble in from the left and settle ────────
    def throw(count, color, done, extra=None):
        g["busy"] = True
        final = roll(count)
        spots = [180 + i * (DIE_SIZE + 30) for i in range(count)]

        def frame(n):
            clear_table()
            if extra:
                extra()
            left = n / ROLL_FRAMES
            for i, x in enumerate(spots):
                if n < ROLL_FRAMES:
                    sx = x - 160 * (1 - left) ** 2
                    sy = 95 - abs(math.sin(left * math.pi * 3)) * 45 * (1 - left)
                    draw_die(table, sx, sy, RNG.randint(1, 6), color, RNG.uniform(-40, 40))
                else:
                    draw_die(table, x, 95, final[i], color, RNG.uniform(-6, 6))
            if n < ROLL_FRAMES:
                win.after(FRAME_MS, frame, n + 1)
            else:
                table.create_text(spots[-1] + DIE_SIZE, 95, text="= %d" % sum(final), anchor="w",
                                  fill="white", font=("TkDefaultFont", 26, "bold"))
                g["busy"] = False
                done(final)

        frame(0)

    def enemy_dice():
        # The enemy's two dice, in the other colour: one shows your speed.
        s = g["speed"]
        table.create_text(560, 20, text="Enemy", anchor="n", fill="white", font=("TkDefaultFont", 13, "bold"))
        for i, face in enumerate(enemy_faces(s)):
            draw_die(table, 520 + i * 80, 95, face, g["enemy"], 0, 56)
        table.create_text(560, 150, text="needs more than %d" % enemy_number(s), anchor="n",
                          fill="white", font=("TkDefaultFont", 13))

    def hazard_number():
        table.create_text(560, 60, text="Hazard", anchor="n", fill="white", font=("TkDefaultFont", 13, "bold"))
        table.create_text(560, 95, text="needs more than %d" % g["foe"][3], anchor="n",
                          fill="white", font=("TkDefaultFont", 16, "bold"))

    def foe_side():
        enemy_dice() if g["foe"][0] == "creature" else hazard_number()

    # ── The map, with the traveller ───────────────────────────────────
    def show_map():
        m, at = g["map"], g.get("at", 0)
        nxt = at + 1 if at + 1 < len(m.xs) else None
        focus = None if "at" not in g else (nxt + 1) if nxt is not None else len(m.xs)
        img = area_sheet(m, focus=focus, preview=True)
        draw = ImageDraw.Draw(img)

        for x, y in getattr(m, "spare", []):
            draw.line((x - X_SIZE, y - X_SIZE, x + X_SIZE, y + X_SIZE), fill=X_GREY, width=2)
            draw.line((x - X_SIZE, y + X_SIZE, x + X_SIZE, y - X_SIZE), fill=X_GREY, width=2)

        def dashed(path, color, width):
            for p, q in zip(path, path[1:]):
                dashes = max(1, int(math.hypot(q[0] - p[0], q[1] - p[1]) // 12))
                for k in range(0, dashes, 2):
                    draw.line((p[0] + (q[0] - p[0]) * k / dashes, p[1] + (q[1] - p[1]) * k / dashes,
                               p[0] + (q[0] - p[0]) * (k + 1) / dashes, p[1] + (q[1] - p[1]) * (k + 1) / dashes),
                              fill=color, width=width)

        # The whole route, start to finish: light while travelling, dark
        # while you are choosing it.
        for path in g.get("routes", []):
            dashed(path, (60, 60, 60) if "at" not in g else (150, 150, 150), 3 if "at" not in g else 2)
        if m.xs:
            # Start and Finish: the two locations farthest apart in a straight line.
            label = ImageFont.load_default(18)
            for (px, py), word in ((m.xs[0], "START"), (m.xs[-1], "FINISH")):
                draw.text((px, py + 12), word, fill=(0, 0, 0), font=label, anchor="mt")
        if "leg" in g and nxt is not None:
            # The leg you are on now, darker.
            path = g["path"]
            dashed(path, (40, 40, 40), 4)
            x, y = point_along(path, g["covered"] / g["leg"])
        elif "at" in g:
            x, y = m.xs[at]
        else:
            x = None
        if x is not None:
            body, edge, _ = die_colors(g["color"])
            draw.ellipse((x - 13, y - 13, x + 13, y + 13), fill=body, outline=edge if g["color"] == "white" else "#ffffff", width=3)
        g["pic"], g["size"] = img, None
        win.update_idletasks()
        fit()

    def fit(event=None):
        size = (max(200, view.winfo_width() - 10), max(200, view.winfo_height() - 10))
        if g["pic"] is None or size == g["size"]:
            return
        g["size"], pic = size, g["pic"]
        scale = min(size[0] / pic.width, size[1] / pic.height, 1)
        g["photo"] = ImageTk.PhotoImage(pic.resize((max(1, round(pic.width * scale)), max(1, round(pic.height * scale))), Image.BOX))
        view.config(image=g["photo"])

    view.bind("<Configure>", fit)

    # ── 1. Play ───────────────────────────────────────────────────────
    def title_screen():
        for key in ("health", "map", "at", "leg", "speed", "color", "fox", "ravens", "count", "routes", "path"):
            g.pop(key, None)
        g["pic"] = None
        view.config(image="")
        clear_table()
        say("Dice Adventure", "Roll the dice to cross the land, face what waits on the road, and reach every location alive.")
        offer(("Play", pick_map))

    # ── 2. The area map, just like DnD MapBuilder ─────────────────────
    def pick_map():
        clear_table()
        say("Choose your land", "Click \"Area map\" for a new map. Click it again until you like the land.")
        offer(("Area map", new_map))

    def new_map():
        say("Drawing the land ...")
        win.update()
        started = time.perf_counter()
        g["map"] = new_area_map()
        show_map()
        say("Choose your land", "Area map    Seed %s    Made in %.2f seconds. Click \"Area map\" again for another, or use this one."
            % (g["map"].seed, time.perf_counter() - started))
        offer(("Area map", new_map), ("Use this map", locations_screen))

    # ── 2. 29 red x's, as many times as you like ──────────────────────
    def locations_screen():
        say("Adventure locations", "Click \"Adventure locations\" to scatter %d red x's on your map. Click it again until you like them." % LOCATIONS)
        offer(("Adventure locations", locate))

    def locate():
        m = g["map"]
        m.spare = []
        g.pop("routes", None)
        place_locations(m, LOCATIONS)
        show_map()
        say("Adventure locations",
            "%d red x's. START and FINISH are the two farthest apart. Click \"Adventure locations\" again to scatter them anew, or use these."
            % LOCATIONS)
        offer(("Adventure locations", locate), ("Use these locations", choose_dice))

    # ── 2. Black or white dice ────────────────────────────────────────
    def choose_dice():
        clear_table()
        draw_die(table, 400, 95, 5, "black")
        draw_die(table, 600, 95, 5, "white")
        say("Choose your dice", "Flip a coin, or pick a colour. Your enemies roll the other colour.")
        offer(("Flip a coin", flip_coin), ("Black dice", lambda: dice_chosen("black")), ("White dice", lambda: dice_chosen("white")))

    def flip_coin():
        g["busy"] = True
        result = RNG.choice(("black", "white"))
        turns = 18 + (1 if result == "white" else 0)

        def frame(n):
            clear_table()
            t = n / 3.0
            side = "black" if int(t / math.pi * 2 + 0.5) % 2 == 0 else "white"
            draw_coin(table, 500, 95, math.cos(t), side)
            if n < turns * 2:
                win.after(35, frame, n + 1)
            else:
                clear_table()
                draw_coin(table, 500, 95, 1, result)
                g["busy"] = False
                dice_chosen(result, flipped=True)

        frame(0)

    def dice_chosen(color, flipped=False):
        g["color"], g["enemy"] = color, "white" if color == "black" else "black"
        if not flipped:
            clear_table()
            draw_die(table, 500, 95, 6, color)
        say("You play the %s dice" % color, "%sYour enemies roll the %s dice." % ("The coin landed %s. " % color if flipped else "", g["enemy"]))
        offer(("Roll 3 dice for the stops on your route", roll_locations))

    # ── 3. How many locations, then where they go ─────────────────────
    def roll_locations():
        say("Rolling for the stops on your route ...")

        def done(dice):
            g["count"] = sum(dice)
            say("%d stops" % g["count"], "Finding your route ...")
            win.update()
            g["routes"] = plan_route(g["map"], g["count"])
            miles = [route_miles(r) for r in g["routes"]]
            show_map()
            say("%d stops    %d miles" % (g["count"], sum(miles)),
                "Your route runs from START to FINISH through %d red x's, START and FINISH included: %d legs, %d miles in all, "
                "the longest leg %d miles. It keeps as close to the shortest way as it can while still making %d stops."
                % (g["count"], len(miles), sum(miles), max(miles), g["count"]))
            offer(("Continue", speed_next))

        throw(3, g["color"], done)

    def speed_next():
        clear_table()
        say("Your route is set", "Location 1 to location %d. Now roll for your travel speed." % g["count"])
        offer(("Roll 1 die for your travel speed", roll_speed))

    # ── 4. Travel speed ───────────────────────────────────────────────
    def roll_speed():
        def done(dice):
            g["speed"] = dice[0]
            say("Travel speed %d" % g["speed"],
                "%s In a fight you must roll more than %d." % (SPEED_WORDS[g["speed"]], enemy_number(g["speed"])))
            if g["speed"] == 6:
                message.set(message.get() + " At speed 6 you may roll for companions: a fox and ravens.")
                offer(("Roll for a companion fox", lambda: companion_roll("fox")))
            else:
                offer(("Continue", ready))

        throw(1, g["color"], done)

    def companion_roll(kind):
        def done(dice):
            joined = dice[0] >= COMPANION_JOINS
            g[kind] = joined
            health_bar()
            if kind == "fox":
                say("A fox joins you!" if joined else "No fox this time",
                    ("A red fox trots up and follows at your side. It adds %d to your fights, but hangs back 1 time in %d."
                     % (COMPANION_BONUS, COMPANION_FAILS["fox"])) if joined else "A fox watches you from the trees, then slips away.")
                offer(("Roll for companion ravens", lambda: companion_roll("ravens")))
            else:
                say("Ravens join you!" if joined else "No ravens this time",
                    ("A pair of ravens settles on your shoulders. They add %d to your fights, but stay out of it 1 time in %d."
                     % (COMPANION_BONUS, COMPANION_FAILS["ravens"])) if joined else "Ravens caw from the treetops, but do not follow.")
                if g.get("fox") and joined:
                    message.set(message.get() + " With both at your side, every attack gets +%d, and they never fail." % (2 * COMPANION_BONUS))
                offer(("Continue", ready))

        throw(1, g["color"], done)

    def ready():
        g["health"], g["at"], g["won"], g["lost"], g["avoided"] = START_HEALTH, 0, 0, 0, 0
        clear_table()
        show_map()
        say("Get ready for your adventure", "You have %d health. Lose it all and the adventure is over." % START_HEALTH)
        offer(("Start", new_leg))

    # ── 5. Travel ─────────────────────────────────────────────────────
    def new_leg():
        g["path"] = g["routes"][g["at"]]
        g["leg"] = route_miles(g["path"])
        g["covered"] = 0
        g["stops"] = stops_on_leg(g["leg"], encounters_on_leg(g["speed"], g["leg"]))
        clear_table()
        show_map()
        say("Your next location is %d mile%s away" % (g["leg"], "" if g["leg"] == 1 else "s"),
            "Location %d to location %d, along the dashed route (each map square is %d miles). Roll 2 dice to travel: you go as many miles as you roll."
            % (g["at"] + 1, g["at"] + 2, MILES_PER_SQUARE))
        offer(("Roll to travel", travel))

    def travel():
        def done(dice):
            before = g["covered"]
            g["target"] = min(g["leg"], before + sum(dice))         # the roll is the miles
            g["fights"] = [s for s in g["stops"] if before < s <= g["target"]]
            g["covered"] = g["target"]
            show_map()
            left = g["leg"] - g["covered"]
            text = "You rolled %d: you travel %d mile%s. " % (sum(dice), g["covered"] - before, "" if g["covered"] - before == 1 else "s")
            if g["fights"]:
                g["covered"] = g["fights"][0]
                show_map()
                say("Danger on the road!", text + "Something blocks your way.")
                offer(("Face it", fight))
            elif left == 0:
                arrive()
            else:
                say("%d miles to go" % left, text + "Roll again to keep going.")
                offer(("Roll to travel", travel))

        throw(2, g["color"], done)

    # ── 6. Combat ─────────────────────────────────────────────────────
    def fight():
        # You see it coming: one die, AVOID_AT or more, and you avoid it.
        g["foe"] = encounter_for(g["speed"])
        kind, name, sight, need, harm, _ = g["foe"]
        clear_table()
        say("Hazard!" if kind == "hazard" else name,
            "%s Roll 1 die: %d or more and you avoid it altogether." % (sight, AVOID_AT))
        offer(("Roll to avoid", avoid_roll))

    def avoid_roll():
        def done(dice):
            # Hold the die and its result on the table for a moment first.
            made = dice[0] >= AVOID_AT
            table.create_text(520, 95, anchor="w", fill="#7CFC9A" if made else "#FF8C7A",
                              font=("TkDefaultFont", 20, "bold"),
                              text=("%d or more: avoided!" if made else "needed %d or more: not avoided") % AVOID_AT)
            say("Avoided!" if made else "Not avoided", "You rolled %d." % dice[0])
            offer()
            g["busy"] = True

            def go_on():
                g["busy"] = False
                after_avoid(dice)

            win.after(RESULT_PAUSE_MS, go_on)

        throw(1, g["color"], done)

    def after_avoid(dice):
        # After the pause: go round it, or face it.
        kind, name, sight, need, harm, _ = g["foe"]
        if dice[0] >= AVOID_AT:
            g["fights"].pop(0)
            g["avoided"] += 1
            say("Avoided!", "You see it in time and go round %s." % (name if kind == "hazard" else "the " + name.lower()))
            return next_after_encounter()
        clear_table()
        foe_side()
        if kind == "hazard":
            say("Hazard!", "You can't get round %s. Roll 2 dice: more than %d gets you past it, or lose %d health."
                % (name, need, harm))
            offer(("Roll to dodge", fight_roll))
        else:
            who, whom = {"Old woman": ("She blocks", "her"), "Old man": ("He blocks", "him")}.get(
                name, ("They block", "them") if name in ("Ravens", "Wolves", "Raccoons", "Wild dogs", "Rabid monkeys")
                else ("It blocks", "it"))
            say(name, "%s your way. Roll 2 dice: more than %d drives %s off, or lose %d health." % (who, need, whom, harm))
            offer(("Roll to fight", fight_roll))

    def next_after_encounter():
        if g["fights"]:
            g["covered"] = g["fights"][0]
            offer(("Face the next danger", fight))
        else:
            offer(("Keep travelling", resume))

    def fight_roll():
        def done(dice):
            kind, name, _, need, harm, fall = g["foe"]
            g["fights"].pop(0)
            bonus, story = companion_help(g.get("fox"), g.get("ravens")) if kind == "creature" else (0, "")
            total = sum(dice) + bonus
            if bonus:
                table.create_text(500, 165, text="total with companions: %d" % total, fill="white",
                                  font=("TkDefaultFont", 14, "bold"))
            story = (story + " ") if story else ""
            plural = name in ("Ravens", "Wolves", "Raccoons", "Wild dogs", "Rabid monkeys")
            if beats(total, need, dice, kind == "creature"):
                g["won"] += 1
                head = "You get past it!" if kind == "hazard" else "You win!"
                text = story + ("You get past %s." % name if kind == "hazard" else "You drive off the %s." % name.lower())
            else:
                g["lost"] += 1
                g["health"] -= harm
                health_bar()
                head = "Ouch!"
                if kind == "hazard":
                    text = "%s You lose %d health." % (fall, harm)
                else:
                    text = story + "The %s hurt%s you: you lose %d health." % (name.lower(), "" if plural else "s", harm)
            if g["health"] <= 0:
                return defeat()
            say(head, text)
            next_after_encounter()

        throw(2, g["color"], done, foe_side)

    def resume():
        # After a fight: on to where the last roll would have taken you.
        g["covered"] = g["target"]
        clear_table()
        show_map()
        left = g["leg"] - g["covered"]
        if left <= 0:
            return arrive()
        say("%d miles to go" % left, "Roll 2 dice to keep travelling.")
        offer(("Roll to travel", travel))

    # ── 7. Arriving, winning, losing ──────────────────────────────────
    def arrive():
        g["at"] += 1
        g.pop("leg", None)
        clear_table()
        show_map()
        if g["at"] == len(g["map"].xs) - 1:
            say("Victory!", "You reached all %d locations with %d health left. Avoided: %d, beaten: %d, lost to: %d."
                % (len(g["map"].xs), g["health"], g["avoided"], g["won"], g["lost"]))
            return offer(("Play again", title_screen))
        say("You reach location %d" % (g["at"] + 1), "%d location%s to go." % (
            len(g["map"].xs) - 1 - g["at"], "" if len(g["map"].xs) - 1 - g["at"] == 1 else "s"))
        offer(("Travel on", new_leg))

    def defeat():
        g["health"] = 0
        health_bar()
        say("Your adventure ends here", "You fell on the way to location %d of %d. Avoided: %d, beaten: %d, lost to: %d."
            % (g["at"] + 2, len(g["map"].xs), g["avoided"], g["won"], g["lost"]))
        offer(("Play again", title_screen))

    title_screen()
    win.mainloop()


# ============================================================================
# START
# ============================================================================

if __name__ == "__main__":
    run_game()
