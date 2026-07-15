"""
Excel-like table widget with sorting, multi-select, and context menu.

Provides keyboard navigation (built into QTableWidget), resizable columns,
Copy / Delete / Export actions via right-click, and optional paste hooks.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, List, Optional, Sequence

from utils.qt import (
    QAbstractItemView,
    QAction,
    QApplication,
    QFileDialog,
    QHeaderView,
    QKeySequence,
    QMenu,
    Qt,
    QTableWidget,
    QTableWidgetItem,
    Signal,
    qt_popup,
)


class ExcelTableWidget(QTableWidget):
    """
    Professional desktop grid used for vendor and product lists.

    Signals
    -------
    edit_requested(int)
        Emitted with the row's stored entity id (Qt.UserRole).
    delete_requested(list[int])
        Emitted with selected entity ids.
    """

    edit_requested = Signal(int)
    delete_requested = Signal(list)
    selection_ids_changed = Signal(list)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._id_role = Qt.UserRole
        self._export_headers: List[str] = []
        self._on_paste: Optional[Callable[[List[List[str]]], None]] = None

        self.setSortingEnabled(True)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setWordWrap(False)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.horizontalHeader().setSectionsMovable(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._open_context_menu)
        self.itemDoubleClicked.connect(self._on_double_click)
        self.itemSelectionChanged.connect(self._emit_selection)

        copy_action = QAction("Copy", self)
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(self.copy_selection)
        self.addAction(copy_action)

        delete_action = QAction("Delete", self)
        delete_action.setShortcut(QKeySequence.Delete)
        delete_action.triggered.connect(self._emit_delete)
        self.addAction(delete_action)

    def set_paste_handler(self, handler: Callable[[List[List[str]]], None]) -> None:
        """Optional paste callback (rows of cell strings)."""
        self._on_paste = handler
        paste_action = QAction("Paste", self)
        paste_action.setShortcut(QKeySequence.Paste)
        paste_action.triggered.connect(self.paste_from_clipboard)
        self.addAction(paste_action)

    def configure_columns(self, headers: Sequence[str]) -> None:
        self._export_headers = list(headers)
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(list(headers))

    def clear_rows(self) -> None:
        self.setSortingEnabled(False)
        self.setRowCount(0)
        self.setSortingEnabled(True)

    def set_row_values(
        self,
        row: int,
        entity_id: int,
        values: Sequence[str],
        sort_keys: Optional[Sequence[object]] = None,
    ) -> None:
        """
        Populate a row.

        ``sort_keys`` (optional) stores typed values in UserRole+1 so numeric /
        date columns sort correctly while display stays as text.
        """
        for col, text in enumerate(values):
            item = QTableWidgetItem(str(text) if text is not None else "")
            item.setFlags(item.flags() ^ Qt.ItemIsEditable)
            if col == 0:
                item.setData(self._id_role, entity_id)
            if sort_keys is not None and col < len(sort_keys):
                item.setData(Qt.UserRole + 1, sort_keys[col])
            self.setItem(row, col, item)

    def selected_ids(self) -> List[int]:
        ids: List[int] = []
        for index in self.selectionModel().selectedRows():
            item = self.item(index.row(), 0)
            if item is None:
                continue
            value = item.data(self._id_role)
            if value is not None:
                ids.append(int(value))
        return ids

    def copy_selection(self) -> None:
        indexes = self.selectionModel().selectedIndexes()
        if not indexes:
            return
        indexes = sorted(indexes, key=lambda i: (i.row(), i.column()))
        rows: dict[int, dict[int, str]] = {}
        for idx in indexes:
            item = self.item(idx.row(), idx.column())
            rows.setdefault(idx.row(), {})[idx.column()] = item.text() if item else ""
        lines = []
        for row in sorted(rows):
            cols = rows[row]
            ordered = [cols[c] for c in sorted(cols)]
            lines.append("\t".join(ordered))
        QApplication.clipboard().setText("\n".join(lines))

    def paste_from_clipboard(self) -> None:
        if self._on_paste is None:
            return
        text = QApplication.clipboard().text()
        if not text.strip():
            return
        rows = [line.split("\t") for line in text.splitlines() if line.strip()]
        self._on_paste(rows)

    def export_to_csv(self, default_name: str = "export.csv") -> Optional[Path]:
        path_str, _ = QFileDialog.getSaveFileName(
            self,
            "Export Table",
            default_name,
            "CSV Files (*.csv);;All Files (*)",
        )
        if not path_str:
            return None
        path = Path(path_str)
        lines = [",".join(self._escape(h) for h in self._export_headers)]
        for row in range(self.rowCount()):
            cells = []
            for col in range(self.columnCount()):
                item = self.item(row, col)
                cells.append(self._escape(item.text() if item else ""))
            lines.append(",".join(cells))
        path.write_text("\n".join(lines), encoding="utf-8")
        return path

    @staticmethod
    def _escape(value: str) -> str:
        if any(ch in value for ch in (",", '"', "\n")):
            return '"' + value.replace('"', '""') + '"'
        return value

    def _open_context_menu(self, pos) -> None:  # noqa: ANN001
        menu = QMenu(self)
        menu.addAction("Copy", self.copy_selection)
        if self._on_paste is not None:
            menu.addAction("Paste", self.paste_from_clipboard)
        menu.addSeparator()
        menu.addAction("Edit", self._emit_edit_first)
        menu.addAction("Delete", self._emit_delete)
        menu.addSeparator()
        menu.addAction("Export…", lambda: self.export_to_csv())
        global_pos = self.viewport().mapToGlobal(pos)
        qt_popup(menu, global_pos)

    def _on_double_click(self, item: QTableWidgetItem) -> None:
        first = self.item(item.row(), 0)
        if first is None:
            return
        entity_id = first.data(self._id_role)
        if entity_id is not None:
            self.edit_requested.emit(int(entity_id))

    def _emit_edit_first(self) -> None:
        ids = self.selected_ids()
        if ids:
            self.edit_requested.emit(ids[0])

    def _emit_delete(self) -> None:
        ids = self.selected_ids()
        if ids:
            self.delete_requested.emit(ids)

    def _emit_selection(self) -> None:
        self.selection_ids_changed.emit(self.selected_ids())
