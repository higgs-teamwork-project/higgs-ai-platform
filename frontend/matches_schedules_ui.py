from PySide6.QtCore import (Qt,
                            QAbstractTableModel)

from PySide6.QtWidgets import (QWidget,
                               QSplitter,
                               QMainWindow,
                               QApplication,
                               QVBoxLayout,
                               QHBoxLayout,
                               QPushButton,
                               QTabWidget,
                               QMessageBox)

import requests
from load_style_ui import loadstylesheet
from list_donors_table_ui import DonorsTableModel, DonorsTable
from show_matches_table_ui import MatchesTable
import sys

"""
!! This is the main output window.
Donors (from donor input page) on LHS
Generated matches + schedule on RHS
"""

class MatchesTabView(QWidget):
    def __init__(self, donor_id):
        super().__init__()
        self.donor_id = donor_id

        # --- layout ---
        self.tab_layout = QVBoxLayout(self)

        # --- the tab widget ---
        self.tab_view = QTabWidget(self)

        self.matches_tab = QWidget()
        self.schedule_tab = QWidget()
        self.tab_view.addTab(self.matches_tab, "Matches")
        self.tab_view.addTab(self.schedule_tab, "Meetings")

        # --- set up matches tab ---
        self.matches_outer_layout = QVBoxLayout(self.matches_tab)    
        self.matches_tab.setLayout(self.matches_outer_layout)

        data = self.parse_matches_table()
        self.matches_table = MatchesTable(data) # data = [] if no saved matches
        self.matches_outer_layout.addWidget(self.matches_table)
            
        self.generate_matches_btn = QPushButton("Generate Matches")
        self.generate_matches_btn.setProperty("styling", "filled")
        self.generate_matches_btn.clicked.connect(self.generate_match)
        self.matches_outer_layout.addWidget(self.generate_matches_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        if len(data) == 0:
            self.matches_table.hide()
        else:
            self.generate_matches_btn.hide()

        # --- schedule tab ---
        # put in nothing for now apart from base layout
        schedule_outer_layout = QVBoxLayout(self.schedule_tab)
        self.schedule_tab.setLayout(schedule_outer_layout)

        # --- set up ---
        self.tab_layout.addWidget(self.tab_view)
        self.setLayout(self.tab_layout)

    def parse_matches_table(self):
        try:
            response = requests.get(f"http://127.0.0.1:8000/api/getmatches/{self.donor_id}")
            data = response.json() # get list of dictionaries
            print(data)
            if len(data) == 0:
                return []
            else:
                parsed_data = [[d["ngo_id"], d["name"], d["similarity"]] for d in data]
                print(parsed_data)
                print(len(parsed_data))
                return parsed_data
        except:
            QMessageBox.critical(self, "Server Error", "Could not retrieve donors. Please try again later.")
            return None

    def generate_match(self):
        try:
            response = requests.get(f"http://127.0.0.1:8000/api/donors/{self.donor_id}/recommendations?top_k=10&save_matches=True")
            data = response.json()
            print(data)
            self.load_matches_table()
        except:
            QMessageBox.critical(self, "Server Error", "Could not generate matches. Please try again later.")
            return None
    
    def load_matches_table(self):
        self.generate_matches_btn.hide()
        data = self.parse_matches_table()
        self.matches_table.set_data(data=data)
        self.matches_table.show()

    def add_generate_btn(self):
        self.generate_matches_btn.show()
        self.matches_table.hide()


class SplitView(QWidget):
    def __init__(self, parent):
        super().__init__(parent=parent)
        """
        Main widget on the screen.
        """

        self.main_view = QSplitter(orientation=Qt.Orientation.Horizontal, parent=self)


style = """
        QWidget{
            background-color: #E9E8E8;
        }

        /* Vertical Scrollbar */
        QScrollBar:vertical {
            border: none;
            background: #d4d4d4; /* Light grey track */
            width: 5px;          /* Thinner, modern width */
            margin: 0px;
        }

        /* Horizontal Scrollbar */
        QScrollBar:horizontal {
            border: none;
            background: #d4d4d4;
            height: 5px;
            margin: 0px;
        }

        /* The Handle (The moving part) */
        QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
            background: #bebebe; /* Medium grey handle */
            min-height: 5px;
            min-width: 20px;
            border-radius: 10px;  /* Rounded ends */
        }

        /* Handle hover state */
        QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {
            background: #94a3b8; /* Darker grey on hover */
        }

        /* Remove the Arrows (Buttons at the top/bottom) */
        /* Modern UIs rarely use these; removing them makes it look much cleaner */
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            border: none;
            background: none;
            width: 0px;
            height: 0px;
        }

        QPushButton[styling="filled"]{
            margin: 5px; 
            color: #FFFFFF; 
            border-radius: 3px; 
            background-color: #C12250;   
            padding: 10px 10px;
            font-size: 16px;   
            font-weight: bold;
        }

        /* The Background Track (Top and Bottom of the handle) */
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical,
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
            background: none;
        }
        """
"""

generating schedule
should regenerate schedule everytime new matches added
should generate schedule at the start 

generate schedule should update db after processing each donor
when you click on a donor, like w matches, retrieve schedule from DB
exact same logic as generate matches then

pseudo code

schedule = (ngo, time) -> donors , for all donors
matched = (donor, ngo) -> time , pairs that already have a meeting
for each donor
for each ngo donor is matched with
if (donor, ngo) is in matched skip
else
current slot = last slot for donor + 13 (with conditions for days)
while not found
if (ngo, time) exists in schedule increment current slot by 13 (w. conditions)
else add to matches, schedule and write to db. set found as true.




"""



class GenerateOutputWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HIGGS AI Platform - Matches")
        self.resize(800, 500)
        central_widget = QWidget()

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.main_view = QSplitter(Qt.Orientation.Horizontal)

        navbar_content = QWidget()
        navbar_content.setProperty("styling", "mainnavbar")
        nav_layout = QHBoxLayout()
        nav_layout.addStretch()
        navbar_content.setLayout(nav_layout)

        self.nav_auth_btn = QPushButton("Logout")
        self.nav_auth_btn.setProperty("styling", "outline")
        nav_layout.addWidget(self.nav_auth_btn)

        donors_table_background = QWidget()
        donors_table_background_layout = QVBoxLayout()
        donors_table_background.setStyleSheet(style)

        self.donors_table = DonorsTable()
        self.donors_table.donor_table_view.selectionModel().currentRowChanged.connect(self.change_detail_window)
        donors_table_background_layout.addWidget(self.donors_table)
        donors_table_background.setLayout(donors_table_background_layout)
        self.main_view.addWidget(donors_table_background)
        self.main_view.setStretchFactor(0,0)

        self.donor_details_panel = QWidget()
        self.donor_details_panel.setStyleSheet(style)
        self.details_layout = QVBoxLayout()
        self.donor_details_panel.setLayout(self.details_layout)
        self.main_view.addWidget(self.donor_details_panel)

        main_layout.addWidget(navbar_content, alignment=Qt.AlignmentFlag.AlignTop)
        main_layout.addWidget(self.main_view, stretch=1)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.current_detail = None

    def change_detail_window(self, current, previous):
        # add a new detail window to RHS
        if not previous.isValid():
            return

        if current.isValid():
            if self.current_detail:
                self.details_layout.removeWidget(self.current_detail)
                self.current_detail.deleteLater()
                self.current_detail = None
            row = current.row()
            data = self.donors_table.get_data(row)
            self.current_detail = MatchesTabView(donor_id=data[0])
            self.details_layout.addWidget(self.current_detail)
            self.main_view.setStretchFactor(1,1)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    style = loadstylesheet()
    if style:
        app.setStyleSheet(style)
    else:
        print("No stylesheet")
    
    window = GenerateOutputWindow()
    window.show()
    sys.exit(app.exec())