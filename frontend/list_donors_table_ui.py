from PySide6.QtCore import (Qt, 
                            QAbstractTableModel)
from PySide6.QtWidgets import (QMainWindow, 
                               QApplication, 
                               QTableView, 
                               QVBoxLayout, 
                               QWidget, 
                               QHeaderView,
                               QMessageBox,
                               QHBoxLayout,
                               QAbstractItemView,
                               QPushButton)
import sys
import requests
from load_style_ui import loadstylesheet

""""
List of donors.
Can select a donor and click match.
Match button generates API request to "/api/matchmaking/generate"
and passes results to 'output_ui' page.
"""

"""
Table view
"""
class DonorsTableModel(QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self._data = self.populate_donor_list()

    def populate_donor_list(self):
        try:
            response = requests.get("http://127.0.0.1:8000/api/donors") 
            donors = response.json()
            ## get just the ids + names + strategies
            donor_table_rows = [[d["id"], d["name"], d["strategy"]] for d in donors]
            #print(donor_table_rows)
            return donor_table_rows      

        except:
            print("Could not retrieve donors.")
            return []

    def rowCount(self, parent = None):
        return len(self._data)

    def columnCount(self, parent = None):
        return 3 if len(self._data) != 0 else 0

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            return str(self._data[index.row()][index.column()]) # data displayed is the string version of the cell
        return None
    
    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole and orientation ==  Qt.Orientation.Horizontal:
            headers = ["Id", "Donor Name", "Donor Strategy"]
            return headers[section]
        return None


class DonorsTable(QWidget):
    def __init__(self):
        super().__init__()
        
        """
        Outer widget for spacing, styling etc
        """
        self.table_layout = QVBoxLayout()
        self.setStyleSheet("background-color: white; border-radius: 3px; border-color: #d4d4d4; border-width: 2px;")
        # --- set up table ---
        self.table_layout.setContentsMargins(10, 10, 10, 10)

        self.donor_table_view = QTableView()
        self.donor_table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.donor_table_view.setWordWrap(True)
        self.donor_table_view.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.donor_table_view.verticalHeader().setVisible(False)
        self.donor_table_view.setAlternatingRowColors(True)
        self.donor_table_view.setProperty("styling", "donors")
        header = self.donor_table_view.horizontalHeader()
        header.setMaximumSectionSize(600)

        ## select rows
        self.donor_table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.donor_table_view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.donor_table_view.clearSelection()
        ## get the data and add to table
        self.donor_table_model = DonorsTableModel()
        self.donor_table_view.setModel(self.donor_table_model)

        # --- layout ---
        self.table_layout.addWidget(self.donor_table_view)
        self.setLayout(self.table_layout)

    def get_selection(self):
        if self.donor_table_view.selectionModel().hasSelection():
            row_index = self.donor_table_view.selectionModel().selectedRows()[0].row()
            data = self.donor_table_model._data[row_index]
        # print(data)

            return data
        else:
            return None

    def get_data(self, row):
        return self.donor_table_model._data[row]





