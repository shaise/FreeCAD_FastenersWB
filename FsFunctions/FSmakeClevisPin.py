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


def makeClevisPin(self, fa):
    if fa.Type.startswith("ISO2341"):
        d, d_k, d_l, c, e, k, l_e, r = fa.dimTable
    else:
        raise NotImplementedError(f"Unknown fastener type: {fa.Type}")
    length = fa.calc_len
    fm = FSFaceMaker()
    fm.AddPoint(0.0, k)
    fm.AddPoint(d_k / 2 - e, k)
    fm.AddPoint(d_k / 2, k - e)
    fm.AddPoint(d_k / 2, 0.0)
    fm.AddPoint(d / 2 + r, 0.0)
    fm.AddArc2(0.0, -r, 90)
    fm.AddPoint(d / 2, -length + c)
    fm.AddPoint(d / 2 - c * math.sqrt(3) / 3, -length)
    fm.AddPoint(0.0, -length)
    shape = self.RevolveZ(fm.GetFace())
    if fa.Type == "ISO2341B":
        # cut out the cross-hole
        drill = Part.makeCylinder(
            d_l / 2,
            1.1 * d,
            Base.Vector(0.0, 0.55 * d, -length + l_e),
            Base.Vector(0.0, -1.0, 0.0),
        )
        shape = shape.cut(drill)
        # chamfer the cross hole. This is needed to create a circular edge
        # that can be selected for a split pin to attach to
        # chamfer the cross-holes
        cham_cutter = Part.makeCone(
            0.6 * d_l,
            0,
            0.6 * d_l,
            Base.Vector(0.0, -d / 2, -length + l_e),
            Base.Vector(0.0, 1.0, 0.0),
        )
        # rotate cone to align seam with the through-hole
        cham_cutter = cham_cutter.rotate(
            Base.Vector(0.0, 0.0, -length + l_e),
            Base.Vector(0.0, 1.0, 0.0),
            180
        )
        cham_cutter = cham_cutter.fuse(
            cham_cutter.mirror(
                Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 1.0, 0.0)
            )
        )
        shape = shape.cut(cham_cutter)
    return shape
