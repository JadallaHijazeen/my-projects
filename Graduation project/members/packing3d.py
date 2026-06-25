from itertools import permutations

EPS = 1e-9

def rotations(lwh):
    
    l, w, h = lwh
    return list(set(permutations([l, w, h], 3)))

def inside_bin(pos, size, bin_size):
    x, y, z = pos
    dx, dy, dz = size
    L, W, H = bin_size
    return (0 <= x and 0 <= y and 0 <= z and x + dx <= L and y + dy <= W and z + dz <= H)

def overlap(p1, s1, p2, s2):
    x1, y1, z1 = p1; dx1, dy1, dz1 = s1
    x2, y2, z2 = p2; dx2, dy2, dz2 = s2
    return not (
        x1 + dx1 <= x2 or x2 + dx2 <= x1 or
        y1 + dy1 <= y2 or y2 + dy2 <= y1 or
        z1 + dz1 <= z2 or z2 + dz2 <= z1
    )

def collides(pos, size, placed):
    for it in placed:
        if overlap(pos, size, it["pos"], it["size"]):
            return True
    return False

def _eq(a, b, eps=EPS):
    return abs(a - b) <= eps

def _rect_intersection(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1 = max(ax1, bx1)
    iy1 = max(ay1, by1)
    ix2 = min(ax2, bx2)
    iy2 = min(ay2, by2)
    if ix2 <= ix1 + EPS or iy2 <= iy1 + EPS:
        return None
    return (ix1, iy1, ix2, iy2)

def fully_supported(pos, size, placed):
    """
    100% stability:
    - z == 0 => supported by floor
    - z > 0  => base rectangle must be fully covered by top faces at height z
    """
    x, y, z = pos
    dx, dy, dz = size

    if _eq(z, 0.0):
        return True

    base = (x, y, x + dx, y + dy)

    supporters = []
    for p in placed:
        px, py, pz = p["pos"]
        pdx, pdy, pdz = p["size"]
        if _eq(pz + pdz, z):
            inter = _rect_intersection(base, (px, py, px + pdx, py + pdy))
            if inter:
                supporters.append(inter)

    if not supporters:
        return False

    
    xs = {base[0], base[2]}
    ys = {base[1], base[3]}
    for r in supporters:
        xs.add(r[0]); xs.add(r[2])
        ys.add(r[1]); ys.add(r[3])
    xs = sorted(xs)
    ys = sorted(ys)

    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            x1, x2 = xs[i], xs[i + 1]
            y1, y2 = ys[j], ys[j + 1]
            if x2 <= x1 + EPS or y2 <= y1 + EPS:
                continue

            cx = (x1 + x2) / 2.0
            cy = (y1 + y2) / 2.0

            covered = False
            for rx1, ry1, rx2, ry2 in supporters:
                if (rx1 - EPS <= cx <= rx2 + EPS) and (ry1 - EPS <= cy <= ry2 + EPS):
                    covered = True
                    break
            if not covered:
                return False

    return True

def score(pos, size, placed, bin_size):
    """
    Storage-oriented score (lower is better):
    1) keep max height low (practical stacking)
    2) pack tightly (reduce leftover space)
    3) tie-break z/y/x low
    """
    x, y, z = pos
    dx, dy, dz = size
    L, W, H = bin_size

    current_max_z = 0
    for p in placed:
        current_max_z = max(current_max_z, p["pos"][2] + p["size"][2])
    new_max_z = max(current_max_z, z + dz)

    # "waste" encourages tight placement into corners / less empty remainder
    waste = (L - (x + dx)) + (W - (y + dy)) + (H - (z + dz))

    return (new_max_z, waste, z, y, x)

def update_points(points, pos, size, bin_size=None):
    x, y, z = pos
    dx, dy, dz = size

    base = [p for p in points if p != pos]
    cand = base + [(x + dx, y, z), (x, y + dy, z), (x, y, z + dz)]
    cand = list(dict.fromkeys(cand))

   
    if bin_size is not None:
        L, W, H = bin_size
        cand = [p for p in cand if 0 <= p[0] <= L and 0 <= p[1] <= W and 0 <= p[2] <= H]

    pruned = []
    for p in cand:
        dominated = False
        for q in cand:
            if q != p and q[0] <= p[0] and q[1] <= p[1] and q[2] <= p[2]:
                dominated = True
                break
        if not dominated:
            pruned.append(p)

    pruned.sort(key=lambda t: (t[2], t[1], t[0]))
    return pruned

def pack_boxes(bin_size, boxes):
    """
    bin_size: (L, W, H)
    boxes: list of dicts: {"id": box_id, "lwh": (l,w,h), "weight": w, "color": "..."}
    returns: placed, not_packed
    """

    
    def key(b):
        l, w, h = b["lwh"]
        return -(l * w * h), -max(b["lwh"]), -b.get("weight", 0)

    remaining = sorted(boxes, key=key)
    placed = []
    points = [(0, 0, 0)]

    for b in remaining:
        best = None  

        for p in points:
            for r in rotations(b["lwh"]):
                if not inside_bin(p, r, bin_size):
                    continue
                if collides(p, r, placed):
                    continue
                if not fully_supported(p, r, placed):
                    continue

                sc = score(p, r, placed, bin_size)
                if best is None or sc < best[0]:
                    best = (sc, p, r)

        if best is None:
            continue

        _, pos, size = best
        placed.append({
            "id": b["id"],
            "pos": pos,
            "size": size,
            "color": b.get("color", "#ffffff"),
        })
        points = update_points(points, pos, size, bin_size)

    packed_ids = {p["id"] for p in placed}
    not_packed = [b["id"] for b in remaining if b["id"] not in packed_ids]
    return placed, not_packed
