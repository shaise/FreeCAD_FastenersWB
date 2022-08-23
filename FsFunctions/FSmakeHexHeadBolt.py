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

# make the ISO 4017 Hex-head-screw
# make the ISO 4014 Hex-head-bolt
# make the ASMEB18.2.1.6 Hex-head-bolt

def makeHexHeadBolt(self, fa): # dynamically loaded method of class Screw
    dia = self.getDia(fa.calc_diam, False)
    l = fa.calc_len
    #FreeCAD.Console.PrintMessage("the head with thread type: " + str(ThreadType) + "\n")
    if fa.type == 'ISO4017':
        P, c, dw, e, k, r, s = fa.dimTable
        b = l

    if fa.type == 'ISO4014':
        P, b1, b2, b3, c, dw, e, k, r, s = fa.dimTable
        if l <= 125.0:
            b = b1
        else:
            if l <= 200.0:
                b = b2
            else:
                b = b3

    if fa.type == 'ASMEB18.2.1.6':
        b, P, c, dw, e, k, r, s = fa.dimTable
        if l > 6 * 25.4:
            b += 6.35

    a = l - b
    sqrt2_ = 1.0 / math.sqrt(2.0)
    cham = (e - s) * math.sin(math.radians(15))  # needed for chamfer at head top

    # Head Points  Usage of k, s, cham, c, dw, dia, r, a
    # FreeCAD.Console.PrintMessage("the head with halfturns: " + str(halfturns) + "\n")
    Pnt0 = Base.Vector(0.0, 0.0, k)
    Pnt2 = Base.Vector(s / 2.0, 0.0, k)
    Pnt3 = Base.Vector(s / math.sqrt(3.0), 0.0, k - cham)
    Pnt4 = Base.Vector(s / math.sqrt(3.0), 0.0, c)
    Pnt5 = Base.Vector(dw / 2.0, 0.0, c)
    Pnt6 = Base.Vector(dw / 2.0, 0.0, 0.0)
    Pnt7 = Base.Vector(dia / 2.0 + r, 0.0, 0.0)  # start of fillet between head and shank
    Pnt8 = Base.Vector(dia / 2.0 + r - r * sqrt2_, 0.0, -r + r * sqrt2_)  # arc-point of fillet
    Pnt9 = Base.Vector(dia / 2.0, 0.0, -r)  # end of fillet
    Pnt10 = Base.Vector(dia / 2.0, 0.0, -a)  # Start of thread

    edge1 = Part.makeLine(Pnt0, Pnt2)
    edge2 = Part.makeLine(Pnt2, Pnt3)
    edge3 = Part.makeLine(Pnt3, Pnt4)
    edge4 = Part.makeLine(Pnt4, Pnt5)
    edge5 = Part.makeLine(Pnt5, Pnt6)
    edge6 = Part.makeLine(Pnt6, Pnt7)
    edge7 = Part.Arc(Pnt7, Pnt8, Pnt9).toShape()

    # create cutting tool for hexagon head
    # Parameters s, k, outer circle diameter =  e/2.0+10.0
    extrude = self.makeHextool(s, k, s * 2.0)

    # if self.RealThread.isChecked():
    if fa.thread:
        Pnt11 = Base.Vector(0.0, 0.0, -r)  # helper point for real thread
        edgeZ1 = Part.makeLine(Pnt9, Pnt11)
        edgeZ0 = Part.makeLine(Pnt11, Pnt0)
        aWire = Part.Wire([edge1, edge2, edge3, edge4, edge5, edge6, edge7, \
                            edgeZ1, edgeZ0])

        aFace = Part.Face(aWire)
        head = self.RevolveZ(aFace.revolve)
        # FreeCAD.Console.PrintMessage("the head with revolve: " + str(dia) + "\n")
        #Part.show(head1)

        # Part.show(extrude)
        head = head.cut(extrude)
        # FreeCAD.Console.PrintMessage("the head cut: " + str(dia) + "\n")
        # Part.show(head)
        headFaces = []
        for face in head.Faces:
            if face.CenterOfMass[2] > -r + 0.001:
                headFaces.append(face)

        rthread = self.makeShellthread(dia, P, l - r, True, -r, b)
        # Part.show(rthread)
        for tFace in rthread.Faces:
            headFaces.append(tFace)
        headShell = Part.Shell(headFaces)
        head = Part.Solid(headShell)

    else:
        # bolt points
        cham_t = P * math.sqrt(3.0) / 2.0 * 17.0 / 24.0

        PntB0 = Base.Vector(0.0, 0.0, -a)
        PntB1 = Base.Vector(dia / 2.0, 0.0, -l + cham_t)
        PntB2 = Base.Vector(dia / 2.0 - cham_t, 0.0, -l)
        PntB3 = Base.Vector(0.0, 0.0, -l)

        edgeB1 = Part.makeLine(Pnt10, PntB1)
        edgeB2 = Part.makeLine(PntB1, PntB2)
        edgeB3 = Part.makeLine(PntB2, PntB3)

        edgeZ0 = Part.makeLine(PntB3, Pnt0)
        if a <= r:
            edgeB1 = Part.makeLine(Pnt9, PntB1)
            aWire = Part.Wire([edge1, edge2, edge3, edge4, edge5, edge6, edge7, \
                                edgeB1, edgeB2, edgeB3, edgeZ0])

        else:
            edge8 = Part.makeLine(Pnt9, Pnt10)
            edgeB1 = Part.makeLine(Pnt10, PntB1)
            aWire = Part.Wire([edge1, edge2, edge3, edge4, edge5, edge6, edge7, edge8, \
                                edgeB1, edgeB2, edgeB3, edgeZ0])

        aFace = Part.Face(aWire)
        head = self.RevolveZ(aFace)
        # FreeCAD.Console.PrintMessage("the head with revolve: " + str(dia) + "\n")

        # Part.show(extrude)
        head = head.cut(extrude)
        # FreeCAD.Console.PrintMessage("the head cut: " + str(dia) + "\n")

    return head
