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

# make ISO 2009 Slotted countersunk flat head screws
# make ISO 2010 Slotted raised countersunk head screws
# make ISO 1580 Pan head slotted screw (Code is nearly identical to iso1207)
# make ASMEB18.6.3.1A Slotted countersunk flat head screws

def makeSlottedScrew(self): # dynamically loaded method of class Screw
    dia = self.getDia(self.fastenerDiam, False)
    SType = self.fastenerType
    l = self.fastenerLen
    if SType == 'ISO1580':
        # FreeCAD.Console.PrintMessage("the head with l: " + str(l) + "\n")
        P, a, b, dk_max, da, k, n_min, r, rf, t_min, x = self.dimTable
        # FreeCAD.Console.PrintMessage("the head with iso: " + str(dk_max) + "\n")
        ht = k

        # Length for calculation of head fillet
        sqrt2_ = 1.0 / math.sqrt(2.0)
        r_fil = rf
        beta = math.radians(5.0)  # angle of pan head edge
        alpha = math.radians(90.0 - (90.0 + 5.0) / 2.0)
        tan_beta = math.tan(beta)
        # top head diameter without fillet
        rK_top = dk_max / 2.0 - k * tan_beta
        fillet_center_x = rK_top - r_fil + r_fil * tan_beta
        fillet_center_z = k - r_fil
        fillet_arc_x = fillet_center_x + r_fil * math.sin(alpha)
        fillet_arc_z = fillet_center_z + r_fil * math.cos(alpha)
        # FreeCAD.Console.PrintMessage("rK_top: " + str(rK_top) + "\n")

        # Head Points
        Pnt0 = Base.Vector(0.0, 0.0, k)
        Pnt2 = Base.Vector(fillet_center_x, 0.0, k)
        Pnt3 = Base.Vector(fillet_arc_x, 0.0, fillet_arc_z)
        Pnt4 = Base.Vector(fillet_center_x + r_fil * math.cos(beta), 0.0, fillet_center_z + r_fil * math.sin(beta))
        Pnt5 = Base.Vector(dk_max / 2.0, 0.0, 0.0)
        Pnt6 = Base.Vector(dia / 2.0 + r, 0.0, 0.0)  # start of fillet between head and shank
        Pnt7 = Base.Vector(dia / 2.0 + r - r * sqrt2_, 0.0, -r + r * sqrt2_)  # arc-point of fillet
        # Pnt8 = Base.Vector(dia/2.0,0.0,-r)        # end of fillet
        PntR = Base.Vector(dia / 2.0, 0.0, -r)  # end of fillet
        PntT0 = Base.Vector(0.0, 0.0, -r)  # helper point for real thread

        edge1 = Part.makeLine(Pnt0, Pnt2)
        edge2 = Part.Arc(Pnt2, Pnt3, Pnt4).toShape()
        edge3 = Part.makeLine(Pnt4, Pnt5)
        edge4 = Part.makeLine(Pnt5, Pnt6)
        edge5 = Part.Arc(Pnt6, Pnt7, PntR).toShape()
        headWire = Part.Wire([edge1, edge2, edge3, edge4, edge5])

    if SType == 'ISO2009' or SType == 'ISO2010' or SType == 'ASMEB18.6.3.1A':
        if SType == 'ISO2009' or SType == 'ISO2010':
            P, a, b, dk_theo, dk_mean, k, n_min, r, t_mean, x = self.dimTable
        elif SType == 'ASMEB18.6.3.1A':
            P, b, dk_theo, dk_mean, k, n_min, r, t_mean = self.dimTable
        dk_max = dk_theo
        t_min = t_mean
        ht = 0.0  # Head height of flat head
        if SType == 'ISO2010':
            rf, t_mean, cT, mH, mZ = FsData["Raised_countersunk_def"][self.fastenerDiam]
            # Lengths and angles for calculation of head rounding
            beta = math.asin(dk_mean / 2.0 / rf)  # angle of head edge
            tan_beta = math.tan(beta)
            alpha = beta / 2.0  # half angle
            # height of raised head top
            ht = rf - (dk_mean / 2.0) / tan_beta
            h_arc_x = rf * math.sin(alpha)
            h_arc_z = ht - rf + rf * math.cos(alpha)

        cham = (dk_theo - dk_mean) / 2.0
        rad225 = math.radians(22.5)
        rad45 = math.radians(45.0)
        rtan = r * math.tan(rad225)

        # Head Points
        Pnt0 = Base.Vector(0.0, 0.0, ht)
        Pnt1 = Base.Vector(dk_mean / 2.0, 0.0, 0.0)
        Pnt2 = Base.Vector(dk_mean / 2.0, 0.0, -cham)
        Pnt3 = Base.Vector(dia / 2.0 + r - r * math.cos(rad45), 0.0, -k - rtan + r * math.sin(rad45))
        # Arc-points
        Pnt4 = Base.Vector(dia / 2.0 + r - r * (math.cos(rad225)), 0.0, -k - rtan + r * math.sin(rad225))
        PntR = Base.Vector(dia / 2.0, 0.0, -k - rtan)
        # PntA = Base.Vector(dia/2.0,0.0,-a_point)
        PntT0 = Base.Vector(0.0, 0.0, -k - rtan)  # helper point for real thread

        if SType == 'ISO2010':  # make raised head rounding
            Pnt0arc = Base.Vector(h_arc_x, 0.0, h_arc_z)
            edge1 = Part.Arc(Pnt0, Pnt0arc, Pnt1).toShape()
        else:
            edge1 = Part.makeLine(Pnt0, Pnt1)  # make flat head

        edge2 = Part.makeLine(Pnt1, Pnt2)
        edge3 = Part.makeLine(Pnt2, Pnt3)
        edgeArc = Part.Arc(Pnt3, Pnt4, PntR).toShape()
        headWire = Part.Wire([edge1, edge2, edge3, edgeArc])

    flat_len = l + PntT0.z
    thread_start = -l + b
    PntA = Base.Vector(dia / 2.0, 0.0, thread_start)  # Start of thread

    if self.rThread:
        edgeZ1 = Part.makeLine(PntR, PntT0)
        edgeZ0 = Part.makeLine(PntT0, Pnt0)
        aWire = Part.Wire([headWire, edgeZ1, edgeZ0])

    else:
        # bolt points
        PntB1 = Base.Vector(dia / 2.0, 0.0, -l)
        PntB2 = Base.Vector(0.0, 0.0, -l)

        edgeB2 = Part.makeLine(PntB1, PntB2)
        edgeZ0 = Part.makeLine(PntB2, Pnt0)

        if thread_start >= PntT0.z:
            edgeB1 = Part.makeLine(PntR, PntB1)
            aWire = Part.Wire([headWire, edgeB1, edgeB2, edgeZ0])
        else:
            edgeRA = Part.makeLine(PntR, PntA)
            edgeB1 = Part.makeLine(PntA, PntB1)
            aWire = Part.Wire([headWire, edgeRA, edgeB1, edgeB2, edgeZ0])

    aFace = Part.Face(aWire)
    head = aFace.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360)
    # FreeCAD.Console.PrintMessage("the head with revolve: " + str(dia) + "\n")

    # Parameter for slot-recess: dk_max, n_min, k, t_min
    slot = Part.makePlane(dk_max, n_min, \
                            Base.Vector(dk_max / 2.0, -n_min / 2.0, ht + 1.0), Base.Vector(0.0, 0.0, -1.0))
    slot = slot.extrude(Base.Vector(0.0, 0.0, -t_min - 1.0))
    # Part.show(slot)
    head = head.cut(slot)
    # FreeCAD.Console.PrintMessage("the head cut: " + str(dia) + "\n")
    # Part.show(head)

    # FreeCAD.Console.PrintMessage("flatlen:" + str(flat_len) + "   b:" + str(b) + "   r:" + str(r) + "   a:" + str(a_point) + "\n")
    if self.rThread:
        rthread = self.makeShellthread(dia, P, flat_len, False, PntT0.z, b)
        headFaces = []
        if SType == 'ISO2009' or SType == 'ASMEB18.6.3.1A':
            for i in range(0, len(head.Faces) - 2):
                headFaces.append(head.Faces[i])
            headFaces.append(head.Faces[len(head.Faces) - 1])

        if SType == 'ISO1580' or SType == 'ISO2010':
            for i in range(0, len(head.Faces) - 1):
                headFaces.append(head.Faces[i])
        # Part.show(Part.Shell(headFaces))
    
        for threadFace in rthread.Faces:
            headFaces.append(threadFace)

        newHeadShell = Part.Shell(headFaces)
        # Part.show(newHeadShell)
        head = Part.Solid(newHeadShell)

    return head
