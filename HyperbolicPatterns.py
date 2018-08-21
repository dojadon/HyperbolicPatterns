# -*- coding: utf-8 -*-

import sys
#sys.path.append(r"")

import clr
clr.AddReference("VecMath")

from VecMath import *
import math

MAX_LAYER = 3
EPS = 1E-5

triangles = []

def intersect_pos(p1, d1, p2, d2):
    c1 = d1.y * p1.x - d1.x * p1.y
    c2 = d2.y * p2.x - d2.x * p2.y
 
    f = d1.y * d2.x - d2.y * d1.x

    if abs(f) < EPS: return False, Vector2.Zero
    
    x = (d2.x * c1 - d1.x * c2) / f
    y = (d2.y * c1 - d1.y * c2) / f

    return True, Vector2(x, y)

def circle_center_pos(p1, p2, p3):
    mat = Matrix2(0, 1, -1, 0)

    m1 = (p1 + p2) * 0.5
    m2 = (p2 + p3) * 0.5

    d1 = +(p1 - p2) * mat
    d2 = +(p2 - p3) * mat

    successed, center = intersect_pos(m1, d1, m2, d2)

    return successed, center, (p1 - center).Length()

def reflect(n, p):
    mat = Matrix2(1 - 2 * n.x ** 2, -2 * n.x * n.y, -2 * n.x * n.y, 1 - 2 * n.y ** 2)
    return p * mat

def invert(center, r, p):
    v = p - center
    d = v.Length()

    if abs(d) < EPS: return center

    return center + +v * (r ** 2 / d)

def add_triangle(vertices, UNIT_ANGLE = math.pi / 36):
    center = (vertices[0] + vertices[1] + vertices[2]) * (1.0 / 3)

    def add_edge(e1, e2):
        if e1.Length() < EPS or e2.Length() < EPS or (+e1 - +e2).Length() < EPS:
            triangles.append((center, e1, e2))
            return
        
        successed, c, r = circle_center_pos(e1, e2, invert(Vector2.Zero, 1, e1))
        
        v1 = +(e1 - c)
        v2 = +(e2 - c)

        angle = math.acos(v1 * v2)
        num_split = int(round(abs(angle) / UNIT_ANGLE))

        if num_split == 0:
            triangles.append((center, e1, e2))
            return

        mult = 1.0 / num_split

        for i in range(num_split):
            triangles.append((center, c + Vector2.Interpolate(v2, v1, mult * i) * r, c + Vector2.Interpolate(v2, v1, mult * (i + 1)) * r))

    for i in range(3):
        add_edge(vertices[i], vertices[(i + 1) % 3])

def add_motif(vertices, center, layer):
    def getvtx(idx, num = len(vertices)):
        return vertices[idx % num]

    for i in range(len(vertices)):
        add_triangle((center, getvtx(i), getvtx(i + 1)))
    
    if layer >= MAX_LAYER:
        return

    for i in range(len(vertices)):
        edge = [getvtx(i), getvtx(i + 1)]
        successed, c, r = circle_center_pos(edge[0], edge[1], invert(Vector2.Zero, 1, edge[0]))

        invert_center = invert(c, r, center)

        if invert_center.Length() < center.Length():
            continue

        inverted_vertices = edge + [invert(c, r, getvtx(i + 2 + j)) for j in range(4)]

        add_motif(inverted_vertices, invert_center, layer + 1)

v = Vector2(0, (math.sqrt(6) - math.sqrt(2)) * 0.5)
add_motif([v * Matrix2.Rotation(math.pi / 3 * i) for i in range(6)], Vector2.Zero, 0)

with open("Hyperbolic.obj", "w") as f:
    vertices_lines = []
    triangles_lines = []

    vertices = [v for tri in triangles for v in tri]
    num_vertices = len(vertices)

    for idx, tri in enumerate(triangles):
        for vtx in tri:
            line = "v " + " ".join([str(vtx[i]) for i in range(2)]) + " 0\n"
            vertices_lines.append(line)

        line = "f " + " ".join([str(idx * 3 + j + 1) + "//" for j in range(3)]) + "\n"
        triangles_lines.append(line)
    
    f.writelines(["o Hyperbolic\n"] + vertices_lines + triangles_lines)