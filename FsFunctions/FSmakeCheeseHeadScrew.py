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


def makeCheeseHeadScrew(self, fa):
    """Create a cheese head screw

    Supported types:
    - ISO 1207  slotted screw
    - DIN 84    slotted screw
    - ISO 7048  cross recessed screw
    - ISO 1580  slotted pan head screw
    - ISO 14580 hexalobular socket cheese head screws

    Thread diameter formula (Dipak):
      Metric : thread_dia = dia - 0.15 * P
    """
    SType  = fa.baseType
    length = fa.calc_len
    dia    = self.getDia(fa.calc_diam, False)

    # ── Unpack dimTable ───────────────────────────────────────────────────
    if SType in ("ISO1207", "DIN84"):
        P_tbl, a, b_tbl, dk, dk_mean, da, k, n_min, r, t_min, x = fa.dimTable
        r_fil  = r * 2.0
        recess = self.makeSlotRecess(n_min, t_min, dk)

    elif SType == "ISO7048":
        P_tbl, a, b_tbl, dk, dk_mean, da, k, r, x, cT, mH, mZ = fa.dimTable
        r_fil  = r * 2.0
        recess = self.makeHCrossRecess(cT, mH)

    elif SType == "ISO1580":
        P_tbl, a, b_tbl, dk, da, k, n_min, r, rf, t_min, x = fa.dimTable
        r_fil  = rf
        recess = self.makeSlotRecess(n_min, t_min, dk)

    elif SType == "ISO14580":
        P_tbl, a, b_tbl, dk, dk_mean, da, k, n_min, r, t_min, x = fa.dimTable
        tt, k, A, t_min = FsData["ISO14580extra"][fa.calc_diam]
        r_fil  = r * 2.0
        recess = self.makeHexalobularRecess(tt, t_min, True)

    else:
        raise NotImplementedError(f"Unknown fastener type: {SType}")

    # ── Pitch override (ThreadPitch from dashboard) ───────────────────────
    raw_pitch = getattr(fa, "calc_pitch", None)
    P = raw_pitch if (raw_pitch is not None and raw_pitch > 0.0) else P_tbl

    # ── Thread length override (ThreadLength from dashboard) ──────────────
    raw_tlen = getattr(fa, "calc_thread_length", 0.0) or 0.0
    b = min(float(raw_tlen), length) if raw_tlen > 0.0 else b_tbl

    # ── Thread diameter: metric formula ──────────────────────────────────
    # thread_dia = dia - 0.15 * P
    thread_dia = dia - 0.15 * P
    tr         = thread_dia / 2.0

    FreeCAD.Console.PrintMessage(
        f"[Dipak] Threading: dia={dia:.4f}mm, "
        f"thread_dia={thread_dia:.4f}mm, P={P:.3f}mm, "
        f"allowance={dia - thread_dia:.4f}mm, "
        f"thread_length={b:.2f}mm\n"
    )

    # ── Revolve profile ───────────────────────────────────────────────────
    # Head uses full dia. Arc ends at (dia/2, -r); step inward to tr at
    # same z so the entire shaft is at thread_dia → volume changes correctly.
    head_taper_angle = math.radians(5)

    fm = FSFaceMaker()
    fm.AddPoint(0.0, k)
    fm.AddPoint(
        dk / 2
        - k * math.tan(head_taper_angle)
        - r_fil * math.tan((math.pi / 2 - head_taper_angle) / 2),
        k,
    )
    fm.AddArc2(0.0, -r_fil, -90 + math.degrees(head_taper_angle))
    fm.AddPoint(dk / 2,      0.0)
    fm.AddPoint(dia / 2 + r, 0.0)
    fm.AddArc2(0.0, -r, 90)             # ends at (dia/2, -r)
    fm.AddPoint(tr, -r)                 # step in to thread radius at same z

    if length - r > b:                  # partially threaded
        thread_length = b
        if not fa.Thread:
            fm.AddPoint(tr, -1 * (length - b))
    else:
        thread_length = length - r

    fm.AddPoint(tr,  -length)
    fm.AddPoint(0.0, -length)

    screw = self.RevolveZ(fm.GetFace())

    # ── Cut driving recess into head ──────────────────────────────────────
    recess.translate(Base.Vector(0.0, 0.0, k))
    screw = screw.cut(recess)

    # ── Thread cutter ─────────────────────────────────────────────────────
    if fa.Thread:
        thread_cutter = self.CreateBlindThreadCutter(thread_dia, P, thread_length)
        thread_cutter.translate(Base.Vector(0.0, 0.0, -1 * (length - thread_length)))
        screw = screw.cut(thread_cutter)

    return screw