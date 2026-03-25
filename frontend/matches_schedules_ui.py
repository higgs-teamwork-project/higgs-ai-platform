from PySide6.QtCore import (Qt,
                            QThreadPool)
from PySide6.QtWidgets import (QWidget,
                               QSplitter,
                               QMainWindow,
                               QApplication,
                               QVBoxLayout,
                               QHBoxLayout,
                               QPushButton,
                               QTabWidget,
                               QMessageBox,
                               QProgressBar)

import requests
from load_style_ui import loadstylesheet
from list_donors_table_ui import DonorsTableModel, DonorsTable
from show_matches_table_ui import MatchesTable
from schedule_ui import generate_schedule, Schedule
from navbar_ui import HNavBar
from datetime import datetime, date, time 
import sys
from run_api_req import RequestWorker

"""
!! This is the main output window.
Donors (from donor input page) on LHS
Generated matches + schedule on RHS
"""
# top level style sheet for this page.

class MatchesTabView(QWidget):
    def __init__(self, donor_id, donor_name):
        super().__init__()
        self.donor_id = donor_id
        self.donor_name = donor_name
        self.threadpool = QThreadPool()
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

        self.matches_spinner = QProgressBar()
        self.matches_spinner.setRange(0, 0)
        self.matches_spinner.setTextVisible(False)
        self.matches_outer_layout.addWidget(self.matches_spinner)

        data = self.parse_matches_table()
        self.matches_table = MatchesTable(data) # data = [] if no saved matches
        self.matches_outer_layout.addWidget(self.matches_table)
            
        self.generate_matches_btn = QPushButton("Generate Matches")
        self.generate_matches_btn.setProperty("styling", "filled")
        self.generate_matches_btn.clicked.connect(self.generate_match)
        self.matches_outer_layout.addWidget(self.generate_matches_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.matches_spinner.hide()
        if len(data) == 0:
            self.matches_table.hide()
        else:
            self.generate_matches_btn.hide()

        # --- schedule tab ---
        self.donor_schedule = self.parse_schedule()
        self.schedule = Schedule(self.donor_schedule, datetime(2026, 7, 1))
        self.schedule.remake(self.donor_schedule)
        schedule_outer_layout = QVBoxLayout(self.schedule_tab)
        self.schedule_tab.setLayout(schedule_outer_layout)
        schedule_outer_layout.addWidget(self.schedule)

        # --- set up ---
        self.tab_layout.addWidget(self.tab_view)
        self.setLayout(self.tab_layout)

    def return_results(self, d):
        return d

    def parse_matches_table(self):
        try:
            response = requests.get(f"http://127.0.0.1:8000/api/getmatches/{self.donor_id}")
            data = response.json() # get list of dictionaries
            #print(data)
            if len(data) == 0:
                return []
            else:
                parsed_data = [[d["ngo_id"], d["name"], d["similarity"]] for d in data]
             #   print(parsed_data)
              #  print(len(parsed_data))
                return parsed_data
        except:
            QMessageBox.critical(self, "Server Error", "Could not retrieve donors. Please try again later.")
            return None

    def parse_schedule(self):
        try:
            response = requests.get(f"http://127.0.0.1:8000/api/schedule/donor/{self.donor_id}/meetings")
            data = response.json()
            #print(data)

            if len(data) == 0:
                return []
            else:
                return data
        except:
            QMessageBox.critical(self, "Server Error", "Could not retrieve schedule for donor. Please try again later.")
            return None

    def get_existing_meetings(self):
        try:
            response = requests.get(f"http://127.0.0.1:8000/api/schedule/get-all-meetings")
            data = response.json()
            #print(data)

            if len(data) == 0:
                return []
            else:
                return data
        except:
            QMessageBox.critical(self, "Server Error", "Could not retrieve schedule. Please try again later.")
            return None

    def get_recs_req(self, id):
        try:
            response = requests.get(f"http://127.0.0.1:8000/api/donors/{id}/recommendations?top_k=22 &save_matches=True")
            data = response.json()
            #print(data)
            return data
        except Exception as e:
            QMessageBox.critical(self, "Server Error", "Could not generate matches. Please try again later.")
            print("ERROR: "+ e)
            return None
        
    def handle_new_matches(self, data):
        self.matches_spinner.hide()
        self.load_matches_table()
        self.make_donor_schedule(data["recommendations"])


    def generate_match(self):
        self.generate_matches_btn.hide()
        self.matches_spinner.show()
        worker = RequestWorker(
            self.get_recs_req,
            self.donor_id
        )
        worker.signals.result.connect(self.handle_new_matches)
        self.threadpool.start(worker)
    
    def load_matches_table(self):
        self.generate_matches_btn.hide()
        data = self.parse_matches_table()
        self.matches_table.set_data(data=data)
        self.matches_table.show()

    def add_generate_btn(self):
        self.generate_matches_btn.show()
        self.matches_table.hide()

    def make_donor_schedule(self, results: list):
        existing_meetings = self.get_existing_meetings()
        # first make recs into right format
        recs = [{"donor_id": self.donor_id, "ngo_id": d["ngo_id"], "ngo_name": d["ngo"]["name"]} for d in results]
        generate_schedule(existing_meetings, recs, datetime(2026, 7, 1), self.donor_name)
        donor_data = self.parse_schedule()
        self.schedule.remake(donor_data)


class SplitView(QWidget):
    def __init__(self, parent):
        super().__init__(parent=parent)
        """
        Main widget on the screen.
        """

        self.main_view = QSplitter(orientation=Qt.Orientation.Horizontal, parent=self)

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

        self.nav_bar = HNavBar(["export-matches", "export-schedule", "dashboard", "add-orgs", "logout"], self)

        donors_table_background = QWidget()
        donors_table_background_layout = QVBoxLayout()

        self.donors_table = DonorsTable()
        self.donors_table.donor_table_view.selectionModel().currentRowChanged.connect(self.change_detail_window)
        donors_table_background_layout.addWidget(self.donors_table)
        donors_table_background.setLayout(donors_table_background_layout)
        self.main_view.addWidget(donors_table_background)
        self.main_view.setStretchFactor(0,0)

        self.donor_details_panel = QWidget()
        self.details_layout = QVBoxLayout()
        self.donor_details_panel.setLayout(self.details_layout)
        self.main_view.addWidget(self.donor_details_panel)

        main_layout.addWidget(self.nav_bar, alignment=Qt.AlignmentFlag.AlignTop)
        main_layout.addWidget(self.main_view, stretch=1)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.current_detail = None

    def change_detail_window(self, current, previous):
        # add a new detail window to RHS
        if current.isValid():
            if self.current_detail:
                self.details_layout.removeWidget(self.current_detail)
                self.current_detail.deleteLater()
                self.current_detail = None
            row = current.row()
            data = self.donors_table.get_data(row)
            self.current_detail = MatchesTabView(donor_id=data[0], donor_name=data[1])
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