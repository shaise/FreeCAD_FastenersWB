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

def makeRoundHeadScrew(self, fa):
    """Create a screw with a round head
    
    Supported types:
    - ASMEB18.6.3 UNC round head screws
    """
    SType = fa.baseType
    length = fa.calc_len
    dia = self.getDia(fa.calc_diam, False)
    half_dia = dia / 2.0

    # Screw specific imports and calculations:
    if SType == "ASMEB18.6.3.16A":
        P, A, H, J, T = fa.dimTable
        A, H, J, T = (25.4 * x for x in (A, H, J, T))
        recess = self.makeSlotRecess(J, T, A)
        recess.translate(Base.Vector(0.0, 0.0, H))
        b = 1.5 * 25.4    # Assume maximum threaded length of 1.5" per paragraph 2.4.1(b)
    elif SType == "ASMEB18.6.3.16B":
        P, A, H, _, _ = fa.dimTable
        mH, cT = FsData["ASMEB18.6.3.16Bextra"][fa.calc_diam]
        A, H, mH = (25.4 * x for x in (A, H, mH))
        recess = self.makeHCrossRecess(cT, mH)
        recess.translate(Base.Vector(0.0, 0.0, H))
        b = 1.5 * 25.4    # Assume maximum threaded length of 1.5" per paragraph 2.4.1(b)
    
    # Calculate head curve radius (r) and height (zm) on curve at 1/4 head diameter
    r = (4 * H * H + A * A) / (8 * H)
    zm = math.sqrt(1 - A * A / (16 * r * r)) * r - (r - H)
    
    # partially threaded fastener
    if length > b:  
        thread_length = b
    else:
        thread_length = length

    # Create a profile for head
    fm = FastenerBase.FSFaceMaker()
    fm.AddPoints(
        (0, H),
        (A / 4, zm, A / 2, 0),
        (half_dia, 0),
        (half_dia, -length),
        (0, -length))

    profile = fm.GetFace()   
    screw = self.RevolveZ(fm.GetFace())
    screw = screw.cut(recess)

    # Add modeled threads if needed
    if fa.Thread:
        thread_cutter = self.CreateBlindThreadCutter(dia, P, length)
        thread_cutter.translate(Base.Vector(0.0, 0.0, -1 * (length - thread_length)))
        screw = screw.cut(thread_cutter)
    return screw
