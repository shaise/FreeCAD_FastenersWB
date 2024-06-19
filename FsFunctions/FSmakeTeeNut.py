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


def makeTeeNut(self, fa):
    """Creates a threaded insert with 4 prongs, intended to be driven into
    soft material such as wood. Also known as a 'Tee Nut'.
    Supported types:
    - DIN 1624 Tee nuts
    """
    dia = self.getDia(fa.calc_diam, True)
    if fa.baseType == "4PWTI":
        P, d2, d3, l1, l2, a = fa.dimTable
    else:
        raise NotImplementedError(f"Unknown fastener type: {fa.Type}")
    # lay out the fastener profile
    id = self.GetInnerThreadMinDiameter(dia, P, 0.0)
    bore_cham_ht = (dia * 1.05 - id) / 2 * math.tan(math.radians(30))
    fm = FSFaceMaker()
    fm.AddPoint(1.05 * dia / 2, 0.0)
    fm.AddPoint(d3 / 2, 0.0)
    fm.AddPoint(d3 / 2, a)
    boss_flange_fillet_r = 0.25 * a
    fm.AddPoint(d2 / 2 + boss_flange_fillet_r, a)
    fm.AddArc2(0.0, boss_flange_fillet_r, -90)
    top_fillet_r = (d2 - 1.05 * dia) / 2
    fm.AddPoint(d2 / 2, l1 - top_fillet_r)
    fm.AddArc2(-top_fillet_r, 0.0, 90)
    fm.AddPoint(id / 2, l1 - bore_cham_ht)
    fm.AddPoint(id / 2, bore_cham_ht)
    shape = self.RevolveZ(fm.GetFace())
    # model the insert barbs
    fm.Reset()
    fm.AddPoint(0.0, 0.0)
    fm.AddArc2(0.0, 1.1 * a, -90)
    fm.AddPoint(-1.1 * a, l2)
    fm.AddPoint(-0.1 * a, l2)
    fm.AddPoint(-0.1 * a, 1.1 * a)
    fm.AddArc2(0.1 * a, 0.0, 90)
    barb_th = (d3 - d2) / 4
    barb_shape = fm.GetFace().extrude(Base.Vector(0.0, barb_th, 0.0))
    fm.Reset()
    chord_l = math.sqrt((l2 - 1.1 * a) ** 2 + barb_th ** 2)
    arc_th = math.pi - 2 * math.atan((l2 - 1.1 * a) / barb_th)
    arc_r = chord_l / (2 * math.sin(arc_th / 2))
    fm.AddPoint(0.0, 1.1 * a)
    fm.AddArc2(arc_r, 0.0, -1 * math.degrees(arc_th))
    fm.AddPoint(0.0, l2)
    barb_trim = fm.GetFace().extrude(Base.Vector(0.0, 2 * a, 0.0))
    barb_trim.rotate(Base.Vector(0.0, 0.0, 0.0),
                     Base.Vector(0.0, 0.0, 1.0), 90)
    barb_shape = barb_shape.cut(barb_trim)
    barb_shape.translate(Base.Vector(0.0, -d3 / 2, 0.0))
    clearance_box = Part.makeBox(d3, d3, d3)
    clearance_box.translate(Base.Vector(-d3, -1.5 * d3 + barb_th, 0.0))
    for _ in range(4):
        clearance_box.rotate(Base.Vector(0.0, 0.0, 0.0),
                             Base.Vector(0.0, 0.0, 1.0), 90)
        shape = shape.cut(clearance_box)
        barb_shape.rotate(Base.Vector(0.0, 0.0, 0.0),
                          Base.Vector(0.0, 0.0, 1.0), 90)
        shape = shape.fuse(barb_shape)
    # add modelled threads if needed
    if fa.Thread:
        thread_cutter = self.CreateInnerThreadCutter(dia, P, l1 + P)
        shape = shape.cut(thread_cutter)
    return shape
