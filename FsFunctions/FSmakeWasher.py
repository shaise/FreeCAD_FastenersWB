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

# make Washer
# ISO7089 Washer
# ISO7090 Washer
# ISO7091 Washer
# ISO7092 Washer
# ISO7093-1 Washer
# ISO7094 Washer
# NFE27-619 Washer
# ASMEB18.21.1.12A Washer
# ASMEB18.21.1.12B Washer
# ASMEB18.21.1.12C Washer

def makeWasher(self, fa): # dynamically loaded method of class Screw
    SType = fa.type
    # FreeCAD.Console.PrintMessage("the disc with dia: " + str(dia) + "\n")
    if SType[:3] == 'ISO':
        d1_min, d2_max, h, h_max = fa.dimTable
    elif SType[:3] == 'ASM':
        d1_min, d2_max, h = fa.dimTable
    elif SType[:3] == 'NFE':
        d1_min, d2_max, d3, h, h_min = fa.dimTable

    # Washer Points
    Pnt0 = Base.Vector(d1_min / 2.0, 0.0, h)
    Pnt2 = Base.Vector(d2_max / 2.0, 0.0, h)
    Pnt3 = Base.Vector(d2_max / 2.0, 0.0, 0.0)
    Pnt4 = Base.Vector(d1_min / 2.0, 0.0, 0.0)
    if SType == 'ISO7090':
        Pnt1 = Base.Vector(d2_max / 2.0 - h / 4.0, 0.0, h)
        Pnt2 = Base.Vector(d2_max / 2.0, 0.0, h * 0.75)
        edge1 = Part.makeLine(Pnt0, Pnt1)
        edgeCham = Part.makeLine(Pnt1, Pnt2)
        edge1 = Part.Wire([edge1, edgeCham])
    elif SType == 'NFE27-619':
        Pnt0 = Base.Vector(d1_min / 2.0, 0.0, h_min)
        Pnt2 = Base.Vector(d3 / 2.0, 0.0, h)
        edge1 = Part.makeLine(Pnt0, Pnt2)
    else:
        edge1 = Part.makeLine(Pnt0, Pnt2)

    edge2 = Part.makeLine(Pnt2, Pnt3)
    edge3 = Part.makeLine(Pnt3, Pnt4)
    edge4 = Part.makeLine(Pnt4, Pnt0)
    # FreeCAD.Console.PrintMessage("Edges made Pnt2: " + str(Pnt2) + "\n")

    aWire = Part.Wire([edge1, edge2, edge3, edge4])
    # Part.show(aWire)
    aFace = Part.Face(aWire)
    head = self.RevolveZ(aFace)
    # FreeCAD.Console.PrintMessage("Washer revolved: " + str(dia) + "\n")

    return head
