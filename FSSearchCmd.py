# -*- coding: utf-8 -*-

import os
import FreeCADGui
import FreeCAD
from FreeCAD import Gui
from FSAliases import FSGetIconAlias
import FSutils
import FastenerBase
from FastenersCmd import FSScrewCommandTable
from FSutils import iconPath

try:
    from PySide import QtCore, QtGui, QtWidgets
except ImportError:
    from PySide2 import QtCore, QtGui, QtWidgets

translate = FreeCAD.Qt.translate

# Locate the icons directory shipped with the workbench
_FW_DIR = os.path.dirname(__file__)
_ICONS_DIR = os.path.join(_FW_DIR, "Icons")


class _FastenerRow(QtWidgets.QWidget):
    """A row widget that properly reports its own size to QListWidget."""

    def __init__(self, icon_pixmap, desc_text, icon_size=48, parent=None):
        super().__init__(parent)
        self._icon_size = icon_size

        lay = QtWidgets.QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(14)
        lay.setAlignment(QtCore.Qt.AlignVCenter)

        # Icon
        lbl_icon = QtWidgets.QLabel()
        lbl_icon.setFixedSize(icon_size, icon_size)
        lbl_icon.setAlignment(QtCore.Qt.AlignCenter)
        lbl_icon.setScaledContents(True)
        if icon_pixmap and not icon_pixmap.isNull():
            lbl_icon.setPixmap(icon_pixmap)
        else:
            lbl_icon.setText("\U0001F527")
            lbl_icon.setStyleSheet(
                "font-size: 28px; background: #333; border-radius: 2px;"
            )
        lay.addWidget(lbl_icon, 0, QtCore.Qt.AlignVCenter)

        # Description
        lbl_desc = QtWidgets.QLabel(desc_text)
        lbl_desc.setWordWrap(True)
        lbl_desc.setTextFormat(QtCore.Qt.PlainText)
        lbl_desc.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        font = lbl_desc.font()
        font.setPointSize(font.pointSize() + 1)
        lbl_desc.setFont(font)
        lbl_desc.setStyleSheet("color: #1a1a1a; padding: 2px 0;")
        lay.addWidget(lbl_desc, 1)

    def sizeHint(self):
        # Force the layout to compute its geometry
        self.layout().activate()
        sh = self.layout().totalSizeHint()
        # Ensure minimum height = icon + vertical padding
        min_h = self._icon_size + 16
        return QtCore.QSize(sh.width(), max(sh.height(), min_h))

