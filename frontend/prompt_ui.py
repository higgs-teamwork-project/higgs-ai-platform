import os
import sys
import PySide6

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QComboBox, QProgressBar, QStackedWidget, QDialog,
                             QMessageBox, QTreeWidget, QTreeWidgetItem, QListWidgetItem)
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QFont, QIntValidator

from load_style_ui import loadstylesheet
from navbar_ui import HNavBar

# --- DESIGN RICHTLINIEN (Aus deinen Anforderungen) ---
COLOR_RED = "#E52C4E"
COLOR_GREEN = "#7EE081"
COLOR_GREY = "#E9E8E8"
COLOR_WHITE = "#FFFFFF"
COLOR_BLACK = "#000000"
FONT_FAMILY = "Inter"

# # Basis-Style für Eingabefelder (8px Radius, grauer Rand)
# INPUT_STYLE_DEFAULT = f"""
#     QLineEdit {{
#         border: 2px solid {COLOR_GREY}; 
#         border-radius: 8px; 
#         padding: 10px; 
#         background-color: {COLOR_WHITE};
#         color: {COLOR_BLACK};  
#         font-family: '{FONT_FAMILY}';
#         font-size: 14px;
#     }}
# """
# INPUT_STYLE_ERROR = f"""
#     border: 2px solid {COLOR_RED}; 
#     border-radius: 8px; 
#     padding: 10px; 
#     background-color: {COLOR_WHITE};
#     color: {COLOR_BLACK};  
#     font-family: '{FONT_FAMILY}';
#     font-size: 14px;
# """

import requests

