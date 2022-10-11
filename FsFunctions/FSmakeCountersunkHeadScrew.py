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


# used for ISO 7046 countersunk flat head screws with H cross recess
# also used for ISO 7047 raised countersunk head screws with H cross recess
# also used for ISO 10642 Hexagon socket countersunk head screws
# also used for ISO 14582 Hexalobular socket countersunk head screws, high head
# also used for ISO 14584 Hexalobular socket raised countersunk head screws
# also used for ASMEB18.3.2 UNC Hexagon socket countersunk head screws

def makeCountersunkHeadScrew(self, fa): # dynamically loaded method of class Screw
    SType = fa.type
    l = fa.calc_len
    dia = self.getDia(fa.calc_diam, False)
    # FreeCAD.Console.PrintMessage("der 2009Kopf mit l: " + str(l) + "\n")
    if SType == 'ISO10642':
        P, b, dk_theo, dk_mean, da, ds_min, e, k, r, s_mean, t, w = fa.dimTable
        ePrax = s_mean / math.sqrt(3.0) / 0.99
        ht = 0.0
        a = 2 * P
        t_mean = t
    elif SType == 'ASMEB18.3.2':
        P, b, dk_theo, dk_mean, k, r, s_mean, t = fa.dimTable
        ePrax = s_mean / math.sqrt(3.0) / 0.99
        ht = 0.0
        a = 2 * P
        t_mean = t
    else:  # still need the data from iso2009def, but this screw can not created here
        P, a, b, dk_theo, dk_mean, k, n_min, r, t_mean, x = FsData["ISO2009def"][fa.calc_diam]
        ht = 0.0  # Head height of flat head
    if SType == 'ISO7046':
        cT, mH, mZ = FsData["ISO7046extra"][fa.calc_diam]
    if SType == 'ISO7047':
        rf, t_mean, cT, mH, mZ = FsData["Raised_countersunk_def"][fa.calc_diam]
        # Lengths and angles for calculation of head rounding
        beta = math.asin(dk_mean / 2.0 / rf)  # angle of head edge
        tan_beta = math.tan(beta)
        alpha = beta / 2.0  # half angle
        # height of raised head top
        ht = rf - (dk_mean / 2.0) / tan_beta
        # print 'he: ', he
        h_arc_x = rf * math.sin(alpha)
        h_arc_z = ht - rf + rf * math.cos(alpha)
        # FreeCAD.Console.PrintMessage("h_arc_z: " + str(h_arc_z) + "\n")

    if SType == 'ISO14582':
        P, a, b, dk_theo, dk_mean, k, r, tt, A, t_mean = fa.dimTable
        ePrax = A / 2.0 / 0.99

    if SType == 'ISO14584':
        P, b, dk_theo, dk_mean, f, k, r, rf, x, tt, A, t_mean = fa.dimTable
        ePrax = A / 2.0 / 0.99
        # Lengths and angles for calculation of head rounding
        beta = math.asin(dk_mean / 2.0 / rf)  # angle of head edge
        tan_beta = math.tan(beta)
        ctp = - (dk_mean / 2.0) / tan_beta  # Center Top Edge = center for rf
        betaA = math.asin(ePrax / rf)  # angle of head edge at start of recess
        ht = ctp + ePrax / math.tan(betaA)
        alpha = betaA + (beta - betaA) / 2.0  # half angle of top Arc
        h_arc_x = rf * math.sin(alpha)
        h_arc_z = ctp + rf * math.cos(alpha)

    # FreeCAD.Console.PrintMessage("the head with iso r: " + str(r) + "\n")
    cham = (dk_theo - dk_mean) / 2.0
    rad225 = math.radians(22.5)
    rad45 = math.radians(45.0)
    rtan = r * math.tan(rad225)
    # FreeCAD.Console.PrintMessage("Checking rtan: " + str(rtan) + "\n")

    # Head Points
    Pnt1 = Base.Vector(dk_mean / 2.0, 0.0, 0.0)
    Pnt2 = Base.Vector(dk_mean / 2.0, 0.0, -cham)
    Pnt3 = Base.Vector(dia / 2.0 + r - r * math.cos(rad45), 0.0, -k - rtan + r * math.sin(rad45))

    # Arc-points
    Pnt4 = Base.Vector(dia / 2.0 + r - r * (math.cos(rad225)), 0.0, -k - rtan + r * math.sin(rad225))
    Pnt5 = Base.Vector(dia / 2.0, 0.0, -k - rtan)

    flat_len = l + Pnt5.z
    thread_start = -l + b
    Pnt6 = Base.Vector(dia / 2.0, 0.0, thread_start)

    if SType == 'ISO10642' or SType == 'ISO14582' or SType == 'ASMEB18.3.2':
        if SType == 'ISO10642' or SType == 'ASMEB18.3.2':
            recess, recessShell = self.makeAllen2(s_mean, t_mean, 0.0)
            Pnt0 = Base.Vector(ePrax / 2.0, 0.0, -ePrax / 2.0)
            PntCham = Base.Vector(ePrax, 0.0, 0.0)
            edge1 = Part.makeLine(Pnt0, PntCham)
            edgeCham2 = Part.makeLine(PntCham, Pnt1)
            edge2 = Part.makeLine(Pnt1, Pnt2)
            edge2 = Part.Wire([edgeCham2, edge2])
            PntH0 = Base.Vector(ePrax / 2.0, 0.0, ht + k)
            PntH1 = Base.Vector(ePrax, 0.0, ht + k)
        if SType == 'ISO14582':
            recess, recessShell = self.makeIso10664_3(tt, t_mean, 0.0)  # hexalobular recess
            Pnt0 = Base.Vector(0.0, 0.0, 0.0)
            edge1 = Part.makeLine(Pnt0, Pnt1)
            edge2 = Part.makeLine(Pnt1, Pnt2)

        # bolt points with bolt chamfer
        cham_b = P * math.sqrt(3.0) / 2.0 * 17.0 / 24.0

        PntB1 = Base.Vector(dia / 2.0, 0.0, -l + cham_b)
        PntB2 = Base.Vector(dia / 2.0 - cham_b, 0.0, -l)
        PntB3 = Base.Vector(0.0, 0.0, -l)
        if thread_start >= Pnt5.z:
            edgeB0 = Part.makeLine(Pnt5, PntB1)
        else:
            edgeB0 = Part.makeLine(Pnt6, PntB1)
        edgeB2 = Part.makeLine(PntB1, PntB2)
        edgeB3 = Part.makeLine(PntB2, PntB3)
        edgeB1 = Part.Wire([edgeB2, edgeB3])

    else:
        # bolt points
        PntB1 = Base.Vector(dia / 2.0, 0.0, -l)
        PntB2 = Base.Vector(0.0, 0.0, -l)
        if thread_start >= Pnt5.z:
            edgeB0 = Part.makeLine(Pnt5, PntB1)
        else:
            edgeB0 = Part.makeLine(Pnt6, PntB1)
        edgeB1 = Part.makeLine(PntB1, PntB2)

        if SType == 'ISO7047':  # make raised head rounding
            Pnt0 = Base.Vector(0.0, 0.0, ht)
            Pnt0arc = Base.Vector(h_arc_x, 0.0, h_arc_z)
            edge1 = Part.Arc(Pnt0, Pnt0arc, Pnt1).toShape()
            edge2 = Part.makeLine(Pnt1, Pnt2)
            PntH0 = Base.Vector(0.0, 0.0, ht + k)
            PntH1 = Base.Vector(dk_mean / 2.0, 0.0, ht + k)
            recess, recessShell = self.makeCross_H3(cT, mH, ht)
        if SType == 'ISO7046':
            # ISO7046
            Pnt0 = Base.Vector(0.0, 0.0, ht)
            edge1 = Part.makeLine(Pnt0, Pnt1)  # make flat head
            edge2 = Part.makeLine(Pnt1, Pnt2)
            recess, recessShell = self.makeCross_H3(cT, mH, ht)

        if SType == 'ISO14584':  # make raised head rounding with chamfer
            Pnt0 = Base.Vector(ePrax / 2.0, 0.0, ht - ePrax / 4.0)
            PntCham = Base.Vector(ePrax, 0.0, ht)
            PntArc = Base.Vector(h_arc_x, 0.0, h_arc_z)
            edge1 = Part.makeLine(Pnt0, PntCham)
            edgeArc = Part.Arc(PntCham, PntArc, Pnt1).toShape()
            edge2 = Part.makeLine(Pnt1, Pnt2)
            edge2 = Part.Wire([edgeArc, edge2])
            PntH0 = Base.Vector(ePrax / 2.0, 0.0, ht + k)
            PntH1 = Base.Vector(ePrax, 0.0, ht + k)
            recess, recessShell = self.makeIso10664_3(tt, t_mean, ht)  # hexalobular recess

    edge3 = Part.makeLine(Pnt2, Pnt3)
    edgeArc = Part.Arc(Pnt3, Pnt4, Pnt5).toShape()
    edgeArc1 = Part.makeLine(Pnt3, Pnt4)
    edgeArc2 = Part.makeLine(Pnt4, Pnt5)
    edge6 = Part.makeLine(Pnt5, Pnt6)

    if fa.thread:
        # aWire=Part.Wire([edge1,edge2,edge3,edgeArc])
        aWire = Part.Wire([edge2, edge3, edgeArc])
    else:
        if thread_start >= Pnt5.z:
            aWire = Part.Wire([edge2, edge3, edgeArc, edgeB0, edgeB1])
        else:
            aWire = Part.Wire([edge2, edge3, edgeArc, edge6, edgeB0, edgeB1])

    # Part.show(aWire)
    headShell = self.RevolveZ(aWire)
    headFaces = headShell.Faces
    # Part.show(headShell)

    if SType == 'ISO7046' or SType == 'ISO14582':
        # hCut is just a cylinder for ISO7046
        hCut = Part.makeCylinder(dk_mean / 2.0, k, Pnt0)
        # Part.show(hCut)
        topFace = hCut.Faces[2]
    else:
        edgeH1 = Part.makeLine(Pnt1, PntH1)
        edgeH2 = Part.makeLine(PntH1, PntH0)
        edgeH3 = Part.makeLine(PntH0, Pnt0)
        edgeH4 = Part.makeLine(PntCham, Pnt1)
        hWire = Part.Wire([edge1, edgeH3, edgeH2, edgeH1, edgeH4])  # Cutter for recess-Shell
        hWire.reverse()  # a fix to work with ver 18
        hFace = Part.Face(hWire)
        hCut = self.RevolveZ(hFace)
        # Part.show(hWire)
        topFace = hCut.Faces[0]

    recessShell = recessShell.cut(hCut)
    topFace = topFace.cut(recess)
    # Part.show(topFace)
    # Part.show(recessShell)
    # Part.show(headShell)
    headFaces.append(topFace.Faces[0])
    headFaces.extend(recessShell.Faces)

    if SType == 'ISO10642' or SType == 'ISO14582' or SType == 'ASMEB18.3.2':
        if fa.thread:
            # if True:
            rthread = self.makeShellthread(dia, P, flat_len, True, Pnt5.z, b)
            # head = head.fuse(rthread)
            # Part.show(rthread)
            for threadFace in rthread.Faces:
                headFaces.append(threadFace)

            screwShell = Part.Shell(headFaces)
            screw = Part.Solid(screwShell)
        else:
            screwShell = Part.Shell(headFaces)
            screw = Part.Solid(screwShell)

    else:
        if fa.thread:
            rthread = self.makeShellthread(dia, P, flat_len, False, Pnt5.z, b)
            # head = head.fuse(rthread)
            # Part.show(rthread)
            for threadFace in rthread.Faces:
                headFaces.append(threadFace)

        screwShell = Part.Shell(headFaces)
        screw = Part.Solid(screwShell)

    return screw

def init():
    Screw.makeCountersunkHeadScrew = makeCountersunkHeadScrew
