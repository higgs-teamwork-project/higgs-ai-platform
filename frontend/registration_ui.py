# frontend/registration_ui.py
import requests
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                               QLabel, QLineEdit, QPushButton, QMessageBox)
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

        # Email input
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Organization Email")
        self.email_input.textChanged.connect(self.validate_form) # Check form validity on text change
        
        # Password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.textChanged.connect(self.validate_form) # Check form validity on text change

        # Confirm password input
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm Password")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.textChanged.connect(self.validate_form) # Check form validity on text change 

        # Error label for form validation feedback
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red; font-size: 12px; margin-bottom: 5px;")
        self.error_label.setAlignment(Qt.AlignCenter)

        # Register button
        self.register_button = QPushButton("Register")
        self.register_button.setStyleSheet("""
            QPushButton {
                padding: 8px; 
                background-color: #28a745; 
                color: white; 
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:disabled {
                background-color: #a5d6a7; /* Lighter/Faded Green */
                color: #eeeeee;            /* Faded Text */
                border: 1px solid #cccccc;
            }   
        """)
        self.register_button.setEnabled(False) # Disable the register button until the form is valid
        self.register_button.clicked.connect(self.handle_register)

        # Back to login button
        self.back_button = QPushButton("Back to Login")
        self.back_button.setStyleSheet("padding: 8px; background-color: #6c757d; color: white;")
        self.back_button.clicked.connect(self.go_back_to_login)

        # Add widgets to layout
        layout.addWidget(self.title_label)
        layout.addWidget(self.email_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.confirm_password_input)
        layout.addWidget(self.error_label)
        layout.addWidget(self.register_button)
        layout.addWidget(self.back_button)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    # This function checks if the password and confirm password fields match before allowing registration
    def validate_form(self):
        email = self.email_input.text()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()

        email_valid = "@" in email and "." in email # Basic email validation
        password_secure = len(password) >= 6 # Basic password strength check
        passwords_match = password == confirm_password # Check if passwords match

        # Enable the register button only if all fields are filled and passwords match
        if email_valid and password_secure and passwords_match:
            self.register_button.setEnabled(True)
            self.error_label.setText("") # Clear any previous error messages
            self.register_button.setToolTip("Ready to register")
        else:
            self.register_button.setEnabled(False)

            # Provide feedback on why the form is invalid
            if not email_valid:
                self.error_label.setText("Please enter a valid email address")
            elif not password_secure:
                self.error_label.setText("Password must be at least 6 characters")
            elif not passwords_match:
                self.error_label.setText("Passwords do not match")

    # The user presses the register button and we send the data to the backend
    def handle_register(self):
        email = self.email_input.text()
        password = self.password_input.text()

        if email and password:
            payload = {
                "email": email,
                "password": password,
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
        # Clear the fields in case the user wants to register again
        self.email_input.clear()
        self.password_input.clear()
        self.confirm_password_input.clear()

        # Bring the login window back and hide the registration window
        self.hide()
        self.login_window.show()