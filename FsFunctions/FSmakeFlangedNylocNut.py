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


def makeFlangedNylocNut(self, fa):
    """Creates a non-metallic insert lock nut with a flange
    Supported types:
    - ISO 7043 nyloc nuts with flange
    - ISO 12125 flanged nyloc nuts with fine pitch thread
    """
    dia = self.getDia(fa.calc_diam, True)
    if fa.baseType in ["ISO7043", "ISO12125"]:
        P, c, _, _, dc, _, _, h, _, m, _, s, _, _ = fa.dimTable
    else:
        raise NotImplementedError(f"Unknown fastener type: {fa.Type}")
    # main hexagonal body of the nut
    shape = self.makeHexPrism(s, h)

    # non-metallic insert representation
    fm = FSFaceMaker()
    fm.AddPoint(0.0, h - 0.5 * P)
    fm.AddPoint(1.05 * dia / 2, h - 0.5 * P)
    fm.AddPoint(1.05 * dia / 2, h)
    fm.AddPoint(0.95 * s / 2 - 0.5 * P, h)
    fm.AddArc2(0.0, -0.5 * P, -90)
    fm.AddPoint(0.95 * s / 2, m)
    fm.AddPoint(0.95 * s / 2 + m, 0.0)
    fm.AddPoint(0.0, 0.0)
    common = self.RevolveZ(fm.GetFace())
    shape = shape.common(common)

    # flange of the hex
    fm.Reset()
    fm.AddPoint((1.05 * dia + s) / 4, 0.0)
    fm.AddPoint((dc + math.sqrt(3) * c) / 2, 0.0)
    fm.AddPoint((dc - c) / 2, 0.0)
    fm.AddArc2(0, c / 2, 150)
    fm.AddPoint(
        (1.05 * dia + s) / 4,
        math.sqrt(3)
        / 3
        * ((dc - c) / 2 + c / (4 - 2 * math.sqrt(3)) - (1.05 * dia + s) / 4),
    )
    flange = self.RevolveZ(fm.GetFace())
    shape = shape.fuse(flange).removeSplitter()

    # internal bore
    fm.Reset()
    id = self.GetInnerThreadMinDiameter(dia, P, 0.0)
    bore_cham_ht = (dia * 1.05 - id) / 2 * math.tan(math.radians(15))
    fm.AddPoint(0.0, 0.0)
    fm.AddPoint(dia * 1.05 / 2, 0.0)
    fm.AddPoint(id / 2, bore_cham_ht)
    fm.AddPoint(id / 2, h)
    fm.AddPoint(0.0, h)
    bore_cutter = self.RevolveZ(fm.GetFace())
    shape = shape.cut(bore_cutter)

    # add modelled threads if needed
    if fa.Thread:
        thread_cutter = self.CreateInnerThreadCutter(dia, P, h + P)
        shape = shape.cut(thread_cutter)
    return shape
