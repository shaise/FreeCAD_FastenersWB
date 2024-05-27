# -*- coding: utf-8 -*-
###############################################################################
#
#  CountersunkHoles.py
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

###############################################################################
# replace below with generated code from pyuic4
###############################################################################

from PySide import QtCore, QtGui
import sys
from FreeCAD import Gui
from FreeCAD import Base
import FreeCAD
import os
import FastenerBase
from FSAliases import FSGetIconAlias
import ScrewMaker

# Enable text translation support
from TranslateUtils import translate
from FSutils import iconPath

screwMaker = ScrewMaker.Instance

QTVer = int(QtCore.qVersion().split(".")[0])

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:

    def _fromUtf8(s):
        return s


try:
    _encoding = QtGui.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)

except AttributeError:

    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class Ui_DlgCountersunktHoles(object):
    def setupUi(self, DlgCountersunktHoles):
        DlgCountersunktHoles.setObjectName(_fromUtf8("DlgCountersunktHoles"))
        DlgCountersunktHoles.resize(424, 426)
        self.gridLayout_2 = QtGui.QGridLayout(DlgCountersunktHoles)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.groupBox = QtGui.QGroupBox(DlgCountersunktHoles)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.hboxlayout = QtGui.QHBoxLayout(self.groupBox)
        # self.hboxlayout.setMargin(9)
        self.hboxlayout.setSpacing(6)
        self.hboxlayout.setObjectName(_fromUtf8("hboxlayout"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.hboxlayout.addWidget(self.label)
        self.labelBaseObject = QtGui.QLabel(self.groupBox)
        self.labelBaseObject.setObjectName(_fromUtf8("labelBaseObject"))
        self.hboxlayout.addWidget(self.labelBaseObject)
        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 1)
        self.groupBox_2 = QtGui.QGroupBox(DlgCountersunktHoles)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox_2)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(-1, 5, -1, -1)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem = QtGui.QSpacerItem(
            221, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum
        )
        self.horizontalLayout_2.addItem(spacerItem)
        self.selectAllButton = QtGui.QPushButton(self.groupBox_2)
        self.selectAllButton.setObjectName(_fromUtf8("selectAllButton"))
        self.horizontalLayout_2.addWidget(self.selectAllButton)
        self.selectNoneButton = QtGui.QPushButton(self.groupBox_2)
        self.selectNoneButton.setObjectName(_fromUtf8("selectNoneButton"))
        self.horizontalLayout_2.addWidget(self.selectNoneButton)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.treeView = QtGui.QTreeView(self.groupBox_2)
        self.treeView.setObjectName(_fromUtf8("treeView"))
        self.verticalLayout.addWidget(self.treeView)
        self.hboxlayout1 = QtGui.QHBoxLayout()
        # self.hboxlayout1.setMargin(0)
        self.hboxlayout1.setSpacing(6)
        self.hboxlayout1.setObjectName(_fromUtf8("hboxlayout1"))
        self.labelRadius = QtGui.QLabel(self.groupBox_2)
        self.labelRadius.setObjectName(_fromUtf8("labelRadius"))
        self.hboxlayout1.addWidget(self.labelRadius)
        self.comboDiameter = QtGui.QComboBox(self.groupBox_2)
        self.comboDiameter.setObjectName(_fromUtf8("comboDiameter"))
        self.comboDiameter.addItem(_fromUtf8(""))
        self.hboxlayout1.addWidget(self.comboDiameter)
        spacerItem1 = QtGui.QSpacerItem(
            40, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum
        )
        self.hboxlayout1.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.hboxlayout1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label_2 = QtGui.QLabel(self.groupBox_2)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout.addWidget(self.label_2)
        self.comboScrewType = QtGui.QComboBox(self.groupBox_2)
        self.comboScrewType.setObjectName(_fromUtf8("comboScrewType"))
        self.comboScrewType.addItem(_fromUtf8(""))
        self.horizontalLayout.addWidget(self.comboScrewType)
        spacerItem2 = QtGui.QSpacerItem(
            40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum
        )
        self.horizontalLayout.addItem(spacerItem2)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout_2.addWidget(self.groupBox_2, 1, 0, 1, 1)

        self.retranslateUi(DlgCountersunktHoles)
        QtCore.QMetaObject.connectSlotsByName(DlgCountersunktHoles)

    def retranslateUi(self, DlgCountersunktHoles):
        DlgCountersunktHoles.setWindowTitle(
            _translate("DlgCountersunktHoles", "Countersunk screw holes", None)
        )
        self.groupBox.setTitle(_translate(
            "DlgCountersunktHoles", "Shape", None))
        self.label.setText(_translate(
            "DlgCountersunktHoles", "Base shape:", None))
        self.labelBaseObject.setText(_translate(
            "DlgCountersunktHoles", "Base", None))
        self.groupBox_2.setTitle(
            _translate("DlgCountersunktHoles", "Chamfer Parameters", None)
        )
        self.selectAllButton.setText(_translate(
            "DlgCountersunktHoles", "All", None))
        self.selectNoneButton.setText(_translate(
            "DlgCountersunktHoles", "None", None))
        self.labelRadius.setText(_translate(
            "DlgCountersunktHoles", "Diameter:", None))
        self.comboDiameter.setItemText(
            0, _translate("DlgCountersunktHoles", "No selection", None)
        )
        self.label_2.setText(_translate(
            "DlgCountersunktHoles", "Screw type:", None))
        self.comboScrewType.setItemText(
            0, _translate("DlgCountersunktHoles", "No Selection", None)
        )

        #######################################################################
        # End position for generated code from pyuic4
        #######################################################################

    def fillTable(self, parent, baseObj, edgelist):
        self.comboDiameter.currentIndexChanged.connect(self.onDiameterChange)
        self.comboScrewType.currentIndexChanged.connect(self.onScrewChange)
        self.selectNoneButton.clicked.connect(self.onNoneClicked)
        self.selectAllButton.clicked.connect(self.onAllClicked)
        self.itemRefreshDisabled = False

        dm = FSDiameterModel(parent)
        dm.insertColumns(0, 2)
        dm.setHeaderData(
            0,
            QtCore.Qt.Horizontal,
            translate("DlgCountersunktHoles", "Edges to chamfer"),
            QtCore.Qt.DisplayRole,
        )
        dm.setHeaderData(
            1,
            QtCore.Qt.Horizontal,
            translate("DlgCountersunktHoles", "Diameter"),
            QtCore.Qt.DisplayRole,
        )
        edges = []
        for i in range(len(baseObj.Shape.Edges)):
            edge = "Edge" + str(i + 1)
            if FSIsValidEdge(baseObj, edge):
                edges.append(edge)
        nedges = len(edges)
        dm.insertRows(0, nedges)

        self.treeView.setRootIsDecorated(False)
        idelegate = FSDiameterDelegate(parent)
        idelegate.setUi(self)
        self.treeView.setItemDelegate(idelegate)
        self.treeView.setModel(dm)
        self.model = dm

        header = self.treeView.header()
        header.setResizeMode(0, QtGui.QHeaderView.Stretch)
        header.setDefaultAlignment(QtCore.Qt.AlignLeft)
        # header.setMovable(False)

        edgediams = {}
        type = "Default"
        # FreeCAD.Console.PrintLog("Num Edge:" + str(len(edgelist)) + "\n")
        for edgediam in edgelist:
            edge, diam, invert, offset, type = cshSplitEdgeDiam(edgediam)
            # FreeCAD.Console.PrintLog("Add Edge:" + str(edge) + "'" + str(diam) + "\n")
            edgediams[edge] = diam

        self.fillScrewType(screwMaker.GetAllCountersunkTypes())
        idx = self.comboScrewType.findText(type)
        if idx >= 0:
            self.comboScrewType.setCurrentIndex(idx)
        self.fillDiameters(type)

        for i in range(nedges):
            edge = edges[i]
            dm.setData(dm.index(i, 0), edge)
            if edge in edgediams:
                dm.setData(dm.index(i, 0), QtCore.Qt.Checked,
                           QtCore.Qt.CheckStateRole)
                dm.setData(dm.index(i, 1), edgediams[edge])
            else:
                # dm.setData(dm.index(i,0), i, QtCore.Qt.UserRole)
                dm.setData(
                    dm.index(i, 0), QtCore.Qt.Unchecked, QtCore.Qt.CheckStateRole
                )
                dm.setData(dm.index(i, 1), self.comboDiameter.itemText(0))

    def fillScrewType(self, screwList):
        self.comboScrewType.clear()
        self.comboScrewType.addItem(translate("Fasteners", "Default"))
        for screw in screwList:
            self.comboScrewType.addItem(
                QtGui.QIcon(os.path.join(iconPath, FSGetIconAlias(screw) + ".svg")), screw
            )

    def fillDiameters(self, type):
        self.diamTable = cshGetTable(type)
        self.diamList = sorted(self.diamTable, key=FastenerBase.MToFloat)
        self.comboDiameter.clear()
        self.comboDiameter.addItems(self.diamList)

    def GetData(self):
        dm = self.model
        nedges = dm.rowCount()
        listEdges = []
        for i in range(nedges):
            if dm.data(dm.index(i, 0), QtCore.Qt.CheckStateRole) == QtCore.Qt.Unchecked:
                continue
            listEdges.append(
                dm.data(dm.index(i, 0))
                + ":"
                + dm.data(dm.index(i, 1))
                + ":0:0:"
                + self.SelectedType()
            )
        return listEdges

    def AddEdges(self, obj, edges):
        dm = self.model
        nedges = dm.rowCount()
        self.treeView.selectionModel().clearSelection()
        self.itemRefreshDisabled = True
        for edge in edges:
            # FreeCAD.Console.PrintLog("Diam Table:" + str(edge) + "\n")
            for i in range(nedges):
                if dm.data(dm.index(i, 0)) == edge:
                    m = FastenerBase.FSAutoDiameterM(
                        obj.Shape.getElement(edge), self.diamTable, -1
                    )
                    index = dm.index(i, 0)
                    dm.setData(index, QtCore.Qt.Checked,
                               QtCore.Qt.CheckStateRole)
                    dm.setData(dm.index(i, 1), m)
                    if QTVer >= 5:
                        self.treeView.selectionModel().select(
                            index, QtCore.QItemSelectionModel.Select
                        )
                    else:
                        self.treeView.selectionModel().select(
                            index, QtGui.QItemSelectionModel.Select
                        )

        self.itemRefreshDisabled = False
        dm.itemChanged.emit(None)

    def SelectedType(self):
        return self.comboScrewType.currentText()

    def GetClosest(self, diam):
        if diam in self.diamList:
            return diam
        d = FastenerBase.MToFloat(diam)
        l = len(self.diamList)
        if l == 1:
            return self.diamList[0]
        if d > FastenerBase.MToFloat(self.diamList[l - 1]):
            return self.diamList[l - 1]
        for d1 in self.diamList:
            if d < FastenerBase.MToFloat(d1):
                return d1

    def onDiameterChange(self, diamindex):
        if self.itemRefreshDisabled:
            return
        diam = self.comboDiameter.itemText(diamindex)
        dm = self.model
        nedges = dm.rowCount()
        self.itemRefreshDisabled = True
        for i in range(nedges):
            if dm.data(dm.index(i, 0), QtCore.Qt.CheckStateRole) == QtCore.Qt.Checked:
                dm.setData(dm.index(i, 1), diam)
        self.itemRefreshDisabled = False
        dm.itemChanged.emit(None)

    def onScrewChange(self, screwindex):
        if screwindex < 0:
            return
        self.itemRefreshDisabled = True
        type = self.comboScrewType.itemText(screwindex)
        # FreeCAD.Console.PrintLog("ScrewChange " + str(screwindex) + ":" + str(type) + "\n")
        self.fillDiameters(type)
        # update diameters if needed
        dm = self.model
        nedges = dm.rowCount()
        isChange = False
        for i in range(nedges):
            diam = dm.data(dm.index(i, 1))
            # FreeCAD.Console.PrintLog("Looking for diam:" + str(i) + "," + str(diam) + "\n")
            if diam is None:
                continue
            diam1 = self.GetClosest(diam)
            # FreeCAD.Console.PrintLog(diam + "->" + diam1 + "\n")
            if diam != diam1:
                dm.setData(dm.index(i, 1), diam1)
                if (
                    dm.data(dm.index(i, 0), QtCore.Qt.CheckStateRole)
                    == QtCore.Qt.Checked
                ):
                    isChange = True
        self.itemRefreshDisabled = False
        if isChange:
            dm.itemChanged.emit(None)

    def onNoneClicked(self):
        dm = self.model
        nedges = dm.rowCount()
        self.itemRefreshDisabled = True
        for i in range(nedges):
            dm.setData(dm.index(i, 0), QtCore.Qt.Unchecked,
                       QtCore.Qt.CheckStateRole)
        self.itemRefreshDisabled = False
        dm.itemChanged.emit(None)

    def onAllClicked(self):
        dm = self.model
        nedges = dm.rowCount()
        self.itemRefreshDisabled = True
        for i in range(nedges):
            dm.setData(dm.index(i, 0), QtCore.Qt.Checked,
                       QtCore.Qt.CheckStateRole)
        self.itemRefreshDisabled = False
        dm.itemChanged.emit(None)


