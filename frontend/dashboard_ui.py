# frontend/dashboard_ui.py
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QLabel, QMessageBox)
from PySide6.QtCore import Qt

# ---- THE MAGIC LINK: Import your sub-pages here! ----
from prompt_ui import HIGGSApp
from setting_ui import SettingsWindow

class DashboardWindow(QMainWindow):
    def __init__(self, parent_window=None):
        super().__init__()
        self.parent_window = parent_window 
        self.setWindowTitle("HIGGS AI Platform - Dashboard")
        self.resize(800, 500)

        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: #F2F2F2; color: #333;")
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0) 
        main_layout.setSpacing(20)

        # Navigation Bar
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(0, 0, 10, 0) 
        nav_layout.addStretch()

        self.nav_auth_btn = QPushButton("Logout")
        self.nav_auth_btn.setStyleSheet("padding: 5px 15px; margin: 5px; color: #C12250; border: 1px solid #C12250; border-radius: 3px; background-color: transparent;")
        self.nav_auth_btn.clicked.connect(self.logout)
        nav_layout.addWidget(self.nav_auth_btn)

        self.nav_settings_btn = QPushButton("Settings")
        self.nav_settings_btn.setStyleSheet("padding: 5px 15px; margin: 5px; color: #C12250; border: 1px solid #C12250; border-radius: 3px; background-color: transparent;")
        self.nav_settings_btn.clicked.connect(self.open_settings_page)
        nav_layout.addWidget(self.nav_settings_btn)

        main_layout.addLayout(nav_layout)
        main_layout.addStretch()

       
        # Page Title
        self.title_label = QLabel("Donors Speed Dating Event")
        self.title_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #C12250; margin-bottom: 20px;")
        self.title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.title_label)
        main_layout.addStretch()

        # Tiles (Match, Schedule, Admin)
        tiles_layout = QHBoxLayout()
        tiles_layout.setSpacing(30)
        tiles_layout.setContentsMargins(50, 0, 50, 0) 

        tile_base_style = "background-color: white; color: black; font-size: 22px; font-weight: bold; border: none; border-radius: 10px; min-width: 180px; min-height: 180px;"

        tiles_layout.addStretch()

        self.tile_match_btn = QPushButton("Match")
        self.tile_match_btn.setStyleSheet(tile_base_style)
        self.tile_match_btn.clicked.connect(self.open_prompt_page)
        tiles_layout.addWidget(self.tile_match_btn)

        self.tile_schedule_btn = QPushButton("Schedule")
        self.tile_schedule_btn.setStyleSheet(tile_base_style)
        self.tile_schedule_btn.clicked.connect(self.open_profile_page)
        tiles_layout.addWidget(self.tile_schedule_btn)

        self.tile_admin_btn = QPushButton("Admin")
        self.tile_admin_btn.setStyleSheet(tile_base_style)
        self.tile_admin_btn.clicked.connect(self.open_admin_dashboard)
        tiles_layout.addWidget(self.tile_admin_btn)

        tiles_layout.addStretch()
        main_layout.addLayout(tiles_layout)
        
        main_layout.addStretch()
        main_layout.addStretch()

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        try:
            self.prompt_window = HIGGSApp(parent_window=self)
        except TypeError:
            self.prompt_window = HIGGSApp()
            self.prompt_window.dashboard_window = self
            
        self.settings_window = SettingsWindow(parent_window=self)


    def open_prompt_page(self):
        self.hide() 
        self.prompt_window.show()

    def open_admin_dashboard(self):
        QMessageBox.information(self, "Coming Soon", "The Admin module is currently under development.")

    def open_settings_page(self):
        self.hide() 
        self.settings_window.show()

    def open_profile_page(self):
        QMessageBox.information(self, "Coming Soon", "The Schedule module is currently under development.")

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
    window = DashboardWindow() 
    window.show()
    sys.exit(app.exec())