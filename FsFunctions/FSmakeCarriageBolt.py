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
import FastenerBase

# ASMEB18.5.2 UNC Round head square neck bolts
cos22_5 = math.cos(math.radians(22.5))
sin22_5 = math.sin(math.radians(22.5))
sqrt2 = math.sqrt(2)

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
        
    head_r = A / sqrt2
    flat_len = l - P

    # create a profile for head generation. Basially when this profile revolves we get the head solid
    # FSFaceMaker is a nice helper to build a profile from lines and arcs it make a profile on the x,z plane
    fm = FastenerBase.FSFaceMaker()
    fm.AddPoint(0, H)
    fm.AddArc(head_r * sin22_5, H - head_r + head_r * cos22_5, A / 2, 0) # arcs are 3 point arcs where the first point is the last added
    fm.AddPoint(sqrt2 / 2 * O, 0)
    fm.AddPoint(sqrt2 / 2 * O, -1 * P + (sqrt2 / 2 * O - d / 2))
    fm.AddPoint(d / 2, -1 * P)
    wire1 = fm.GetWire()
    head_shell = wire1.revolve(Base.Vector(0, 0, 0), Base.Vector(0, 0, 1), 360)
    if not fa.thread:
        # simplified threaded section
        fm.Reset()
        fm.AddPoint(d / 2, -1 * P)
        if (flat_len > L_t):
            fm.AddPoint(d / 2, -l + L_t)
        fm.AddPoint(d / 2, -l + d / 10)
        fm.AddPoint(d / 2 - d / 10, -l)
        fm.AddPoint(0, -l)
        thread_profile_wire = fm.GetWire()
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
    # removeSplitter is equivalent to the 'Refine' option for FreeCAD PartDesign objects
    # return p_solid.removeSplitter()
    return p_solid # not refining so thread location will be visible when not using real thread
