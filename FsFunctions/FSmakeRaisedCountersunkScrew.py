# -*- coding: utf-8 -*-
"""
***************************************************************************
*   Copyright (c) 2022                                                    *
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


def makeRaisedCountersunkScrew(self, fa):
    """creates a countersunk (or 'flat-head') screw
    The top of the screw is rounded.
    supported types:
    - ISO 2010 Slotted raised countersunk head screws
    - ISO 7047 raised countersunk head screws with H cross recess
    - ISO 14584 raised countersunk head screws with hexalobular recess
    """
    SType = fa.baseType
    length = fa.calc_len
    dia = self.getDia(fa.calc_diam, False)
    if SType == "ISO2010":
        csk_angle = math.radians(90)
        P, _, b, dk_theo, dk_mean, _, n_min, r, t_mean, _ = fa.dimTable
        rf, t_mean, cT, mH, _ = FsData["Raised_countersunk_def"][fa.calc_diam]
        # Lengths and angles for calculation of head rounding
        head_arc_angle = math.asin(dk_mean / 2.0 / rf)  # angle of head edge
        # height of raised head top
        ht = rf - (dk_mean / 2.0) / math.tan(head_arc_angle)
        recess = self.makeSlotRecess(n_min, t_mean, dk_theo)
        recess.translate(Base.Vector(0.0, 0.0, ht))
    elif SType == "ISO7047":
        csk_angle = math.radians(90)
        P, _, b, dk_theo, dk_mean, _, n_min, r, t_mean, _ = fa.dimTable
        rf, t_mean, cT, mH, _ = FsData["Raised_countersunk_def"][fa.calc_diam]
        head_arc_angle = math.asin(dk_mean / 2.0 / rf)
        ht = rf - (dk_mean / 2.0) / math.tan(head_arc_angle)
        recess = self.makeHCrossRecess(cT, mH)
        recess.translate(Base.Vector(0.0, 0.0, ht))
    elif SType == "ISO14584":
        csk_angle = math.radians(90)
        P, b, dk_theo, dk_mean, f, _, r, rf, _, tt, A, t_mean = fa.dimTable
        head_arc_angle = math.asin(dk_mean / 2.0 / rf)
        ht = rf - math.sqrt(rf**2 - A**2 / 4) + f
        recess = self.makeHexalobularRecess(tt, t_mean, True)
        recess.translate(Base.Vector(0.0, 0.0, f))
    elif SType == "ASMEB18.6.3.4A":
        csk_angle = math.radians(82)
        P, dk_theo, dk_mean, _, f, n_min, t_mean = fa.dimTable
        # Lengths and angles for calculation of head rounding
        r = 0.25  # ASME doesn't spec a radius, so just assume 0.25mm
        b = 25.4  # ASME doesn't spec, so just assume 1"
        # Calculate head radius (rf)
        rf = (4 * f * f + dk_theo * dk_theo) / (8 * f)
        head_arc_angle = math.asin(dk_mean / 2.0 / rf)  # angle of head edge
        # height of raised head top
        ht = rf - (dk_mean / 2.0) / math.tan(head_arc_angle)
        recess = self.makeSlotRecess(n_min, t_mean, dk_theo)
        recess.translate(Base.Vector(0.0, 0.0, ht))
    elif SType == 'ASMEB18.6.3.4B':
        csk_angle = math.radians(82)
        P, dk_theo, dk_mean, _, f, _, _ = fa.dimTable
        # Lengths and angles for calculation of head rounding
        r = 0.25    #ASME doesn't spec a radius, so just assume 0.25mm
        b = 25.4    #ASME doesn't spec, so just assume 1"
        #Calculate head radius (rf)
        rf = (4 * f * f + dk_theo * dk_theo) / (8 * f)
        head_arc_angle = math.asin(dk_mean / 2.0 / rf)  # angle of head edge
        # height of raised head top
        ht = rf - (dk_mean / 2.0) / math.tan(head_arc_angle)
        cT, mH = FsData["ASMEB18.6.3.4Bextra"][fa.calc_diam]
        recess = self.makeHCrossRecess(cT, mH * 25.4)
        recess.translate(Base.Vector(0.0, 0.0, ht))                               
    # lay out fastener profile
    head_flat_ht = (dk_theo - dk_mean) / 2 / math.tan(csk_angle / 2)
    sharp_corner_ht = -1 * (
        head_flat_ht + (dk_mean - dia) / (2 * math.tan(csk_angle / 2))
    )
    fillet_start_ht = sharp_corner_ht - r * math.tan(csk_angle / 4)
    fm = FSFaceMaker()
    fm.AddPoint(0.0, -length)
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
    fm.AddArc(
        rf * math.sin(head_arc_angle / 2),
        ht + rf * (math.cos(head_arc_angle / 2) - 1),
        0.0,
        ht,
    )
    shape = self.RevolveZ(fm.GetFace())
    shape = shape.cut(recess)
    if fa.Thread:
        thread_cutter = self.CreateBlindThreadCutter(dia, P, thread_length)
        thread_cutter.translate(Base.Vector(0.0, 0.0, -1 * (length - thread_length)))
        shape = shape.cut(thread_cutter)
    return shape
