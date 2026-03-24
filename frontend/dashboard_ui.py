# frontend/dashboard_ui.py
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QLabel, QMessageBox)
from PySide6.QtCore import Qt
from load_style_ui import loadstylesheet
from navbar_ui import HNavBar
class DashboardWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HIGGS AI Platform - Dashboard")
        self.resize(800, 500)

        central_widget = QWidget()

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0) 
        main_layout.setSpacing(20)

        # Navigation Bar
        navbar_content = HNavBar(["settings", "logout"], self)
        main_layout.addWidget(navbar_content)

        # Page Title
        self.title_label = QLabel("Donors Speed Dating Event")
        self.title_label.setProperty("styling", "titleLabel")
        self.title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.title_label)

        # Tiles (Match, Schedule, Admin)
        tiles_content =  QWidget()
        tiles_layout = QHBoxLayout()
        tiles_layout.setSpacing(30)
        tiles_layout.setContentsMargins(50, 0, 50, 0) 
        tiles_content.setLayout(tiles_layout)

        tiles_layout.addStretch()

        self.tile_match_btn = QPushButton("Add Orgs")
        self.tile_match_btn.setProperty("styling", "tileButton")
        self.tile_match_btn.clicked.connect(self.open_prompt_page)
        self.tile_match_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        tiles_layout.addWidget(self.tile_match_btn)

        self.tile_schedule_btn = QPushButton("Match & Schedule")
        self.tile_schedule_btn.setProperty("styling", "tileButton")
        self.tile_schedule_btn.clicked.connect(self.open_match_page)
        self.tile_schedule_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        tiles_layout.addWidget(self.tile_schedule_btn)

        self.tile_admin_btn = QPushButton("Admin")
        self.tile_admin_btn.setProperty("styling", "tileButton")
        self.tile_admin_btn.clicked.connect(self.open_admin_dashboard)
        self.tile_admin_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        tiles_layout.addWidget(self.tile_admin_btn)

        tiles_layout.addStretch()
        main_layout.addWidget(tiles_content)
        main_layout.addStretch(1)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def open_prompt_page(self):
        from prompt_ui import HIGGSApp
        prompt_window = HIGGSApp()
        self.hide()
        prompt_window.show()

    def open_admin_dashboard(self):
        QMessageBox.information(self, "Coming Soon", "The Admin module is currently under development.")

    def open_match_page(self):
        from matches_schedules_ui import GenerateOutputWindow
        output_window = GenerateOutputWindow()
        self.hide()
        output_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    style = loadstylesheet()
    if style:
        app.setStyleSheet(style)
    else:
        print("No stylesheet")
        
    window = DashboardWindow() 
    window.show()
    sys.exit(app.exec())