class FSDiameterDelegate(QtGui.QItemDelegate):
    def createEditor(self, parent, option, index):
        if index.column() < 1:
            return None

        editor = QtGui.QComboBox(parent)
        try:
            editor.addItems(self.ui.diamList)
        except:
            FreeCAD.Console.PrintLog(str(sys.exc_info()) + "\n")
        return editor

    def setEditorData(self, editor, index):
        value = index.data(QtCore.Qt.EditRole)
        index = editor.findText(value)
        if index >= 0:
            editor.setCurrentIndex(index)

    def setModelData(self, editor, model, index):
        value = editor.currentText()
        model.setData(index, value, QtCore.Qt.EditRole)

    def pdateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def setUi(self, ui):
        self.ui = ui


class FSDiameterModel(QtGui.QStandardItemModel):
    def updateCheckStates(self):
        self.layoutChanged()

    def flags(self, index):
        # fl = QtGui.QStandardItemModel.flags(index)
        fl = super(FSDiameterModel, self).flags(index)
        if index.column() == 0:
            # FreeCAD.Console.PrintLog(str(fl) + "\n")
            fl = fl | QtCore.Qt.ItemIsUserCheckable
        return fl

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        # ok = QStandardItemModel::setData(index, value, role);
        ok = super(FSDiameterModel, self).setData(index, value, role)
        # if role == QtCore.Qt.CheckStateRole:
        #    self.toggleCheckState(index)
        return ok


