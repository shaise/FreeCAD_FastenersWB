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


def makePanHeadScrew(self, fa):
    """Create a pan-head screw with a rounded top and cylindrical sides

    Supported types:
    -ISO 7045 Pan head screws with type H or type Z cross recess
    - ISO 14583 Hexalobular socket pan head screws
    """
    SType = fa.baseType
    length = fa.calc_len
    dia = self.getDia(fa.calc_diam, False)
    if SType == "ISO7045":
        P, a, b, dk_max, da, k, r, rf, x, cT, mH, mZ = \
            FsData["ISO7045def"][fa.calc_diam]
        recess = self.makeHCrossRecess(cT, mH)
        # angle of recess edge
        beta_cr = math.asin(mH / 2.0 / rf)
        tan_beta_cr = math.tan(beta_cr)
        # height of cross recess cutting
        hcr = k - rf + (mH / 2.0) / tan_beta_cr
        recess.translate(Base.Vector(0.0, 0.0, hcr))
    elif SType == "ISO14583":
        P, a_max, b ,d_a_max, dk_max, k_torx, r, rf, \
            x_max, tt, t, A_ref = fa.dimTable
        k = rf - math.sqrt(rf ** 2 - A_ref ** 2 / 4) + k_torx
        recess = self.makeHexalobularRecess(tt, t, True)
        recess.translate(Base.Vector(0.0, 0.0, k_torx))
    elif SType == "ASMEB18.6.3.9A":
        P, A, H, R_head, J, T = fa.dimTable
        P, A, H, R_head, J, T = (25.4 * x for x in (P, A, H, R_head, J, T))
        dk_max = A
        k = H
        rf = dk_max  # To avoid error in evaluating alpha/beta (not actually needed)
        recess = self.makeSlotRecess(J, T, dk_max)
        recess.translate(Base.Vector(0.0, 0.0, k))
    elif SType == "ASMEB18.6.3.9B":
        P, A, H, R_head, mH, cT = fa.dimTable
        P, A, H, R_head, mH = (25.4 * x for x in (P, A, H, R_head, mH))
        # ASME doesn't clearly define head profile for anything other than slotted
        # Assume the head's top radius is 80% of head diameter (this closely matches vendor diagrams)
        dk_max = A
        k = H
        rf = dk_max * 0.8
        # Calculate the angle where the two curves intersect
        intersect_angle_rad = math.acos((A/2 - R_head) / (rf - R_head))  # This could likely be improved, but it works?
        intersect_angle_deg = math.degrees(intersect_angle_rad)
        recess = self.makeHCrossRecess(cT, mH)
        recess.translate(Base.Vector(0.0, 0.0, k))
    elif SType == "ASMEB18.6.3.10A":
        P, A, H, O, J, T = fa.dimTable
        P, A, H, O, J, T = (25.4 * x for x in (P, A, H, O, J, T))
        dk_max = A
        k = O
        rh = O - H
        rf = (4 * rh * rh + A * A) / (8 * rh)
        recess = self.makeSlotRecess(J, T, dk_max)
        recess.translate(Base.Vector(0.0, 0.0, k))
    elif SType == "ASMEB18.6.3.10B":
        P, A, H, O, _, _ = fa.dimTable
        mH, cT = FsData["ASMEB18.6.3.10Bextra"][fa.calc_diam]
        P, A, H, O, mH = (25.4 * x for x in (P, A, H, O, mH))
        dk_max = A
        k = O
        rh = O - H
        rf = (4 * rh * rh + A * A) / (8 * rh)
        recess = self.makeHCrossRecess(cT, mH)
        recess.translate(Base.Vector(0.0, 0.0, k))
    elif SType == "ASMEB18.6.3.12A":
        P, A, H, rf, J, T = fa.dimTable
        P, A, H, rf, J, T = (25.4 * x for x in (P, A, H, rf, J, T))
        dk_max = A
        k = H
        recess = self.makeSlotRecess(J, T, dk_max)
        recess.translate(Base.Vector(0.0, 0.0, k))
    elif SType == "ASMEB18.6.3.12C":
        P, A, H, rf, _, _ = fa.dimTable
        mH, cT = FsData["ASMEB18.6.3.12Cextra"][fa.calc_diam]
        P, A, H, rf, mH = (25.4 * x for x in (P, A, H, rf, mH))
        dk_max = A
        k = H
        recess = self.makeHCrossRecess(cT, mH)
        recess.translate(Base.Vector(0.0, 0.0, k))
        
    if SType.split("B18.6.3")[0] == "ASME":
        r = 0.25   # Not specified in ASME, assume 0.25mm
        b = 1.5*25.4    # Assume maximum threaded length of 1.5" per paragraph 2.4.1(b)
        
    beta = math.asin(dk_max / 2.0 / rf)  # angle of head edge
    tan_beta = math.tan(beta)
    alpha = beta / 2.0  # half angle
    # height of head edge
    he = k - rf + (dk_max / 2.0) / tan_beta
    h_arc_x = rf * math.sin(alpha)
    h_arc_z = k - rf + rf * math.cos(alpha)
    
    # lay out the fastener profile
    fm = FastenerBase.FSFaceMaker()
    fm.AddPoint(0.0, k)
    
    if SType == "ASMEB18.6.3.9A":
        fm.AddPoint(dk_max/2 - R_head, k)
        fm.AddArc2(0, -R_head, -90)
    elif SType == "ASMEB18.6.3.9B":
        fm.AddArc2(0.0, -rf, intersect_angle_deg - 90)
        fm.AddArc2(-R_head*math.cos(intersect_angle_rad), -R_head*math.sin(intersect_angle_rad), -intersect_angle_deg)
    elif SType == "ASMEB18.6.3.10A" or "ASMEB18.6.3.10B" or "ASME.B18.6.3.12A" or "ASME.B18.6.3.12C":
        fm.AddArc2(0.0, -rf, -math.degrees(beta))
    else:
        fm.AddArc(h_arc_x, h_arc_z, dk_max / 2.0, he)
        
    fm.AddPoint(dk_max / 2.0, 0.0)
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
    shape = self.RevolveZ(fm.GetFace())
    shape = shape.cut(recess)
    
    if fa.Thread:
        thread_cutter = self.CreateBlindThreadCutter(dia, P, thread_length)
        thread_cutter.translate(Base.Vector(0.0, 0.0, -1 * (length - thread_length)))
        shape = shape.cut(thread_cutter)
        
    return shape
