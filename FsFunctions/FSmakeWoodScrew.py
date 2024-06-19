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

def makeWoodScrew(self, fa): # dynamically loaded method of class Screw
    SType = fa.baseType
    if SType == "DIN571":
        return makeDIN571(self, fa)
    elif SType == "DIN96":
        return makeDIN96(self, fa)
    elif SType == "DIN7996":
        return makeDIN7996(self, fa)
    elif SType == "GOST1144-1" or SType == "GOST1144-2" or SType == "GOST1144-3" or SType == "GOST1144-4":
        return makeGOST1144(self, fa)
    elif SType == "ASMEB18.6.1.2" or SType == "ASMEB18.6.1.3" or SType == "ASMEB18.6.1.4" or SType == "ASMEB18.6.1.5":
        return makeASMEB1861(self, fa)

# DIN571 Wood screw

def makeDIN571(screw_obj, fa):
    l = fa.calc_len
    dia = float(fa.calc_diam.split()[0])
    ds, da, d3, k, s, P = fa.dimTable
    d = dia / 2.0
    d3h = d3 / 2.0
    r = (da-ds)/2.0
    e = s/math.cos(math.radians(30))
    sqrt2_ = 1.0 / math.sqrt(2.0)
    cham = (e - s) * math.sin(math.radians(15))  # needed for chamfer at head top

    Pnt0 = Base.Vector(0.0, 0.0, k)
    Pnt2 = Base.Vector(s / 2.0, 0.0, k)
    Pnt3 = Base.Vector(s / math.sqrt(3.0), 0.0, k - cham)
    Pnt4 = Base.Vector(s / math.sqrt(3.0), 0.0, 0.0)
    Pnt7 = Base.Vector(d + r, 0.0, 0.0)  # start of fillet between head and shank
    Pnt8 = Base.Vector(d + r - r * sqrt2_, 0.0, -r + r * sqrt2_)  # arc-point of fillet
    Pnt9 = Base.Vector(d, 0.0, -r)  # end of fillet

    edge1 = Part.makeLine(Pnt0, Pnt2)
    edge2 = Part.makeLine(Pnt2, Pnt3)
    edge3 = Part.makeLine(Pnt3, Pnt4)
    edge4 = Part.makeLine(Pnt4, Pnt7)
    edge5 = Part.Arc(Pnt7, Pnt8, Pnt9).toShape()

    # create cutting tool for hexagon head
    # Parameters s, k, outer circle diameter =  e/2.0+10.0
    extrude = screw_obj.makeHexPrism(s, k + l * 2)
    extrude.translate(Base.Vector(0.0, 0.0, -1.5 * l))
    #if fa.Thread:
    #  pass
    #else:
    if fa.Thread:
        dt = d3 / 2.0
    else:
        dt = d
    angle = math.radians(20)
    x2 = dt * math.cos(angle)
    z2 = dt * math.sin(angle)
    z3 = x2 / math.tan(angle)
    ftl = l - z2 - z3 # flat part (total length - tip)
    PntB0 = Base.Vector(d, 0.0, 0.4 * -ftl)
    PntB1 = Base.Vector(dt, 0.0, -ftl)
    PntB2 = Base.Vector(dt * math.cos(angle / 2.0),
                        0.0,
                        -l + z2 + z3 - d * math.sin(angle / 2.0))
    PntB3 = Base.Vector(x2, 0.0, -l + z3)
    PntB4 = Base.Vector(0.0, 0.0, -l)

    edge6 = Part.makeLine(Pnt9, PntB0)
    edge8 = Part.Arc(PntB1, PntB2, PntB3).toShape()
    edge9 = Part.makeLine(PntB3, PntB4)
    edgeZ0 = Part.makeLine(PntB4, Pnt0)

    if fa.Thread:
        PntB0t = Base.Vector(dt, 0.0, 0.4 * -ftl - (d - dt))
        edge7 = Part.makeLine(PntB0, PntB0t)
        edge7t = Part.makeLine(PntB0t, PntB1)
        aWire = Part.Wire([edge1, edge2, edge3, edge4, edge5, edge6,\
                        edge7, edge7t, edge8, edge9, edgeZ0])
    else:
        edge7 = Part.makeLine(PntB0, PntB1)
        aWire = Part.Wire([edge1, edge2, edge3, edge4, edge5, edge6,\
                        edge7, edge8, edge9, edgeZ0])

    aFace = Part.Face(aWire)
    # Part.show(aFace)
    head = screw_obj.RevolveZ(aFace)
    head = head.common(extrude)
    if fa.Thread:
        thread = screw_obj.makeDin7998Thread(0.4 * -ftl, -ftl, -l, d3h, d, P)
        #Part.show(thread)
        head = head.fuse(thread)

    return head