# ═══════════════════════════════════════════════════════════════════════════
#  Dialog
# ═══════════════════════════════════════════════════════════════════════════
class FastenerSearchDialog(QtWidgets.QDialog):
    """Pop-up that lets the user search every fastener by description and
    insert one into the active document with a single click."""

    ICON_SIZE = 48
    MAX_DESC_LINES = 3

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Search Fasteners")
        self.setMinimumSize(520, 620)
        self.resize(560, 700)
        self.setWindowFlags(
            self.windowFlags()
            | QtCore.Qt.WindowMinMaxButtonsHint
            | QtCore.Qt.WindowCloseButtonHint
        )
        self._build_ui()
        self._apply_filter("")  # show everything at first

    # ── UI construction ─────────────────────────────────────────────────
    def _build_ui(self):
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 6)
        root.setSpacing(4)

        # Title
        title = QtWidgets.QLabel(translate("FastenerSearch", "Search Fasteners"))
        title.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #848484;"
        )
        root.addWidget(title)

        # Search bar
        self.search_edit = QtWidgets.QLineEdit()
        self.search_edit.setPlaceholderText(
            translate("FastenerSearch", "Type to search by description") + "\u2026"
        )
        self.search_edit.setClearButtonEnabled(True)
        self.search_edit.setStyleSheet(
            "QLineEdit {"
            "  padding: 4px 6px;"
            "  border: 2px solid #444;"
            "  border-radius: 2px;"
            "  background: #bababa;"
            "  color: #1a1a1a;"
            "  font-size: 14px;"
            "  selection-background-color: #5a5a5a;"
            "}"
            "QLineEdit:focus { border-color: #6a9fd8; }"
        )
        root.addWidget(self.search_edit)

        # Result count
        self.count_label = QtWidgets.QLabel("")
        self.count_label.setStyleSheet(
            "color: #777; font-size: 11px; padding-left: 2px;"
        )
        root.addWidget(self.count_label)

        # List
        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.setSpacing(3)
        self.list_widget.setUniformItemSizes(False)
        self.list_widget.setIconSize(QtCore.QSize(self.ICON_SIZE, self.ICON_SIZE))
        self.list_widget.setResizeMode(QtWidgets.QListWidget.Adjust)
        self.list_widget.setStyleSheet(
            "QListWidget {"
            "  border: 1px solid #3a3a3a;"
            "  border-radius: 2px;"
            "  background: #bababa;"
            "  padding: 4px;"
            "  outline: none;"
            "}"
            "QListWidget::item {"
            "  border-radius: 2px;"
            "  padding: 2px;"
            "  height: 48px;"
            "  margin: 1px 2px;"
            "  color: #1a1a1a;"
            "}"
            "QListWidget::item:selected {"
            "  background: #909090;"
            "  border: 1px solid #5a7a9a;"
            "  color: #d0d0d0;"
            "}"
            "QListWidget::item:hover {"
            "  background: #a0a0a0;"
            "  color: #d0d0d0;"
            "}"
        )
        root.addWidget(self.list_widget, 1)

        # Buttons
        btn_row = QtWidgets.QHBoxLayout()
        btn_row.addStretch()

        self.insert_btn = QtWidgets.QPushButton(translate("FastenerSearch", "Insert Fastener"))
        self.insert_btn.setEnabled(False)
        self.insert_btn.setFixedHeight(36)
        self.insert_btn.setStyleSheet(
            "QPushButton {"
            "  padding: 6px 24px;"
            "  background: #3d6b99;"
            "  color: #fff;"
            "  border: none;"
            "  border-radius: 4px;"
            "  font-weight: bold;"
            "  font-size: 13px;"
            "}"
            "QPushButton:hover  { background: #4a7fb3; }"
            "QPushButton:pressed { background: #2d5580; }"
            "QPushButton:disabled { background: #bababa; color: #aaa; }"
        )

        cancel_btn = QtWidgets.QPushButton(translate("FastenerSearch", "Close"))
        cancel_btn.setFixedHeight(36)
        cancel_btn.setStyleSheet(
            "QPushButton {"
            "  padding: 6px 24px;"
            "  background: #bababa;"
            "  color: #111;"
            "  border: none;"
            "  border-radius: 2px;"
            "  font-size: 13px;"
            "}"
            "QPushButton:hover { background: #aaa; }"
        )

        btn_row.addWidget(self.insert_btn)
        btn_row.addWidget(cancel_btn)
        root.addLayout(btn_row)

        # Connections
        self.search_edit.textChanged.connect(self._apply_filter)
        self.list_widget.itemDoubleClicked.connect(self._on_insert)
        self.insert_btn.clicked.connect(self._on_insert)
        cancel_btn.clicked.connect(self.reject)
        self.list_widget.itemSelectionChanged.connect(
            lambda: self.insert_btn.setEnabled(
                self.list_widget.currentItem() is not None
            )
        )

    # ── Filtering ───────────────────────────────────────────────────────
    def _apply_filter(self, text):
        self.list_widget.clear()
        self.insert_btn.setEnabled(False)
        text_lower = text.strip().lower()
        if len(text_lower) < 2:
            self.count_label.setText(translate("FastenerSearch", "Type at least 2 characters to search"))
            return
        matched = []
        for ftype, info in FSScrewCommandTable.items():
            desc = info[0]
            group = info[1]
            cmd_name = 'FS' + ftype
            icon = os.path.join(iconPath, FSGetIconAlias(ftype) + '.svg')
            # Search against both the menu text, group  and the description
            searchable = (ftype + " " + desc + " " + group).lower()
            text_words = text_lower.split()
            if all(word in searchable for word in text_words):
                matched.append((cmd_name, ftype, desc, group, icon))

        self.count_label.setText(
            f"{len(matched)} fastener{'s' if len(matched) != 1 else ''} found"
        )

        for cmd_name, ftype, desc, group, icon in matched:
            self._add_item(cmd_name, ftype, desc, group, icon)

    def _add_item(self, cmd_name, ftype, desc, group, pixmap):
        icon = self._load_icon(pixmap)

        item = QtWidgets.QListWidgetItem()
        item.setData(QtCore.Qt.UserRole, cmd_name)
        # item.setToolTip(desc)

        pixmap_obj = None
        if icon and not icon.isNull():
            pixmap_obj = icon.pixmap(self.ICON_SIZE, self.ICON_SIZE)

        desc_text = ftype + "       (" + group + ")" + "\n" + desc if desc else ftype
        row = _FastenerRow(pixmap_obj, desc_text, self.ICON_SIZE)

        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, row)

    # ── Icon loader ─────────────────────────────────────────────────────
    def _load_icon(self, pixmap_path):
        if not pixmap_path:
            return QtGui.QIcon()
        icon = QtGui.QIcon(pixmap_path)
        if not icon.isNull():
            return icon
        return QtGui.QIcon()

    # ── Insert action ───────────────────────────────────────────────────
    def _on_insert(self):
        item = self.list_widget.currentItem()
        if item is None:
            return
        cmd_name = item.data(QtCore.Qt.UserRole)
        if not cmd_name:
            return

        if FreeCAD.ActiveDocument is None:
            FreeCAD.newDocument("Fasteners")

        try:
            FreeCADGui.runCommand(str(cmd_name))
        except Exception as exc:
            FreeCAD.Console.PrintError(
                f"[FastenerSearch] Failed to run '{cmd_name}': {exc}\n"
            )


# ═══════════════════════════════════════════════════════════════════════════
#  FreeCAD Command wrapper
# ═══════════════════════════════════════════════════════════════════════════
class FSSearchCommand:
    """FreeCAD command that opens the fastener search dialog."""

    _dialog = None

    def GetResources(self):
        icon = os.path.join(FSutils.iconPath, "IconSearch.svg")
        return {
            "Pixmap": icon,
            "MenuText": translate("FastenerSearch", "Search Fasteners"),
            "ToolTip": (translate(
                "FastenerSearch", 
                "Search fasteners by name or description."
            )),
        }

    def Activated(self):
        # Re-use a single dialog instance; bring it forward if already open
        if FSSearchCommand._dialog is None:
            FSSearchCommand._dialog = FastenerSearchDialog(
                FreeCADGui.getMainWindow()
            )
            FSSearchCommand._dialog.setAttribute(
                QtCore.Qt.WA_DeleteOnClose
            )
            FSSearchCommand._dialog.destroyed.connect(
                lambda: setattr(FSSearchCommand, "_dialog", None)
            )
        FSSearchCommand._dialog.show()
        FSSearchCommand._dialog.raise_()
        FSSearchCommand._dialog.activateWindow()
        FSSearchCommand._dialog.search_edit.setFocus()

    def IsActive(self):
        return True

Gui.addCommand("Fasteners_Search", FSSearchCommand())
FastenerBase.FSCommands.append("Fasteners_Search", "command")
