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

# DIN917 Cap nuts, thin style

def makeThinCupNut(self, fa): # dynamically loaded method of class Screw
    dia = self.getDia(fa.calc_diam, True)
    P, g2, h, r, s, t, w = fa.dimTable

    H = P * math.cos(math.radians(30)) * 5.0 / 8.0 # Gewindetiefe H
    if fa.thread: H *= 1.1
    e = s / math.sqrt(3) * 2.0
    cham_i = H * math.tan(math.radians(15.0))
    cham_o = (e - s) * math.tan(math.radians(15.0))
    d = dia / 2.0
        
    Pnt0 = Base.Vector(d - H, 0.0, cham_i)
    Pnt1 = Base.Vector(d, 0.0, 0.0)
    Pnt2 = Base.Vector(s / 2.0, 0.0, 0.0)
    Pnt3 = Base.Vector(e / 2.0, 0.0, cham_o)
    Pnt4 = Base.Vector(e / 2.0, 0.0, h - r + math.sqrt(r * r - e * e / 4.0))
    Pnt5 = Base.Vector(e / 4.0, 0.0, h - r + math.sqrt(r * r - e * e / 16.0))
    Pnt6 = Base.Vector(0.0, 0.0, h)
    Pnt7 = Base.Vector(0.0, 0.0, h-w)
    Pnt8 = Base.Vector(d - H, 0.0, t)

    edge0 = Part.makeLine(Pnt0, Pnt1)
    edge1 = Part.makeLine(Pnt1, Pnt2)
    edge2 = Part.makeLine(Pnt2, Pnt3)
    edge3 = Part.makeLine(Pnt3, Pnt4)
    edge4 = Part.Arc(Pnt4, Pnt5, Pnt6).toShape()
    edge5 = Part.makeLine(Pnt6, Pnt7)
    edge6 = Part.makeLine(Pnt7, Pnt8)
    edge7 = Part.makeLine(Pnt8, Pnt0)

    aWire = Part.Wire([edge0, edge1, edge2, edge3, edge4, edge5, edge6, edge7])
    # Part.show(aWire)
    aFace = Part.Face(aWire)
    head = self.RevolveZ(aFace)
    extrude = self.makeHextool(s, h, s * 2.0)
    nut = head.cut(extrude)

    if fa.thread:
        turns = int(math.floor(t/P))
        threadCutter = self.makeInnerThread_2(dia, P, turns, None, t)
        threadCutter.translate(Base.Vector(0.0, 0.0, turns * P))
        nut = nut.cut(threadCutter)

    return nut
