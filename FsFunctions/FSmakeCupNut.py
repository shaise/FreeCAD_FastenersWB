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
import FastenerBase


def makeCupNut(self, fa):
    """Creates a blind-threaded cap nut
    Supported types:
    - DIN1587 cap nut
    - GOST11860-1 cap (or 'acorn') nut
    - SAE J483a cap nuts, both low and high styles
    """
    SType = fa.baseType
    dia = self.getDia(fa.calc_diam, True)
    if SType == "DIN1587" or SType == "GOST11860-1":
        P, d_k, h, m, s, t, w = fa.dimTable
    elif SType == "SAEJ483a1" or SType == "SAEJ483a2":
        TPI, F, A, H, Q, U = fa.dimTable
        P = 1 / TPI * 25.4
        s = F * 25.4
        d_k = A * 25.4
        m = Q * 25.4
        t = U * 25.4
        h = H * 25.4
        w = h - t - dia / 2 / math.tan(math.radians(60))
    else:
        raise RuntimeError("unknown screw type")
    # create the profile of the nut in the x-z plane
    sq3 = math.sqrt(3)
    ec = (2 - sq3) * s / 6
    fm = FastenerBase.FSFaceMaker()
    fm.AddPoint(0, 1.1 * dia / 4)
    fm.AddPoint(1.1 * dia / 2, 0)
    fm.AddPoint(s / 2, 0)
    fm.AddPoint(s * sq3 / 3, ec)
    fm.AddPoint(s * sq3 / 3, m - ec)
    fm.AddPoint(d_k / 2, (m - ec) + (2 * s - sq3 * d_k) / 6)
    fm.AddPoint(d_k / 2, h - d_k / 2)
    fm.AddArc(
        d_k / 2 * math.sqrt(2) / 2, h - d_k / 2 + d_k /
        2 * math.sqrt(2) / 2, 0, h
    )
    solid = self.RevolveZ(fm.GetFace())
    # create an additional solid to cut the hex flats with
    solidHex = self.makeHexPrism(s, h * 1.1)
    solid = solid.common(solidHex)
    # cut the threads
    if fa.Thread:
        tap_tool = self.CreateBlindInnerThreadCutter(dia, P, h - w)
        fm.Reset()
        fm.AddPoint(0, h - w),
        fm.AddPoint(1.1 * dia / 2, t),
        fm.AddPoint(1.1 * dia / 2, h),
        fm.AddPoint(0, h)
        thread_chamfer = self.RevolveZ(fm.GetFace())
        tap_tool = tap_tool.cut(thread_chamfer)
        solid = solid.cut(tap_tool)
    # if real threads are not needed, cut a drilled hole at
    # the minor diameter of the threads
    else:
        fm.Reset()
        fm.AddPoint(0, 0),
        fm.AddPoint(0, h - w)
        fm.AddPoint(dia / 2 - 0.625 * P * sq3 / 2, t)
        fm.AddPoint(dia / 2 - 0.625 * P * sq3 / 2, 0)
        hole = self.RevolveZ(fm.GetFace())
        solid = solid.cut(hole)
    return solid
