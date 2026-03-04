import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QLabel, QLineEdit, QPushButton, QMessageBox)
from PySide6.QtCore import Qt
import requests

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HIGGS AI Platform - Login")
        self.resize(400, 300)

        # 1. Create the central layout
        central_widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter) # Center everything

        # 2. Create the UI Widgets (Text, Inputs, Buttons)
        self.title_label = QLabel("Welcome to HIGGS Matchmaking")
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 20px;")

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Organization Email")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password) # Hides the typing

        self.login_button = QPushButton("Login")
        self.login_button.setStyleSheet("padding: 8px; background-color: #007bff; color: white; font-weight: bold;")

        # 3. Connect the button to a function
        self.login_button.clicked.connect(self.handle_login)

        # 4. Add widgets to the layout
        layout.addWidget(self.title_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)

        # 5. Set the layout to the window
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def handle_login(self):
        email_input = self.username_input.text()
        password_input = self.password_input.text()

        if email_input and password_input:
            # 1. Package the data into a Python dictionary
            payload = {
                "email": email_input,
                "password": password_input
            }
            
            try:
                # 2. Send it to the FastAPI backend!
                response = requests.post("http://127.0.0.1:8000/api/login", json=payload)
                
                # 3. Read the backend's response
                backend_data = response.json()
                
                if backend_data.get("status") == "success":
                    QMessageBox.information(self, "Login Successful", backend_data.get("message"))
                else:
                    QMessageBox.warning(self, "Login Failed", backend_data.get("message"))
                    
            except requests.exceptions.ConnectionError:
                QMessageBox.critical(self, "Server Error", "Could not connect to the backend server. Is it running?")
        else:
            QMessageBox.warning(self, "Error", "Please enter both email and password.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())    