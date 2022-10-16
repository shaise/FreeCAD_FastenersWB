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

# make ISO 4026 Hexagon socket set screws with flat point
# make ISO 4027 Hexagon socket set screws with cone point
# make ISO 4028 Hexagon socket set screws with dog point
# make ISO 4029 Hexagon socket set screws with cup point
# make ASMEB18.3.5A UNC Hexagon socket set screws with flat point
# make ASMEB18.3.5B UNC Hexagon socket set screws with cone point
# make ASMEB18.3.5C UNC Hexagon socket set screws with dog point
# make ASMEB18.3.5D UNC Hexagon socket set screws with cup point

def makeSetScrew(self, fa): # dynamically loaded method of class Screw
    SType = fa.type
    l = fa.calc_len
    if SType == 'ISO4026' or SType == 'ISO4027' or SType == 'ISO4029':
        P, t, dp, dt, df, s = fa.dimTable
    elif SType == 'ISO4028':
        P, t, dp, df, z, s = fa.dimTable
    elif SType[:-1] == 'ASMEB18.3.5':
        P, t, dp, dt, df, s, z = fa.dimTable
    d = self.getDia(fa.calc_diam, False)
    d = d * 1.01
    # generate the profile of the set-screw
    if SType == 'ISO4026' or SType == 'ASMEB18.3.5A':
        p0 = Base.Vector(0, 0, 0)
        p1 = Base.Vector(df / 2, 0, 0)
        p2 = Base.Vector(d / 2, 0, -1 * ((d - df) / 2))
        p3 = Base.Vector(d / 2, 0, -1 * l + ((d - dp) / 2))
        p4 = Base.Vector(dp / 2, 0, -1 * l)
        p5 = Base.Vector(0, 0, -1 * l)
        e1 = Part.makeLine(p0, p1)
        e2 = Part.makeLine(p1, p2)
        e3 = Part.makeLine(p2, p3)
        e4 = Part.makeLine(p3, p4)
        e5 = Part.makeLine(p4, p5)
        p_profile = Part.Wire([e2, e3, e4, e5])
    elif SType == 'ISO4027' or SType == 'ASMEB18.3.5B':
        p0 = Base.Vector(0, 0, 0)
        p1 = Base.Vector(df / 2, 0, 0)
        p2 = Base.Vector(d / 2, 0, -1 * ((d - df) / 2))
        p3 = Base.Vector(d / 2, 0, -1 * l + ((d - dt) / 2))
        p4 = Base.Vector(dt / 2, 0, -1 * l)
        p5 = Base.Vector(0, 0, -1 * l)
        e1 = Part.makeLine(p0, p1)
        e2 = Part.makeLine(p1, p2)
        e3 = Part.makeLine(p2, p3)
        e4 = Part.makeLine(p3, p4)
        e5 = Part.makeLine(p4, p5)
        p_profile = Part.Wire([e2, e3, e4, e5])
    elif SType == 'ISO4028' or SType == 'ASMEB18.3.5C':
        # the shortest available dog-point set screws often have
        # shorter dog-points. There  is not much hard data accessible for this
        # approximate by halving the dog length for short screws
        if l < 1.5 * d:
            z = z * 0.5
        p0 = Base.Vector(0, 0, 0)
        p1 = Base.Vector(df / 2, 0, 0)
        p2 = Base.Vector(d / 2, 0, -1 * ((d - df) / 2))
        p3 = Base.Vector(d / 2, 0, -1 * l + ((d - dp) / 2 + z))
        p4 = Base.Vector(dp / 2, 0, -1 * l + z)
        p5 = Base.Vector(dp / 2, 0, -1 * l)
        p6 = Base.Vector(0, 0, -1 * l)
        e1 = Part.makeLine(p0, p1)
        e2 = Part.makeLine(p1, p2)
        e3 = Part.makeLine(p2, p3)
        e4 = Part.makeLine(p3, p4)
        e5 = Part.makeLine(p4, p5)
        e6 = Part.makeLine(p5, p6)
        p_profile = Part.Wire([e2, e3, e4, e5, e6])
    elif SType == 'ISO4029' or SType == 'ASMEB18.3.5D':
        p0 = Base.Vector(0, 0, 0)
        p1 = Base.Vector(df / 2, 0, 0)
        p2 = Base.Vector(d / 2, 0, -1 * ((d - df) / 2))
        p3 = Base.Vector(d / 2, 0, -1 * l + ((d - dp) / 2))
        p4 = Base.Vector(dp / 2, 0, -1 * l)
        p5 = Base.Vector(0, 0, -1 * l + math.sqrt(3) / 6 * dp)
        e1 = Part.makeLine(p0, p1)
        e2 = Part.makeLine(p1, p2)
        e3 = Part.makeLine(p2, p3)
        e4 = Part.makeLine(p3, p4)
        e5 = Part.makeLine(p4, p5)
        p_profile = Part.Wire([e2, e3, e4, e5])

    p_shell = self.RevolveZ(p_profile)
    #Part.show(p_shell)
    #Part.show(p_profile)
    # generate a top face with a hex-key recess
    top_face_profile = Part.Wire([e1])
    
    top_face = self.RevolveZ(top_face_profile)
    hex_solid, hex_shell = self.makeAllen2(s, t - 1, 0)
    top_face = top_face.cut(hex_solid)
    p_faces = p_shell.Faces
    p_faces.extend(top_face.Faces)
    # Part.show(p_faces)
    
    hex_shell.translate(Base.Vector(0, 0, -1))
    p_faces.extend(hex_shell.Faces)
    #Part.show(p_faces)
    p_shell = Part.Shell(p_faces)
    screw = Part.Solid(p_shell)
    # chamfer the hex recess
    cham_p1 = Base.Vector(0, 0, 0)
    cham_p2 = Base.Vector(s / math.sqrt(3), 0, 0)
    cham_p3 = Base.Vector(0, 0, 0 - s / math.sqrt(3))  # 45 degree chamfer
    cham_e1 = Part.makeLine(cham_p1, cham_p2)
    cham_e2 = Part.makeLine(cham_p2, cham_p3)
    cham_profile = Part.Wire([cham_e1, cham_e2])
    cham_shell = self.RevolveZ(cham_profile)
    cham_solid = Part.Solid(cham_shell)
    screw = screw.cut(cham_solid)
    # produce a modelled thread if necessary
    if fa.thread:
        # make the threaded section
        d = d / 1.01
        shell_thread = self.makeShellthread(d, P, l, False, 0)
        # FixMe: can be made simpler by cutting tyhread helix. 
        thr_p1 = Base.Vector(0, 0, 0)
        thr_p2 = Base.Vector(d / 2, 0, 0)
        thr_e1 = Part.makeLine(thr_p1, thr_p2)
        thr_cap_profile = Part.Wire([thr_e1])
        thr_cap = self.RevolveZ(thr_cap_profile)
        thr_faces = shell_thread.Faces
        thr_faces.extend(thr_cap.Faces)
        thread_shell = Part.Shell(thr_faces)
        thread_solid = Part.Solid(thread_shell)
        # Part.show(thread_solid)
        screw = screw.common(thread_solid)
    return screw
