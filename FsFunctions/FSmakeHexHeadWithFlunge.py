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

# EN 1662 Hex-head-bolt with flange - small series
# EN 1665 Hexagon bolts with flange, heavy series
# ASMEB18.2.1.8 Hexagon bolts with flange, heavy series

def makeHexHeadWithFlunge(self, fa): # dynamically loaded method of class Screw
    dia = self.getDia(fa.calc_diam, False)
    SType = fa.type
    l = fa.calc_len
    # FreeCAD.Console.PrintMessage("the head with l: " + str(l) + "\n")
    if SType == 'EN1662' or SType == 'EN1665':
        P, b0, b1, b2, b3, c, dc, dw, e, k, kw, f, r1, s = fa.dimTable
    elif SType == 'ASMEB18.2.1.8':
        b0, P, c, dc, kw, r1, s = fa.dimTable
        b = b0
    if l < b0:
        b = l - 2 * P
    elif SType != 'ASMEB18.2.1.8':
        if l <= 125.0:
            b = b1
        else:
            if l <= 200.0:
                b = b2
            else:
                b = b3

    # FreeCAD.Console.PrintMessage("the head with isoEN1662: " + str(c) + "\n")
    cham = s * (2.0 / math.sqrt(3.0) - 1.0) * math.sin(math.radians(25))  # needed for chamfer at head top

    thread_start = l - b
    sqrt2_ = 1.0 / math.sqrt(2.0)

    # Flange is made with a radius of c
    beta = math.radians(25.0)
    tan_beta = math.tan(beta)

    # Calculation of Arc points of flange edge using dc and c
    arc1_x = dc / 2.0 - c / 2.0 + (c / 2.0) * math.sin(beta)
    arc1_z = c / 2.0 + (c / 2.0) * math.cos(beta)

    hF = arc1_z + (arc1_x - s / 2.0) * tan_beta  # height of flange at center

    kmean = arc1_z + (arc1_x - s / math.sqrt(3.0)) * tan_beta + kw * 1.1 + cham
    # kmean = k * 0.95

    # Hex-Head Points
    # FreeCAD.Console.PrintMessage("the head with math a: " + str(a_point) + "\n")
    PntH0 = Base.Vector(0.0, 0.0, kmean * 0.9)
    PntH1 = Base.Vector(s / 2.0 * 0.8 - r1 / 2.0, 0.0, kmean * 0.9)
    PntH1a = Base.Vector(s / 2.0 * 0.8 - r1 / 2.0 + r1 / 2.0 * sqrt2_, 0.0,
                            kmean * 0.9 + r1 / 2.0 - r1 / 2.0 * sqrt2_)
    PntH1b = Base.Vector(s / 2.0 * 0.8, 0.0, kmean * 0.9 + r1 / 2.0)
    PntH2 = Base.Vector(s / 2.0 * 0.8, 0.0, kmean - r1)
    PntH2a = Base.Vector(s / 2.0 * 0.8 + r1 - r1 * sqrt2_, 0.0, kmean - r1 + r1 * sqrt2_)
    PntH2b = Base.Vector(s / 2.0 * 0.8 + r1, 0.0, kmean)
    PntH3 = Base.Vector(s / 2.0, 0.0, kmean)
    # PntH4 = Base.Vector(s/math.sqrt(3.0),0.0,kmean-cham)   #s/math.sqrt(3.0)
    # PntH5 = Base.Vector(s/math.sqrt(3.0),0.0,c)
    # PntH6 = Base.Vector(0.0,0.0,c)

    edgeH1 = Part.makeLine(PntH0, PntH1)
    edgeH2 = Part.Arc(PntH1, PntH1a, PntH1b).toShape()
    edgeH3 = Part.makeLine(PntH1b, PntH2)
    edgeH3a = Part.Arc(PntH2, PntH2a, PntH2b).toShape()
    edgeH3b = Part.makeLine(PntH2b, PntH3)

    hWire = Part.Wire([edgeH1, edgeH2, edgeH3, edgeH3a, edgeH3b])
    topShell = hWire.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360)
    # Part.show(hWire)
    # Part.show(topShell)

    # create a cutter ring to generate the chamfer at the top of the hex
    chamHori = s / math.sqrt(3.0) - s / 2.0
    PntC1 = Base.Vector(s / 2.0 - chamHori, 0.0, kmean + kmean)
    PntC2 = Base.Vector(s / math.sqrt(3.0) + chamHori, 0.0, kmean + kmean)
    PntC3 = Base.Vector(s / 2.0 - chamHori, 0.0, kmean + cham)
    PntC4 = Base.Vector(s / math.sqrt(3.0) + chamHori, 0.0, kmean - cham - cham)  # s/math.sqrt(3.0)
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
    vhex = Base.Vector(s / math.sqrt(3.0), 0.0, kmean)
    for i in range(6):
        polygon.append(vhex)
        vhex = mhex.multiply(vhex)
    polygon.append(vhex)
    hexagon = Part.makePolygon(polygon)
    hexFace = Part.Face(hexagon)
    solidHex = hexFace.extrude(Base.Vector(0.0, 0.0, c - kmean))
    # Part.show(solidHex)
    hexCham = solidHex.cut(chamCut)
    # Part.show(hexCham)

    topFaces = topShell.Faces

    topFaces.append(hexCham.Faces[6])
    topFaces.append(hexCham.Faces[12])
    topFaces.append(hexCham.Faces[14])
    topFaces.append(hexCham.Faces[13])
    topFaces.append(hexCham.Faces[8])
    topFaces.append(hexCham.Faces[2])
    topFaces.append(hexCham.Faces[1])

    hexFaces = [hexCham.Faces[5], hexCham.Faces[11], hexCham.Faces[10]]
    hexFaces.extend([hexCham.Faces[9], hexCham.Faces[3], hexCham.Faces[0]])
    hexShell = Part.Shell(hexFaces)

    # Center of flange:
    Pnt0 = Base.Vector(0.0, 0.0, hF)
    Pnt1 = Base.Vector(s / 2.0, 0.0, hF)

    # arc edge of flange:
    Pnt2 = Base.Vector(arc1_x, 0.0, arc1_z)
    Pnt3 = Base.Vector(dc / 2.0, 0.0, c / 2.0)
    Pnt4 = Base.Vector((dc - c) / 2.0, 0.0, 0.0)

    Pnt5 = Base.Vector(dia / 2.0 + r1, 0.0, 0.0)  # start of fillet between head and shank
    Pnt6 = Base.Vector(dia / 2.0 + r1 - r1 * sqrt2_, 0.0, -r1 + r1 * sqrt2_)  # arc-point of fillet
    Pnt7 = Base.Vector(dia / 2.0, 0.0, -r1)  # end of fillet
    Pnt8 = Base.Vector(dia / 2.0, 0.0, -thread_start)  # Start of thread

    edge1 = Part.makeLine(Pnt0, Pnt1)
    edge2 = Part.makeLine(Pnt1, Pnt2)
    edge3 = Part.Arc(Pnt2, Pnt3, Pnt4).toShape()
    edge4 = Part.makeLine(Pnt4, Pnt5)
    edge5 = Part.Arc(Pnt5, Pnt6, Pnt7).toShape()

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

    # bolt points
    cham_t = P * math.sqrt(3.0) / 2.0 * 17.0 / 24.0

    PntB0 = Base.Vector(0.0, 0.0, -thread_start)
    PntB1 = Base.Vector(dia / 2.0, 0.0, -l + cham_t)
    PntB2 = Base.Vector(dia / 2.0 - cham_t, 0.0, -l)
    PntB3 = Base.Vector(0.0, 0.0, -l)

    edgeB2 = Part.makeLine(PntB1, PntB2)
    edgeB3 = Part.makeLine(PntB2, PntB3)

    # if self.RealThread.isChecked():
    if fa.thread:
        aWire = Part.Wire([edge2, edge3, edge4, edge5])
        boltIndex = 4

    else:
        if thread_start <= r1:
            edgeB1 = Part.makeLine(Pnt7, PntB1)
            aWire = Part.Wire([edge2, edge3, edge4, edge5, edgeB1, edgeB2, edgeB3])
            boltIndex = 7
        else:
            edgeB1 = Part.makeLine(Pnt8, PntB1)
            edge6 = Part.makeLine(Pnt7, Pnt8)
            aWire = Part.Wire([edge2, edge3, edge4, edge5, edge6, \
                                edgeB1, edgeB2, edgeB3])
            boltIndex = 8

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
        rthread = self.makeShellthread(dia, P, l - r1, True, -r1, b)
        for tFace in rthread.Faces:
            topFaces.append(tFace)
        headShell = Part.Shell(topFaces)
        screw = Part.Solid(headShell)
    else:
        screwShell = Part.Shell(topFaces)
        screw = Part.Solid(screwShell)

    return screw
