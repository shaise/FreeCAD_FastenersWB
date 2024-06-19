# -*- coding: utf-8 -*-
"""
***************************************************************************
*   Copyright (c) 2022                                                    *
*   Shai Seger <shaise[at]gmail>                                          *
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
import FastenerBase

tan30 = math.tan(math.radians(30))

# PEM Self Clinching standoffs types: SO/SOS/SOA/SO4


def soMakeFace(b, c, h, d, l1, bl, isBlind):
    h10 = h / 10.0
    h102 = h10 + h10 / 2
    c12 = c / 12.5
    c20 = c / 20.0
    c40 = c / 40.0
    b = b / 2
    c = c / 2
    d = d / 2
    ch1 = b - d
    ch2 = d * tan30
    l2 = l1 - bl
    c1 = c - c40
    c2 = c - c20
    l3 = h10 * 2 + (c12 + c20) * 2

    fm = FastenerBase.FSFaceMaker()
    if isBlind:
        fm.AddPoints(
            (0, 0),
            (0, -h102),
            (d, -(h102 + ch2)),
            (d, -(l1 - ch1)),
            (b, -l1)
        )
    else:
        fm.AddPoints((b, 0), (d, -ch1), (d, -(l2 - ch1)), (b, -l2))
        if (l1 - l2) > 0.01:
            fm.AddPoint(b, -l1)
    fm.AddPoint(c, -l1)
    if l3 < l1:
        fm.AddPoints((c, -l3), (c1, -l3), (c1, -(l3 - c20)), (c, -(l3 - c20)))
    fm.AddPoints(
        (c, -(h10 * 2 + c12 + c20)),
        (c1, -(h10 * 2 + c12 + c20)),
        (c1, -(h10 * 2 + c12)),
        (c, -(h10 * 2 + c12)),
        (c, -h10 * 2),
        (c2, -h10 * 2),
        (c2, -h10),
        (h * 0.6, -h10),
        (h * 0.6, 0),
    )
    return fm.GetFace()


def makePEMStandoff(self, fa):
    l = fa.calc_len
    plen = fa.Length
    _, c, h, _, lmin, lmax = fa.dimTable
    # there is an additional M3 size available for this fastener type,
    # designated by "3.5M3".
    # We must account for the fact that this size is not available in
    # thread data tables
    if fa.Diameter.startswith("3.5"):
        dia_key = "M3"
    else:
        dia_key = fa.Diameter
    dia = self.getDia(dia_key, True)
    b = dia * 1.05
    P = FsData["ISO262def"][dia_key][0]
    d = self.GetInnerThreadMinDiameter(dia, P)
    if fa.Blind and l < 6:
        l = 6
        plen = "6"

    bl = FsData[fa.baseType + "length"][plen][0]
    f = soMakeFace(b, c, h, d, l, bl, fa.Blind)
    p = self.RevolveZ(f)
    htool = self.makeHexPrism(h, l * 1.1)
    htool.translate(Base.Vector(0.0, 0.0, -1.05 * l))
    fSolid = p.common(htool)
    if fa.Thread:
        thread_cutter = self.CreateInnerThreadCutter(dia, P, l * 1.25)
        thread_cutter.rotate(
            Base.Vector(0.0, 0.0, 0.0), Base.Vector(1.0, 0.0, 0.0), 180.0
        )
        if fa.Blind:
            thread_cutter.translate(Base.Vector(0.0, 0.0, -d))
        fSolid = fSolid.cut(thread_cutter)
    return fSolid
