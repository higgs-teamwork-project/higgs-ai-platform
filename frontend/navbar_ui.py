from PySide6.QtCore import (Qt)
from typing import List
from PySide6.QtWidgets import (QWidget,
                               QHBoxLayout,
                               QPushButton)
from load_style_ui import loadstylesheet
""""
Possible options on the horizontal menu at the top of the pages:
logout 
dashboard
add-orgs (add donors + ngos page)
login
signup
settings
event-matches (output page)

"""

class HNavBar(QWidget):
    def __init__(self, options: List[str], mainwindow):
        super().__init__()

        # main layout set up
        self.setProperty("styling", "mainnavbar")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.nav_bar = QHBoxLayout()
        self.nav_bar.addStretch()
        self.setLayout(self.nav_bar)
        self.main_window = mainwindow
        self.add_buttons(options)

    def add_buttons(self, options):
        for opt in options:
            match opt:
                case "logout":
                    self.create_nav_button("Logout", self.logout)
                case "dashboard":
                    self.create_nav_button("Dashboard", self.dashboard)
                case "add-orgs":
                    self.create_nav_button("Add Orgs", self.input_page)
                case "login":
                    self.create_nav_button("Login", self.login)
                case "signup":
                    self.create_nav_button("Sign up", self.signup)
                case "settings":
                    self.create_nav_button("Settings", self.settings)
                case "event-matches":
                    self.create_nav_button("View Matches", self.output_page)
                
    def create_nav_button(self, lbl: str, cb):
        nav_btn = QPushButton(text=lbl)
        nav_btn.setProperty("styling", "outline")
        self.nav_bar.addWidget(nav_btn)
        nav_btn.clicked.connect(cb)

    def logout(self):
        from main_ui import LoginWindow
        self.main_window.hide()
        login_window = LoginWindow()
        login_window.show()

    def dashboard(self):
        from dashboard_ui import DashboardWindow
        dashboard_window = DashboardWindow()
        self.main_window.hide()
        dashboard_window.show()

    def input_page(self):
        from prompt_ui import HIGGSApp
        self.main_window.hide()
        input_pg = HIGGSApp()
        input_pg.show()

    def login(self):
        from main_ui import LoginWindow
        self.main_window.hide()
        login_window = LoginWindow()
        login_window.show()
    
    def signup(self):
        from registration_ui import RegistrationWindow
        self.main_window.hide()
        reg_pg = RegistrationWindow()
        reg_pg.show()
    
    def settings(self):
        self.main_window.hide()
        # need to look more carefully to finish off

    def output_page(self):
        from matches_schedules_ui import GenerateOutputWindow
        self.main_window.hide()
        output_pg = GenerateOutputWindow()
        output_pg.show()
        

