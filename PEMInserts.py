# -*- coding: utf-8 -*-
###############################################################################
#
#  PEMInserts.py
#
#  Copyright 2015 Shai Seger <shaise at gmail dot com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#
###############################################################################

import FastenerBase
from FastenersCmd import FSScrewObject
import ScrewMaker

screwMaker = ScrewMaker.Instance

# functions for backward compatibility.
# suggest to delete this file starting from FreeCAD 0.23


class FSPressNutObject(FSScrewObject):
    def onDocumentRestored(self, obj):
        self.originalType = "PEMPressNut"
        super().onDocumentRestored(obj)


class FSStandOffObject(FSScrewObject):
    def onDocumentRestored(self, obj):
        self.originalType = "PEMStandoff"
        super().onDocumentRestored(obj)


class FSStudObject(FSScrewObject):
    def onDocumentRestored(self, obj):
        self.originalType = "PEMStud"
        super().onDocumentRestored(obj)


class FSPcbStandOffObject(FSScrewObject):
    def onDocumentRestored(self, obj):
        self.originalType = "PCBStandoff"
        super().onDocumentRestored(obj)


class FSPcbSpacerObject(FSScrewObject):
    def onDocumentRestored(self, obj):
        self.originalType = "PCBSpacer"
        super().onDocumentRestored(obj)


class FSHeatSetObject(FSScrewObject):
    def onDocumentRestored(self, obj):
        self.originalType = "IUTHeatInsert"
        super().onDocumentRestored(obj)


FastenerBase.FSClassIcons[FSPcbSpacerObject] = 'PCBSpacer.svg'
FastenerBase.FSClassIcons[FSPcbStandOffObject] = 'PCBStandoff.svg'
FastenerBase.FSClassIcons[FSPressNutObject] = 'PEMPressNut.svg'
FastenerBase.FSClassIcons[FSStandOffObject] = 'PEMStandoff.svg'
FastenerBase.FSClassIcons[FSStudObject] = 'PEMStud.svg'
FastenerBase.FSClassIcons[FSHeatSetObject] = 'IUTHeatInsert.svg'
