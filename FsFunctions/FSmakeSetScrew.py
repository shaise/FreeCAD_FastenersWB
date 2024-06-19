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


def makeSetScrew(self, fa):
    """Creates a set screw or grub screw

    Supported types:
    - ISO 4026 Hexagon socket set screws with flat point
    - ISO 4027 Hexagon socket set screws with cone point
    - ISO 4028 Hexagon socket set screws with dog point
    - ISO 4029 Hexagon socket set screws with cup point
    - ISO 4766 Slotted set screws with flat point
    - ISO 7434 Slotted set screws with cone point
    - ISO 7435 Slotted set screws with long dog point
    - ISO 7436 Slotted set screws with cup point
    - ASMEB18.3.5A UNC Hexagon socket set screws with flat point
    - ASMEB18.3.5B UNC Hexagon socket set screws with cone point
    - ASMEB18.3.5C UNC Hexagon socket set screws with dog point
    - ASMEB18.3.5D UNC Hexagon socket set screws with cup point
    """
    SType = fa.baseType
    length = fa.calc_len
    dia = self.getDia(fa.calc_diam, False)
    if SType in ['ISO4026', 'ISO4027', 'ISO4029']:
        P, t, dp, dt, df, s = fa.dimTable
    elif SType == 'ISO4028':
        P, dp, _, _, s, _, _, td, te, zd, _, ze, _ = fa.dimTable
        df = self.getDia1(dia, P)
        # NOTE: In the norm 't' and 'z' depend on d/e
        # d: For screws with nominal lengths in the shaded areas.
        # e: For screws with nominal lengths below the shaded areas.
        shaded_areas = {
            "M1.6": {2.0, 2.5},
            "M2": {2.5, 3.0},
            "M2.5": {3.0, 4.0},
            "M3": {4.0, 5.0},
            "M4": {5.0, 6.0},
            "M5": {6.0},
            "M6": {8.0},
            "M8": {8.0, 10.0},
            "M10": {10.0, 12.0},
            "M12": {12.0, 16.0},
            "M16": {16.0, 20.0},
            "M20": {20.0, 25.0},
            "M24": {25.0, 30.0}
        }
        if length in shaded_areas.get(fa.calc_diam, set()):
            # short dog point
            t = td
            z = zd
        else:
            # long dog point
            t = te
            z = ze
    elif SType == 'ISO4766' or SType[:5] == 'ISO74':
        P = FsData["ISO262def"][fa.Diameter][0] # coarse pitch
        df = self.getDia1(dia, P)
        if SType == 'ISO7434':
            dt, _, n, _, t, _ = fa.dimTable
        elif SType == 'ISO7435':
            dp, _, _, n, _, t, _, z, _ = fa.dimTable
        elif SType == 'ISO7436':
            dz, _, _, n, _, t, _ = fa.dimTable
        else:
            dp, _, _, _, n, t, _ = fa.dimTable
    elif SType[:-1] == 'ASMEB18.3.5':
        P, t, dp, dt, df, s, z = fa.dimTable

    # Revolve face
    if SType in ['ISO4026', 'ISO4766', 'ASMEB18.3.5A']:
        screw = self.RevolveZ(makeFlatConeFace(dia, length, df, dp))
    elif SType in ['ISO4027', 'ISO7434', 'ASMEB18.3.5B']:
        screw = self.RevolveZ(makeFlatConeFace(dia, length, df, dt))
    elif SType in ['ISO4028', 'ISO7435', 'ASMEB18.3.5C']:
        screw = self.RevolveZ(makeDogFace(dia, length, df, dp, z))
    elif SType in ['ISO4029', 'ASMEB18.3.5D']:
        screw = self.RevolveZ(makeCupFace(dia, length, df, dp))
    elif SType == 'ISO7436':
        screw = self.RevolveZ(makeCupFace(dia, length, df, dz))

    # Make recess
    if SType == 'ISO4766' or SType[:5] == 'ISO74':
        recess = self.makeSlotRecess(n, t, dia)
    else:
        recess = self.makeHexRecess(s, t - 1, True)
    screw = screw.cut(recess)

    # produce a modelled thread if necessary
    if fa.Thread:
        thread_cutter = self.CreateThreadCutter(dia, P, length)
        screw = screw.cut(thread_cutter)

    return screw

def makeFlatConeFace(dia, length, df, dpt):
    """ Make the face for a set screw with flat or cone point """
    # These 2 types share geometry
    fm = FSFaceMaker()
    fm.AddPoint(0, 0)
    fm.AddPoint(df / 2, 0)
    fm.AddPoint(dia / 2, -1 * ((dia - df) / 2))
    fm.AddPoint(dia / 2, -1 * length + ((dia - dpt) / 2))
    fm.AddPoint(dpt / 2, -1 * length)
    fm.AddPoint(0, -1 * length)

    return fm.GetFace()

def makeDogFace(dia, length, df, dp, z):
    """ Make the face for a set screw with dog point """
    fm = FSFaceMaker()
    fm.AddPoint(0, 0)
    fm.AddPoint(df / 2, 0)
    fm.AddPoint(dia / 2, -1 * ((dia - df) / 2))
    fm.AddPoint(dia / 2, -1 * length + ((dia - dp) / 2 + z))
    fm.AddPoint(dp / 2, -1 * length + z)
    fm.AddPoint(dp / 2, -1 * length)
    fm.AddPoint(0, -1 * length)

    return fm.GetFace()

def makeCupFace(dia, length, df, dz, angle=120):
    """ Make the face for a set screw with cup point """
    fm = FSFaceMaker()
    fm.AddPoint(0, 0)
    fm.AddPoint(df / 2, 0)
    fm.AddPoint(dia / 2, -1 * ((dia - df) / 2))
    fm.AddPoint(dia / 2, -1 * length + ((dia - dz) / 2))
    fm.AddPoint(dz / 2, -1 * length)
    fm.AddPoint(0, -1 * length + dz / (2 * math.tan(math.radians(angle / 2))))

    return fm.GetFace()
