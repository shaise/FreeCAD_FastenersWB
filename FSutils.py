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

_dir = os.path.dirname(__file__)
iconPath = os.path.join(_dir, 'Icons')
fsdatapath = os.path.join(_dir, 'FsData')
LanguagePath = os.path.join(_dir, 'translations')
pref_file_path = os.path.join(_dir, "FSprefs.ui")

# read .csv files into dictionary tables
# multiple tables can be put in a single file by placing the table name as a single word before the table
# several names can share the same table by placing all the names as a single word line above the table


def csv2dict(filename, defaultTableName, fieldsnamed=True):
    with open(filename) as fp:
        reader = csv.reader(
            fp,
            skipinitialspace=True,
            dialect='unix',
            quoting=csv.QUOTE_NONNUMERIC,
        )
        tables = {}
        tables['titles'] = {}
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
                        tables['titles'][tablename] = data
                    continue
            cur_table[key] = data
        return tables
