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


def makeRoundHeadScrew(self, fa):
    """Create a screw with a round head

    Supported types:
    - ASMEB18.6.3.16A  UNC slotted round head screws
    - ASMEB18.6.3.16B  UNC cross-recessed round head screws

    Thread diameter formula (Dipak):
      ASME/inch : thread_dia = dia - 0.15 / TPI
    """
    SType  = fa.baseType
    length = fa.calc_len
    dia    = self.getDia(fa.calc_diam, False)

    # ── Unpack dimTable per screw type ────────────────────────────────────
    if SType == "ASMEB18.6.3.16A":
        P_tbl, A, H, J, T = fa.dimTable
        A, H, J, T = (25.4 * x for x in (A, H, J, T))
        recess = self.makeSlotRecess(J, T, A)
        recess.translate(Base.Vector(0.0, 0.0, H))
        b_tbl = 1.5 * 25.4      # max threaded length per para 2.4.1(b)

    elif SType == "ASMEB18.6.3.16B":
        P_tbl, A, H, _, _ = fa.dimTable
        mH, cT = FsData["ASMEB18.6.3.16Bextra"][fa.calc_diam]
        A, H, mH = (25.4 * x for x in (A, H, mH))
        recess = self.makeHCrossRecess(cT, mH)
        recess.translate(Base.Vector(0.0, 0.0, H))
        b_tbl = 1.5 * 25.4      # max threaded length per para 2.4.1(b)

    else:
        raise NotImplementedError(f"Unknown fastener type: {SType}")

    # ── Pitch override (ThreadTPI from dashboard) ─────────────────────────
    raw_pitch = getattr(fa, "calc_pitch", None)
    P = raw_pitch if (raw_pitch is not None and raw_pitch > 0.0) else P_tbl

    # ── Thread length override (ThreadLength from dashboard) ──────────────
    raw_tlen = getattr(fa, "calc_thread_length", 0.0) or 0.0
    b = min(float(raw_tlen), length) if raw_tlen > 0.0 else b_tbl

    # ── Thread diameter: ASME inch formula ────────────────────────────────
    # thread_dia = dia - 0.15 / TPI
    tpi = getattr(fa, "calc_tpi", None)
    if not tpi or tpi <= 0:
        tpi = round(25.4 / P_tbl)          # standard TPI from table
    thread_dia = dia - (0.15 / tpi)
    tr         = thread_dia / 2.0

    FreeCAD.Console.PrintMessage(
        f"[Dipak] Threading: dia={dia:.4f}mm, "
        f"thread_dia={thread_dia:.4f}mm, TPI={tpi}, "
        f"allowance={dia - thread_dia:.4f}mm, "
        f"thread_length={b:.2f}mm\n"
    )

    # ── Thread length for cutter ──────────────────────────────────────────
    thread_length = b if length > b else length

    # ── Head curve geometry ───────────────────────────────────────────────
    r  = (4 * H * H + A * A) / (8 * H)
    zm = math.sqrt(1 - A * A / (16 * r * r)) * r - (r - H)

    # ── Revolve profile ───────────────────────────────────────────────────
    # Shaft uses tr (= thread_dia/2) instead of half_dia so the revolved
    # solid is at thread_dia → volume changes correctly.
    fm = FastenerBase.FSFaceMaker()
    fm.AddPoints(
        (0,      H),
        (A / 4,  zm,  A / 2,  0),  # round head arc
        (tr,     0),                # shaft starts at thread radius
        (tr,    -length),
        (0,     -length),
    )

    screw = self.RevolveZ(fm.GetFace())
    screw = screw.cut(recess)

    # ── Thread cutter ─────────────────────────────────────────────────────
    if fa.Thread:
        thread_cutter = self.CreateBlindThreadCutter(thread_dia, P, thread_length)
        thread_cutter.translate(Base.Vector(0.0, 0.0, -1 * (length - thread_length)))
        screw = screw.cut(thread_cutter)

    return screw