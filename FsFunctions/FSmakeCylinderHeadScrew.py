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

# make ISO 4762 Allan Screw head
# DIN 7984 Allan Screw head
# ISO 14579 Hexalobular socket head cap screws
# ASMEB18.3.1A Allan Screw head

def makeCylinderHeadScrew(self, fa): # dynamically loaded method of class Screw
    SType = fa.type
    l = fa.calc_len
    dia = self.getDia(fa.calc_diam, False)
    # FreeCAD.Console.PrintMessage("der 4762Kopf mit l: " + str(l) + "\n")
    # FreeCAD.Console.PrintMessage("the head with iso r: " + str(r) + "\n")
    if SType == 'ISO14579':
        P, b, dk_max, da, ds_mean, e, lf, k, r, s_mean, t, v, dw, w = FsData["ISO4762def"][fa.calc_diam]
        tt, A, t = fa.dimTable
        # Head Points 30° countersunk
        # Pnt0 = Base.Vector(0.0,0.0,k-A/4.0) #Center Point for countersunk
        Pnt0 = Base.Vector(0.0, 0.0, k - A / 8.0)  # Center Point for flat countersunk
        PntFlat = Base.Vector(A / 8.0, 0.0, k - A / 8.0)  # End of flat part
        Pnt1 = Base.Vector(A / 1.99, 0.0, k)  # countersunk edge at head
        edgeCham0 = Part.makeLine(Pnt0, PntFlat)
        edgeCham1 = Part.makeLine(PntFlat, Pnt1)
        edge1 = Part.Wire([edgeCham0, edgeCham1])

        # Here is the next approach to shorten the head building time
        # Make two helper points to create a cutting tool for the
        # recess and recess shell.
        PntH1 = Base.Vector(A / 1.99, 0.0, 2.0 * k)

    elif SType == 'DIN7984' or SType == 'ASMEB18.3.1G':
        if SType == 'DIN7984':
            P, b, dk_max, da, ds_min, e, k, r, s_mean, t, v, dw = fa.dimTable
        elif SType == 'ASMEB18.3.1G':
            P, b, A, H, C_max, J, T, K, r = (x*25.4 for x in fa.dimTable)
            dk_max = A
            k = H
            v = C_max
            s_mean = J
            t = T
            dw = A - K
        e_cham = 2.0 * s_mean / math.sqrt(3.0)
        # Head Points 45° countersunk
        Pnt0 = Base.Vector(0.0, 0.0, k - e_cham / 1.99 / 2.0)  # Center Point for countersunk
        PntFlat = Base.Vector(e_cham / 1.99 / 2.0, 0.0, k - e_cham / 1.99 / 2.0)  # End of flat part
        Pnt1 = Base.Vector(e_cham / 1.99, 0.0, k)  # countersunk edge at head
        edgeCham0 = Part.makeLine(Pnt0, PntFlat)
        edgeCham1 = Part.makeLine(PntFlat, Pnt1)
        edge1 = Part.Wire([edgeCham0, edgeCham1])
        PntH1 = Base.Vector(e_cham / 1.99, 0.0, 2.0 * k)

    elif SType == 'DIN6912':
        P, b, dk_max, da, ds_min, e, k, r, s_mean, t, t2, v, dw = fa.dimTable
        e_cham = 2.0 * s_mean / math.sqrt(3.0)
        # Head Points 45° countersunk
        Pnt0 = Base.Vector(0.0, 0.0, k - e_cham / 1.99 / 2.0)  # Center Point for countersunk
        PntFlat = Base.Vector(e_cham / 1.99 / 2.0, 0.0, k - e_cham / 1.99 / 2.0)  # End of flat part
        Pnt1 = Base.Vector(e_cham / 1.99, 0.0, k)  # countersunk edge at head
        edgeCham0 = Part.makeLine(Pnt0, PntFlat)
        edgeCham1 = Part.makeLine(PntFlat, Pnt1)
        edge1 = Part.Wire([edgeCham0, edgeCham1])
        PntH1 = Base.Vector(e_cham / 1.99, 0.0, 2.0 * k)

    elif SType == 'ISO4762' or SType == 'ASMEB18.3.1A':
        if SType == 'ISO4762':
            P, b, dk_max, da, ds_mean, e, lf, k, r, s_mean, t, v, dw, w = fa.dimTable
        if SType == 'ASMEB18.3.1A':
            P, b, dk_max, k, r, s_mean, t, v, dw = fa.dimTable
        e_cham = 2.0 * s_mean / math.sqrt(3.0)
        # Head Points 45° countersunk
        Pnt0 = Base.Vector(0.0, 0.0, k - e_cham / 1.99 / 2.0)  # Center Point for countersunk
        PntFlat = Base.Vector(e_cham / 1.99 / 2.0, 0.0, k - e_cham / 1.99 / 2.0)  # End of flat part
        Pnt1 = Base.Vector(e_cham / 1.99, 0.0, k)  # countersunk edge at head
        edgeCham0 = Part.makeLine(Pnt0, PntFlat)
        edgeCham1 = Part.makeLine(PntFlat, Pnt1)
        edge1 = Part.Wire([edgeCham0, edgeCham1])
        PntH1 = Base.Vector(e_cham / 1.99, 0.0, 2.0 * k)

    PntH2 = Base.Vector(0.0, 0.0, 2.0 * k)
    edgeH1 = Part.makeLine(Pnt1, PntH1)
    edgeH2 = Part.makeLine(PntH1, PntH2)
    edgeH3 = Part.makeLine(PntH2, Pnt0)
    hWire = Part.Wire([edge1, edgeH1, edgeH2, edgeH3])  # Cutter for recess-Shell
    hFace = Part.Face(hWire)
    hCut = self.RevolveZ(hFace)
    # Part.show(hWire)

    sqrt2_ = 1.0 / math.sqrt(2.0)
    # depth = s_mean / 3.0

    thread_start = l - b
    # rad30 = math.radians(30.0)
    # Head Points
    Pnt2 = Base.Vector(dk_max / 2.0 - v, 0.0, k)  # start of fillet
    Pnt3 = Base.Vector(dk_max / 2.0 - v + v * sqrt2_, 0.0, k - v + v * sqrt2_)  # arc-point of fillet
    Pnt4 = Base.Vector(dk_max / 2.0, 0.0, k - v)  # end of fillet
    Pnt5 = Base.Vector(dk_max / 2.0, 0.0, (dk_max - dw) / 2.0)  # we have a chamfer here
    Pnt6 = Base.Vector(dw / 2.0, 0.0, 0.0)  # end of chamfer
    Pnt7 = Base.Vector(dia / 2.0 + r, 0.0, 0.0)  # start of fillet between head and shank
    Pnt8 = Base.Vector(dia / 2.0 + r - r * sqrt2_, 0.0, -r + r * sqrt2_)  # arc-point of fillet
    Pnt9 = Base.Vector(dia / 2.0, 0.0, -r)  # end of fillet
    Pnt10 = Base.Vector(dia / 2.0, 0.0, -thread_start)  # start of thread

    edge1 = Part.makeLine(Pnt0, Pnt1)
    edge2 = Part.makeLine(Pnt1, Pnt2)
    edge3 = Part.Arc(Pnt2, Pnt3, Pnt4).toShape()
    edge4 = Part.makeLine(Pnt4, Pnt5)
    edge5 = Part.makeLine(Pnt5, Pnt6)
    edge6 = Part.makeLine(Pnt6, Pnt7)
    edge7 = Part.Arc(Pnt7, Pnt8, Pnt9).toShape()

    if fa.thread:
        aWire = Part.Wire([edge2, edge3, edge4, edge5, edge6, edge7])

    else:
        # bolt points
        cham_t = P * math.sqrt(3.0) / 2.0 * 17.0 / 24.0

        PntB1 = Base.Vector(dia / 2.0, 0.0, -l + cham_t)
        PntB2 = Base.Vector(dia / 2.0 - cham_t, 0.0, -l)
        PntB3 = Base.Vector(0.0, 0.0, -l)

        # edgeB1 = Part.makeLine(Pnt10,PntB1)
        edgeB2 = Part.makeLine(PntB1, PntB2)
        edgeB3 = Part.makeLine(PntB2, PntB3)

        if thread_start <= (r + 0.0001):
            edgeB1 = Part.makeLine(Pnt9, PntB1)
            aWire = Part.Wire([edge2, edge3, edge4, edge5, edge6, edge7, \
                                edgeB1, edgeB2, edgeB3])
        else:
            edge8 = Part.makeLine(Pnt9, Pnt10)
            edgeB1 = Part.makeLine(Pnt10, PntB1)
            aWire = Part.Wire([edge2, edge3, edge4, edge5, edge6, edge7, edge8, \
                                edgeB1, edgeB2, edgeB3])
        # Part.show(aWire)

    headShell = self.RevolveZ(aWire)
    # head = Part.Solid(headShell)
    # Part.show(aWire)
    # FreeCAD.Console.PrintMessage("the head with revolve: " + str(dia) + "\n")
    headFaces = headShell.Faces

    # Hex cutout
    if SType == 'ISO14579':
        # recess = self.makeIso10664(tt, t, k) # hexalobular recess
        recess, recessShell = self.makeIso10664_3(tt, t, k)  # hexalobular recess
    elif SType == 'DIN6912':
        recess, recessShell = self.makeAllen2(s_mean, t, k, t2)  # hex with center
    else:
        recess, recessShell = self.makeAllen2(s_mean, t, k)

    recessShell = recessShell.cut(hCut)
    topFace = hCut.Faces[1]
    # topFace = hCut.Faces[0]
    topFace = topFace.cut(recess)
    # Part.show(topFace)
    # Part.show(recessShell)
    # Part.show(headShell)
    headFaces.append(topFace.Faces[0])
    # headFaces.append(hCut.Faces[2])

    # allenscrew = head.cut(recess)
    # Part.show(hCut)
    headFaces.extend(recessShell.Faces)

    # if self.RealThread.isChecked():
    if fa.thread:
        # head = self.cutIsoThread(head, dia, P, turns, l)
        rthread = self.makeShellthread(dia, P, l - r, True, -r, b)
        # Part.show(rthread)
        for tFace in rthread.Faces:
            headFaces.append(tFace)
        headShell = Part.Shell(headFaces)
        allenscrew = Part.Solid(headShell)
    else:
        headShell = Part.Shell(headFaces)
        allenscrew = Part.Solid(headShell)

    return allenscrew
