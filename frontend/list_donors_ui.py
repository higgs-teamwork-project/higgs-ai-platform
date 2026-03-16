from PySide6.QtCore import (Qt, QAbstractTableModel)
from PySide6.QtWidgets import (QMainWindow, QApplication, QListView, QVBoxLayout, QWidget, QMessageBox)
import sys
import requests

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
        super.__init__()
        self._data = self.populateDonorList()

    def populateDonorList(self):
        try:
            response = requests.get("http://127.0.0.1:8000/api/donors") 
            donors = response.json()
            ## get just the ids + names + strategies
            donor_table_rows = [[d["id"], d["name"], d["strategy"]] for d in donors]
            return donor_table_rows      

        except:
            QMessageBox.critical(self, "Server Error", "Could not retrieve donors.")
            return []

    def rowCount(self, parent = None):
        return len(self._data)

    def columnCount(self, parent = None):
        return 3 if len(self._data) != 0 else 0

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            return str(self._data[index.row()][index.column()]) # data displayed is the string version of the cell


class ListDonorsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HIGGS AI Platform - List Donors")

        centralWidget = QWidget()  
        layout = QVBoxLayout()

        self.donor_list_view = QListView()
        self.donor_list_model = QStringListModel()

        layout.addWidget(self.donor_list_view)
        
        centralWidget.setLayout(self.layout)
        self.setCentralWidget(centralWidget)        
    

    def populateDonorList(self):
        try:
            response = requests.get("http://127.0.0.1:8000/api/donors") 
            donors = response.json()
            ## get just the ids + names + strategies
            donor_table_rows = [[d["id"], d["name"], d["strategy"]] for d in donors]


            self.donor_list_model.setStringList        



        except:
            QMessageBox.critical(self, "Server Error", "Could not retrieve donors.")
