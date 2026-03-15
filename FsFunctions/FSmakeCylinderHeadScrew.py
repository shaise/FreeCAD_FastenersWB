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


def makeCylinderHeadScrew(self, fa):
    """Create a cylinder head fastener (or 'cap screw')

    Supported types:
    - ISO 4762 / ISO 14579 / DIN 7984 / DIN 6912
    - ASMEB18.3.1A / ASMEB18.3.1G

    Thread diameter formulas (Dipak):
      ASME/inch : thread_dia = dia - 0.15 / TPI
      Metric    : thread_dia = dia - 0.15 * P
    """
    SType   = fa.baseType
    length  = fa.calc_len
    dia     = self.getDia(fa.calc_diam, False)
    is_asme = SType.startswith("ASME")

    # ── Unpack dimTable per screw type ────────────────────────────────────
    if SType == 'ISO4762':
        P_tbl, b_tbl, dk_max, da, ds_mean, e, lf, k, r, s_mean, t, v, dw, w = fa.dimTable
        recess = self.makeHexRecess(s_mean, t, True)

    elif SType == 'ISO14579':
        P_tbl, b_tbl, dk_max, da, ds_mean, e, lf, k, r, s_mean, t, v, dw, w = \
            FsData["ISO4762def"][fa.calc_diam]
        tt, A, t = fa.dimTable
        recess = self.makeHexalobularRecess(tt, t, True)

    elif SType == 'DIN7984':
        P_tbl, b_tbl, dk_max, da, ds_min, e, k, r, s_mean, t, v, dw = fa.dimTable
        recess = self.makeHexRecess(s_mean, t, True)

    elif SType == 'DIN6912':
        P_tbl, b_tbl, dk_max, da, ds_min, e, k, r, s_mean, t, t2, v, dw = fa.dimTable
        recess = self.makeHexRecess(s_mean, t, True)
        d_cent     = s_mean / 3.0
        depth_cent = d_cent * math.tan(math.pi / 6.0)
        fm = FSFaceMaker()
        fm.AddPoint(0.0,    0.0)
        fm.AddPoint(d_cent, 0.0)
        fm.AddPoint(d_cent, -t2)
        fm.AddPoint(0.0,    -t2 - depth_cent)
        recess = recess.fuse(self.RevolveZ(fm.GetFace()))

    elif SType == 'ASMEB18.3.1A':
        P_tbl, b_tbl, dk_max, k, r, s_mean, t, v, dw = fa.dimTable
        recess = self.makeHexRecess(s_mean, t, True)

    elif SType == 'ASMEB18.3.1G':
        P_tbl, b_tbl, A, H, C_max, J, T, K, r = (x * 25.4 for x in fa.dimTable)
        dk_max = A
        k      = H
        v      = C_max
        s_mean = J
        t      = T
        dw     = A - K
        recess = self.makeHexRecess(s_mean, t, True)

    else:
        raise NotImplementedError(f"Unknown fastener type: {SType}")

    # ── Pitch override (from ThreadPitch mm / ThreadTPI) ──────────────────
    raw_pitch = getattr(fa, "calc_pitch", None)
    P = raw_pitch if (raw_pitch is not None and raw_pitch > 0.0) else P_tbl

    # ── Thread length override (from ThreadLength property) ───────────────
    raw_tlen = getattr(fa, "calc_thread_length", 0.0) or 0.0
    b = min(float(raw_tlen), length) if raw_tlen > 0.0 else b_tbl

    # ── Thread diameter ───────────────────────────────────────────────────
    # ASME/inch : thread_dia = dia - 0.15 / TPI
    #             TPI = user override (fa.calc_tpi) or standard (25.4 / P_tbl)
    # Metric    : thread_dia = dia - 0.15 * P   (P in mm)
    if is_asme:
        tpi = getattr(fa, "calc_tpi", None)
        if not tpi or tpi <= 0:
            tpi = round(25.4 / P_tbl)          # standard TPI from table
        thread_dia = dia - (0.15 / tpi)
        log_extra  = f"TPI={tpi}"
    else:
        thread_dia = dia - 0.15 * P
        log_extra  = f"P={P:.3f}mm"

    tr = thread_dia / 2.0

    FreeCAD.Console.PrintMessage(
        f"[Dipak] Threading: dia={dia:.4f}mm, "
        f"thread_dia={thread_dia:.4f}mm, {log_extra}, "
        f"allowance={dia - thread_dia:.4f}mm, "
        f"thread_length={b:.2f}mm\n"
    )

    # ── Revolve profile ───────────────────────────────────────────────────
    fm = FSFaceMaker()
    fm.AddPoint(0.0,           k)
    fm.AddPoint(dk_max / 2 - v, k)
    fm.AddArc2(0.0, -v, -90)
    fm.AddPoint(dk_max / 2,    (dk_max - dw) / 2)
    fm.AddPoint(dw / 2,        0.0)
    fm.AddPoint(dia / 2 + r,   0.0)
    fm.AddArc2(0.0, -r, 90)             # ends at (dia/2, -r)
    fm.AddPoint(tr, -r)                 # step in to thread radius at same z

    if length - r > b:                  # partially threaded
        thread_length = b
        if not fa.Thread:
            fm.AddPoint(tr, -1 * (length - b))
    else:
        thread_length = length - r

    fm.AddPoint(tr,           -length + dia / 10)
    fm.AddPoint(dia * 4 / 10, -length)
    fm.AddPoint(0.0,          -length)

    shape = self.RevolveZ(fm.GetFace())

    # ── Cut recess into head ──────────────────────────────────────────────
    recess.translate(Base.Vector(0.0, 0.0, k))
    shape = shape.cut(recess)

    # ── Thread cutter ─────────────────────────────────────────────────────
    if fa.Thread:
        thread_cutter = self.CreateBlindThreadCutter(thread_dia, P, thread_length)
        thread_cutter.translate(Base.Vector(0.0, 0.0, -1 * (length - thread_length)))
        shape = shape.cut(thread_cutter)

    return shape