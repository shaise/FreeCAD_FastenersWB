# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '..\DlgChangeParams.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

# Enable text translation support
from TranslateUtils import translate
import os
from FastenerBase import FSShowError
from FastenerBase import FSFastenerTypeDB
from FastenerBase import FSRemoveDigits
from FastenerBase import FSCommands
from FastenerBase import FSParam
from PySide import QtCore, QtGui
from FreeCAD import Gui
import FreeCAD
import ScrewMaker
import FastenersCmd
import PEMInserts
from FSutils import iconPath
from FSAliases import FSGetIconAlias
screwMaker = ScrewMaker.Instance

###############################################################################
# replace below with generated code from pyuic4
###############################################################################


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


class Ui_DlgChangeParams(object):
    def setupUi(self, DlgChangeParams):
        DlgChangeParams.setObjectName(_fromUtf8("DlgChangeParams"))
        DlgChangeParams.resize(451, 216)
        self.gridLayout_2 = QtGui.QGridLayout(DlgChangeParams)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.mainGroup = QtGui.QGroupBox(DlgChangeParams)
        self.mainGroup.setObjectName(_fromUtf8("mainGroup"))
        self.verticalLayout = QtGui.QVBoxLayout(self.mainGroup)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.labelFastenerType = QtGui.QLabel(self.mainGroup)
        self.labelFastenerType.setObjectName(_fromUtf8("labelFastenerType"))
        self.horizontalLayout.addWidget(self.labelFastenerType)
        self.comboFastenerType = QtGui.QComboBox(self.mainGroup)
        self.comboFastenerType.setObjectName(_fromUtf8("comboFastenerType"))
        self.horizontalLayout.addWidget(self.comboFastenerType)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.checkAutoDiameter = QtGui.QCheckBox(self.mainGroup)
        self.checkAutoDiameter.setObjectName(_fromUtf8("checkAutoDiameter"))
        self.horizontalLayout_2.addWidget(self.checkAutoDiameter)
        self.comboMatchType = QtGui.QComboBox(self.mainGroup)
        self.comboMatchType.setObjectName(_fromUtf8("comboMatchType"))
        self.horizontalLayout_2.addWidget(self.comboMatchType)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.labelDiameter = QtGui.QLabel(self.mainGroup)
        self.labelDiameter.setObjectName(_fromUtf8("labelDiameter"))
        self.horizontalLayout_3.addWidget(self.labelDiameter)
        self.comboDiameter = QtGui.QComboBox(self.mainGroup)
        self.comboDiameter.setObjectName(_fromUtf8("comboDiameter"))
        self.horizontalLayout_3.addWidget(self.comboDiameter)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.labelLength = QtGui.QLabel(self.mainGroup)
        self.labelLength.setObjectName(_fromUtf8("labelLength"))
        self.horizontalLayout_4.addWidget(self.labelLength)
        self.comboLength = QtGui.QComboBox(self.mainGroup)
        self.comboLength.setObjectName(_fromUtf8("comboLength"))
        self.horizontalLayout_4.addWidget(self.comboLength)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.layoutSetVarLength = QtGui.QHBoxLayout()
        self.layoutSetVarLength.setObjectName(_fromUtf8("layoutSetVarLength"))
        self.checkSetLength = QtGui.QCheckBox(self.mainGroup)
        self.checkSetLength.setObjectName(_fromUtf8("checkSetLength"))
        self.layoutSetVarLength.addWidget(self.checkSetLength)
        self.spinLength = QtGui.QDoubleSpinBox(self.mainGroup)
        self.spinLength.setMinimum(2.0)
        self.spinLength.setMaximum(9999.99)
        self.spinLength.setObjectName(_fromUtf8("spinLength"))
        self.layoutSetVarLength.addWidget(self.spinLength)
        self.verticalLayout.addLayout(self.layoutSetVarLength)
        spacerItem = QtGui.QSpacerItem(
            20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.gridLayout_2.addWidget(self.mainGroup, 0, 0, 1, 1)

        self.retranslateUi(DlgChangeParams)
        QtCore.QMetaObject.connectSlotsByName(DlgChangeParams)

    def retranslateUi(self, DlgChangeParams):
        DlgChangeParams.setWindowTitle(_translate(
            "DlgChangeParams", "Change fastener parameters", None))
        self.mainGroup.setTitle(_translate(
            "DlgChangeParams", "Fastener Parameters", None))
        self.labelFastenerType.setText(_translate(
            "DlgChangeParams", "Fastener type:", None))
        self.checkAutoDiameter.setText(_translate(
            "DlgChangeParams", "Auto set diameter", None))
        self.labelDiameter.setText(_translate(
            "DlgChangeParams", "Diameter:", None))
        self.labelLength.setText(_translate(
            "DlgChangeParams", "Length:", None))
        self.checkSetLength.setText(_translate(
            "DlgChangeParams", "Set length (mm):", None))

        #######################################################################
        # End position for generated code from pyuic4
        #######################################################################


def FSCPGetDiameters(type, item):
    if type == "Screw" or type == "Washer" or type == "ScrewTap" or type == "Nut":
        return screwMaker.GetAllDiams(item)
    if type == "PressNut" or type == "StandOff" or type == "Stud" or type == "HeatSet":
        return PEMInserts.FSPIGetAllDiameters(type)
    return []


def FSCPGetLengths(type, item, diam):
    if type == "Screw":
        return screwMaker.GetAllLengths(item, diam)
    if type == "StandOff" or type == "Stud":
        return PEMInserts.FSPIGetAllLengths(item, diam)
    return []


def FSCPGetDiametersFromSelection(sel):
    try:
        if len(sel) == 0:
            return []
        obj0 = sel[0]
        listDiams = screwMaker.GetAllDiams(obj0.Type)
        if len(sel) == 1:
            return listDiams
        listTypes = [obj0.Type]
        for obj in sel:
            if obj.Type in listTypes:
                continue
            listTypes.append(obj.Type)
            tmpList = listDiams
            listDiams = []
            for diam in screwMaker.GetAllDiams(obj.Type):
                if diam in tmpList:
                    listDiams.append(diam)
        return listDiams
    except:
        FSShowError()
        return []


class FSCPSelectionFilter:
    ''' Disable selection changes '''

    def allow(self, doc, obj, sub):
        return False


FSCPSelectionFilterGate = FSCPSelectionFilter()


class FSCPSelObserver:
    ''' monitor and disable selection changes '''

    def __init__(self, curSel):
        self.selection = curSel
        self.disableObserver = False

    def addSelection(self, doc, obj, sub, pnt):
        FreeCAD.Console.PrintLog("FSO-AddObj:" + "\n")
        return True

    def removeSelection(self, doc, obj, sub):  # Delete the selected object
        FreeCAD.Console.PrintLog(
            "FSO-RemSel:" + str(obj) + ":" + str(sub) + "\n")

    def setSelection(self, doc):  # Selection in ComboView
        FreeCAD.Console.PrintLog("FSO-SetSel:" + "\n")

    def clearSelection(self, doc):  # If click on the screen, clear the selection
        # if self.disableObserver:
        #  FreeCAD.Console.PrintLog("FSO-Reentering:" + "\n")
        #  return
        self.disableObserver = True
        # FreeCAD.Console.PrintLog("Clearing:" + str(len(Gui.Selection.getSelection())) + "\n")
        # Gui.Selection.clearSelection()
        for obj in self.selection:
            # FreeCAD.Console.PrintLog("Adding:" + str(obj) + "\n")
            Gui.Selection.addSelection(obj)
        FreeCAD.Console.PrintLog("FSO-ClrSel:" + "\n")
        # self.disableObserver = False
        return False


class FSTaskChangeParamDialog:
    def __init__(self, obj):
        self.object = obj
        self.baseObj = obj
        self.disableUpdate = True
        self.selection = Gui.Selection.getSelection()
        self.MatchOuter = FSParam.GetBool("MatchOuterDiameter")
        FSChangeParamDialog = QtGui.QWidget()
        FSChangeParamDialog.ui = Ui_DlgChangeParams()
        FSChangeParamDialog.ui.setupUi(FSChangeParamDialog)
        ui = FSChangeParamDialog.ui
        # FSChangeParamDialog.ui.widgetVarLength.hide()

        self.form = FSChangeParamDialog
        self.form.setWindowTitle(_translate(
            "DlgChangeParams", "Change fastener parameters", None))
        Gui.Selection.addSelectionGate(FSCPSelectionFilterGate)
        self.selobserver = FSCPSelObserver(self.selection)
        Gui.Selection.addObserver(self.selobserver)
        ui.comboFastenerType.currentIndexChanged.connect(self.onFastenerChange)
        ui.comboDiameter.currentIndexChanged.connect(self.onDiameterChange)
        ui.checkAutoDiameter.stateChanged.connect(self.onAutoDiamChange)
        ui.checkSetLength.stateChanged.connect(self.onSetLengthChange)
        ui.spinLength.setEnabled(False)
        self.hatMatchOption = False
        if len(self.selection) > 0:
            selobj = self.selection[0]
            # FreeCAD.Console.PrintLog("selobj: " + str(selobj.Proxy) + "\n")
            if hasattr(selobj, 'Proxy') and hasattr(selobj.Proxy, 'VerifyCreateMatchOuter'):
                self.hatMatchOption = True
        if self.hatMatchOption:
            ui.comboMatchType.addItem("No Change")
            ui.comboMatchType.addItem(QtGui.QIcon(os.path.join(
                iconPath, 'IconMatchTypeInner.svg')), "Match inner thread")
            ui.comboMatchType.addItem(QtGui.QIcon(os.path.join(
                iconPath, 'IconMatchTypeOuter.svg')), "Match outer thread")
            ui.comboMatchType.setEnabled(False)
            ui.comboMatchType.setCurrentIndex(0)
        else:
            ui.comboMatchType.hide()

    def FillFields(self, fstype):
        ui = self.form.ui
        self.fstype = fstype
        # FreeCAD.Console.PrintLog(fstype.typeName + str(fstype.hasLength) + str(fstype.lengthFixed) + "\n")
        ui.comboFastenerType.addItem(_translate(
            "DlgChangeParams", 'No Change', None))
        # FreeCAD.Console.PrintLog("nitems: " + str(len(fstype.items)) + "\n")
        for screw in fstype.items:
            ui.comboFastenerType.addItem(QtGui.QIcon(
                os.path.join(iconPath, FSGetIconAlias(screw) + '.svg')), screw)
        if len(fstype.items) == 1:
            ui.comboFastenerType.setCurrentIndex(1)
            ui.comboFastenerType.setEnabled(False)
        # FreeCAD.Console.PrintLog("manual\n")
        self.disableUpdate = False
        self.UpdateDiameters()
        return

    def UpdateDiameters(self):
        if self.disableUpdate:
            return
        try:
            ui = self.form.ui
            ui.comboDiameter.clear()
            ui.comboDiameter.addItem(_translate(
                "DlgChangeParams", 'No Change', None))
            # FreeCAD.Console.PrintLog(str(ui.comboFastenerType.currentIndex()) + " " + str(ui.comboFastenerType.count()) + "\n")
            if ui.comboFastenerType.currentIndex() == 0 and ui.comboFastenerType.isEnabled():
                listDiams = FSCPGetDiametersFromSelection(self.selection)
            else:
                listDiams = FSCPGetDiameters(
                    self.fstype.typeName, ui.comboFastenerType.currentText())
            for diam in listDiams:
                ui.comboDiameter.addItem(diam)
        except:
            FSShowError()
        return

    def UpdateLengths(self):
        try:
            ui = self.form.ui
            self.fixedLength = ui.comboFastenerType.currentIndex(
            ) > 0 and ui.comboDiameter.currentIndex() > 0 and self.fstype.lengthFixed
            if not self.fstype.hasLength:
                ui.labelLength.hide()
                ui.comboLength.hide()
                ui.checkSetLength.hide()
                ui.spinLength.hide()
            elif self.fixedLength:
                ui.labelLength.show()
                ui.comboLength.show()
                ui.checkSetLength.hide()
                ui.spinLength.hide()
                ui.comboLength.clear()
                ui.comboLength.addItem(_translate(
                    "DlgChangeParams", 'No Change', None))
                for slen in FSCPGetLengths(self.fstype.typeName, ui.comboFastenerType.currentText(), ui.comboDiameter.currentText()):
                    ui.comboLength.addItem(slen)
            else:
                ui.labelLength.hide()
                ui.comboLength.hide()
                ui.checkSetLength.show()
                ui.spinLength.show()
        except:
            FSShowError()
        return

    def onFastenerChange(self, findex):
        # FreeCAD.Console.PrintLog("fastener change\n")
        self.UpdateDiameters()
        return

    def onDiameterChange(self, dindex):
        self.UpdateLengths()
        return

    def onAutoDiamChange(self, val):
        try:
            ui = self.form.ui
            if ui.checkAutoDiameter.isChecked():
                ui.comboDiameter.setEnabled(False)
                ui.comboMatchType.setEnabled(True)
            else:
                ui.comboDiameter.setEnabled(True)
                ui.comboMatchType.setEnabled(False)
        except:
            FSShowError()
        return

    def onSetLengthChange(self, val):
        try:
            ui = self.form.ui
            if ui.checkSetLength.isChecked():
                ui.spinLength.setEnabled(True)
            else:
                ui.spinLength.setEnabled(False)
        except:
            FSShowError()
        return

    def accept(self):
        ui = self.form.ui
        try:
            # apply type and diameter
            for obj in self.selection:
                if ui.comboFastenerType.isEnabled() and ui.comboFastenerType.currentIndex() > 0:
                    obj.Type = str(ui.comboFastenerType.currentText())
                if ui.checkAutoDiameter.isChecked():
                    if self.hatMatchOption and ui.comboMatchType.currentIndex() > 0:
                        obj.Proxy.VerifyCreateMatchOuter(obj)
                        obj.MatchOuter = ui.comboMatchType.currentIndex() == 2
                    obj.Diameter = 'Auto'
                elif ui.comboDiameter.currentIndex() > 0:
                    obj.Diameter = str(ui.comboDiameter.currentText())
            FreeCAD.ActiveDocument.recompute()

            # apply length
            for obj in self.selection:
                if self.fstype.hasLength:
                    if self.fixedLength:
                        obj.Length = str(ui.comboLength.currentText())
                    else:
                        if ui.checkSetLength.isChecked():
                            if not self.fstype.lengthFixed:
                                obj.Length = ui.spinLength.value()
                            else:
                                d, l = screwMaker.FindClosest(
                                    obj.Type, obj.Diameter, ui.spinLength.value())
                                obj.Length = l
            FreeCAD.ActiveDocument.recompute()
        except:
            FSShowError()
        self.DialogClosing()
        return True

    def reject(self):
        self.DialogClosing()
        return True

    def DialogClosing(self):
        Gui.Selection.removeSelectionGate()
        Gui.Selection.removeObserver(self.selobserver)
        return

    def getStandardButtons(self):
        return QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel


class FSChangeParamCommand:
    """Make holes for countersunk screws"""

    def GetResources(self):
        icon = os.path.join(iconPath, 'IconChangeParam.svg')
        return {
            'Pixmap': icon,  # the name of a svg file available in the resources
            'MenuText': _translate("DlgChangeParams", "Change fastener parameters", None),
            'ToolTip': _translate("DlgChangeParams", "Change parameters of selected fasteners", None)
        }

    def Activated(self):
        dlg = FSTaskChangeParamDialog(None)
        fstype = FSFastenerTypeDB[self.Type]
        dlg.FillFields(fstype)
        Gui.Control.showDialog(dlg)
        return

    def IsActive(self):
        sel = Gui.Selection.getSelection()
        if len(sel) == 0:
            return False
        self.Type = None
        tmaxlen = 0
        for typename in FSFastenerTypeDB:
            # FreeCAD.Console.PrintLog(typename + "\n")
            if FSRemoveDigits(sel[0].Name) == typename:
                self.Type = typename
        if self.Type is None:
            return False
        for obj in sel:
            if FSRemoveDigits(obj.Name) != self.Type:
                return False
        return True


Gui.addCommand("Fasteners_ChangeParameters", FSChangeParamCommand())
FSCommands.append("Fasteners_ChangeParameters", "command")
