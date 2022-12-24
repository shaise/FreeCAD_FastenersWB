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
    - ASMEB18.3.5A UNC Hexagon socket set screws with flat point
    - ASMEB18.3.5B UNC Hexagon socket set screws with cone point
    - ASMEB18.3.5C UNC Hexagon socket set screws with dog point
    - ASMEB18.3.5D UNC Hexagon socket set screws with cup point
    """
    SType = fa.type
    length = fa.calc_len
    if SType == 'ISO4026' or SType == 'ISO4027' or SType == 'ISO4029':
        P, t, dp, dt, df, s = fa.dimTable
    elif SType == 'ISO4028':
        P, t, dp, df, z, s = fa.dimTable
    elif SType[:-1] == 'ASMEB18.3.5':
        P, t, dp, dt, df, s, z = fa.dimTable
    dia = self.getDia(fa.calc_diam, False)
    # generate the profile of the set-screw
    fm = FSFaceMaker()
    if SType == 'ISO4026' or SType == 'ASMEB18.3.5A':
        fm.AddPoint(0, 0)
        fm.AddPoint(df / 2, 0)
        fm.AddPoint(dia / 2, -1 * ((dia - df) / 2))
        fm.AddPoint(dia / 2, -1 * length + ((dia - dp) / 2))
        fm.AddPoint(dp / 2, -1 * length)
        fm.AddPoint(0, -1 * length)
    elif SType == 'ISO4027' or SType == 'ASMEB18.3.5B':
        fm.AddPoint(0, 0)
        fm.AddPoint(df / 2, 0)
        fm.AddPoint(dia / 2, -1 * ((dia - df) / 2))
        fm.AddPoint(dia / 2, -1 * length + ((dia - dt) / 2))
        fm.AddPoint(dt / 2, -1 * length)
        fm.AddPoint(0, -1 * length)
    elif SType == 'ISO4028' or SType == 'ASMEB18.3.5C':
        # the shortest available dog-point set screws often have
        # shorter dog-points. There  is not much hard data accessible for this
        # approximate by halving the dog length for short screws
        if length < 1.5 * dia:
            z = z * 0.5
        fm.AddPoint(0, 0)
        fm.AddPoint(df / 2, 0)
        fm.AddPoint(dia / 2, -1 * ((dia - df) / 2))
        fm.AddPoint(dia / 2, -1 * length + ((dia - dp) / 2 + z))
        fm.AddPoint(dp / 2, -1 * length + z)
        fm.AddPoint(dp / 2, -1 * length)
        fm.AddPoint(0, -1 * length)
    elif SType == 'ISO4029' or SType == 'ASMEB18.3.5D':
        fm.AddPoint(0, 0)
        fm.AddPoint(df / 2, 0)
        fm.AddPoint(dia / 2, -1 * ((dia - df) / 2))
        fm.AddPoint(dia / 2, -1 * length + ((dia - dp) / 2))
        fm.AddPoint(dp / 2, -1 * length)
        fm.AddPoint(0, -1 * length + math.sqrt(3) / 6 * dp)
    screw = self.RevolveZ(fm.GetFace())
    recess = self.makeHexRecess(s, t - 1, True)
    screw = screw.cut(recess)
    # produce a modelled thread if necessary
    if fa.thread:
        thread_cutter = self.CreateThreadCutter(dia, P, length)
        screw = screw.cut(thread_cutter)
    return screw
