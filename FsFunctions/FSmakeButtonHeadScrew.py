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

# make ISO 7380-1 Button head Screw
# make ISO 7380-2 Button head Screw with collar
# make DIN 967 cross recessed pan head Screw with collar
# make ASMEB18.3.3A UNC Hex socket button head screws
# make ASMEB18.3.3B UNC Hex socket button head screws with flange

def makeButtonHeadScrew(self): # dynamically loaded method of class Screw
    SType = self.fastenerType
    l = self.fastenerLen
    dia = self.getDia(self.fastenerDiam, False)
    # todo: different radii for screws with thread to head or with shaft?
    sqrt2_ = 1.0 / math.sqrt(2.0)

    if SType == 'DIN967':
        P, b, c, da, dk, r, k, rf, x, cT, mH, mZ = self.dimTable

        rH = rf  # radius of button arc
        alpha = math.acos((rf - k + c) / rf)

        # Head Points
        Pnt0 = Base.Vector(0.0, 0.0, k)
        PntArc = Base.Vector(rf * math.sin(alpha / 2.0), 0.0,
                                k - rf + rf * math.cos(alpha / 2.0))  # arc-point of button
        Pnt1 = Base.Vector(rf * math.sin(alpha), 0.0, c)  # end of button arc
        PntC0 = Base.Vector((dk) / 2.0, 0.0, c)  # collar points
        PntC2 = Base.Vector((dk) / 2.0, 0.0, 0.0)  # collar points
        Pnt4 = Base.Vector(dia / 2.0 + r, 0.0, 0.0)  # start of fillet between head and shank

        edge1 = Part.Arc(Pnt0, PntArc, Pnt1).toShape()
        edgeC0 = Part.makeLine(Pnt1, PntC0)
        edgeC1 = Part.makeLine(PntC0, PntC2)
        edge2 = Part.Wire([edgeC0, edgeC1])
        edge3 = Part.makeLine(PntC2, Pnt4)
        # Points for recessShell cutter
        PntH0 = Base.Vector(0.0, 0.0, 2.0 * k)
        PntH1 = Base.Vector(rf * math.sin(alpha), 0.0, 2.0 * k)
        recess, recessShell = self.makeCross_H3(cT, mH, k)

    else:
        if SType == 'ISO7380-1':
            P, b, a, da, dk, dk_mean, s_mean, t_min, r, k, e, w = self.dimTable

            # Bottom of recess
            e_cham = 2.0 * s_mean / math.sqrt(3.0) / 0.99
            # depth = s_mean / 3.0

            ak = -(4 * k ** 2 + e_cham ** 2 - dk ** 2) / (8 * k)  # helper value for button arc
            rH = math.sqrt((dk / 2.0) ** 2 + ak ** 2)  # radius of button arc
            alpha = (math.atan(2 * (k + ak) / e_cham) + math.atan((2 * ak) / dk)) / 2

            Pnt2 = Base.Vector(rH * math.cos(alpha), 0.0, -ak + rH * math.sin(alpha))  # arc-point of button
            Pnt3 = Base.Vector(dk / 2.0, 0.0, 0.0)  # end of fillet
            Pnt4 = Base.Vector(dia / 2.0 + r, 0.0, 0.0)  # start of fillet between head and shank
            edge3 = Part.makeLine(Pnt3, Pnt4)

        if SType == 'ASMEB18.3.3A':
            P, b, da, dk, s_mean, t_min, r, k = self.dimTable
            # Bottom of recess
            e_cham = 2.0 * s_mean / math.sqrt(3.0) / 0.99
            # depth = s_mean / 3.0
            ak = -(4 * k ** 2 + e_cham ** 2 - dk ** 2) / (8 * k)  # helper value for button arc
            rH = math.sqrt((dk / 2.0) ** 2 + ak ** 2)  # radius of button arc
            alpha = (math.atan(2 * (k + ak) / e_cham) + math.atan((2 * ak) / dk)) / 2
            Pnt2 = Base.Vector(rH * math.cos(alpha), 0.0, -ak + rH * math.sin(alpha))  # arc-point of button
            Pnt3 = Base.Vector(dk / 2.0, 0.0, 0.0)  # end of fillet
            Pnt4 = Base.Vector(dia / 2.0 + r, 0.0, 0.0)  # start of fillet between head and shank
            edge3 = Part.makeLine(Pnt3, Pnt4)

        if SType == 'ISO7380-2' or SType == 'ASMEB18.3.3B':
            if SType == 'ISO7380-2':
                P, b, c, da, dk, dk_c, s_mean, t_min, r, k, e, w = self.dimTable
            if SType == 'ASMEB18.3.3B':
                P, b, c, dk, dk_c, s_mean, t_min, r, k = self.dimTable

            # Bottom of recess
            e_cham = 2.0 * s_mean / math.sqrt(3.0) / 0.99
            # depth = s_mean / 3.0

            ak = -(4 * (k - c) ** 2 + e_cham ** 2 - dk ** 2) / (8 * (k - c))  # helper value for button arc
            rH = math.sqrt((dk / 2.0) ** 2 + ak ** 2)  # radius of button arc
            alpha = (math.atan(2 * (k - c + ak) / e_cham) + math.atan((2 * ak) / dk)) / 2

            Pnt2 = Base.Vector(rH * math.cos(alpha), 0.0, c - ak + rH * math.sin(alpha))  # arc-point of button
            Pnt3 = Base.Vector(dk / 2.0, 0.0, c)  # end of fillet
            Pnt4 = Base.Vector(dia / 2.0 + r, 0.0, 0.0)  # start of fillet between head and shank
            PntC0 = Base.Vector((dk_c - c) / 2.0, 0.0, c)  # collar points
            PntC1 = Base.Vector(dk_c / 2.0, 0.0, c / 2.0)  # collar points
            PntC2 = Base.Vector((dk_c - c) / 2.0, 0.0, 0.0)  # collar points

            edgeC0 = Part.makeLine(Pnt3, PntC0)
            edgeC1 = Part.Arc(PntC0, PntC1, PntC2).toShape()
            edge3 = Part.makeLine(PntC2, Pnt4)
            edge3 = Part.Wire([edgeC0, edgeC1, edge3])

        # Head Points
        Pnt0 = Base.Vector(e_cham / 4.0, 0.0, k - e_cham / 4.0)  # Center Point for chamfer
        Pnt1 = Base.Vector(e_cham / 2.0, 0.0, k)  # inner chamfer edge at head
        # Points for recessShell cutter
        PntH0 = Base.Vector(e_cham / 4.0, 0.0, 2.0 * k)
        PntH1 = Base.Vector(e_cham / 2.0, 0.0, 2.0 * k)

        edge1 = Part.makeLine(Pnt0, Pnt1)
        edge2 = Part.Arc(Pnt1, Pnt2, Pnt3).toShape()
        recess, recessShell = self.makeAllen2(s_mean, t_min, k)

    thread_start = l - b

    Pnt5 = Base.Vector(dia / 2.0 + r - r * sqrt2_, 0.0, -r + r * sqrt2_)  # arc-point of fillet
    Pnt6 = Base.Vector(dia / 2.0, 0.0, -r)  # end of fillet
    Pnt7 = Base.Vector(dia / 2.0, 0.0, -thread_start)  # start of thread

    edge4 = Part.Arc(Pnt4, Pnt5, Pnt6).toShape()
    edge5 = Part.makeLine(Pnt6, Pnt7)

    if SType == 'DIN967':
        # bolt points
        PntB1 = Base.Vector(dia / 2.0, 0.0, -l)
        PntB2 = Base.Vector(0.0, 0.0, -l)
        edgeB2 = Part.makeLine(PntB1, PntB2)
    else:
        # bolt points
        cham_b = P * math.sqrt(3.0) / 2.0 * 17.0 / 24.0

        PntB1 = Base.Vector(dia / 2.0, 0.0, -l + cham_b)
        PntB2 = Base.Vector(dia / 2.0 - cham_b, 0.0, -l)
        PntB3 = Base.Vector(0.0, 0.0, -l)

        edgeB2 = Part.makeLine(PntB1, PntB2)
        edgeB3 = Part.makeLine(PntB2, PntB3)
        edgeB2 = Part.Wire([edgeB2, edgeB3])

    if self.rThread:
        aWire = Part.Wire([edge2, edge3, edge4])
    else:
        if thread_start <= r:
            edgeB1 = Part.makeLine(Pnt6, PntB1)
            aWire = Part.Wire([edge2, edge3, edge4, edgeB1, edgeB2])
        else:
            edge5 = Part.makeLine(Pnt6, Pnt7)
            edgeB1 = Part.makeLine(Pnt7, PntB1)
            aWire = Part.Wire([edge2, edge3, edge4, edge5, edgeB1, edgeB2])

    # Part.show(aWire)
    headShell = aWire.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360)
    # Part.show(headShell)
    headFaces = headShell.Faces

    edgeH1 = Part.makeLine(Pnt1, PntH1)
    edgeH2 = Part.makeLine(PntH1, PntH0)
    edgeH3 = Part.makeLine(PntH0, Pnt0)
    hWire = Part.Wire([edge1, edgeH1, edgeH2, edgeH3])  # Cutter for recess-Shell
    hFace = Part.Face(hWire)
    hCut = hFace.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360)
    # Part.show(hWire)
    topFace = hCut.Faces[0]

    recessShell = recessShell.cut(hCut)
    topFace = topFace.cut(recess)
    # Part.show(topFace)
    # Part.show(recessShell)
    # Part.show(headShell)
    headFaces.append(topFace.Faces[0])
    headFaces.extend(recessShell.Faces)

    if self.rThread:
        if SType == 'DIN967':
            rthread = self.makeShellthread(dia, P, l - r, False, -r, b)
        else:
            rthread = self.makeShellthread(dia, P, l - r, True, -r, b)
        for threadFace in rthread.Faces:
            headFaces.append(threadFace)

        screwShell = Part.Shell(headFaces)
        screw = Part.Solid(screwShell)
    else:
        screwShell = Part.Shell(headFaces)
        screw = Part.Solid(screwShell)

    return screw
