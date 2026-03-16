from PySide6.QtCore import (Qt, QAbstractTableModel)
from PySide6.QtWidgets import (QMainWindow, 
                               QApplication, 
                               QTableView, 
                               QVBoxLayout, 
                               QWidget, 
                               QHeaderView,
                               QMessageBox,
                               QHBoxLayout)
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
        super().__init__()
        self._data = self.populate_donor_list()
        #self._data = self.test_populate()

    def test_populate(self):
        data = [
            ["1", "ABC", "Stuff1"],
            ["2", "CDE", "Stuff2"],
            ["3", "EFG", "Stuff3"],
            ["4", "EFG", "Stuff4"]
        ]
        return data

    def populate_donor_list(self):
        try:
            response = requests.get("http://127.0.0.1:8000/api/donors") 
            donors = response.json()
            ## get just the ids + names + strategies
            donor_table_rows = [[d["id"], d["name"], d["strategy"]] for d in donors]
            print(donor_table_rows)
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
        return None
    
    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole and orientation ==  Qt.Orientation.Horizontal:
            headers = ["Id", "Donor Name", "Donor Strategy"]
            return headers[section]
        return None


class ListDonorsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HIGGS AI Platform - List Donors")
        self.resize(800, 500)

        centralWidget = QWidget()  
        layout = QVBoxLayout()

        # set up navigation bar
        #self.nav = QH


        ## set up table
        self.donor_table_view = QTableView()
        self.donor_table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.donor_table_view.setWordWrap(True)
        self.donor_table_view.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        ## get the data and add to table
        self.donor_table_model = DonorsTableModel()
        self.donor_table_view.setModel(self.donor_table_model)

        layout.addWidget(self.donor_table_view)
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ListDonorsWindow()
    window.show()
    sys.exit(app.exec())


