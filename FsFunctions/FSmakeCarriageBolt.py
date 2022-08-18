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

# ASMEB18.5.2 UNC Round head square neck bolts

def makeCarriageBolt(self, fa): # dynamically loaded method of class Screw
    SType = fa.type
    l = fa.calc_len
    d = self.getDia(fa.calc_diam, False)
    if SType == 'ASMEB18.5.2':
        tpi, _, A, H, O, P, _, _ = fa.dimTable
        A, H, O, P = (25.4 * x for x in (A, H, O, P))
        pitch = 25.4 / tpi
        if l <= 152.4:
            L_t = d * 2 + 6.35
        else:
            L_t = d * 2 + 12.7
    # lay out points for head generation
    p1 = Base.Vector(0, 0, H)
    head_r = A / math.sqrt(2)
    p2 = Base.Vector(head_r * math.sin(math.pi / 8), 0, H - head_r + head_r * math.cos(math.pi / 8))
    p3 = Base.Vector(A / 2, 0, 0)
    p4 = Base.Vector(math.sqrt(2) / 2 * O, 0, 0)
    p5 = Base.Vector(math.sqrt(2) / 2 * O, 0, -1 * P + (math.sqrt(2) / 2 * O - d / 2))
    p6 = Base.Vector(d / 2, 0, -1 * P)
    # arcs must be converted to shapes in order to be merged with other line segments
    a1 = Part.Arc(p1, p2, p3).toShape()
    l2 = Part.makeLine(p3, p4)
    l3 = Part.makeLine(p4, p5)
    l4 = Part.makeLine(p5, p6)
    wire1 = Part.Wire([a1, l2, l3, l4])
    head_shell = wire1.revolve(Base.Vector(0, 0, 0), Base.Vector(0, 0, 1), 360)
    flat_len = l - P
    if not fa.thread:
        # simplified threaded section
        p7 = Base.Vector(d / 2, 0, -l + d / 10)
        p7a = Base.Vector(d / 2, 0, -l + L_t)
        p8 = Base.Vector(d / 2 - d / 10, 0, -l)
        p9 = Base.Vector(0, 0, -l)
        l6 = Part.makeLine(p7, p8)
        l7 = Part.makeLine(p8, p9)
        if (flat_len <= L_t):
            l5 = Part.makeLine(p6, p7)
            thread_profile_wire = Part.Wire([l5, l6, l7])
        else:
            l5a = Part.makeLine(p6, p7a)
            l5b = Part.makeLine(p7a, p7)
            thread_profile_wire = Part.Wire([l5a, l5b, l6, l7])
        shell_thread = thread_profile_wire.revolve(Base.Vector(0, 0, 0), Base.Vector(0, 0, 1), 360)
    else:
        # modeled threaded section
        shell_thread = self.makeShellthread(d, pitch, flat_len, False, -P, L_t)
    p_shell = Part.Shell(head_shell.Faces + shell_thread.Faces)
    p_solid = Part.Solid(p_shell)
    # cut 4 flats under the head
    d_mod = d + 0.0002
    outerBox = Part.makeBox(A * 4, A * 4, P + 0.0001, Base.Vector(-A * 2, -A * 2, -P + 0.0001))
    innerBox = Part.makeBox(d_mod, d_mod, P * 3, Base.Vector(-d_mod / 2, -d_mod / 2, -P * 2))
    tool = outerBox.cut(innerBox)
    p_solid = p_solid.cut(tool)
    #for i in range(4):
    #    p_solid = p_solid.cut(
    #        Part.makeBox(d, A, P, Base.Vector(d / 2, -1 * A / 2, -1 * P)).rotate(Base.Vector(0, 0, 0),
    #                                                                             Base.Vector(0, 0, 1), i * 90))
    # removeSplitter is equivalent to the 'Refine' option for FreeCAD PartDesign objects
    # return p_solid.removeSplitter()
    return p_solid # not refining so thread location will be visible when not using real thread
