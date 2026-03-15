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
# DIN603 Mushroom head square neck bolts
cos22_5 = math.cos(math.radians(22.5))
sin22_5 = math.sin(math.radians(22.5))


def makeCarriageBolt(self, fa):
    """Creates a carriage bolt (round head square neck).

    Supported types:
    - ASMEB18.5.2  UNC round head square neck bolts
    - DIN 603      Mushroom head square neck bolts

    Thread diameter formulas (Dipak):
      ASME/inch : thread_dia = dia - 0.15 / TPI
      Metric    : thread_dia = dia - 0.15 * P
    """
    SType   = fa.baseType
    length  = fa.calc_len
    d       = self.getDia(fa.calc_diam, False)
    is_asme = SType.startswith("ASME")

    # ── Unpack dimTable ───────────────────────────────────────────────────
    if SType == 'ASMEB18.5.2':
        tpi_tbl, _, A, H, O, P_dim, _, _ = fa.dimTable
        A, H, O, P_dim = (25.4 * x for x in (A, H, O, P_dim))
        P_tbl  = 25.4 / tpi_tbl
        L_t = (d * 2 + 6.35) if length <= 152.4 else (d * 2 + 12.7)

    elif SType == 'DIN603':
        P_tbl, b1, b2, b3, dk_max, dk_min, ds_max, ds_min, f_max, f_min, \
            k_max, k_min, r1_approx, r2_max, r2_max2, v_max, v_min = fa.dimTable
        A     = (dk_max + dk_min) / 2
        H     = k_max
        O     = v_max
        P_dim = f_max
        L_t   = b1 if length <= 125 else (b2 if length <= 200 else b3)

    else:
        raise NotImplementedError(f"Unknown fastener type: {SType}")

    # ── Pitch override (ThreadPitch mm / ThreadTPI) ───────────────────────
    raw_pitch = getattr(fa, "calc_pitch", None)
    pitch = raw_pitch if (raw_pitch is not None and raw_pitch > 0.0) else P_tbl

    # ── Thread length override (ThreadLength from dashboard) ──────────────
    raw_tlen = getattr(fa, "calc_thread_length", 0.0) or 0.0
    L_t = min(float(raw_tlen), length) if raw_tlen > 0.0 else L_t

    # ── Thread diameter ───────────────────────────────────────────────────
    # ASME/inch : thread_dia = dia - 0.15 / TPI
    # Metric    : thread_dia = dia - 0.15 * P
    if is_asme:
        tpi = getattr(fa, "calc_tpi", None)
        if not tpi or tpi <= 0:
            tpi = round(25.4 / P_tbl)
        thread_dia = d - (0.15 / tpi)
        log_extra  = f"TPI={tpi}"
    else:
        thread_dia = d - 0.15 * pitch
        log_extra  = f"P={pitch:.3f}mm"

    tr = thread_dia / 2.0

    FreeCAD.Console.PrintMessage(
        f"[Dipak] Threading: dia={d:.4f}mm, "
        f"thread_dia={thread_dia:.4f}mm, {log_extra}, "
        f"allowance={d - thread_dia:.4f}mm, "
        f"thread_length={L_t:.2f}mm\n"
    )

    # ── Revolve profile ───────────────────────────────────────────────────
    # Head uses full d. Shaft uses tr (= thread_dia/2) so the revolved
    # solid is at thread_dia → volume changes correctly.
    head_r    = A / sqrt2
    flat_len  = length - P_dim
    r_fillet  = d * 0.05
    theta     = math.pi / 4

    fm = FastenerBase.FSFaceMaker()
    fm.AddPoint(0, H)
    fm.AddArc(
        head_r * math.sin(theta / 2),
        head_r * math.cos(theta / 2) - head_r + H,
        A / 2 - r_fillet + r_fillet * math.sin(theta),
        r_fillet * (1 + math.cos(theta)),
    )
    fm.AddArc(A / 2, r_fillet, A / 2 - r_fillet, 0)
    fm.AddPoint(sqrt2 / 2 * O,  0)
    fm.AddPoint(sqrt2 / 2 * O, -1 * P_dim + (sqrt2 / 2 * O - d / 2))
    fm.AddPoint(tr,             -1 * P_dim)   # shaft starts at thread radius

    if flat_len > L_t:
        if not fa.Thread:
            fm.AddPoint(tr, -length + L_t)
        thread_length = L_t
    else:
        thread_length = flat_len

    fm.AddPoint(tr,        -length + d / 10)
    fm.AddPoint(tr - d / 10, -length)
    fm.AddPoint(0,         -length)

    p_solid = self.RevolveZ(fm.GetFace())

    # ── Cut 4 flats under head ────────────────────────────────────────────
    d_mod    = d + 0.0002
    outerBox = Part.makeBox(
        A * 4, A * 4, P_dim + 0.0001,
        Base.Vector(-A * 2, -A * 2, -P_dim + 0.0001)
    )
    innerBox = Part.makeBox(
        d_mod, d_mod, P_dim * 3,
        Base.Vector(-d_mod / 2, -d_mod / 2, -P_dim * 2)
    )
    edgelist         = innerBox.Edges
    edges_to_fillet  = [
        e for e in edgelist
        if (abs(abs(e.CenterOfMass.x) - d_mod / 2) < 0.0001 and
            abs(abs(e.CenterOfMass.y) - d_mod / 2) < 0.0001)
    ]
    innerBox = innerBox.makeFillet(d * 0.08, edges_to_fillet)
    tool     = outerBox.cut(innerBox)
    p_solid  = p_solid.cut(tool)

    # ── Thread cutter ─────────────────────────────────────────────────────
    if fa.Thread:
        thread_cutter = self.CreateBlindThreadCutter(thread_dia, pitch, thread_length)
        thread_cutter.translate(Base.Vector(0.0, 0.0, -1 * (length - thread_length)))
        p_solid = p_solid.cut(thread_cutter)

    return Part.Solid(p_solid)