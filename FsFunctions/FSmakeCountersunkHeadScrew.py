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
from FastenerBase import FSFaceMaker
import math


def makeCountersunkHeadScrew(self, fa):
    """creates a countersunk (or 'flat-head') screw

    supported types:
    - ISO 10642 Hexagon socket countersunk head screws
    - ASMEB18.3.2 UNC Hexagon socket countersunk head screws
    - ISO 2009 countersunk slotted flat head screws
    - ISO 7046 countersunk flat head screws with H cross recess
    - ISO 14581 Hexalobular socket countersunk head screws, flat head
    - ISO 14582 Hexalobular socket countersunk head screws, high head
    """
    SType = fa.baseType
    length = fa.calc_len
    dia = self.getDia(fa.calc_diam, False)
    if SType == "ISO10642":
        csk_angle = math.radians(90)
        P, b, dk_theo, dk_mean, _, _, _, _, r, s_mean, t, _ = fa.dimTable
        chamfer_end = True
        recess = self.makeHexRecess(s_mean, t, True)
    elif SType == "ASMEB18.3.2":
        csk_angle = math.radians(82)
        P, b, dk_theo, dk_mean, _, r, s_mean, t = fa.dimTable
        chamfer_end = True
        recess = self.makeHexRecess(s_mean, t, True)
    elif SType == "ISO2009":
        csk_angle = math.radians(90)
        P, _, b, dk_theo, dk_mean, _, n_min, r, t_mean, _ = fa.dimTable
        chamfer_end = False
        recess = self.makeSlotRecess(n_min, t_mean, dk_theo)
    elif SType == "ASMEB18.6.3.1A":
        csk_angle = math.radians(82)
        P, b, dk_theo, dk_mean, _, n_min, r, t_mean = fa.dimTable
        chamfer_end = False
        recess = self.makeSlotRecess(n_min, t_mean, dk_theo)
    elif SType == "ASMEB18.6.3.1B":
        csk_angle = math.radians(82)
        P, b, dk_theo, dk_mean, _, n_min, r, t_mean = fa.dimTable
        chamfer_end = False
        cT, mH = FsData["ASMEB18.6.3.1Bextra"][fa.calc_diam]
        recess = self.makeHCrossRecess(cT, mH * 25.4)
    elif SType == "ISO7046":
        csk_angle = math.radians(90)
        P, _, b, dk_theo, dk_mean, _, n_min, r, t_mean, _ = fa.dimTable
        chamfer_end = False
        cT, mH, _ = FsData["ISO7046extra"][fa.calc_diam]
        recess = self.makeHCrossRecess(cT, mH)
    elif SType == "ISO14581":
        csk_angle = math.radians(90)
        P, a, b, dk_theo, dk_mean, k, r, tt, A, t_mean = fa.dimTable
        chamfer_end = True
        recess = self.makeHexalobularRecess(tt, t_mean, False)
    elif SType == "ISO14582":
        csk_angle = math.radians(90)
        P, _, b, dk_theo, dk_mean, _, r, tt, _, t_mean = fa.dimTable
        chamfer_end = True
        recess = self.makeHexalobularRecess(tt, t_mean, False)
    # lay out fastener profile
    head_flat_ht = (dk_theo - dk_mean) / 2 / math.tan(csk_angle / 2)
    sharp_corner_ht = -1 * (
        head_flat_ht + (dk_mean - dia) / (2 * math.tan(csk_angle / 2))
    )
    fillet_start_ht = sharp_corner_ht - r * math.tan(csk_angle / 4)
    fm = FSFaceMaker()
    fm.AddPoint(0.0, -length)
    if chamfer_end:
        fm.AddPoint(dia * 4 / 10, -length)
        fm.AddPoint(dia / 2, -length + dia / 10)
    else:
        fm.AddPoint(dia / 2, -length)
    if length + fillet_start_ht > b:  # partially threaded fastener
        thread_length = b
        if not fa.Thread:
            fm.AddPoint(dia / 2, -length + thread_length)
    else:
        thread_length = length + fillet_start_ht
    fm.AddPoint(dia / 2, fillet_start_ht)
    fm.AddArc2(r, 0.0, -math.degrees(csk_angle / 2))
    fm.AddPoint(dk_mean / 2, -head_flat_ht)
    fm.AddPoint(dk_mean / 2, 0.0)
    fm.AddPoint(0.0, 0.0)
    shape = self.RevolveZ(fm.GetFace())
    shape = shape.cut(recess)
    if fa.Thread:
        thread_cutter = self.CreateBlindThreadCutter(dia, P, thread_length)
        thread_cutter.translate(Base.Vector(0.0, 0.0, -1 * (length - thread_length)))
        shape = shape.cut(thread_cutter)
    return shape
