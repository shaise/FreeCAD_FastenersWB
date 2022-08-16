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

# make Cheese head screw
# ISO 1207 slotted screw
# ISO 7048 cross recessed screw
# ISO 14580 Hexalobular socket cheese head screws

def makeCheeseHeadScrew(self): # dynamically loaded method of class Screw
    SType = self.fastenerType
    l = self.fastenerLen
    dia = self.getDia(self.fastenerDiam, False)

    # FreeCAD.Console.PrintMessage("the head with l: " + str(l) + "\n")
    if SType == 'ISO1207' or SType == 'ISO14580':
        P, a, b, dk, dk_mean, da, k, n_min, r, t_min, x = self.dimTable
    if SType == 'ISO7048':
        P, a, b, dk, dk_mean, da, k, r, x, cT, mH, mZ = self.dimTable
    if SType == 'ISO14580':
        tt, k, A, t_min = FsData["ISO14580extra"][self.fastenerDiam]

    # FreeCAD.Console.PrintMessage("the head with iso: " + str(dk) + "\n")

    # Length for calculation of head fillet
    r_fil = r * 2.0
    beta = math.radians(5.0)  # angle of cheese head edge
    alpha = math.radians(90.0 - (90.0 + 5.0) / 2.0)
    tan_beta = math.tan(beta)
    # top head diameter without fillet
    rK_top = dk / 2.0 - k * tan_beta
    fillet_center_x = rK_top - r_fil + r_fil * tan_beta
    fillet_center_z = k - r_fil
    fillet_arc_x = fillet_center_x + r_fil * math.sin(alpha)
    fillet_arc_z = fillet_center_z + r_fil * math.cos(alpha)
    # FreeCAD.Console.PrintMessage("rK_top: " + str(rK_top) + "\n")

    thread_start = l - b
    sqrt2_ = 1.0 / math.sqrt(2.0)

    # Head Points
    Pnt2 = Base.Vector(fillet_center_x, 0.0, k)
    Pnt3 = Base.Vector(fillet_arc_x, 0.0, fillet_arc_z)
    Pnt4 = Base.Vector(fillet_center_x + r_fil * math.cos(beta), 0.0, fillet_center_z + r_fil * math.sin(beta))
    Pnt5 = Base.Vector(dk / 2.0, 0.0, 0.0)
    Pnt6 = Base.Vector(dia / 2.0 + r, 0.0, 0.0)  # start of fillet between head and shank
    Pnt7 = Base.Vector(dia / 2.0 + r - r * sqrt2_, 0.0, -r + r * sqrt2_)  # arc-point of fillet
    Pnt8 = Base.Vector(dia / 2.0, 0.0, -r)  # end of fillet
    Pnt9 = Base.Vector(dia / 2.0, 0.0, -thread_start)  # Start of thread
    # FreeCAD.Console.PrintMessage("Points defined fillet_center_x: " + str(fillet_center_x) + "\n")

    if SType == 'ISO14580':
        # Pnt0 = Base.Vector(0.0,0.0,k-A/4.0) #Center Point for countersunk
        Pnt0 = Base.Vector(0.0, 0.0, k - A / 8.0)  # Center Point for flat countersunk
        PntFlat = Base.Vector(A / 8.0, 0.0, k - A / 8.0)  # End of flat part
        Pnt1 = Base.Vector(A / 1.99, 0.0, k)  # countersunk edge at head
        edgeCham0 = Part.makeLine(Pnt0, PntFlat)
        edgeCham1 = Part.makeLine(PntFlat, Pnt1)
        edgeCham2 = Part.makeLine(Pnt1, Pnt2)
        edge1 = Part.Wire([edgeCham1, edgeCham2])  # make head with countersunk
        PntH1 = Base.Vector(A / 1.99, 0.0, 2.0 * k)

    else:
        Pnt0 = Base.Vector(0.0, 0.0, k)
        edge1 = Part.makeLine(Pnt0, Pnt2)  # make flat head

    edge2 = Part.Arc(Pnt2, Pnt3, Pnt4).toShape()
    edge3 = Part.makeLine(Pnt4, Pnt5)
    edge4 = Part.makeLine(Pnt5, Pnt6)
    edge5 = Part.Arc(Pnt6, Pnt7, Pnt8).toShape()
    # FreeCAD.Console.PrintMessage("Edges made fillet_center_z: " + str(fillet_center_z) + "\n")

    if SType == 'ISO1207':
        # Parameter for slot-recess: dk, n_min, k, t_min
        recess = Part.makePlane(dk, n_min, \
                                Base.Vector(dk / 2.0, -n_min / 2.0, k + 1.0), Base.Vector(0.0, 0.0, -1.0))
        recess = recess.extrude(Base.Vector(0.0, 0.0, -t_min - 1.0))

        if self.rThread:
            Pnt11 = Base.Vector(0.0, 0.0, -r)  # helper point for real thread
            edgeZ1 = Part.makeLine(Pnt8, Pnt11)
            edgeZ0 = Part.makeLine(Pnt11, Pnt0)
            aWire = Part.Wire([edge1, edge2, edge3, edge4, edge5, \
                                edgeZ1, edgeZ0])
        else:
            # bolt points
            PntB1 = Base.Vector(dia / 2.0, 0.0, -l)
            PntB2 = Base.Vector(0.0, 0.0, -l)

            edgeB2 = Part.makeLine(PntB1, PntB2)

            if thread_start <= r:
                edgeB1 = Part.makeLine(Pnt8, PntB1)
                aWire = Part.Wire([edge1, edge2, edge3, edge4, edge5, \
                                    edgeB1, edgeB2])
            else:
                edge6 = Part.makeLine(Pnt8, Pnt9)
                edgeB1 = Part.makeLine(Pnt9, PntB1)
                aWire = Part.Wire([edge1, edge2, edge3, edge4, edge5, edge6, \
                                    edgeB1, edgeB2])

        aFace = Part.Face(aWire)
        head = aFace.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360.0)
        head = head.cut(recess)
        # FreeCAD.Console.PrintMessage("the head cut: " + str(dia) + "\n")
        # Part.show(head)
        if self.rThread:
            screwFaces = []
            for i in range(0, len(head.Faces) - 1):
                screwFaces.append(head.Faces[i])
            rthread = self.makeShellthread(dia, P, l - r, False, -r, b)
            for threadFace in rthread.Faces:
                screwFaces.append(threadFace)

            screwShell = Part.Shell(screwFaces)
            head = Part.Solid(screwShell)



    else:
        if self.rThread:
            aWire = Part.Wire([edge1, edge2, edge3, edge4, edge5])
        else:
            # bolt points
            PntB1 = Base.Vector(dia / 2.0, 0.0, -l)
            PntB2 = Base.Vector(0.0, 0.0, -l)

            edgeB2 = Part.makeLine(PntB1, PntB2)

            if thread_start <= r:
                edgeB1 = Part.makeLine(Pnt8, PntB1)
                aWire = Part.Wire([edge1, edge2, edge3, edge4, edge5, \
                                    edgeB1, edgeB2])
            else:
                edge6 = Part.makeLine(Pnt8, Pnt9)
                edgeB1 = Part.makeLine(Pnt9, PntB1)
                aWire = Part.Wire([edge1, edge2, edge3, edge4, edge5, edge6, \
                                    edgeB1, edgeB2])

        # aFace =Part.Face(aWire)
        headShell = aWire.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360.0)
        # FreeCAD.Console.PrintMessage("the head with revolve: " + str(dia) + "\n")

        if SType == 'ISO7048':
            # hCut should be just a cylinder
            hCut = Part.makeCylinder(fillet_center_x, k, Pnt0)
            recess, recessShell = self.makeCross_H3(cT, mH, k)
            recessShell = recessShell.cut(hCut)
            topFace = headShell.Faces[0].cut(recess)
            screwFaces = [topFace.Faces[0]]
            screwFaces.extend(recessShell.Faces)
        if SType == 'ISO14580':
            # Ring-cutter for recess shell
            PntH2 = Base.Vector(A / 8.0, 0.0, 2.0 * k)
            edgeH1 = Part.makeLine(Pnt1, PntH1)
            edgeH2 = Part.makeLine(PntH1, PntH2)
            edgeH3 = Part.makeLine(PntH2, PntFlat)
            hWire = Part.Wire([edgeCham1, edgeH1, edgeH2, edgeH3])  # Cutter for recess-Shell
            hFace = Part.Face(hWire)
            hCut = hFace.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360)
            # Part.show(hWire)

            recess, recessShell = self.makeIso10664_3(tt, t_min, k)
            recessShell = recessShell.cut(hCut)
            topFace = headShell.Faces[0].cut(recess)
            screwFaces = [topFace.Faces[0]]
            screwFaces.extend(recessShell.Faces)

        for i in range(1, len(headShell.Faces)):
            screwFaces.append(headShell.Faces[i])

        if self.rThread:
            # head = self.cutIsoThread(head, dia, P, turns, l)
            rthread = self.makeShellthread(dia, P, l - r, False, -r, b)
            # head = head.fuse(rthread)
            # Part.show(rthread)
            for threadFace in rthread.Faces:
                screwFaces.append(threadFace)

        screwShell = Part.Shell(screwFaces)
        head = Part.Solid(screwShell)

    return head