#    connect(model, SIGNAL(toggleCheckState(const QModelIndex&)),
#            this, SLOT(toggleCheckState(const QModelIndex&)));
#    // timer for highlighting
#    d->highlighttimer = new QTimer(this);
#    d->highlighttimer->setSingleShot(true);
#    connect(d->highlighttimer,SIGNAL(timeout()),
#            this, SLOT(onHighlightEdges()));


def FSIsValidEdge(obj, edge):
    # FreeCAD.Console.PrintLog("IsValid " + str(obj) + ":" + str(edge) + "\n")
    shape = obj.Shape.getElement(edge)
    if shape is None:
        return False
    if not (hasattr(shape, "Curve")):
        return False
    if not (hasattr(shape.Curve, "Center")):
        return False
    return True


class FSSelectionFilter:
    """A selection filter that let the user select only the edges that are circular"""

    def allow(self, doc, obj, sub):
        if obj is None or sub is None or len(sub) == 0:
            return True
        if sub[0:4] == "Face":
            return True
        # FreeCAD.Console.PrintLog("testing " + str(obj) + ":" + str(sub) + str(len(sub)) + "\n")
        if FSIsValidEdge(obj, sub) == False:
            return False
        # self.lastobj = obj.Name
        # self.lastedge = sub
        return True


