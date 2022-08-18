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

# ISO 7045 Pan head screws with type H or type Z cross recess
# ISO 14583 Hexalobular socket pan head screws

def makePanHeadScrew(self, fa): # dynamically loaded method of class Screw
    SType = fa.type
    l = fa.calc_len
    dia = self.getDia(fa.calc_diam, False)
    # FreeCAD.Console.PrintMessage("the head with l: " + str(l) + "\n")
    P, a, b, dk_max, da, k, r, rf, x, cT, mH, mZ = FsData["ISO7045def"][fa.calc_diam]
    # FreeCAD.Console.PrintMessage("the head with iso: " + str(dk_max) + "\n")

    # Lengths and angles for calculation of head rounding
    beta = math.asin(dk_max / 2.0 / rf)  # angle of head edge
    # print 'beta: ', math.degrees(beta)
    tan_beta = math.tan(beta)

    if SType == 'ISO14583':
        tt, A, t_mean = fa.dimTable
        beta_A = math.asin(A / 2.0 / rf)  # angle of recess edge
        tan_beta_A = math.tan(beta_A)

        alpha = (beta_A + beta) / 2.0  # half angle
        # print 'alpha: ', math.degrees(alpha)
        # height of head edge
        he = k - A / 2.0 / tan_beta_A + (dk_max / 2.0) / tan_beta
        # print 'he: ', he
        h_arc_x = rf * math.sin(alpha)
        h_arc_z = k - A / 2.0 / tan_beta_A + rf * math.cos(alpha)
        # FreeCAD.Console.PrintMessage("h_arc_z: " + str(h_arc_z) + "\n")
    else:
        alpha = beta / 2.0  # half angle
        # print 'alpha: ', math.degrees(alpha)
        # height of head edge
        he = k - rf + (dk_max / 2.0) / tan_beta
        # print 'he: ', he
        h_arc_x = rf * math.sin(alpha)
        h_arc_z = k - rf + rf * math.cos(alpha)
        # FreeCAD.Console.PrintMessage("h_arc_z: " + str(h_arc_z) + "\n")

    thread_start = l - b
    # FreeCAD.Console.PrintMessage("The transition at a: " + str(a) + " turns " + str(turns) + "\n")

    sqrt2_ = 1.0 / math.sqrt(2.0)

    # Head Points
    Pnt1 = Base.Vector(h_arc_x, 0.0, h_arc_z)
    Pnt2 = Base.Vector(dk_max / 2.0, 0.0, he)
    Pnt3 = Base.Vector(dk_max / 2.0, 0.0, 0.0)
    Pnt4 = Base.Vector(dia / 2.0 + r, 0.0, 0.0)  # start of fillet between head and shank
    Pnt5 = Base.Vector(dia / 2.0 + r - r * sqrt2_, 0.0, -r + r * sqrt2_)  # arc-point of fillet
    Pnt6 = Base.Vector(dia / 2.0, 0.0, -r)  # end of fillet
    Pnt7 = Base.Vector(dia / 2.0, 0.0, -thread_start)  # Start of thread
    # FreeCAD.Console.PrintMessage("Points defined a_point: " + str(a_point) + "\n")

    if SType == 'ISO14583':
        # Pnt0 = Base.Vector(0.0,0.0,k-A/4.0)
        Pnt0 = Base.Vector(0.0, 0.0, k - A / 8.0)
        PntFlat = Base.Vector(A / 8.0, 0.0, k - A / 8.0)
        PntCham = Base.Vector(A / 1.99, 0.0, k)
        edgeCham0 = Part.makeLine(Pnt0, PntFlat)
        edgeCham1 = Part.makeLine(PntFlat, PntCham)
        edgeCham2 = Part.Arc(PntCham, Pnt1, Pnt2).toShape()
        # edge1 = Part.Wire([edgeCham0,edgeCham1,edgeCham2])
        edge1 = Part.Wire([edgeCham0, edgeCham1])
        edge2 = Part.makeLine(Pnt2, Pnt3)
        edge2 = Part.Wire([edgeCham2, edge2])
        # Part.show(edge2)

        # Here is the next approach to shorten the head building time
        # Make two helper points to create a cutting tool for the
        # recess and recess shell.
        PntH1 = Base.Vector(A / 1.99, 0.0, 2.0 * k)
        PntH2 = Base.Vector(0.0, 0.0, 2.0 * k)
        edgeH1 = Part.makeLine(PntCham, PntH1)
        edgeH2 = Part.makeLine(PntH1, PntH2)
        edgeH3 = Part.makeLine(PntH2, Pnt0)

    else:
        Pnt0 = Base.Vector(0.0, 0.0, k)
        edge1 = Part.Arc(Pnt0, Pnt1, Pnt2).toShape()  # make round head
        edge2 = Part.makeLine(Pnt2, Pnt3)

        # Here is the next approach to shorten the head building time
        # Make two helper points to create a cutting tool for the
        # recess and recess shell.
        PntH1 = Base.Vector(dk_max / 2.0, 0.0, 2.0 * k)
        PntH2 = Base.Vector(0.0, 0.0, 2.0 * k)
        edgeH1 = Part.makeLine(Pnt2, PntH1)
        edgeH2 = Part.makeLine(PntH1, PntH2)
        edgeH3 = Part.makeLine(PntH2, Pnt0)

    edge3 = Part.makeLine(Pnt3, Pnt4)
    edge4 = Part.Arc(Pnt4, Pnt5, Pnt6).toShape()
    # FreeCAD.Console.PrintMessage("Edges made h_arc_z: " + str(h_arc_z) + "\n")

    # if self.RealThread.isChecked():
    if fa.thread:
        aWire = Part.Wire([edge2, edge3, edge4])
    else:
        # bolt points
        PntB1 = Base.Vector(dia / 2.0, 0.0, -l)
        PntB2 = Base.Vector(0.0, 0.0, -l)
        edgeB2 = Part.makeLine(PntB1, PntB2)
        if thread_start <= (r + 0.00001):
            edgeB1 = Part.makeLine(Pnt6, PntB1)
            aWire = Part.Wire([edge2, edge3, edge4, edgeB1, edgeB2])
        else:
            edge5 = Part.makeLine(Pnt6, Pnt7)
            edgeB1 = Part.makeLine(Pnt7, PntB1)
            aWire = Part.Wire([edge2, edge3, edge4, edge5, edgeB1, edgeB2])

    hWire = Part.Wire([edge1, edgeH1, edgeH2, edgeH3])  # Cutter for recess-Shell
    hFace = Part.Face(hWire)
    hCut = hFace.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360)
    # Part.show(hWire)

    headShell = aWire.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360)
    # head = Part.Solid(headShell)
    # Part.show(aWire)
    # FreeCAD.Console.PrintMessage("the head with revolve: " + str(dia) + "\n")
    headFaces = headShell.Faces

    if SType == 'ISO14583':
        recess, recessShell = self.makeIso10664_3(tt, t_mean, k)
        recessShell = recessShell.cut(hCut)
        topFace = hCut.Faces[1]
        topFace = topFace.cut(recess)
        # Part.show(topFace)
        # Part.show(recessShell)
        # Part.show(headShell)
        headFaces.append(topFace.Faces[0])
        # headFaces.append(hCut.Faces[2])

    else:
        # Lengths and angles for calculation of recess positioning
        beta_cr = math.asin(mH / 2.0 / rf)  # angle of recess edge
        tan_beta_cr = math.tan(beta_cr)
        # height of cross recess cutting
        hcr = k - rf + (mH / 2.0) / tan_beta_cr
        # print 'hcr: ', hcr

        # Parameter for cross-recess type H: cT, mH
        recess, recessShell = self.makeCross_H3(cT, mH, hcr)
        recessShell = recessShell.cut(hCut)
        topFace = hCut.Faces[0]
        topFace = topFace.cut(recess)
        # Part.show(topFace)
        # Part.show(recessShell)
        # Part.show(headShell)
        headFaces.append(topFace.Faces[0])

    # Part.show(hCut)
    headFaces.extend(recessShell.Faces)

    # if self.RealThread.isChecked():
    if fa.thread:
        # head = self.cutIsoThread(head, dia, P, turns, l)
        rthread = self.makeShellthread(dia, P, l - r, False, -r, b)
        # head = head.fuse(rthread)
        # Part.show(rthread)
        for threadFace in rthread.Faces:
            headFaces.append(threadFace)

    newHeadShell = Part.Shell(headFaces)
    # Part.show(newHeadShell)
    head = Part.Solid(newHeadShell)

    return head
