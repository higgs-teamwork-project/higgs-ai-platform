from PySide6.QtCore import (Qt,
                            QAbstractTableModel)

from PySide6.QtWidgets import (QWidget,
                               QVBoxLayout,
                               QHBoxLayout,
                               QPushButton,
                               QMainWindow,
                               QApplication,
                               QTableView,
                               QHeaderView,
                               QAbstractItemView)
import requests
from load_style_ui import loadstylesheet

class MatchesTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def rowCount(self, parent = None):
        return len(self._data)
    
    def columnCount(self, parent = None):
        return len(self._data[0]) if len(self._data) != 0 else 0
    
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            return str(self._data[index.row()][index.column()]) # cell as string
    
    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            headers = ["ngo_id", "ngo_name", "match_score"]
            return headers[section]
        return None
    

    
class MatchesTable(QWidget):
    def __init__(self, data: list):
        super().__init__()

        """
        For layout 
        """
        self.table_layout = QVBoxLayout(self)
        self.table_layout.setContentsMargins(10, 10, 10, 10)
        self.setStyleSheet("background-color: white; border-radius: 3px; border-color: #d4d4d4; border-width: 2px;")

        self.matches_table_view = QTableView()
        self.matches_table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.matches_table_view.setWordWrap(True)
        self.matches_table_view.setAlternatingRowColors(True)
        self.matches_table_view.verticalHeader().setVisible(False)
        self.matches_table_view.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        self.matches_table_view.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.matches_table_view.setProperty("styling", "matches")
        # --- table model ---
        self.matches_table_model = MatchesTableModel(data=data)
        self.matches_table_view.setModel(self.matches_table_model)

        # --- layout ---
        self.table_layout.addWidget(self.matches_table_view)
        self.setLayout(self.table_layout)

    def set_data(self, data: list):
        self.matches_table_model.beginResetModel()
        self.matches_table_model._data = data
        self.matches_table_model.endResetModel()