# DIN96 Wood screw

def makeDIN96(screw_obj, fa):
    l = fa.calc_len
    dia = float(fa.calc_diam.split()[0])
    dk, k, n, t, d3, P = fa.dimTable
    d = dia / 2.0
    d32 = d3 / 2.0

    # calc head
    r = (4*k*k+dk*dk)/(8*k)
    zm = math.sqrt(1-dk*dk/(16*r*r))*r - (r-k)

    # calc screw
    if fa.Thread:
        dt = d3 / 2.0
    else:
        dt = d
    angle = math.radians(20)
    x2 = dt * math.cos(angle)
    z2 = dt * math.sin(angle)
    z3 = x2 / math.tan(angle)
    ftl = l - z2 - z3 # flat part (total length - tip)

    # make profile
    fm = FastenerBase.FSFaceMaker()
    fm.AddPoints(
        (0, k),
        (dk/4, zm, dk/2, 0),
        (d, 0),
        (d, -0.4*ftl))
    if fa.Thread:
        fm.AddPoints((dt, -0.4*ftl-(d-dt)))
    fm.AddPoints(
        (dt, -ftl),
        (dt*math.cos(angle/2), -l + z2 + z3 - d*math.sin(angle/2), x2, -l+z3),
        (0, -l))
    profile = fm.GetFace()

    # make screw body
    screw = screw_obj.RevolveZ(profile)

    # make slot
    slot = Part.makeBox(dk, n, t+1,
                        Base.Vector(-dk/2, -n/2, k-t))
    screw = screw.cut(slot)

    # make thread
    if fa.Thread:
        thread = screw_obj.makeDin7998Thread(0.4 * -ftl, -ftl, -l, d32, d, P)
        screw = screw.fuse(thread)

    return screw

# DIN7996 Wood screw

def makeDIN7996(screw_obj, fa):
    l = fa.calc_len
    dia = float(fa.calc_diam.split()[0])
    dk, k, da, _, d3, P, PH, m, _ = fa.dimTable
    d = dia/2
    d32 = d3/2
    sa = da/2

    # calc screw
    if fa.Thread:
        dt = d32
    else:
        dt = d
    angle = math.radians(20)
    x2 = dt * math.cos(angle)
    z2 = dt * math.sin(angle)
    z3 = x2 / math.tan(angle)
    ftl = l - z2 - z3 # flat part (total length - tip)

    # make profile
    fm = FastenerBase.FSFaceMaker()
    fm.AddPoint(0, k)
    # using a spline (inspired by makeGOST1144) even it is not correct
    fm.AddBSpline(dk/2, k, dk/2, 0)
    fm.AddPoints(
        (sa, 0),
        (0, d-sa, 90),
        (d, -0.4*ftl))
    if fa.Thread:
        fm.AddPoints((dt, -0.4*ftl-(d-dt)))
    fm.AddPoints(
        (dt, -ftl),
        (dt*math.cos(angle/2), -l + z2 + z3 - d*math.sin(angle/2), x2, -l+z3),
        (0, -l))
    profile = fm.GetFace()

    # make screw body
    screw = screw_obj.RevolveZ(profile)

    # make phillips recess (10% compensation for spline)
    recess = screw_obj.makeHCrossRecess(PH, m*1.1)
    recess = recess.translate(Base.Vector(0.0, 0.0, k))
    screw = screw.cut(recess)

    # make thread
    if fa.Thread:
        thread = screw_obj.makeDin7998Thread(0.4 * -ftl, -ftl, -l, d32, d, P)
        screw = screw.fuse(thread)

    return screw

