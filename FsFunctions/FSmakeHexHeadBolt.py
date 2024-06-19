# -*- coding: utf-8 -*-
"""
***************************************************************************
*   Copyright (c) 2013, 2014, 2015                                        *
*   Original code by:                                                     *
*   Ulrich Brammer <ulrich1a[at]users.sourceforge.net>                    *
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


def makeHexHeadBolt(self, fa):
    """Creates a bolt with a hexagonal head

    supported types:
    - DIN 933 hex head screws
    - DIN 961 hex head screws with fine thread
    - ISO 4014 Hex head bolts
    - ISO 4016 hex head bolts, grade c
    - ISO 4017 Hex head screws
    - ISO 4018 hex head screws, grade c
    - ISO 8676 hex head screws with fine thread
    - ISO 8765 hex head bolts with fine thread
    - ASMEB18.2.1.6 hex head bolts
    """
    dia = self.getDia(fa.calc_diam, False)
    length = fa.calc_len

    if fa.baseType == "DIN933" or fa.baseType == "DIN961":
        P, c, dw, e, k, r, s = fa.dimTable
        b = length
    elif fa.baseType == "ISO4017" or fa.baseType == "ISO8676":
        P, c, dw, e, k, r, s = fa.dimTable
        b = length
    elif fa.baseType == "ISO8765":
        P, b1, b2, b3, c = fa.dimTable[:5]
        dw = fa.dimTable[11]
        e = fa.dimTable[13]
        k = fa.dimTable[15]
        r = fa.dimTable[22]
        s = fa.dimTable[23]

    elif fa.baseType == "ISO4018":
        P, _, _, c, _, dw, e, k, _, _, _, r, s, _ = fa.dimTable
        b = length
    elif fa.baseType == "ISO4014":
        P, b1, b2, b3, c, dw, e, k, r, s = fa.dimTable
    elif fa.baseType == "ISO4016":
        P, b1, b2, b3, c, _, _, _, dw, e, k, _, _, _, r, s, _ = fa.dimTable
    elif fa.baseType == "ASMEB18.2.1.6":
        b, P, c, dw, e, k, r, s = fa.dimTable
        if length > 6 * 25.4:
            b += 6.35
    else:
        raise NotImplementedError(f"Unknown fastener type: {fa.Type}")
    if fa.baseType in ["ISO4014", "ISO4016", "ISO8765"]:
        if length <= 125.0:
            b = b1
        else:
            if length <= 200.0:
                b = b2
            else:
                b = b3

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
    fm.AddPoint(dia / 2.0 + r, 0.0)
    fm.AddArc2(0.0, -r, 90)
    if length - r > b:  # partially threaded fastener
        thread_length = b
        if not fa.Thread:
            fm.AddPoint(dia / 2, -1 * (length - b))
    else:
        thread_length = length - r
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
