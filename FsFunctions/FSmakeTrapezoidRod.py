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


def makeTrapezoidRod(self, fa):
    """make a length of standard threaded rod"""
    dia = self.getDia(fa.calc_diam, False)
    rad = dia / 2
    if not fa.Thread:
        screw = Part.makeCylinder(rad, fa.calc_len)
    else:
        P = fa.calc_pitch
        if fa.Pitch == "Custom":
            if P < 2.0:
                ac = 0.15
            elif P < 6.0:
                ac = 0.25
            elif P < 14.0:
                ac = 0.5
            else:
                ac = 1.0
        else:
            ac = float(FsData[fa.Type + "clearance"][fa.calc_pitch][0])
            
        rin = rad - 0.5 * P - ac
        if rin <= 0.2 * P:
            raise ValueError(
                f"Diameter {dia} is too small for the given pitch {P}"
            )
        lenExtra = fa.calc_len + 2 * P
        screw = Part.makeCylinder(rin, lenExtra)
        tool = self.CreateDin130ThreadTool(dia, P, ac, lenExtra, fa.NumStarts)
        screw = screw.fuse(tool)
        screw.translate(FreeCAD.Vector(0, 0, -P))
        tool = Part.makeCylinder(dia, P * 2)
        tool.translate(FreeCAD.Vector(0, 0, -P * 2))
        screw = screw.cut(tool)
        tool.translate(FreeCAD.Vector(0, 0, fa.calc_len + P * 2))
        screw = screw.cut(tool)

    screw = screw.translate(FreeCAD.Vector(0,0,-fa.calc_len))
    return screw
