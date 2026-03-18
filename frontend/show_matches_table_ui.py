from PySide6.QtCore import (Qt,
                            QAbstractTableModel)

from PySide6.QtWidgets import (QWidget,
                               QVBoxLayout,
                               QHBoxLayout,
                               QPushButton,
                               QMainWindow,
                               QApplication)
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
            headers = ["ngo_id", "ngo_name", "ngo_strategy", "score"]
            return headers[section]
        return None
    

    
        
