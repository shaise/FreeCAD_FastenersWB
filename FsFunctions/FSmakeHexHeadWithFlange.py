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


def makeHexHeadWithFlange(self, fa):
    """Create a fastener with a flanged hexagonal head

    supported types:
    - ISO 4162 hexagon bolts with flange
    - ISO 15071 hexagon bolts with flange
    - ISO 15072 flanged hex head bolts with fine threads
    - EN 1662 Hex-head-bolt with flange - small series
    - EN 1665 Hexagon bolts with flange, heavy series
    - ASMEB18.2.1.8 Hexagon bolts with flange, heavy series
    """
    dia = self.getDia(fa.calc_diam, False)
    SType = fa.baseType
    length = fa.calc_len
    if SType == "EN1662" or SType == "EN1665":
        P, b0, b1, b2, b3, c, dc, dw, e, k, kw, f, r1, s = fa.dimTable
    elif SType == "ASMEB18.2.1.8":
        b0, P, c, dc, kw, r1, s = fa.dimTable
        b = b0
    elif SType == "ISO4162" or SType == "ISO15071":
        P, b0, b1, b2, b3, c = fa.dimTable[:6]
        dc = fa.dimTable[8]
        kw = fa.dimTable[15]
        r1 = fa.dimTable[17]
        s = fa.dimTable[22]
    elif SType == "ISO15072":
        P = fa.dimTable[0]
        b0, b1, b2, b3, c = fa.dimTable[3:8]
        dc = fa.dimTable[10]
        kw = fa.dimTable[17]
        r1 = fa.dimTable[19]
        s = fa.dimTable[24]
    else:
        raise NotImplementedError(f"Unknown fastener type: {fa.Type}")
    if length < b0:
        b = length - r1
    elif SType != "ASMEB18.2.1.8":
        if length <= 125.0:
            b = b1
        elif length <= 200.0:
            b = b2
        else:
            b = b3
    # needed for chamfer at head top
    cham = s * (2.0 / math.sqrt(3.0) - 1.0) * math.sin(math.radians(25))
    sqrt2_ = 1.0 / math.sqrt(2.0)
    # Flange is made with a radius of c
    beta = math.radians(25.0)
    tan_beta = math.tan(beta)
    # Calculation of Arc points of flange edge using dc and c
    arc1_x = dc / 2.0 - c / 2.0 + (c / 2.0) * math.sin(beta)
    arc1_z = c / 2.0 + (c / 2.0) * math.cos(beta)
    kmean = arc1_z + (arc1_x - s / math.sqrt(3.0)) * tan_beta + kw * 1.1 + cham
    # lay out the fastener profile
    fm = FSFaceMaker()
    fm.AddPoint(0.0, kmean * 0.9)
    fm.AddPoint(s / 2.0 * 0.8 - r1 / 2.0, kmean * 0.9)
    fm.AddArc(
        s / 2.0 * 0.8 - r1 / 2.0 + r1 / 2.0 * sqrt2_,
        kmean * 0.9 + r1 / 2.0 - r1 / 2.0 * sqrt2_,
        s / 2.0 * 0.8,
        kmean * 0.9 + r1 / 2.0,
    )
    fm.AddPoint(s / 2.0 * 0.8, kmean - r1)
    fm.AddArc(
        s / 2.0 * 0.8 + r1 - r1 * sqrt2_,
        kmean - r1 + r1 * sqrt2_,
        s / 2.0 * 0.8 + r1,
        kmean,
    )
    fm.AddPoint(s / 2.0, kmean)
    fm.AddPoint(s / 2 + (kmean - 0.1) * math.sqrt(3), 1.0)
    fm.AddPoint(0.0, 0.1)
    head = self.RevolveZ(fm.GetFace())
    # cut the hexagon flats with a boolean operation
    hextool = self.makeHexPrism(s, kmean)
    head = head.common(hextool)
    # add the flange and shaft of the fastener
    fm.Reset()
    fm.AddPoint(0.0, -length)
    fm.AddPoint(dia * 4 / 10, -length)
    fm.AddPoint(dia / 2, -length + dia / 10)
    if length - r1 > b:  # partially threaded fastener
        thread_length = b
        if not fa.Thread:
            fm.AddPoint(dia / 2, -1 * (length - b))
    else:
        thread_length = length - r1
    fm.AddPoint(dia / 2, -r1)
    fm.AddArc2(r1, 0.0, -90)
    fm.AddPoint((dc - c) / 2, 0.0)
    fm.AddArc2(0, c / 2, 180 - math.degrees(beta))
    flange_top_ht = math.tan(beta) * (
        (dc - c) / 2 - s * 0.4 + c / 2 / math.tan(beta / 2)
    )
    fm.AddPoint(s * 0.4, flange_top_ht)
    fm.AddPoint(0.0, flange_top_ht)
    face = fm.GetFace()
    flange = self.RevolveZ(face)
    shape = head.fuse(flange)
    if fa.Thread:
        thread_cutter = self.CreateBlindThreadCutter(dia, P, thread_length)
        thread_cutter.translate(Base.Vector(0.0, 0.0, -1 * (length - thread_length)))
        shape = shape.cut(thread_cutter)
    return shape
