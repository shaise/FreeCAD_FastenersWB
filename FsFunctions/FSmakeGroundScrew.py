# -*- coding: utf-8 -*-
"""
***************************************************************************
*   Copyright (c) 2025                                                    *
*   Joao Matos <joao@tritao.eu>                                           *
*                                                                         *
*   This file is a supplement to the FreeCAD CAx development system.      *
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU Lesser General Public License (LGPL)    *
*   as published by the Free Software Foundation; either version 2 of     *
*   the License, or (at your option) any later version.                   *
*   for detail see the LICENCE text file.                                 *
*                                                                         *
*   This software is distributed in the hope that it will be useful,      *
*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
*   GNU Library General Public License for more details.                  *
*                                                                         *
*   You should have received a copy of the GNU Library General Public     *
*   License along with this macro; if not, write to the Free Software     *
*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
*   USA                                                                   *
*                                                                         *
***************************************************************************
"""

from screw_maker import FSFaceMaker
import FreeCAD as App
import Draft

def makeCapsuleEdges(total_length, width):
    radius = width / 2.0

    line_top = Draft.makeLine(
        App.Vector(radius, width, 0),
        App.Vector(total_length - radius, width, 0)
    )
    line_bottom = Draft.makeLine(
        App.Vector(radius, 0, 0),
        App.Vector(total_length - radius, 0, 0)
    )

    arc_left = Draft.makeCircle(
        radius=radius,
        startangle=90,
        endangle=270,
        placement=App.Placement(App.Vector(radius, radius, 0), App.Rotation(0,0,0)),
        face=False
    )
    arc_right = Draft.makeCircle(
        radius=radius,
        startangle=-90,
        endangle=90,
        placement=App.Placement(App.Vector(total_length - radius, radius, 0), App.Rotation(0,0,0)),
        face=False
    )

    line_top.recompute()
    line_bottom.recompute()
    arc_left.recompute()
    arc_right.recompute()

    return [line_top, line_bottom, arc_left, arc_right]

def makeCapsule(total_length, width):
    all_edges = makeCapsuleEdges(total_length, width)

    # 1) Merge into a single Wire
    wire_objs = Draft.upgrade(all_edges, delete=True)
    capsule_wire = wire_objs[0][0]
    capsule_wire.recompute()

    # 2) Turn that Wire into a Face
    face_objs = Draft.upgrade(capsule_wire, delete=True)
    capsule_face = face_objs[0][0]
    capsule_face.recompute()
    capsule_face.Label = "Capsule"

    return capsule_face

def makeFixedFlangeFace(dia, length, head_w, head_th, center_d, tip_length):
    """Make the face for a ground screw fixed flange."""

    r = dia / 10
    fm = FSFaceMaker()
    fm.AddPoint(center_d, 0.0)
    fm.AddPoint(center_d, head_th)
    fm.AddPoint(head_w / 2, head_th)
    fm.AddPoint(head_w / 2, 0.0)
    fm.AddPoint(dia / 2 + r, 0.0)
    fm.AddArc2(0.0, -r, 90)  # small fillet
    fm.AddPoint(dia / 2, -length + tip_length)
    fm.AddPoint(0.0, -length)
    fm.AddPoint(0.0, -length + head_th)
    fm.AddPoint(dia / 2 - head_th, -length + tip_length)
    fm.AddPoint(dia / 2 - head_th, 0.0)

    shape = fm.GetFace()

    return shape

def makeCapsuleExtrusion(dia, head_w, th):
    total_length = (head_w - dia) / 2 * 0.667
    width = 12
    capsule_face = makeCapsule(total_length, width)

    offset = dia / 2 + 12
    capsule_face.Placement = App.Placement(App.Vector(offset, -width / 2, 0), App.Rotation(0, 0, 0))

    capsule_faces= Draft.make_polar_array(
        capsule_face,
        number=8,
        angle=360.0,
        center=App.Vector(0.0, 0.0, 0.0),
        use_link=True
    )
    capsule_faces.Fuse = True
    capsule_faces.recompute()

    holes = capsule_faces.Shape.extrude(App.Vector(0, 0, th * 2))

    App.ActiveDocument.removeObject(capsule_face.Name)
    App.ActiveDocument.removeObject(capsule_faces.Name)

    return holes

def makeGroundScrew(self, fa):
    length = fa.calc_len
    dia, head_w, th, tip_length = fa.dimTable

    thread_length = 0.667 * length
    thread_tip = 0.333 * tip_length
    center_hole = 20.0

    screw = self.RevolveZ(makeFixedFlangeFace(dia, length, head_w, th, center_hole, tip_length))
    thread = None

    # make thread
    if fa.Thread:
        ro = dia / 2
        ri = dia / 2 + 7
        P = 40.0
        thread = self.makeDin7998Thread(
            -length + thread_length, -length + tip_length + thread_tip, -length, ro, ri, P
        )
        screw = screw.fuse(thread)

    capsule_holes = makeCapsuleExtrusion(dia, head_w, th)
    screw = screw.cut(capsule_holes)

    return screw