FSSelectionFilterGate = FSSelectionFilter()


class FSSelObserver:
    """monitor selection changes to update the task form"""

    def __init__(self, dialog):
        self.dialog = dialog
        self.disableObserver = False

    def enable(self):
        """function for QtCore.QTimer.singleShot"""
        self.disableObserver = False

    def addSelection(self, doc, obj, sub, pnt):
        if self.disableObserver:
            return
        FreeCAD.Console.PrintLog(
            "FSO-AddSel:" + str(obj) + ":" + str(sub) + "\n")
        # if len(sub) == 0 and obj == FSSelectionFilterGate.lastobj:
        #  self.dialog.addSelection(FSSelectionFilterGate.lastedge)
        if sub[0:4] == "Edge":
            self.dialog.addSelectionEdge(obj, sub)
        elif sub[0:4] == "Face":
            self.dialog.addSelectionFace(obj, sub)
        return True

    def removeSelection(self, doc, obj, sub):  # Delete the selected object
        FreeCAD.Console.PrintLog(
            "FSO-RemSel:" + str(obj) + ":" + str(sub) + "\n")

    def setSelection(self, doc):  # Selection in ComboView
        FreeCAD.Console.PrintLog("FSO-SetSel:" + "\n")

    def clearSelection(self, doc):  # If click on the screen, clear the selection
        FreeCAD.Console.PrintLog("FSO-ClrSel:" + "\n")


