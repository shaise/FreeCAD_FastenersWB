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

# make ISO 7379 Hexagon socket head shoulder screw

def makeShoulderScrew(self, fa): # dynamically loaded method of class Screw
    SType = fa.type
    l = fa.calc_len
    #if SType == 'ISO7379' or SType == 'ASMEB18.3.4':
    P, d1, d3, l2, l3, SW = fa.dimTable
    d2 = self.getDia(fa.calc_diam, False)
    l1 = l
    # define the fastener head and shoulder
    # applicable for both threaded and unthreaded versions
    point1 = Base.Vector(0, 0, l1 + l3)
    point2 = Base.Vector(d3 / 2 - 0.04 * d3, 0, l3 + l1)
    point3 = Base.Vector(d3 / 2, 0, l3 - 0.04 * d3 + l1)
    point4 = Base.Vector(d3 / 2, 0, l1)
    point5 = Base.Vector(d1 / 2, 0, l1)
    point6 = Base.Vector(d1 / 2 - 0.04 * d1, 0, l1 - 0.1 * l3)
    point7 = Base.Vector(d1 / 2, 0, l1 - 0.2 * l3)
    point8 = Base.Vector(d1 / 2, 0, 0)
    point9 = Base.Vector(d2 / 2, 0, 0)
    edge1 = Part.makeLine(point1, point2)
    edge2 = Part.makeLine(point2, point3)
    edge3 = Part.makeLine(point3, point4)
    edge4 = Part.makeLine(point4, point5)
    edge5 = Part.Arc(point5, point6, point7).toShape()
    edge6 = Part.makeLine(point7, point8)
    edge7 = Part.makeLine(point8, point9)
    top_face_profile = Part.Wire([edge1])
    top_face = self.RevolveZ(top_face_profile)
    head_shoulder_profile = Part.Wire([edge2, edge3, edge4, edge5, edge6, edge7])
    if not fa.thread:
        # if a modelled thread is not desired:
        # add a cylindrical section to represent the threads
        point10 = Base.Vector(d2 / 2 - 0.075 * d2, 0, -0.075 * l2)
        point11 = Base.Vector(d2 / 2, 0, -0.15 * l2)
        point12 = Base.Vector(d2 / 2, 0, -1 * l2 + 0.1 * d2)
        point13 = Base.Vector(d2 / 2 - 0.1 * d2, 0, -1 * l2)
        point14 = Base.Vector(0, 0, -1 * l2)
        edge8 = Part.Arc(point9, point10, point11).toShape()
        edge9 = Part.makeLine(point11, point12)
        edge10 = Part.makeLine(point12, point13)
        edge11 = Part.makeLine(point13, point14)
        # append the wire with the added section
        p_profile = Part.Wire([head_shoulder_profile, edge8, edge9, edge10, edge11])
        # revolve the profile into a shell object
        p_shell = self.RevolveZ(p_profile)
    else:
        # if we need a modelled thread:
        # the revolved profile is only the head and shoulder
        p_profile = head_shoulder_profile
        p_shell = self.RevolveZ(p_profile)
        # calculate the number of thread half turns
        # make the threaded section
        shell_thread = self.makeShellthread(d2, P, l2, True, 0)
        # FixMe: can be made better by cutting thread helix. 

        # combine the top & threaded section
        p_faces = p_shell.Faces
        p_faces.extend(shell_thread.Faces)
        p_shell = Part.Shell(p_faces)
    # make a hole for a hex key in the head
    hex_solid, hex_shell = self.makeAllen2(SW, l3 * 0.4, l3 + l1)
    top_face = top_face.cut(hex_solid)
    p_faces = p_shell.Faces
    p_faces.extend(top_face.Faces)
    hex_shell.translate(Base.Vector(0, 0, -1))
    p_faces.extend(hex_shell.Faces)
    p_shell = Part.Shell(p_faces)
    screw = Part.Solid(p_shell)
    # chamfer the hex recess
    cham_p1 = Base.Vector(0, 0, l3 + l1)
    cham_p2 = Base.Vector(SW / math.sqrt(3), 0, l3 + l1)
    cham_p3 = Base.Vector(0, 0, l3 + l1 - SW / math.sqrt(3))  # 45 degree chamfer
    cham_e1 = Part.makeLine(cham_p1, cham_p2)
    cham_e2 = Part.makeLine(cham_p2, cham_p3)
    cham_profile = Part.Wire([cham_e1, cham_e2])
    cham_shell = self.RevolveZ(cham_profile)
    cham_solid = Part.Solid(cham_shell)
    screw = screw.cut(cham_solid)
    return screw