# GOST1144-1 Wood screw
# GOST1144-2 Wood screw
# GOST1144-3 Wood screw
# GOST1144-4 Wood screw

def makeGOST1144(self, fa):
    SType = fa.baseType
    l = fa.calc_len
    dia = float(fa.calc_diam.split()[0])

    # load screw parameters from *.csv tables
    if SType == "GOST1144-1" or SType == "GOST1144-2":
        d2, P, D, K, sb, h = fa.dimTable
    elif SType == "GOST1144-3" or SType == "GOST1144-4":
        d2, P, D, K, PH, m, h = fa.dimTable

    # types 2 and 4 have full length thread while types 1 and 3 do not
    b = l
    full_length=True
    if SType == "GOST1144-1" or SType == "GOST1144-3":
       b = l * 0.6
       full_length=False

    ri = d2 / 2.0   # inner thread radius
    ro = dia / 2.0  # outer thread radius
 
    # inner radius of screw section
    sr = ro
    if fa.Thread:
        sr = ri

    # length of cylindrical part where thread begins to grow.
    slope_length = ro - ri

    # calculation of screw tip length
    # Sharpness of screw tip is equal 40 degrees. If imagine half of screw tip
    # as a triangle, then acute-angled angle of the triangle (alpha) be which
    # is equal to half of the screw tip angle.
    alpha = 40/2
    # And the adjacent cathetus be which is equal to least screw radius (sr)
    # Then the opposite cathetus can be getted by formula: tip_length=sr/tg(alpha)
    tip_length = sr/math.tan(math.radians(alpha))

    ###########################
    # Make full screw profile #
    ###########################

    fm = FastenerBase.FSFaceMaker()

    # 1) screw head
    # Head of screw builds by B-Spline instead two arcs builded by two radii
    # (values R1 and R2). A curve built with two arcs and a curve built with a
    # B-Spline are almost identical. That can be verified if build a contour of
    # screw head by two ways in Sketch workbench and compare them. B-Spline also
    # allows to remove the contour that appears between two arcs during creation
    # process, and it use fewer points than two arcs.
    fm.AddPoint(0, K)
    fm.AddBSpline(D/2, K, D/2, 0)

    # 2) add rounding under screw head
    rr = dia / 10
    fm.AddPoint(ro + rr, 0)      # first point of rounding
    if fa.Thread and full_length:
       fm.AddBSpline(ro, 0, sr, -slope_length) # create spline rounding
    else:
       fm.AddArc2(+0, -rr, 90) # in other cases create arc rounding

    # 3) cylindrical part (place where thread will be added)
    if not full_length:
       if fa.Thread:
          fm.AddPoint(ro, -l+b+slope_length)    # entery point of thread
       fm.AddPoint(sr, -l+b)   # start of full width thread b >= l*0.6

    # 4) sharp end (cone shape)
    fm.AddPoint(sr, -l+tip_length)
    fm.AddPoint(0, -l)

    # make profile from points (lines and arcs)
    profile = fm.GetFace()

    # make screw solid body by revolve a profile
    screw = self.RevolveZ(profile)

    # make slot in screw head
    if SType == "GOST1144-1" or SType == "GOST1144-2":
        recess = Part.makeBox(D, sb, h+1, Base.Vector(-D/2, -sb/2, K-h))
    elif SType == "GOST1144-3" or SType == "GOST1144-4":
        recess = self.makeHCrossRecess(PH, m)
        recess = recess.translate(Base.Vector(0.0, 0.0, h))
    screw = screw.cut(recess)

    # make thread
    if fa.Thread:
        thread = self.makeDin7998Thread(-l+b+slope_length, -l+tip_length, -l, ri, ro, P)
        screw = screw.fuse(thread)

    return screw

