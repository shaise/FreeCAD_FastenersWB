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


def makeInternalThreadedTaperPin(self, fa):
    length = fa.calc_len
    if fa.Type == "ISO8736":
        d_1, a, d_2, P, d_3, t_1, t_2, t_3 = fa.dimTable
        d_5 = d_1 + (length - 2 * a) / 50
    else:
        raise NotImplementedError(f"Unknown fastener type: {fa.Type}")
    fm = FSFaceMaker()
    cham_top = math.tan(math.radians(15)) * a
    fm.AddPoint(0.0, -t_2)
    d_4 = self.GetInnerThreadMinDiameter(d_2, P)
    fm.AddPoint(d_4 / 2, d_4 / (2 * math.tan(math.radians(59))) - t_2)
    fm.AddPoint(d_4 / 2, -t_3 - math.tan(math.radians(30)) * (d_3 - d_4))
    fm.AddPoint(d_3 / 2, -t_3)
    fm.AddPoint(d_3 / 2, 0.0)
    fm.AddPoint(d_5 / 2 - cham_top, 0.0)
    fm.AddPoint(d_5 / 2, -a)
    fm.AddPoint(d_1 / 2, a - length)

    fm.AddArc(
        d_1 * math.sin(math.pi / 12),
        d_1 * (1 - math.cos(math.pi / 12)) - length,
        0.0,
        -length,
    )
    shape = self.RevolveZ(fm.GetFace())
    if fa.Thread:
        thread_cutter = self.CreateBlindInnerThreadCutter(d_2, P, t_1)
        thread_cutter.rotate(
            Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 1.0, 0.0), 180
        )
        shape = shape.cut(thread_cutter)
    return shape
