# frontend/main_ui.py
import sys
import requests
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QLabel, QLineEdit, QPushButton, QMessageBox)
from PySide6.QtCore import Qt

# ---- THE MAGIC LINK: Import your new file here! ----
from registration_ui import RegistrationWindow 

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HIGGS AI Platform - Login")
        self.resize(400, 300)

        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        self.title_label = QLabel("Welcome to HIGGS Matchmaking")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 20px;")

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Organization Email")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Login")
        self.login_button.setStyleSheet("padding: 8px; background-color: #007bff; color: white; font-weight: bold;")
        self.login_button.clicked.connect(self.handle_login)

        self.signup_button = QPushButton("Don't have an account? Sign Up")
        self.signup_button.setStyleSheet("padding: 8px; border: none; color: #007bff; text-decoration: underline;")
        self.signup_button.clicked.connect(self.open_registration)

        layout.addWidget(self.title_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.signup_button)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # It still works exactly the same because we imported the class!
        self.registration_window = RegistrationWindow(self)

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
    window.show()
    sys.exit(app.exec())