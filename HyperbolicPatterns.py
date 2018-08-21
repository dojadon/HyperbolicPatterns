# -*- coding: utf-8 -*-

import sys
#sys.path.append(r"")

import clr
clr.AddReference("VecMath")

from VecMath import *
import math

MAX_LAYER = 8
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

def add_triangle(p, l1, l2, layer):
    triangles.append((p, l1, l2))

    if layer >= MAX_LAYER: return
    
    if l1.Length() < EPS or l2.Length() < EPS:
        p_inv = reflect(+(l1 - l2), p)
    else:
        l3 = invert(Vector2.Zero, 1, l1)
        successed, center, r = circle_center_pos(l1, l2, l3)

        if not successed:
            print "Did not Successed! layer:" + str(layer)
            return
        p_inv = invert(center, r, p)
    
    if layer > 1: add_triangle(l1, l2, p_inv, layer + 1)
    add_triangle(l2, p_inv, l1, layer + 1)

v1 = Vector2(0.26012, -0.450529)
m = Matrix2.Rotation(math.pi / 3)

for i in range(6):
    v2 = v1 * m
    add_triangle(Vector2.Zero, v1, v2, 0)
    v1 = v2

with open("Hyperbolic.obj", "w") as f:
    vertices_lines = []
    triangles_lines = []

    vertices = [v for tri in triangles for v in tri]
    num_vertices = len(vertices)

    for idx, tri in enumerate(triangles):
        for vtx in tri:
            line = "v " + " ".join([str(vtx[i]) for i in range(2)]) + " 0\n"
            vertices_lines.append(line)

        line = "f "
        for vtx in tri:
            line += str(1 + next(iter([j for j in range(num_vertices) if Vector2.EpsilonEquals(vertices[j], vtx, EPS)]), False)) + "// "
        triangles_lines.append(line + "\n")
    
    f.writelines(["o Hyperbolic\n"] + vertices_lines + triangles_lines)

