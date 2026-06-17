# -*- coding: utf-8 -*-
"""
***************************************************************************
*   Copyright (c) 2022 - FreeCAD FastenersWB Authors                      *
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

import os
import csv
import FreeCAD

_dir = os.path.dirname(__file__)
iconPath = os.path.join(_dir, "Icons")
fsdatapath = os.path.join(_dir, "FsData")
languagePath = os.path.join(_dir, "Resources", "translations")
pref_file_path = os.path.join(_dir, "FSprefs.ui")
settings3d_file_path = os.path.join(_dir, "Widget3DPrintSettings.ui")

# read .csv files into dictionary tables
# multiple tables can be put in a single file by placing the table name as a single word before the table
# several names can share the same table by placing all the names as a single word line above the table


def csv2dict(filename, defaultTableName, fieldsnamed=True):
    with open(filename) as fp:
        reader = csv.reader(
            fp,
            skipinitialspace=True,
            dialect="unix",
            quoting=csv.QUOTE_NONNUMERIC,
        )
        tables = {}
        tables["titles"] = {}
        newTable = False
        firstTime = True
        cur_table = {}
        table_names = {defaultTableName}

        # if fieldsnamed:
        # skip the first line
        #    next(reader)
        for line_list in reader:
            if len(line_list) == 0:
                continue
            elif len(line_list) == 1:
                tablename = line_list[0]
                if not newTable:
                    cur_table = {}
                    table_names = set()
                    newTable = True
                table_names.add(tablename)
                continue
            key = line_list[0]
            data = tuple(line_list[1:])
            if newTable or firstTime:
                firstTime = False
                newTable = False
                for tablename in table_names:
                    tables[tablename] = cur_table
                if fieldsnamed:
                    for tablename in table_names:
                        tables["titles"][tablename] = data
                    continue
            cur_table[key] = data
        return tables


def isGuiLoaded():
    """Check if the FreeCAD GUI is loaded."""
    if hasattr(FreeCAD, "GuiUp"):
        return FreeCAD.GuiUp
    return False

def parseInch(txt : str):
    """Parse a string representing an inch measurement, 
       which may include fractions, and return its value in mm as a float.
       Examples of valid formats:
       "1" -> 25.4
       "1/2" -> 12.7
       "1 1/2in" -> 38.1
       """
    clean_txt = ""
    for c in txt:
        if c.isdecimal() or c in ".-":
            clean_txt += c
        else:
            clean_txt += " "
    parts = [float(x) for x in clean_txt.split()]
    if len(parts) == 1:
        return parts[0] * 25.4
    elif len(parts) == 2:
        return (parts[0] / parts[1]) * 25.4
    elif len(parts) == 3:
        return (parts[0] + parts[1] / parts[2]) * 25.4
    else:
        raise ValueError(f"Invalid inch format: '{txt}'")
    
def parseLength(txt : str):
    """Parse a length string after cleaning all non-digit characters. return the first float value found.
       if the string contains "in", it will be parsed as an inch measurement and converted to mm.
       if the string start with K, (as in WN standard) length is devided by 10
       Examples of valid formats:
       "10" -> 10.0
       "10mm" -> 10.0
       "M8" -> 8.0
       "1in" -> 25.4
       "K60" -> 6.0
       """
    if "in" in txt:
        # handle inch format, e.g: "1in", "1.5in", etc.
        return parseInch(txt)

    clean_txt = ""
    leftover_txt = ""
    for c in txt:
        if c.isdecimal() or c in ".-":
            clean_txt += c
            leftover_txt += " "
        else:
            clean_txt += " "
            leftover_txt += c
    parts = clean_txt.split()
    if len(parts) > 0:
        res = float(parts[0])
        if leftover_txt.rstrip() == "K":
            res /= 10.0
        return res
    else:
        raise ValueError(f"Invalid float format: '{txt}'")