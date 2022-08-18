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

# EN 1661 Hexagon nuts with flange
# chamfer at top of hexagon is wrong = more than 30°

def makeHexNutWFlunge(self, fa): # dynamically loaded method of class Screw
    dia = self.getDia(fa.calc_diam, True)
    P, da, c, dc, dw, e, m, mw, r1, s = fa.dimTable

    residue, turns = math.modf(m / P)
    # halfturns = 2*int(turns)

    if residue > 0.0:
        turns += 1.0

    # FreeCAD.Console.PrintMessage("the nut with isoEN1661: " + str(c) + "\n")
    cham = s * (2.0 / math.sqrt(3.0) - 1.0) * math.sin(math.radians(25))  # needed for chamfer at head top

    sqrt2_ = 1.0 / math.sqrt(2.0)

    # Flange is made with a radius of c
    beta = math.radians(25.0)
    tan_beta = math.tan(beta)

    # Calculation of Arc points of flange edge using dc and c
    arc1_x = dc / 2.0 - c / 2.0 + (c / 2.0) * math.sin(beta)
    arc1_z = c / 2.0 + (c / 2.0) * math.cos(beta)

    hF = arc1_z + (arc1_x - s / 2.0) * tan_beta  # height of flange at center

    # kmean = arc1_z + (arc1_x - s/math.sqrt(3.0)) * tan_beta + mw * 1.1 + cham
    # kmean = k * 0.95

    # Hex-Head Points
    # FreeCAD.Console.PrintMessage("the nut with kmean: " + str(m) + "\n")
    PntH0 = Base.Vector(da / 2.0, 0.0, m)
    PntH1 = Base.Vector(s / 2.0, 0.0, m)
    edgeH1 = Part.makeLine(PntH0, PntH1)

    hWire = Part.Wire([edgeH1])
    topShell = hWire.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360)
    # Part.show(hWire)
    # Part.show(topShell)

    # create a cutter ring to generate the chamfer at the top of the hex
    chamHori = s / math.sqrt(3.0) - s / 2.0
    PntC1 = Base.Vector(s / 2.0 - chamHori, 0.0, m + m)
    PntC2 = Base.Vector(s / math.sqrt(3.0) + chamHori, 0.0, m + m)
    PntC3 = Base.Vector(s / 2.0 - chamHori, 0.0, m + cham)
    PntC4 = Base.Vector(s / math.sqrt(3.0) + chamHori, 0.0, m - cham - cham)  # s/math.sqrt(3.0)
    edgeC1 = Part.makeLine(PntC3, PntC1)
    edgeC2 = Part.makeLine(PntC1, PntC2)
    edgeC3 = Part.makeLine(PntC2, PntC4)
    edgeC4 = Part.makeLine(PntC4, PntC3)
    cWire = Part.Wire([edgeC4, edgeC1, edgeC2, edgeC3])
    cFace = Part.Face(cWire)
    chamCut = cFace.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360)
    # Part.show(cWire)
    # Part.show(chamCut)

    # create hexagon
    mhex = Base.Matrix()
    mhex.rotateZ(math.radians(60.0))
    polygon = []
    vhex = Base.Vector(s / math.sqrt(3.0), 0.0, m)
    for i in range(6):
        polygon.append(vhex)
        vhex = mhex.multiply(vhex)
    polygon.append(vhex)
    hexagon = Part.makePolygon(polygon)
    hexFace = Part.Face(hexagon)
    solidHex = hexFace.extrude(Base.Vector(0.0, 0.0, c - m))
    # Part.show(solidHex)
    hexCham = solidHex.cut(chamCut)
    # Part.show(hexCham)

    topFaces = topShell.Faces

    topFaces.append(hexCham.Faces[1])
    topFaces.append(hexCham.Faces[2])
    topFaces.append(hexCham.Faces[8])
    topFaces.append(hexCham.Faces[13])
    topFaces.append(hexCham.Faces[14])
    topFaces.append(hexCham.Faces[12])
    topFaces.append(hexCham.Faces[6])

    hexFaces = [hexCham.Faces[5], hexCham.Faces[11], hexCham.Faces[10]]
    hexFaces.extend([hexCham.Faces[9], hexCham.Faces[3], hexCham.Faces[0]])
    hexShell = Part.Shell(hexFaces)

    H = P * math.cos(math.radians(30))  # Thread depth H
    cham_i_delta = da / 2.0 - (dia / 2.0 - H * 5.0 / 8.0)
    cham_i = cham_i_delta * math.tan(math.radians(15.0))

    # Center of flange:
    Pnt0 = Base.Vector(0.0, 0.0, hF)
    Pnt1 = Base.Vector(s / 2.0, 0.0, hF)

    # arc edge of flange:
    Pnt2 = Base.Vector(arc1_x, 0.0, arc1_z)
    Pnt3 = Base.Vector(dc / 2.0, 0.0, c / 2.0)
    Pnt4 = Base.Vector((dc - c) / 2.0, 0.0, 0.0)
    Pnt5 = Base.Vector(da / 2.0, 0.0, 0.0)  # start of fillet between flat and thread

    edge1 = Part.makeLine(Pnt0, Pnt1)
    edge2 = Part.makeLine(Pnt1, Pnt2)
    edge3 = Part.Arc(Pnt2, Pnt3, Pnt4).toShape()
    edge4 = Part.makeLine(Pnt4, Pnt5)

    # make a cutter for the hexShell
    PntHC1 = Base.Vector(0.0, 0.0, arc1_z)
    PntHC2 = Base.Vector(0.0, 0.0, 0.0)

    edgeHC1 = Part.makeLine(Pnt2, PntHC1)
    edgeHC2 = Part.makeLine(PntHC1, PntHC2)
    edgeHC3 = Part.makeLine(PntHC2, Pnt0)

    HCWire = Part.Wire([edge2, edgeHC1, edgeHC2, edgeHC3, edge1])
    HCFace = Part.Face(HCWire)
    hex2Cut = HCFace.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360)

    hexShell = hexShell.cut(hex2Cut)
    # Part.show(hexShell)

    topFaces.extend(hexShell.Faces)

    if fa.thread and (dia > 4.0):
        aWire = Part.Wire([edge2, edge3, edge4])
        boltIndex = 3

    else:
        if fa.thread:
            Pnt7 = Base.Vector(dia / 2.1 - H * 5.0 / 8.0, 0.0, m - cham_i)
            Pnt6 = Base.Vector(dia / 2.1 - H * 5.0 / 8.0, 0.0, 0.0 + cham_i)

        else:
            Pnt7 = Base.Vector(dia / 2.0 - H * 5.0 / 8.0, 0.0, m - cham_i)
            Pnt6 = Base.Vector(dia / 2.0 - H * 5.0 / 8.0, 0.0, 0.0 + cham_i)
        edge5 = Part.makeLine(Pnt5, Pnt6)
        edge6 = Part.makeLine(Pnt6, Pnt7)
        edge7 = Part.makeLine(Pnt7, PntH0)
        aWire = Part.Wire([edge2, edge3, edge4, edge5, edge6, edge7])
        boltIndex = 6

    # aFace =Part.Face(aWire)
    # Part.show(aWire)
    headShell = aWire.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360)
    # FreeCAD.Console.PrintMessage("the head with revolve: " + str(dia) + "\n")
    # Part.show(headShell)
    chamFace = headShell.Faces[0].cut(solidHex)
    # Part.show(chamFace)

    topFaces.append(chamFace.Faces[0])
    for i in range(1, boltIndex):
        topFaces.append(headShell.Faces[i])

    if fa.thread:
        if dia < 5.0:
            nutShell = Part.Shell(topFaces)
            nut = Part.Solid(nutShell)
            # Part.show(nut, 'unthreadedNut')
            threadCutter = self.makeInnerThread_2(dia, P, int(turns + 1), None, m)
            threadCutter.translate(Base.Vector(0.0, 0.0, turns * P + 0.5 * P))
            # Part.show(threadCutter, 'threadCutter')
            nut = nut.cut(threadCutter)

        else:
            threadShell = self.makeInnerThread_2(dia, P, int(turns), da, m)
            # threadShell.translate(Base.Vector(0.0, 0.0,turns*P))
            # Part.show(threadShell)
            for tFace in threadShell.Faces:
                topFaces.append(tFace)
            headShell = Part.Shell(topFaces)
            nut = Part.Solid(headShell)
    else:
        nutShell = Part.Shell(topFaces)
        nut = Part.Solid(nutShell)

    return nut