def makeASMEB1861(self, fa):
    SType = fa.baseType
    length = fa.calc_len
    P, E, F, A_max, A_min, H, J, T, r = fa.dimTable
    P, E, F, A_max, A_min, H, J, T, r = (x * 25.4 for x in (P, E, F, A_max, A_min, H, J, T, r))
    
    if SType == "ASMEB18.6.1.2" or SType == "ASMEB18.6.1.4":
        recess = self.makeSlotRecess(J, T, E)
    elif SType == "ASMEB18.6.1.3" or SType == "ASMEB18.6.1.5":
        cT, M = FsData["ASMEB18.6.1.3extra"][fa.calc_diam]
        M = M * 25.4
        recess = self.makeHCrossRecess(cT, M)

    A_mean = (A_max - A_min) / 2 + A_min
    dia = E
    b = 0.667 * length  # Per paragraph 2.4.1

    csk_angle = math.radians(82)    
    head_flat_ht = (A_max - A_mean) / 2 / math.tan(csk_angle / 2)
    sharp_corner_ht = -1 * (head_flat_ht + (A_mean - dia) / (2 * math.tan(csk_angle / 2)))
    fillet_start_ht = sharp_corner_ht - r * math.tan(csk_angle / 4)        

    if length + fillet_start_ht > b:  # partially threaded fastener
        thread_length = b
    else:
        thread_length = length + fillet_start_ht
        
    fm = FastenerBase.FSFaceMaker()
    fm.AddPoint(0.0, -length)
    
    if fa.Thread:
        fm.AddPoint(dia / 2 - F, -length + dia) # Assume length of taper = diameter
        fm.AddPoint(dia / 2 - F, -length + thread_length - dia);
        fm.AddPoint(dia / 2, -length + thread_length) 
    else:
        fm.AddPoint(dia / 2, -length + dia)
        fm.AddPoint(dia / 2, -length + thread_length)
        
    fm.AddPoint(dia / 2, fillet_start_ht)
    fm.AddArc2(r, 0.0, -math.degrees(csk_angle / 2))
    fm.AddPoint(A_mean / 2, -head_flat_ht)
    fm.AddPoint(A_mean / 2, 0.0)
    
    if SType == "ASMEB18.6.1.4" or SType == "ASMEB18.6.1.5" :
        O, _ = FsData["ASMEB18.6.1.4extra"][fa.calc_diam]
        C = O * 25.4 - H
        # Calculate head radius (rf)
        rf = (4 * C * C + A_max * A_max) / (8 * C)
        head_arc_angle = math.asin(A_mean / 2.0 / rf)  # angle of head edge
        # height of raised head top
        ht = rf - (A_mean / 2.0) / math.tan(head_arc_angle)

        fm.AddArc(
            rf * math.sin(head_arc_angle / 2),
            ht + rf * (math.cos(head_arc_angle / 2) - 1),
            0.0,
            ht,
        )
        recess.translate(Base.Vector(0.0, 0.0, 1.0 * C))
    else:
        fm.AddPoint(0.0, 0.0)

    # make profile from points (lines and arcs)
    profile = fm.GetFace()

    # make screw solid body by revolve a profile
    screw = self.RevolveZ(profile)
    screw = screw.cut(recess)

    # make thread
    if fa.Thread:
        thread = self.makeDin7998Thread(-length + thread_length, -length + dia, -length, E/2 - F, E/2, P)
        screw = screw.fuse(thread)

    return screw
