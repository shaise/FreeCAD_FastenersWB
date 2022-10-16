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

# make T-Slot nut
# DIN508

def makeTSlotNut(self, fa): # dynamically loaded method of class Screw
    FreeCAD.Console.PrintMessage("Start")
    SType = fa.type
    dia = self.getDia(fa.calc_diam, True)

    if SType[:3] == 'DIN':
        # a, e_max, f, h, k_max, P
        a, e, f, h, k, P = fa.dimTable

    # T-Slot nut Points, transversal cut
    # Drawing in plane y = -e / 2 to extrude up to y = e / 2
    Pnt0 = Base.Vector(e / 2 - f, - e / 2, - h)
    Pnt1 = Base.Vector(e / 2, - e / 2, - h + f)
    Pnt2 = Base.Vector(e / 2, - e / 2, -h + k)
    Pnt3 = Base.Vector(a / 2, - e / 2, - h + k)
    Pnt4 = Base.Vector(a / 2, - e / 2, 0.0)
    Pnt5 = Base.Vector(- a / 2, - e / 2, 0.0)
    Pnt6 = Base.Vector(- a / 2, - e / 2, - h + k)
    Pnt7 = Base.Vector(- e / 2, - e / 2, - h + k)
    Pnt8 = Base.Vector(- e / 2, - e / 2, - h + f)
    Pnt9 = Base.Vector(- e / 2 + f, - e / 2, - h)

    edge0 = Part.makeLine(Pnt0, Pnt1)
    edge1 = Part.makeLine(Pnt1, Pnt2)
    edge2 = Part.makeLine(Pnt2, Pnt3)
    edge3 = Part.makeLine(Pnt3, Pnt4)
    edge4 = Part.makeLine(Pnt4, Pnt5)
    edge5 = Part.makeLine(Pnt5, Pnt6)
    edge6 = Part.makeLine(Pnt6, Pnt7)
    edge7 = Part.makeLine(Pnt7, Pnt8)
    edge8 = Part.makeLine(Pnt8, Pnt9)
    edge9 = Part.makeLine(Pnt9, Pnt0)
    
    aWire = Part.Wire([edge0, edge1, edge2, edge3, edge4, edge5, edge6, edge7, edge8, edge9])
    # Part.show(aWire) # See profile
    aFace = Part.Face(aWire)
    nut = aFace.extrude(Base.Vector(0.0, e, 0.0))

    residue, turns = math.modf(h / P)
    if residue > 0.0:
        turns += 1.0
    
    if fa.thread:
        threadShell = self.makeInnerThread_2(dia, P, int(turns), None, h)
    else:
        myCyl = Part.makeCylinder(dia/2, h)
        myCyl.translate(Base.Vector(0, 0, -h))
        nut = nut.cut(myCyl)
    
    # Ulices' comment: I'm a little confused about the next lines
    if fa.thread:
        if threadShell is None:
            # thread shell method failed, use slower method
            FreeCAD.Console.PrintLog("Revert to slow thread generation\n")
            turns += 1
            threadCutter = self.makeInnerThread_2(dia, P, int(turns), None, h)
            threadCutter.translate(Base.Vector(0.0, 0.0, h + P))
            # Part.show(threadCutter, 'threadCutter')
            nut = nut.cut(threadCutter)
        else:
            # # FreeCAD.Console.PrintMessage(str((dia, P, int(turns), None, h)) + "\n")
            # nutFaces = nut.Faces
            # nutFaces.extend(threadShell.Faces)
            # nutShell = Part.Shell(nutFaces)
            # nut = Part.Solid(nutShell)
            nut = nut.cut(threadShell)

    return nut
