from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QMainWindow, QWidget, QScrollArea, QVBoxLayout, QSplitter, QStackedLayout, QListView, QPushButton)
from generate_schedule import (generate_schedule, donor_matches, donor_schedule)

class ScheduleWindow(QMainWindow):
    def __init__(self):
        super().__init__(self)

        self.setWindowTitle("HIGGS AI Platform - Scheduling")
        

        base_widget = QWidget()
        layout = QVBoxLayout()

        """
        Will eventually have menu + search bar then split pane...
        """

        # main part, LHS is list view, RHS is schedule that will show up
        self.main_pane = QSplitter()
        self.donors_list_view = QListView()
        

        # schedule bit
        schedule_scroll = QScrollArea()
        schedule_content = QWidget()
        self.schedule = QVBoxLayout()

        schedule_content.setLayout(self.schedule)
        schedule_scroll.setWidget(schedule_content)
        self.main_pane.addWidget(self.donors_list_view)
        layout.addWidget(self.main_pane)

        base_widget.setLayout(self.layout)
        self.setCentralWidget(base_widget)