# -*- coding: utf-8 -*-
"""
***************************************************************************
*   Copyright (c) 2024                                                    *
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


def makeHeadlessScrew(self, fa):
    """creates a headless screw with a smooth shank
    supported types:
      ISO 2342 - slotted headless screws with shank
    """
    SType = fa.baseType
    dia = self.getDia(fa.calc_diam, False)
    length = fa.calc_len
    if SType == "ISO2342":
        P, b, d_s_min, d_s_max, n_nom, _, _, t_min, t_max, _ = fa.dimTable
        t = (t_min + t_max) / 2
        n = n_nom
        cham = dia / 10
    else:
        raise NotImplementedError(f"Unknown fastener type: {fa.Type}")
    fm = FSFaceMaker()
    fm.AddPoint(0.0, 0.0)
    fm.AddPoint(dia / 2 - cham, 0.0)
    fm.AddPoint(dia / 2, -cham)
    fm.AddPoint(dia / 2, -length + b)
    fm.AddPoint(dia / 2, -length + cham)
    fm.AddPoint(dia / 2 - cham, -length)
    fm.AddPoint(0.0, -length)
    shape = self.RevolveZ(fm.GetFace())
    if SType == "ISO2342":
        # cut a slot recess
        slot_shape = Part.makeBox(
            n, 1.1 * dia, 1.1 * t, Base.Vector(-n / 2, -0.55 * dia, -t)
        )
        shape = shape.cut(slot_shape)
    if fa.Thread:
        thread_cutter = self.CreateBlindThreadCutter(dia, P, b)
        thread_cutter.translate(Base.Vector(0.0, 0.0, -1 * (length - b)))
        shape = shape.cut(thread_cutter)
    return shape