class FSTaskFilletDialog:
    def __init__(self, obj):
        self.object = obj
        if obj is None:
            self.baseObj = Gui.Selection.getSelection()[0]
            edgelist = []
        else:
            edgelist = obj.diameters
            self.baseObj = obj.baseObject[0]
            Gui.ActiveDocument.getObject(obj.Name).Visibility = False
            Gui.ActiveDocument.getObject(self.baseObj.Name).Visibility = True
        FSFilletDialog = QtGui.QWidget()
        FSFilletDialog.ui = Ui_DlgCountersunktHoles()
        FSFilletDialog.ui.setupUi(FSFilletDialog)
        FreeCAD.Console.PrintLog(str(self.baseObj) + "\n")
        FSFilletDialog.ui.fillTable(FSFilletDialog, self.baseObj, edgelist)
        FSFilletDialog.ui.labelBaseObject.setText(self.baseObj.Name)
        FSFilletDialog.ui.model.itemChanged.connect(self.onItemChanged)

        self.form = FSFilletDialog
        self.form.setWindowTitle(
            translate("DlgCountersunktHoles",
                      "Chamfer holes for countersunk screws")
        )
        Gui.Selection.addSelectionGate(FSSelectionFilterGate)
        self.selobserver = FSSelObserver(self)
        Gui.Selection.addObserver(self.selobserver)
        self.RefreshSelection()

    def accept(self):
        if self.object is None:
            self.object = FreeCAD.ActiveDocument.addObject(
                "Part::FeaturePython", "Countersunk"
            )
            FSCountersunkObject(self.object, self.baseObj)
            # self.object.ViewObject.Proxy = 0
            FSViewProviderCountersunk(self.object.ViewObject)
        self.object.diameters = self.form.ui.GetData()
        FreeCAD.Console.PrintLog(str(self.object.diameters) + "\n")
        FreeCAD.ActiveDocument.recompute()
        self.DialogClosing()
        return True

    def reject(self):
        self.DialogClosing()
        return True

    def DialogClosing(self):
        if self.object is not None:
            Gui.ActiveDocument.getObject(self.object.Name).Visibility = True
            Gui.ActiveDocument.getObject(self.baseObj.Name).Visibility = False
        Gui.ActiveDocument.resetEdit()
        Gui.Selection.removeSelectionGate()
        Gui.Selection.removeObserver(self.selobserver)

    def getStandardButtons(self):
        return QtGui.QDialogButtonBox.Ok + QtGui.QDialogButtonBox.Cancel

    def addSelectionEdge(self, objname, edge):
        if objname == self.baseObj.Name:
            self.form.ui.AddEdges(self.baseObj, [edge])
        self.RefreshSelection()

    def addSelectionFace(self, objname, name):
        obj = self.baseObj
        if objname == obj.Name:
            face = obj.Shape.getElement(name)
            if face is None:
                return
            edges = []
            for edge in face.Edges:
                if not (hasattr(edge, "Curve")):
                    continue
                if not (hasattr(edge.Curve, "Center")):
                    continue
                edges.append(FastenerBase.GetEdgeName(obj.Shape, edge))
            self.form.ui.AddEdges(obj, edges)
        self.RefreshSelection()

    def RefreshSelection(self):
        FreeCAD.Console.PrintLog("Refresh: " "\n")
        self.selobserver.disableObserver = True
        Gui.Selection.clearSelection()
        edges = self.form.ui.GetData()
        FreeCAD.Console.PrintLog("Reselect: " + str(edges) + "\n")
        for edge in edges:
            # Note: edge has this format: "Edge15:M5:0:0:Default".
            Gui.Selection.addSelection(self.baseObj, edge.split(":")[0])
        QtCore.QTimer.singleShot(0, self.selobserver.enable)

    def onItemChanged(self, item):
        # FreeCAD.Console.PrintLog("itemChanged: " "\n")
        if not (self.form.ui.itemRefreshDisabled):
            self.RefreshSelection()


