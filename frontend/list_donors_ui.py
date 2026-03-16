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
        layout.setContentsMargins(0, 0, 0, 0)
        # set up navigation bar
        
        nav_content = QWidget()
        nav_content.setProperty("styling", "mainnavbar")
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(10, 5, 10, 0) 
        nav_layout.addStretch()
        nav_content.setLayout(nav_layout)

        ## will add more later 
        self.nav_auth_btn = QPushButton("Logout")
        self.nav_auth_btn.setProperty("styling", "outline")
        self.nav_auth_btn.clicked.connect(self.logout)
        nav_layout.addWidget(self.nav_auth_btn)
    
        ## set up table
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        table_layout.setContentsMargins(10, 10, 10, 10)

        self.donor_table_view = QTableView()
        self.donor_table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.donor_table_view.setWordWrap(True)
        self.donor_table_view.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        table_layout.addWidget(self.donor_table_view)

        ## select rows
        self.donor_table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.donor_table_view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        ## get the data and add to table
        self.donor_table_model = DonorsTableModel()
        self.donor_table_view.setModel(self.donor_table_model)

        ## generate matches button
        self.generate_match_button = QPushButton("Generate Matches")
        self.generate_match_button.clicked.connect(self.generate_match)
        self.generate_match_button.setProperty("styling", "filled")

        ## main layout set up
        layout.addWidget(nav_content)
        layout.addWidget(table_widget)
        layout.addWidget(self.generate_match_button, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addStretch()
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)        

    ## to generate matches 
    def generate_match(self):
        if self.donor_table_view.selectionModel().hasSelection():
            row_index = self.donor_table_view.selectionModel().selectedRows()[0].row()
            data = self.donor_table_model._data[row_index]
            print(data)

            payload = {
                "donor_name": data[1],
                "donor_strategy": data[2]
            }

            try: 
                response = requests.post("http://127.0.0.1:8000/api/matchmaking/generate", json=payload) 
                # get json as dictionary 
                data = response.json()
                print(data["matches"])
            except Exception as e:
                print(f"Error in generating matches: {e}")
                return
        else:
            QMessageBox.critical(self, "No Row Selected", "Please select a row in the donor table to generate matches")
            return
        
    ## load matches page. pass in matches that have been generated + donor data of selected donor.
    def load_matches_page(self):
        return
    
    ## nav
    def logout(self):
        self.hide()
        if self.parent_window:
            self.parent_window.show() 
        else:
            try:
                from main_ui import LoginWindow
                self.login_window = LoginWindow()
                self.login_window.show()
            except ImportError:
                pass

if __name__ == "__main__":
    app = QApplication(sys.argv)

    style = loadstylesheet()
    if style:
        app.setStyleSheet(style)
    else:
        print("No stylesheet")

    window = ListDonorsWindow()
    window.show()
    sys.exit(app.exec())


