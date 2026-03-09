# frontend/registration_ui.py
import requests
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                               QLabel, QLineEdit, QPushButton, QMessageBox, QComboBox)
from PySide6.QtCore import Qt

class RegistrationWindow(QMainWindow):
    def __init__(self, login_window):
        super().__init__()
        self.login_window = login_window # Save a reference so we can go back!
        self.setWindowTitle("HIGGS AI Platform - Register")
        self.resize(400, 350)

        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # UI Elements
        self.title_label = QLabel("Create a HIGGS Account")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 20px;")

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Organization Email")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)

        # Dropdown for selecting the role
        self.role_input = QLineEdit()
        self.role_input.setPlaceholderText("Role")

        self.register_button = QPushButton("Register")
        self.register_button.setStyleSheet("padding: 8px; background-color: #28a745; color: white; font-weight: bold;")
        self.register_button.clicked.connect(self.handle_register)

        self.back_button = QPushButton("Back to Login")
        self.back_button.setStyleSheet("padding: 8px; background-color: #6c757d; color: white;")
        self.back_button.clicked.connect(self.go_back_to_login)

        # Add widgets to layout
        layout.addWidget(self.title_label)
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.role_input)
        layout.addWidget(self.register_button)
        layout.addWidget(self.back_button)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def handle_register(self):
        email = self.email_input.text()
        password = self.password_input.text()
        role = self.role_input.text()

        if email and password:
            payload = {
                "email": email,
                "password": password,
                "role": role
            }
            try:
                response = requests.post("http://127.0.0.1:8000/api/register", json=payload)
                backend_data = response.json()
                
                if response.status_code == 200 and backend_data.get("status") == "success":
                    QMessageBox.information(self, "Success", "Account created! You can now log in.")
                    self.go_back_to_login()
                else:
                    QMessageBox.warning(self, "Registration Failed", backend_data.get("detail", "Unknown error occurred."))
                    
            except requests.exceptions.ConnectionError:
                QMessageBox.critical(self, "Server Error", "Could not connect to the backend server.")
        else:
            QMessageBox.warning(self, "Error", "Please enter an email and password.")

    def go_back_to_login(self):
        self.hide()
        self.login_window.show()