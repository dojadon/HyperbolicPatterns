# -*- coding: utf-8 -*-

import clr
clr.AddReference("VecMath")

from VecMath import *
import math

wavefront_txt = "o Hyperbolic\n" + "mtllib Hyperbolic.mtl\n"

MAX_LAYER = 3
EPS = 1E-5

obj_vertices = []
triangles_mtl = [], []

materials = "Material1", "Material2"

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

    return center + v * (r ** 2 / d ** 2)

def add_vertex(vtx):
    num_vertices = len(obj_vertices)
    idx = next(iter([i for i in range(num_vertices) if Vector2.EpsilonEquals(obj_vertices[i], vtx, EPS)]), num_vertices)

    if idx == num_vertices:
        obj_vertices.append(vtx)
    return idx

def add_triangle(vertices, center, mtl_idx, UNIT_ANGLE = math.pi / 36):
    triangles = triangles_mtl[mtl_idx]

    def add_triangle_to_list(*vertices):
        triangles.append([add_vertex(v) for v in vertices])

    def add_edge(e1, e2):
        if e1.Length() < EPS or e2.Length() < EPS or (+e1 - +e2).Length() < EPS:
            add_triangle_to_list(center, e1, e2)
            return
        
        successed, c, r = circle_center_pos(e1, e2, invert(Vector2.Zero, 1, e1))
        
        v1 = +(e1 - c)
        v2 = +(e2 - c)

        angle = math.acos(v1 * v2)
        num_split = int(round(abs(angle) / UNIT_ANGLE))

        if num_split == 0:
            add_triangle_to_list(center, e1, e2)
            return

        mult = 1.0 / num_split

        def interpolate(t):
            return Vector2.Interpolate(v2, v1, t)

        for i in range(num_split):
            add_triangle_to_list(center, c + interpolate(mult * i) * r, c + interpolate(mult * (i + 1)) * r)

    for i in range(3):
        add_edge(vertices[i], vertices[(i + 1) % 3])

def add_motif(vertices, triangle_centers, center, mtl_idx, layer):
    num_vertices = len(vertices)

    def getvtx(idx):
        return vertices[idx % num_vertices]

    for i in range(num_vertices):
        add_triangle((center, getvtx(i), getvtx(i + 1)), triangle_centers[i], (mtl_idx + i) % 2)
    
    if layer >= MAX_LAYER:
        return

    for i in range(num_vertices):
        edge = [getvtx(i), getvtx(i + 1)]
        successed, c, r = circle_center_pos(edge[0], edge[1], invert(Vector2.Zero, 1, edge[0]))

        invert_center = invert(c, r, center)

        if invert_center.Length() < center.Length():
            continue

        inverted_vertices = edge + [invert(c, r, getvtx(i + 2 + j)) for j in range(num_vertices - 2)]
        inverted_triangle_centers = [invert(c, r, triangle_centers[(i + j) % num_vertices]) for j in range(num_vertices)]

        add_motif(inverted_vertices, inverted_triangle_centers, invert_center, (mtl_idx + i + 1) % 2, layer + 1)


v = Vector2(0, (math.sqrt(6) - math.sqrt(2)) * 0.5)
c = v * 0.5 * Matrix2.Rotation(math.pi / 6)
add_motif([v * Matrix2.Rotation(math.pi / 3 * i) for i in range(6)], [c * Matrix2.Rotation(math.pi / 3 * i) for i in range(6)], Vector2.Zero, 0, 0)

with open("Hyperbolic.obj", "w") as f:
    lines = [wavefront_txt]

    print len(obj_vertices)
    for vtx in obj_vertices:
        line = "v " + " ".join([str(vtx[i]) for i in range(2)]) + " 0\n"
        lines.append(line)
    
    for i in range(2):
        lines.append("usemtl " + materials[i] + "\n")

        for tri in triangles_mtl[i]:
            line = "f " + " ".join([str(idx + 1) + "//" for idx in tri]) + "\n"
            lines.append(line)
    f.writelines(lines)