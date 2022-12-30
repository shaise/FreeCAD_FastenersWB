# -*- coding: utf-8 -*-
"""
***************************************************************************
*   Copyright (c) 2022                                                    *
*   Alex Neufeld <alex.d.neufeld@gmail.com>                               *
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

from screw_maker import *


def makeWeldNut(self, fa):
    """Creates a nut with geometry optimized for resistance welding to a
    flat surface.
    Supported types:
    - DIN 928 square weld nuts
    - DIN 929 hexagon weld nuts
    """
    if fa.type == "DIN928":
        return _makeSquareWeldNut(self, fa)
    elif fa.type == "DIN929":
        return _makeHexWeldNut(self, fa)
    else:
        raise NotImplementedError(f"Unknown fastener type: {fa.type}")


def _makeHexWeldNut(self, fa):
    dia = self.getDia(fa.calc_diam, True)
    P, b, d2, d3, h1, h2, m, s = fa.dimTable
    # overall hexagon shape
    shape = self.makeHexPrism(s, m)
    # add the chamfer to the top of the nut
    fm = FSFaceMaker()
    fm.AddPoint(s / 2, m)
    fm.AddPoint(s / math.sqrt(3),  m)
    cham_ht = s * (1 / math.sqrt(3) - 0.5) * math.tan(math.radians(30))
    fm.AddPoint(s / math.sqrt(3), m - cham_ht)
    top_cham_cutter = self.RevolveZ(fm.GetFace())
    shape = shape.cut(top_cham_cutter)
    # make another shape to cut the protrusions on the bottom of the nut
    bottom_cutter = Part.makeCylinder(s, h1)
    fm.Reset()
    fm.AddPoint(s / math.sqrt(3) - b, h1)
    lug_w = (h1 - h2) * math.tan(math.radians(25))
    fm.AddPoint(s / math.sqrt(3) - b + lug_w, h1 - h2)
    fm.AddPoint(s, h1 - h2)
    fm.AddPoint(s, h1)
    lug_cutter = fm.GetFace().extrude(Base.Vector(0.0, 2 * s, 0.0))
    lug_cutter.translate(Base.Vector(0.0, -s, 0.0))
    for i in range(3):
        lug_cutter.rotate(Base.Vector(0.0, 0.0, 0.0),
                          Base.Vector(0.0, 0.0, 1.0), 120)
        bottom_cutter = bottom_cutter.cut(lug_cutter)
    inner_cyl = Part.makeCylinder(d2 / 2, h1)
    bottom_cutter = bottom_cutter.cut(inner_cyl)
    shape = shape.cut(bottom_cutter)
    # add the bore for the threads.
    # there is also a shallow counterbore at the top face of the nut
    fm.Reset()
    id = self.GetInnerThreadMinDiameter(dia, P, 0.0)
    bore_cham_ht = (dia * 1.05 - id) / 2 * math.tan(math.radians(30))
    fm.AddPoint(0.0, 0.0)
    fm.AddPoint(dia * 1.05 / 2, 0.0)
    fm.AddPoint(id / 2, bore_cham_ht)
    fm.AddPoint(id / 2, m - bore_cham_ht - 0.2)
    fm.AddPoint(dia * 1.05 / 2, m - 0.2)
    fm.AddPoint(d3 / 2, m - 0.2)
    fm.AddPoint(d3 / 2, m)
    fm.AddPoint(0.0, m)
    bore_cutter = self.RevolveZ(fm.GetFace())
    shape = shape.cut(bore_cutter)
    # add modelled threads if needed
    if fa.thread:
        thread_cutter = self.CreateInnerThreadCutter(dia, P, m + P)
        shape = shape.cut(thread_cutter)
    # transform so that the XY-plane relates better to the installed height
    mat = Base.Matrix()
    mat.move(Base.Vector(0.0, 0.0, -h1))
    shape = shape.transformGeometry(mat)
    return shape


def _makeSquareWeldNut(self, fa):
    dia = self.getDia(fa.calc_diam, True)
    if fa.type == "DIN928":
        P, b, d2, d4, h1, h2, m, s = fa.dimTable
    # the main body of the nut is a rectangular prism
    shape = Part.makeBox(s, s, m + h1 + h2)
    shape.translate(Base.Vector(-s / 2, -s / 2, 0.0))
    # make another shape to cut the protrusions on the bottom of the nut
    bottom_cutter = Part.makeCylinder(s, h1)
    fm = FSFaceMaker()
    fm.AddPoint(s, 0.0)
    fm.AddPoint(s * math.sqrt(2) / 2 - b, 0.0)
    fm.AddPoint(s * math.sqrt(2) / 2 - b - h1, h1)
    fm.AddPoint(s, h1)
    lug_cutter = fm.GetFace().extrude(Base.Vector(0.0, 2 * s, 0.0))
    lug_cutter.translate(Base.Vector(0.0, -s, 0.0))
    lug_cutter.rotate(Base.Vector(0.0, 0.0, 0.0),
                      Base.Vector(0.0, 0.0, 1.0), 45)
    for _ in range(4):
        lug_cutter.rotate(Base.Vector(0.0, 0.0, 0.0),
                          Base.Vector(0.0, 0.0, 1.0), 90)
        bottom_cutter = bottom_cutter.cut(lug_cutter)
    shape = shape.cut(bottom_cutter)
    # lay out a cutting tool to define the other features of the nut
    fm.Reset()
    id = self.GetInnerThreadMinDiameter(dia, P, 0.0)
    bore_cham_ht = (dia * 1.05 - id) / 2 * math.tan(math.radians(45))
    fm.AddPoint(s * math.sqrt(2) / 2, 0.0)
    fm.AddPoint(dia * 1.05 / 2, 0.0)
    fm.AddPoint(dia * 1.05 / 2, h1)
    fm.AddPoint(id / 2, h1 + bore_cham_ht)
    fm.AddPoint(id / 2, m + h2 - bore_cham_ht)
    fm.AddPoint(dia * 1.05 / 2, m + h2 - 0.02)
    fm.AddPoint(d2 / 2, m + h2 - 0.02)
    fm.AddPoint(d2 / 2, m + h2)
    fm.AddPoint(d4 / 2, m + h2)
    fm.AddPoint(d4 / 2, m)
    fm.AddPoint(s / 2, m)
    top_cham_ht = s * (math.sqrt(2) - 1) / 2 * math.tan(math.radians(15))
    fm.AddPoint(s * math.sqrt(2) / 2, m - top_cham_ht)
    revolve = self.RevolveZ(fm.GetFace())
    shape = shape.common(revolve)
    # add modelled threads if needed
    if fa.thread:
        thread_cutter = self.CreateInnerThreadCutter(dia, P, m + h1 + h2 + P)
        shape = shape.cut(thread_cutter)
    # transform so that the XY-plane relates better to the installed height
    mat = Base.Matrix()
    mat.move(Base.Vector(0.0, 0.0, -h1))
    shape = shape.transformGeometry(mat)
    return shape
