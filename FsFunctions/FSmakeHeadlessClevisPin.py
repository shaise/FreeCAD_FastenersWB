# -*- coding: utf-8 -*-
"""
***************************************************************************
*   Copyright (c) 2023                                                    *
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


def makeHeadlessClevisPin(self, fa):
    if fa.Type.startswith("ISO2340"):
        d_1, d_2, c, l_e = fa.dimTable
    else:
        raise NotImplementedError(f"Unknown fastener type: {fa.Type}")
    length = fa.calc_len
    fm = FSFaceMaker()
    fm.AddPoint(0.0, 0.0)
    fm.AddPoint(d_1 / 2 - c * math.tan(math.pi / 6), 0.0)
    fm.AddPoint(d_1 / 2, -c)
    fm.AddPoint(d_1 / 2, c - length)
    fm.AddPoint(d_1 / 2 - c * math.tan(math.pi / 6), -length)
    fm.AddPoint(0.0, -length)
    shape = self.RevolveZ(fm.GetFace())
    if fa.Type == "ISO2340B":
        # cut the split-pin holes
        drill = Part.makeCylinder(
            d_2 / 2,
            1.1 * d_1,
            Base.Vector(0.0, 0.55 * d_1, -length + l_e),
            Base.Vector(0.0, -1.0, 0.0),
        )
        shape = shape.cut(drill)
        shape = shape.cut(
            drill.mirror(Base.Vector(0.0, 0.0, -length / 2), Base.Vector(0.0, 0.0, 1.0))
        )
        # chamfer the holes
        cham_cutter = Part.makeCone(
            0.6 * d_2,
            0,
            0.6 * d_2,
            Base.Vector(0.0, -d_1 / 2, -l_e),
            Base.Vector(0.0, 1.0, 0.0),
        )
        cham_cutter = cham_cutter.fuse(
            cham_cutter.mirror(
                Base.Vector(0.0, 0.0, -length / 2), Base.Vector(0.0, 0.0, 1.0)
            )
        )
        cham_cutter = cham_cutter.fuse(
            cham_cutter.mirror(
                Base.Vector(0.0, 0.0, -length / 2), Base.Vector(0.0, 1.0, 0.0)
            )
        )
        shape = shape.cut(cham_cutter)
    return shape