class FSViewProviderCountersunk:
    "A View provider for countersunk holes"

    def __init__(self, obj):
        obj.Proxy = self
        self.Object = obj.Object

    def attach(self, obj):
        self.Object = obj.Object
        return

    # def updateData(self, fp, prop):
    #  return

    def getDisplayModes(self, obj):
        modes = []
        return modes

    def setDisplayMode(self, mode):
        return mode

    def onChanged(self, vp, prop):
        return

    def dumps(self):
        #        return {'ObjectName' : self.Object.Name}
        return None

    def loads(self, state):
        if state is not None:
            import FreeCAD
            doc = FreeCAD.ActiveDocument  # crap
            self.Object = doc.getObject(state["ObjectName"])

    if FastenerBase.FsUseGetSetState: # compatibility with old versions
        def __getstate__(self):
            return self.dumps()

        def __setstate__(self, state):
            self.loads(state)

    def claimChildren(self):
        objs = []
        if hasattr(self.Object, "baseObject"):
            objs.append(self.Object.baseObject[0])
        return objs

    def getIcon(self):
        return os.path.join(iconPath, "IconCSHole.svg")

    def setEdit(self, vobj, mode=0):
        # FreeCADGui.runCommand("Draft_Edit")
        Gui.Control.showDialog(FSTaskFilletDialog(self.Object))
        return True

    def unsetEdit(self, vobj, mode=0):
        # self.__vobject__.finishEditing()
        FreeCAD.Console.PrintLog("Finish edit\n")
        # self.finishEditing();
        Gui.Control.closeDialog()
        return False


