import sys
import requests
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QLabel, QLineEdit, QPushButton, QMessageBox)
from PySide6.QtCore import Qt
from load_style_ui import loadstylesheet
from output_ui import MatchmakingResultWindow
from prompt_ui import HIGGSApp
from matches_schedules_ui import GenerateOutputWindow

from registration_ui import RegistrationWindow 
from dashboard_ui import DashboardWindow

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HIGGS AI Platform - Login")
        self.resize(400, 300)

        central_widget = QWidget()
        central_widget.setProperty("styling", "mainnavbar")
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        self.title_label = QLabel("Welcome to HIGGS Matchmaking")
        self.title_label.setProperty("styling", "titleLabel")
        self.title_label.setAlignment(Qt.AlignCenter)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Organization Email")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Login")
        self.login_button.setProperty("styling", "filled")
        self.login_button.clicked.connect(self.handle_login)

        self.signup_button = QPushButton("Don't have an account? Sign Up")
        self.signup_button.setProperty("styling", "outline")
        self.signup_button.clicked.connect(self.open_registration)

        layout.addWidget(self.title_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.signup_button)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.registration_window = RegistrationWindow(self)
        self.dashboard_window = DashboardWindow()

    def open_dashboard(self):
        self.hide()
        self.dashboard_window = DashboardWindow(parent_window=self)
        self.dashboard_window.show()

    def handle_login(self):
        email_input = self.username_input.text()
        password_input = self.password_input.text()

        if email_input and password_input:
            payload = {"email": email_input, "password": password_input}
            try:
                response = requests.post("http://127.0.0.1:8000/api/login", json=payload)
                backend_data = response.json()
                if response.status_code == 200 and backend_data.get("status") == "success":
                    QMessageBox.information(self, "Login Successful", backend_data.get("message"))
                    self.open_dashboard()
                else:
                    QMessageBox.warning(self, "Login Failed", backend_data.get("detail", "Invalid credentials"))
            except requests.exceptions.ConnectionError:
                QMessageBox.critical(self, "Server Error", "Could not connect to the backend server.")
        else:
            QMessageBox.warning(self, "Error", "Please enter both email and password.")

    def open_registration(self):
        self.hide()
        self.registration_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    ## FOR TESTING PURPOSES
    #window = GenerateOutputWindow()
    style = loadstylesheet()
    #print(style)
    if style:
        app.setStyleSheet(style)
    else:
        print("No stylesheet")

    window.show()
    sys.exit(app.exec())