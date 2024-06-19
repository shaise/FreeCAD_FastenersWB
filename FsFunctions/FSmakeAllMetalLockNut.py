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


def makeAllMetalLockNut(self, fa):
    """Creates a distorted thread lock nut
    Supported types:
    - ISO 7719 all metal lock nuts
    - ISO 7720 all metal lock nuts, style 2
    - ISO 10513 all metal lock nuts with fine pitch thread
    """
    dia = self.getDia(fa.calc_diam, True)
    if fa.baseType in ["ISO7719", "ISO7720", "ISO10513"]:
        P, _, _, _, _, h, _, m_w, s, _ = fa.dimTable
    else:
        raise NotImplementedError(f"Unknown fastener type: {fa.Type}")
    # main hexagonal body of the nut
    shape = self.makeHexPrism(s, h)

    # internal bore
    fm = FSFaceMaker()
    id = self.GetInnerThreadMinDiameter(dia, P, 0.0)
    bore_cham_ht = (dia * 1.05 - id) / 2 * math.tan(math.radians(15))
    fm.AddPoint(0.0, 0.0)
    fm.AddPoint(dia * 1.05 / 2, 0.0)
    fm.AddPoint(id / 2, bore_cham_ht)
    fm.AddPoint(id / 2, h - bore_cham_ht)
    fm.AddPoint(dia * 1.05 / 2, h)
    fm.AddPoint(0.0, h)
    bore_cutter = self.RevolveZ(fm.GetFace())
    shape = shape.cut(bore_cutter)
    # outer chamfer on the hex
    fm.Reset()
    fm.AddPoint((s / math.sqrt(3) + 1.05 * dia / 2) / 2, h)
    fm.AddPoint(s / math.sqrt(3), h)
    fm.AddPoint(s / math.sqrt(3), m_w)
    top_cham_cutter = self.RevolveZ(fm.GetFace())
    shape = shape.cut(top_cham_cutter)
    # bottom chamfer
    fm.Reset()
    fm.AddPoint(s / 2, 0.0)
    fm.AddPoint(s / math.sqrt(3), 0.0)
    cham_ht = s * (1 / math.sqrt(3) - 0.5) * math.tan(math.radians(22.5))
    fm.AddPoint(s / math.sqrt(3), cham_ht)
    top_cham_cutter = self.RevolveZ(fm.GetFace())
    shape = shape.cut(top_cham_cutter)
    # add modelled threads if needed
    if fa.Thread:
        thread_cutter = self.CreateInnerThreadCutter(dia, P, h + P)
        shape = shape.cut(thread_cutter)
    return shape
