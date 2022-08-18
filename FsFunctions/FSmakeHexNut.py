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

# make the ISO 4032 Hex-nut
# make the ISO 4033 Hex-nut

def makeHexNut(self, fa): # dynamically loaded method of class Screw
    SType = fa.type
    dia = self.getDia(fa.calc_diam, True)
    #         P, tunIn, tunEx
    # Ptun, self.tuning, tunEx = tuningTable[ThreadType]
    if SType[:3] == 'ISO':
        # P, c, damax,  dw,    e,     m,   mw,   s_nom
        P, c, da, dw, e, m, mw, s = fa.dimTable
    elif SType == 'ASMEB18.2.2.1A':
        P, da, e, m, s = fa.dimTable
    elif SType == 'ASMEB18.2.2.4A':
        P, da, e, m_a, m_b, s = fa.dimTable
        m = m_a
    elif SType == 'ASMEB18.2.2.4B':
        P, da, e, m_a, m_b, s = fa.dimTable
        m = m_b

    residue, turns = math.modf(m / P)
    # halfturns = 2*int(turns)

    if residue > 0.0:
        turns += 1.0
    if SType == 'ISO4033' and fa.calc_diam == '(M14)':
        turns -= 1.0
    if SType == 'ISO4035' and fa.calc_diam == 'M56':
        turns -= 1.0

    sqrt2_ = 1.0 / math.sqrt(2.0)
    cham = (e - s) * math.sin(math.radians(15))  # needed for chamfer at nut top
    H = P * math.cos(math.radians(30))  # Gewindetiefe H
    cham_i_delta = da / 2.0 - (dia / 2.0 - H * 5.0 / 8.0)
    cham_i = cham_i_delta * math.tan(math.radians(15.0))

    if fa.thread:
        Pnt0 = Base.Vector(da / 2.0 - 2.0 * cham_i_delta, 0.0, m - 2.0 * cham_i)
        Pnt7 = Base.Vector(da / 2.0 - 2.0 * cham_i_delta, 0.0, 0.0 + 2.0 * cham_i)
    else:
        Pnt0 = Base.Vector(dia / 2.0 - H * 5.0 / 8.0, 0.0, m - cham_i)
        Pnt7 = Base.Vector(dia / 2.0 - H * 5.0 / 8.0, 0.0, 0.0 + cham_i)

    Pnt1 = Base.Vector(da / 2.0, 0.0, m)
    Pnt2 = Base.Vector(s / 2.0, 0.0, m)
    Pnt3 = Base.Vector(s / math.sqrt(3.0), 0.0, m - cham)
    Pnt4 = Base.Vector(s / math.sqrt(3.0), 0.0, cham)
    Pnt5 = Base.Vector(s / 2.0, 0.0, 0.0)
    Pnt6 = Base.Vector(da / 2.0, 0.0, 0.0)

    edge0 = Part.makeLine(Pnt0, Pnt1)
    edge1 = Part.makeLine(Pnt1, Pnt2)
    edge2 = Part.makeLine(Pnt2, Pnt3)
    edge3 = Part.makeLine(Pnt3, Pnt4)
    edge4 = Part.makeLine(Pnt4, Pnt5)
    edge5 = Part.makeLine(Pnt5, Pnt6)
    edge6 = Part.makeLine(Pnt6, Pnt7)
    edge7 = Part.makeLine(Pnt7, Pnt0)

    # create cutting tool for hexagon head
    # Parameters s, k, outer circle diameter =  e/2.0+10.0
    extrude = self.makeHextool(s, m, s * 2.0)

    aWire = Part.Wire([edge0, edge1, edge2, edge3, edge4, edge5, edge6, edge7])
    # Part.show(aWire)
    aFace = Part.Face(aWire)
    head = aFace.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360.0)
    # Part.show(head)

    # Part.show(extrude)
    nut = head.cut(extrude)
    # Part.show(nut, 'withoutTread')

    if fa.thread:
        # if (dia < 1.6)or (dia > 52.0):
        if (dia < 1.6) or (dia > 64.0):
            # if (dia < 3.0):
            threadCutter = self.makeInnerThread_2(dia, P, int(turns + 1), None, m)
            threadCutter.translate(Base.Vector(0.0, 0.0, turns * P + 0.5 * P))
            # Part.show(threadCutter, 'threadCutter')
            nut = nut.cut(threadCutter)
            # chamFace = nut.Faces[0].cut(threadCutter)
            # Part.show(chamFace, 'chamFace0_')
        else:
            nutFaces = [nut.Faces[2]]
            for i in range(4, 25):
                nutFaces.append(nut.Faces[i])
            # Part.show(Part.Shell(nutFaces), 'OuterNutshell')

            threadShell = self.makeInnerThread_2(dia, P, int(turns), da, m)
            # threadShell.translate(Base.Vector(0.0, 0.0,turns*P))
            # Part.show(threadShell, 'threadShell')
            nutFaces.extend(threadShell.Faces)

            nutShell = Part.Shell(nutFaces)
            nut = Part.Solid(nutShell)
            # Part.show(nutShell)
    return nut