# FSCSHSizes = ['M1.6', 'M2', 'M2.5', 'M3', 'M3.5', 'M4', 'M5', 'M6', 'M8', 'M10', 'M12', 'M14', 'M16', 'M20']
FSCSHTable = {
    #       d     k
    "M1.6": (2.8, 1.0),
    "M2": (3.6, 1.2),
    "M2.5": (4.5, 1.5),
    "M3": (6.0, 1.86),
    "M3.5": (7.1, 2.35),
    "M4": (8.0, 2.48),
    "M5": (10.0, 3.10),
    "M6": (12.0, 3.72),
    "M8": (16.0, 4.96),
    "M10": (20.5, 6.20),
    "M12": (25.0, 7.44),
    "M14": (28.4, 8.40),
    "M16": (31.0, 8.80),
    "M20": (38.0, 10.16),
}


def cshMakeFace(m, d, k):
    m = m / 2
    d = (d / 2) + 0.2
    h1 = m + k
    h2 = k - (d - m)

    fm = FastenerBase.FSFaceMaker()
    fm.AddPoint(0, h1)
    fm.AddPoint(d, h2)
    fm.AddPoint(d, -h2)
    fm.AddPoint(0, -h1)
    return fm.GetFace()


def cshGetTable(type):
    if type == "Default":
        table = FSCSHTable
    else:
        table = screwMaker.GetCountersunkDiams(type)
    return table


def cshMakeCSHole(diam, type):
    table = cshGetTable(type)
    if not (diam in table):
        return None

    (key, shape) = FastenerBase.FSGetKey("CSHole", diam, 0)
    if shape is not None:
        return shape

    m = FastenerBase.MToFloat(diam)
    d, k = table[diam]

    f = cshMakeFace(m, d, k)
    p = f.revolve(Base.Vector(0.0, 0.0, 0.0), Base.Vector(0.0, 0.0, 1.0), 360)
    FastenerBase.FSCache[key] = p
    return p


def cshSplitEdgeDiam(edgeParam):
    res = edgeParam.split(":")
    if len(res) < 5:
        res.append("Default")
    return res


class FSCountersunkObject:
    def __init__(self, obj, attachTo):
        '''"Add StandOff (self clinching) type fastener"'''

        obj.addProperty(
            "App::PropertyStringList",
            "diameters",
            "Parameters",
            "Countersunk diameters",
        ).diameters = []
        # obj.addProperty("Part::PropertyFilletEdges","diameters","Parameters","Countersunk diameters").diameters = [(1,1,1), (2,1,1)]
        obj.addProperty(
            "App::PropertyLinkSub", "baseObject", "Parameters", "Base object"
        ).baseObject = attachTo
        obj.setEditorMode("diameters", 2)
        obj.Proxy = self

    def execute(self, fp):
        '''"Print a short message when doing a recomputation, this method is mandatory"'''
        # fp.Shape = Part.makeBox(1,1,1 + len(fp.diameters))
        origshape = fp.baseObject[0].Shape
        shape = origshape
        for diam in fp.diameters:
            FreeCAD.Console.PrintLog(
                "Generating hole tool for: " + diam + "\n")
            edge, m, f, o, type = cshSplitEdgeDiam(diam)
            cshole = cshMakeCSHole(m, type)
            FastenerBase.FSMoveToObject(
                cshole, origshape.getElement(edge), f == "1", float(o)
            )
            shape = shape.cut(cshole)
        fp.Shape = shape

    def loads(self, state):
        FreeCAD.Console.PrintWarning(translate("CountersunkDeprecation", "The Fasteners Workbench countersunk holes feature is deprecated, and may be removed in the future. Please consider using a PartDesign Hole feature instead") + "\n")


# to monitor selections: add SelObserver http://www.freecadweb.org/wiki/index.php?title=Code_snippets#Function_resident_with_the_mouse_click_action
# to filter selections: use Gui.Selection.SelectionGate
