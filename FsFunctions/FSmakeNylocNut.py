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


tan30 = math.tan(math.radians(30.0))


def nylocMakeFace(do, p, da, dw, e, m, h, s):
    di = (do - p) / 2
    do = do / 2
    dw = dw / 2
    da = da / 2
    e = e / 2
    s = s / 2
    s1 = s * 0.999
    ch1 = do - di
    ch2 = (e - dw) * tan30
    ch3 = m - (e - s) * tan30
    h1 = h * 0.9
    r = (s - di) / 3

    fm = FastenerBase.FSFaceMaker()
    fm.AddPoints((di, ch1), (da, 0), (dw, 0), (e, ch2),
                 (e, ch3), (s1, m), (s1, h - r))
    fm.AddArc2(-r, 0, 90)
    fm.AddPoints((di + r, h), (di + r, h1), (di, h1))
    return fm.GetFace()


def makeNylocNut(self, fa):
    """Create a nut with a non-metallic locking insert
    Supported Types:
    - DIN 985 Nyloc nuts
    - ISO 7040 Nyloc nuts
    - ISO 7041 Nyloc nuts
    - ISO 10511 thin nyloc nuts
    - ISO 10512 fine thread nyloc nuts
    """
    if fa.baseType == "DIN985":
        P, da, dw, e, m, h, s = fa.dimTable
    elif fa.baseType in ["ISO7040", "ISO7041", "ISO10511", "ISO10512"]:
        P,da,_,dw,e,h,_,m,_,s,_ = fa.dimTable
    else:
        raise NotImplementedError(f"Unknown fastener type: {fa.Type}")
    dia = self.getDia(fa.calc_diam, True)
    section = nylocMakeFace(dia, P, da, dw, e, m, h, s)
    nutSolid = self.RevolveZ(section)
    htool = htool = self.makeHexPrism(s, m * 3)
    nutSolid = nutSolid.common(htool)
    if fa.Thread:
        threadCutter = self.CreateInnerThreadCutter(dia, P, h + P)
        nutSolid = nutSolid.cut(threadCutter)

    return nutSolid
