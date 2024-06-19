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



def makeCheeseHeadScrew(self, fa):
    """Create a cheese head screw

    supported types:
    - ISO 1207 slotted screw
    - ISO 7048 cross recessed screw
    - ISO 14580 Hexalobular socket cheese head screws
    """
    SType = fa.baseType
    length = fa.calc_len
    dia = self.getDia(fa.calc_diam, False)
    if SType == "ISO1207" or SType == "DIN84":
        P, a, b, dk, dk_mean, da, k, n_min, r, t_min, x = fa.dimTable
        r_fil = r * 2.0
        recess = self.makeSlotRecess(n_min, t_min, dk)
    elif SType == "ISO7048":
        P, a, b, dk, dk_mean, da, k, r, x, cT, mH, mZ = fa.dimTable
        r_fil = r * 2.0
        recess = self.makeHCrossRecess(cT, mH)
    elif SType == "ISO1580":
        P, a, b, dk, da, k, n_min, r, rf, t_min, x = fa.dimTable
        r_fil = rf
        recess = self.makeSlotRecess(n_min, t_min, dk)
    elif SType == "ISO14580":
        P, a, b, dk, dk_mean, da, k, n_min, r, t_min, x = fa.dimTable
        tt, k, A, t_min = FsData["ISO14580extra"][fa.calc_diam]
        r_fil = r * 2.0
        recess = self.makeHexalobularRecess(tt, t_min, True)
    head_taper_angle = math.radians(5)
    # lay out the fastener profile
    fm = FSFaceMaker()
    fm.AddPoint(0.0, k)
    fm.AddPoint(
        dk / 2
        - k * math.tan(head_taper_angle)
        - r_fil * math.tan((math.pi / 2 - head_taper_angle) / 2),
        k,
    )
    fm.AddArc2(0.0, -r_fil, -90 + math.degrees(head_taper_angle))
    fm.AddPoint(dk / 2, 0.0)
    fm.AddPoint(dia / 2 + r, 0.0)
    fm.AddArc2(0.0, -r, 90)
    if length - r > b:  # partially threaded fastener
        thread_length = b
        if not fa.Thread:
            fm.AddPoint(dia / 2, -1 * (length - b))
    else:
        thread_length = length - r
    fm.AddPoint(dia / 2, -length)
    fm.AddPoint(0.0, -length)
    screw = self.RevolveZ(fm.GetFace())
    # cut the driving feature, then add modelled threads if needed
    recess.translate(Base.Vector(0.0, 0.0, k))
    screw = screw.cut(recess)
    if fa.Thread:
        thread_cutter = self.CreateBlindThreadCutter(dia, P, thread_length)
        thread_cutter.translate(Base.Vector(
            0.0, 0.0, -1 * (length - thread_length))
        )
        screw = screw.cut(thread_cutter)
    return screw
