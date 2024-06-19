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


def makePalNut(self, fa):
    """Create a self-locking counter nut (or 'Pal' nut).
    The returned shape simulates a folded sheetmetal hexagon nut that has
    internal serrations, rather than true threads.
    Supported types:
    - DIN 7967 self locking Pal nuts
    """
    if fa.baseType == "DIN7967":
        od, id, m, s, t = fa.dimTable
    else:
        raise NotImplementedError(f"Unknown fastener type: {fa.Type}")
    # construct the base of the hexagonal shape
    fm = FSFaceMaker()
    fm.AddPoint(s / math.sqrt(3), 0.0)
    fm.AddPoint(s / math.sqrt(3), t)
    fm.AddPoint(od / 2, t)
    fm.AddPoint(id / 2, t + (od - id) / 2 * math.tan(math.radians(30)))
    fm.AddPoint(id / 2, (od - id) / 2 * math.tan(math.radians(30)))
    fm.AddPoint(od / 2, 0.0)
    shape = self.RevolveZ(fm.GetFace())
    inner_hex_s = s - 2.2 * t
    shape = shape.common(self.makeHexPrism(inner_hex_s, m))
    # lay out and create the side profile of the nut
    fm.Reset()
    fm.AddPoint(inner_hex_s / 2, 0.0)
    fm.AddArc2(0.0, 1.1 * t, 90)
    fm.AddPoint(s / 2, m + 1)
    fm.AddPoint(s / 2 - t, m + 1)
    fm.AddPoint(s / 2 - t, 1.1 * t)
    fm.AddArc2(-0.1 * t, 0.0, -90)
    side_len = inner_hex_s * math.tan(math.radians(30))
    side_part = fm.GetFace().extrude(Base.Vector(0.0, side_len, 0.0))
    side_part.translate(Base.Vector(0.0, -side_len / 2, 0.0))
    # add rounded edges to the ends of the folded nut sides
    fm.Reset()
    fm.AddPoint(side_len / 2, m + 1)
    fm.AddPoint(side_len / 2, 0.8 * m)
    fm.AddArc(0.0, m, -side_len / 2, 0.8 * m)
    fm.AddPoint(-side_len / 2, m + 1)
    radius_cutter = fm.GetFace().extrude(Base.Vector(0.0, 0.6 * s, 0.0))
    radius_cutter.rotate(Base.Vector(0.0, 0.0, 0.0),
                         Base.Vector(0.0, 0.0, 1.0), -90)
    side_part = side_part.cut(radius_cutter)
    side_part.rotate(Base.Vector(0.0, 0.0, 0.0),
                     Base.Vector(0.0, 0.0, 1.0), 30)
    # add the 6 nut sides to the base
    for i in range(6):
        side_part.rotate(Base.Vector(0.0, 0.0, 0.0),
                         Base.Vector(0.0, 0.0, 1.0), 60)
        shape = shape.fuse(side_part)
    # cut the thread slots in the center bore
    fm.Reset()
    slot_r = s * 0.04
    fm.AddPoint(slot_r, 0.0)
    fm.AddPoint(slot_r, od / 2)
    fm.AddArc2(-slot_r, 0.0, 180)
    fm.AddPoint(-slot_r, 0.0)
    slot_cutter = fm.GetFace().extrude(Base.Vector(0.0, m, 0.0))
    slot_cutter.rotate(Base.Vector(0.0, 0.0, 0.0),
                       Base.Vector(1.0, 0.0, 0.0), 90)
    for i in range(6):
        slot_cutter.rotate(Base.Vector(0.0, 0.0, 0.0),
                           Base.Vector(0.0, 0.0, 1.0), 60)
        shape = shape.cut(slot_cutter)
    return shape
