# -*- coding: utf-8 -*-
"""
***************************************************************************
*   Copyright (c) 2024                                                    *
*   Original code by:                                                     *
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


def makeReducedShankHexHeadBolt(self, fa):
    """Creates a bolt with a hexagonal head and a reduced shank

    supported types:
    - ISO 4015 hexagon head bolts with reduced shank
    """
    dia = self.getDia(fa.calc_diam, False)
    length = fa.calc_len
    if fa.baseType == "ISO4015":
        P, b1, b2, c, _, _, dw, e, k, _, _, _, r, s, _, x = fa.dimTable
        if length > 125 and b2 != 0:
            b = b2
        else:
            b = b1
    else:
        raise NotImplementedError(f"Unknown fastener type: {fa.Type}")
    dp = (dia / 2 - 0.375 * math.sqrt(3) / 2 * P) * 2
    # needed for chamfer at head top
    cham = (e - s) * math.sin(math.radians(15))
    # lay out head profile
    fm = FSFaceMaker()
    fm.AddPoint(0.0, k)
    fm.AddPoint(s / 2.0, k)
    fm.AddPoint(s / math.sqrt(3.0), k - cham)
    fm.AddPoint(s / math.sqrt(3.0), c)
    fm.AddPoint(dw / 2.0, c)
    fm.AddPoint(dw / 2.0, 0.0)
    fm.AddPoint(dp / 2.0 + r, 0.0)
    fm.AddArc2(0.0, -r, 90)
    # this style of fastener should always be partially threaded
    # However, the user may enter a custom length shorter than is typically
    # commercially available. Try to avoid generating invalid geometry in
    # such a case:
    if length - b - x - r < 0.1:
        fm.AddPoint(dp / 2, -r - 0.1)
        fm.AddPoint(dia / 2, -r - 0.1 - x)
        thread_length = length - r
    else:
        fm.AddPoint(dp / 2, -length + b + x)
        fm.AddPoint(dia / 2, -length + b)
        thread_length = b + x
    fm.AddPoint(dia / 2, -length + dia / 10)
    fm.AddPoint(dia * 4 / 10, -length)
    fm.AddPoint(0.0, -length)
    shape = self.RevolveZ(fm.GetFace())
    # create cutting tool for hexagon head
    extrude = self.makeHexPrism(s, k + length + 2)
    extrude.translate(Base.Vector(0.0, 0.0, -length - 1))
    shape = shape.common(extrude)
    if fa.Thread:
        thread_cutter = self.CreateBlindThreadCutter(dia, P, thread_length)
        thread_cutter.translate(Base.Vector(0.0, 0.0, -1 * (length - thread_length)))
        shape = shape.cut(thread_cutter)
    return shape