# Add class to handle ngo management dialog (Extension)
class ManageNGODialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add & Manage NGOs")
        self.setMinimumSize(450, 650)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Section: Add New NGO Form
        layout.addWidget(QLabel("<b>Add New NGO Profile</b>"))
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("NGO Name")
        layout.addWidget(self.name_input)

        self.strategy_input = QLineEdit()
        self.strategy_input.setPlaceholderText("NGO Strategy")
        layout.addWidget(self.strategy_input)

        self.focus_input = QLineEdit()
        self.focus_input.setPlaceholderText("Focus Area")
        layout.addWidget(self.focus_input)

        self.legal_input = QLineEdit()
        self.legal_input.setPlaceholderText("Legal Form")
        layout.addWidget(self.legal_input)
        
        btn_add = QPushButton("Save NGO to Database")
        btn_add.setProperty("styling", "greenbtn")
        btn_add.clicked.connect(self.add_ngo_to_db)
        layout.addWidget(btn_add)

        layout.addWidget(QLabel("<br><b>Existing NGO Database:</b>"))
        
        # List of NGOs with multiple columns
        self.ngo_list = QTreeWidget()
        self.ngo_list.setColumnCount(4)
        self.ngo_list.setHeaderLabels(["Name", "Strategy", "Focus", "Legal Form"])
        self.ngo_list.setProperty("styling", "ngolisttree")
        layout.addWidget(self.ngo_list)
        
        btn_del = QPushButton("Delete Selected NGO")
        btn_del.setProperty("styling", "filled")
        btn_del.clicked.connect(self.delete_selected_ngo)
        layout.addWidget(btn_del)

        self.refresh_data()

    def add_ngo_to_db(self):
        """Sends a POST request to the backend and shows success/failure prompts."""
        name = self.name_input.text().strip()
        
        # Frontend validation prompt
        if not name:
            QMessageBox.warning(self, "Input Error", "NGO Name is mandatory!")
            return

        payload = {
            "name": name,
            "strategy": self.strategy_input.text().strip() or None,
            "focus": self.focus_input.text().strip() or None,
            "legal_form": self.legal_input.text().strip() or None
        }

        try:
            # Send the data to your updated /api/ngos endpoint
            response = requests.post("http://127.0.0.1:8000/api/ngos", json=payload)
            backend_data = response.json()
            
            # Success Prompt
            if response.status_code == 200 and backend_data.get("status") == "ok":
                QMessageBox.information(
                    self, 
                    "NGO Added", 
                    f"Successfully added '{name}' to the database.\nID: {backend_data.get('id')}"
                )
                # Clear fields and refresh the list
                self.name_input.clear()
                self.strategy_input.clear()
                self.focus_input.clear()
                self.legal_input.clear()
                self.refresh_data()
            
            # Unsuccessful Prompt (Backend rejected)
            else:
                error_msg = backend_data.get("detail", "The server rejected the request.")
                QMessageBox.critical(self, "Add Failed", f"Could not save NGO: {error_msg}")

        # Unsuccessful Prompt (Connection error)
        except requests.exceptions.ConnectionError:
            QMessageBox.critical(
                self, 
                "Connection Error", 
                "Could not connect to the backend. Is the server running?"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {str(e)}")

    def refresh_data(self):
        """Fetches the latest NGO list and populates all 4 columns."""
        self.ngo_list.clear()
        try:
            response = requests.get("http://127.0.0.1:8000/api/ngos")
            if response.status_code == 200:
                for ngo in response.json():
                    # Create a multi-column item
                    item = QTreeWidgetItem([
                        ngo.get('name', ''),
                        ngo.get('strategy', 'N/A'),
                        ngo.get('focus', 'N/A'),
                        ngo.get('legal_form', 'N/A')
                    ])
                    
                    # Store the ID in the first column's UserRole for deletion
                    item.setData(0, Qt.UserRole, ngo['id']) 
                    self.ngo_list.addTopLevelItem(item)
        except Exception as e:
            print(f"Fetch error: {e}")

    def delete_selected_ngo(self):
        # Get the currently selected item
        current_item = self.ngo_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Selection Error", "Please select an NGO to delete.")
            return

        # Retrieve the ID from column 0
        ngo_id = current_item.data(0, Qt.UserRole)
        
        try:
            # Send to your existing delete endpoint
            response = requests.delete("http://127.0.0.1:8000/api/ngos", json={"ids": [ngo_id]})
            if response.status_code == 200:
                QMessageBox.information(self, "Deleted", "NGO removed successfully.")
                self.refresh_data()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

# Manage Donor 
class ManageDonorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add & Manage Donors")
        self.setMinimumSize(450, 650)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Add donor form
        layout.addWidget(QLabel("<b>Add New Donor Profile</b>"))
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Donor Name")
        layout.addWidget(self.name_input)

        self.strategy_input = QLineEdit()
        self.strategy_input.setPlaceholderText("Donor Strategy")
        layout.addWidget(self.strategy_input)

        self.legal_input = QLineEdit()
        self.legal_input.setPlaceholderText("Legal Form")
        layout.addWidget(self.legal_input)
        
        btn_add = QPushButton("Save Donor to Database")
        btn_add.setProperty("styling", "greenbtn")
        btn_add.clicked.connect(self.add_donor_to_db)
        layout.addWidget(btn_add)

        layout.addWidget(QLabel("<br><b>Existing Donor Database:</b>"))
        
        # List of donors with multiple columns
        self.donor_list = QTreeWidget()
        self.donor_list.setColumnCount(3)
        self.donor_list.setHeaderLabels(["Name", "Strategy", "Legal Form"])
        self.donor_list.setProperty("styling", "ngolisttree")
        layout.addWidget(self.donor_list)
        
        btn_del = QPushButton("Delete Selected Donor")
        btn_del.setProperty("styling", "filled")
        btn_del.clicked.connect(self.delete_selected_donor)
        layout.addWidget(btn_del)

        self.refresh_data()

    def add_donor_to_db(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Input Error", "Donor Name is mandatory!")
            return

        payload = {"name": name, "strategy": self.strategy_input.text().strip() or None, "legal_form": self.legal_input.text().strip() or None}
        try:
            response = requests.post("http://127.0.0.1:8000/api/donors", json=payload)
            if response.status_code == 200:
                QMessageBox.information(self, "Success", "Donor Added!")
                self.name_input.clear(); self.strategy_input.clear(); self.legal_input.clear()
                self.refresh_data()
            else:
                QMessageBox.warning(self, "Error", response.json().get("detail", "Failed to add Donor."))
        except Exception as e:
            print(f"Add error: {e}")
            QMessageBox.critical(self, "Connection Error", str(e))

    def refresh_data(self):
        self.donor_list.clear()
        try:
            response = requests.get("http://127.0.0.1:8000/api/donors")
            if response.status_code == 200:
                for donor in response.json():
                    item = QTreeWidgetItem([donor.get('name', ''), donor.get('strategy', 'N/A'), donor.get('legal_form', 'N/A')])
                    item.setData(0, Qt.UserRole, donor['id']) 
                    self.donor_list.addTopLevelItem(item)
        except Exception as e:
            pass

    def delete_selected_donor(self):
        current_item = self.donor_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Selection Error", "Please select a Donor to delete.")
            return

        # Retrieve the ID from the selected row
        donor_id = current_item.data(0, Qt.UserRole)
        
        try:
            # Send the DELETE request to the new backend endpoint
            response = requests.delete("http://127.0.0.1:8000/api/donors", json={"ids": [donor_id]})
            
            if response.status_code == 200:
                QMessageBox.information(self, "Deleted", "Donor removed successfully.")
                self.refresh_data()
            else:
                # If the backend returns an error (like 404 Not Found), show it!
                error_msg = response.json().get("detail", "Unknown error")
                QMessageBox.warning(self, "Error", f"Failed to delete Donor: {error_msg} (Code: {response.status_code})")
        except Exception as e:
            print(f"Delete error: {e}")
            QMessageBox.critical(self, "Connection Error", f"Could not connect to backend: {str(e)}")

class HIGGSApp(QMainWindow):
    def __init__(self,dashboard_window=None):
        super().__init__()
        self.dashboard_window = dashboard_window

        # Figma Desktop Frame Size
        self.setWindowTitle("HIGGS AI Matchmaking")

        # add a central widget and layout to hold the pages
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        self.nav_content = HNavBar(["event-matches", "dashboard", "logout"], self)

        self.prompt_page = self.create_prompt_page()

        main_layout.addWidget(self.nav_content)
        main_layout.addWidget(self.prompt_page)
        main_layout.addStretch(1)
        main_layout.setSpacing(100)
        central_widget.setLayout(main_layout)

    def create_prompt_page(self):
        page = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setContentsMargins(20, 20, 20, 20)
        # Background Card
        card = QWidget()
        card.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        card.setProperty("styling", "card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(100, 100, 100, 100)
        card_layout.setSpacing(25)

        title = QLabel("Data management")
        title.setFont(QFont(FONT_FAMILY, 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title)

        # The Two Main Buttons
        self.btn_manage_ngos = QPushButton("Manage NGOs")
        self.btn_manage_donors = QPushButton("Manage Donors")

        for btn in [self.btn_manage_ngos, self.btn_manage_donors]:
            btn.setProperty("styling", "whitebtn")
            btn.setCursor(Qt.PointingHandCursor)
            card_layout.addWidget(btn)

        # Connections
        self.btn_manage_ngos.clicked.connect(self.open_ngo_manager)
        self.btn_manage_donors.clicked.connect(self.open_donor_manager)

        main_layout.addWidget(card)
        page.setLayout(main_layout)
        return page

    def open_donor_manager(self):
        self.donor_dialog = ManageDonorDialog(self)
        self.donor_dialog.exec()

    def open_ngo_manager(self):
        self.dialog = ManageNGODialog(self)
        self.dialog.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    style = loadstylesheet()
    if style:
        app.setStyleSheet(style)
    else:
        print("No stylesheet")

    window = HIGGSApp(None)
    window.show()
    sys.exit(app.exec())