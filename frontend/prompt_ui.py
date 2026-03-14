import os
import sys
import PySide6

# --- MAC REPARATUR-BLOCK ---
# Damit dein M4 Mac die Grafik-Plugins zuverlässig findet
dirname = os.path.dirname(PySide6.__file__)
plugin_path = os.path.join(dirname, 'Qt', 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path
# ---------------------------

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QComboBox, QProgressBar, QStackedWidget, QDialog,
                             QMessageBox, QListWidget, QListWidgetItem)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QIntValidator

# --- DESIGN RICHTLINIEN (Aus deinen Anforderungen) ---
COLOR_RED = "#E52C4E"
COLOR_GREEN = "#7EE081"
COLOR_GREY = "#E9E8E8"
COLOR_WHITE = "#FFFFFF"
COLOR_BLACK = "#000000"
FONT_FAMILY = "Inter"

# Basis-Style für Eingabefelder (8px Radius, grauer Rand)
INPUT_STYLE_DEFAULT = f"""
    QLineEdit {{
        border: 2px solid {COLOR_GREY}; 
        border-radius: 8px; 
        padding: 10px; 
        background-color: {COLOR_WHITE};
        color: {COLOR_BLACK};  
        font-family: '{FONT_FAMILY}';
        font-size: 14px;
    }}
"""
# Style für leere Pflichtfelder (roter Rand)
INPUT_STYLE_ERROR = f"""
    border: 2px solid {COLOR_RED}; 
    border-radius: 8px; 
    padding: 10px; 
    background-color: {COLOR_WHITE};
    color: {COLOR_BLACK};  
    font-family: '{FONT_FAMILY}';
    font-size: 14px;
"""

import requests

# Add class to handle ngo management dialog (Extension)
class ManageNGODialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add & Manage NGOs")
        self.setMinimumSize(450, 650)
        self.setStyleSheet(f"background-color: {COLOR_WHITE}; border-radius: 12px;")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Section: Add New NGO Form
        layout.addWidget(QLabel("<b>Add New NGO Profile</b>"))
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("NGO Name (Required)")
        self.name_input.setStyleSheet(INPUT_STYLE_DEFAULT)
        layout.addWidget(self.name_input)

        self.strategy_input = QLineEdit()
        self.strategy_input.setPlaceholderText("NGO Strategy (e.g. Environmental)")
        self.strategy_input.setStyleSheet(INPUT_STYLE_DEFAULT)
        layout.addWidget(self.strategy_input)

        self.focus_input = QLineEdit()
        self.focus_input.setPlaceholderText("Focus Area (e.g. Reforestation)")
        self.focus_input.setStyleSheet(INPUT_STYLE_DEFAULT)
        layout.addWidget(self.focus_input)

        self.legal_input = QLineEdit()
        self.legal_input.setPlaceholderText("Legal Form (e.g. gGmbH, Foundation)")
        self.legal_input.setStyleSheet(INPUT_STYLE_DEFAULT)
        layout.addWidget(self.legal_input)
        
        btn_add = QPushButton("Save NGO to Database")
        btn_add.setStyleSheet(f"background-color: {COLOR_GREEN}; color: white; padding: 12px; font-weight: bold; border-radius: 8px;")
        btn_add.clicked.connect(self.add_ngo_to_db)
        layout.addWidget(btn_add)

        layout.addWidget(QLabel("<br><b>Existing NGO Database:</b>"))
        
        # --- Section: List & Delete ---
        self.ngo_list = QListWidget()
        self.ngo_list.setStyleSheet(f"border: 1px solid {COLOR_GREY}; border-radius: 8px;")
        layout.addWidget(self.ngo_list)
        
        btn_del = QPushButton("Delete Selected NGO")
        btn_del.setStyleSheet(f"background-color: {COLOR_RED}; color: white; padding: 10px; font-weight: bold; border-radius: 8px;")
        btn_del.clicked.connect(self.delete_selected_ngo)
        layout.addWidget(btn_del)

        self.refresh_data()

    def add_ngo_to_db(self):
        """Matches your AddNGOBody backend model"""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation Error", "NGO Name is mandatory!")
            return

        # Bundle all details from the form
        payload = {
            "name": name,
            "strategy": self.strategy_input.text().strip(),
            "focus": self.focus_input.text().strip(),
            "legal_form": self.legal_input.text().strip()
        }

        try:
            response = requests.post("http://127.0.0.1:8000/api/ngos", json=payload)
            if response.status_code == 200:
                # Clear all fields after success
                for widget in [self.name_input, self.strategy_input, self.focus_input, self.legal_input]:
                    widget.clear()
                self.refresh_data()
            else:
                QMessageBox.warning(self, "Error", response.json().get("detail", "Failed to add NGO."))
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", f"Is the backend running? {e}")

    def refresh_data(self):
        self.ngo_list.clear()
        try:
            response = requests.get("http://127.0.0.1:8000/api/ngos")
            if response.status_code == 200:
                for ngo in response.json():
                    # Format the list display to show some details
                    display_text = f"{ngo['name']} | {ngo.get('strategy', 'N/A')}"
                    item = QListWidgetItem(display_text)
                    item.setData(Qt.UserRole, ngo['id']) 
                    self.ngo_list.addItem(item)
        except:
            pass

    def delete_selected_ngo(self):
        current_item = self.ngo_list.currentItem()
        if current_item:
            ngo_id = current_item.data(Qt.UserRole)
            try:
                requests.delete("http://127.0.0.1:8000/api/ngos", json={"ids": [ngo_id]})
                self.refresh_data()
            except:
                pass


class HIGGSApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # Figma Desktop Frame Size
        self.setWindowTitle("HIGGS AI Matchmaking")
        self.resize(1400, 1024)
        self.setStyleSheet(f"QMainWindow {{ background-color: {COLOR_GREY}; font-family: '{FONT_FAMILY}'; }}")

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.prompt_page = self.create_prompt_page()
        self.result_page = self.create_placeholder_result_page() # Dummy für den Erfolg

        self.stack.addWidget(self.prompt_page)
        self.stack.addWidget(self.result_page)

    def create_prompt_page(self):
        page = QWidget()
        main_layout = QVBoxLayout(page)
        main_layout.setAlignment(Qt.AlignCenter)
        
        # --- KARTEN DESIGN ---
        # Background Frame (White), nesting multiple of 8 (24px)
        card = QWidget()
        card.setFixedWidth(600)
        card.setStyleSheet(f"QWidget {{ background-color: {COLOR_WHITE}; border-radius: 24px; }}")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(50, 50, 50, 50)
        card_layout.setSpacing(25)

        title = QLabel("Matchmaking Configuration")
        title.setFont(QFont(FONT_FAMILY, 24, QFont.Bold))
        title.setStyleSheet(f"color: {COLOR_BLACK};")
        card_layout.addWidget(title)

        # --- 1. DONOR'S NAME (Mandatory) ---
        lbl_name = QLabel(f'Donor\'s Name <span style="color: {COLOR_RED};">*</span>')
        lbl_name.setTextFormat(Qt.RichText)
        lbl_name.setFont(QFont(FONT_FAMILY, 14, QFont.Bold))
        
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText("donor's name")
        self.input_name.setStyleSheet(INPUT_STYLE_DEFAULT)
        
        card_layout.addWidget(lbl_name)
        card_layout.addWidget(self.input_name)

        # --- 2. DONOR'S STRATEGY (Mandatory) ---
        # Anforderung: Dropdown Menü
        lbl_strategy = QLabel(f'Donor\'s Strategy <span style="color: {COLOR_RED};">*</span>')
        lbl_strategy.setTextFormat(Qt.RichText)
        lbl_strategy.setFont(QFont(FONT_FAMILY, 14, QFont.Bold))
        
        self.combo_strategy = QComboBox()
        self.combo_strategy.addItem("donor's strategy") # Index 0 ist der Placeholder
        self.combo_strategy.addItems(["Environmental Sustainability", "Education & Youth", "Healthcare Access", "Poverty Alleviation"])
        self.combo_strategy.setStyleSheet(INPUT_STYLE_DEFAULT)
        
        card_layout.addWidget(lbl_strategy)
        card_layout.addWidget(self.combo_strategy)

        # --- 3. MATCH THRESHOLD CONTROL (Optional) ---
        lbl_threshold = QLabel('Match Threshold Control')
        lbl_threshold.setFont(QFont(FONT_FAMILY, 14, QFont.Bold))
        
        self.input_threshold = QLineEdit()
        self.input_threshold.setPlaceholderText("75% in default")
        self.input_threshold.setValidator(QIntValidator(0, 100)) # Nur Zahlen von 0-100 erlaubt
        self.input_threshold.setStyleSheet(INPUT_STYLE_DEFAULT)
        
        card_layout.addWidget(lbl_threshold)
        card_layout.addWidget(self.input_threshold)

        # --- 4. NGO BUTTONS ---
        ngo_btn_layout = QHBoxLayout()
        
        self.btn_add_ngo = QPushButton("Add NGOs")
        self.btn_del_ngo = QPushButton("Delete NGOs")
        
        button_style = f"""
            QPushButton {{
                background-color: {COLOR_WHITE};
                color: {COLOR_BLACK};
                border: 2px solid {COLOR_GREY};
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: {COLOR_GREY}; }}
        """

        self.btn_add_ngo.setStyleSheet(button_style)
        self.btn_del_ngo.setStyleSheet(button_style)

        # Connect the buttons to the new management functions
        self.btn_add_ngo.clicked.connect(self.open_ngo_manager)
        self.btn_del_ngo.clicked.connect(self.open_ngo_manager) 
        
        ngo_btn_layout.addWidget(self.btn_add_ngo)
        ngo_btn_layout.addWidget(self.btn_del_ngo)
        card_layout.addLayout(ngo_btn_layout)

        # --- 5. GENERATE BUTTON ---
        self.btn_generate = QPushButton("Generate AI matches")
        self.btn_generate.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_RED};
                color: {COLOR_WHITE};
                border-radius: 8px;
                padding: 15px;
                font-weight: bold;
                font-size: 16px;
            }}
            QPushButton:hover {{ background-color: #c42240; }}
        """)
        self.btn_generate.setCursor(Qt.PointingHandCursor)
        self.btn_generate.clicked.connect(self.handle_generate)
        card_layout.addWidget(self.btn_generate)

        main_layout.addWidget(card)
        return page

    def create_placeholder_result_page(self):
        """Eine einfache Dummy-Seite, um den erfolgreichen Sprung zu demonstrieren."""
        page = QWidget()
        layout = QVBoxLayout(page)
        lbl = QLabel("Matchmaking Result Page (Coming next!)")
        lbl.setFont(QFont(FONT_FAMILY, 24, QFont.Bold))
        lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl)
        return page

    def handle_generate(self):
        """Überprüft die Pflichtfelder und startet den Ladevorgang."""
        is_valid = True
        
        # 1. Frontend Check: Mandatory Fields
        name = self.input_name.text().strip()
        strategy_idx = self.combo_strategy.currentIndex()

        # Reset Styles
        self.input_name.setStyleSheet(INPUT_STYLE_DEFAULT)
        self.combo_strategy.setStyleSheet(INPUT_STYLE_DEFAULT)

        # Falls Name fehlt -> Roter Rand
        if not name:
            self.input_name.setStyleSheet(INPUT_STYLE_ERROR)
            is_valid = False

        # Falls Strategy auf Index 0 (Placeholder) steht -> Roter Rand
        if strategy_idx == 0:
            self.combo_strategy.setStyleSheet(INPUT_STYLE_ERROR)
            is_valid = False

        # 2. Wenn nicht valide: Warnung und Abbruch
        if not is_valid:
            # Rote Rahmen sind gesetzt, wir brechen hier ab.
            return

        # 3. Wenn valide: Lade-Dialog anzeigen
        self.loading_dialog = LoadingDialog(self)
        self.loading_dialog.start_loading()
        
        # exec() pausiert das Hauptfenster, bis der Dialog fertig ist
        if self.loading_dialog.exec(): 
            # 4. If successful: Jump to result page
            self.stack.setCurrentIndex(1)
        else:
            # If failed: Display dialogue (Hier simuliert, falls der Dialog abgebrochen würde)
            QMessageBox.critical(self, "Fail to Generate", "An error occurred during AI matching.")

    def open_ngo_manager(self):
        self.dialog = ManageNGODialog(self)
        self.dialog.exec()

    def handle_add_ngo_dialog(self):
        """Opens a simple dialog to add a new NGO."""
        from PySide6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "Add NGO", "Enter NGO Name:")
        if ok and name.strip():
            import requests
            payload = {"name": name.strip()}
            try:
                response = requests.post("http://127.0.0.1:8000/api/ngos", json=payload)
                if response.status_code == 200:
                    QMessageBox.information(self, "Success", f"Added: {name}")
                else:
                    QMessageBox.warning(self, "Error", "Failed to add NGO.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Connection failed: {e}")

    def handle_delete_ngo_dialog(self):
        """Opens a list to select an NGO to delete."""
        import requests
        try:
            # 1. Get the current list of NGOs
            response = requests.get("http://127.0.0.1:8000/api/ngos")
            ngos = response.json()
            ngo_names = [f"{n['id']}: {n['name']}" for n in ngos]

            # 2. Show selection dialog
            from PySide6.QtWidgets import QInputDialog
            item, ok = QInputDialog.getItem(self, "Delete NGO", "Select NGO to remove:", ngo_names, 0, False)
            
            if ok and item:
                # 3. Extract the ID and send delete request
                ngo_id = int(item.split(":")[0])
                # Note: We send a list [id] because your backend expects DeleteNGOsBody(ids: list[int])
                payload = {"ids": [ngo_id]}
                requests.delete("http://127.0.0.1:8000/api/ngos", json=payload)
                QMessageBox.information(self, "Success", "NGO deleted successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not fetch or delete: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HIGGSApp()
    window.show()
    sys.exit(app.exec())

class LoadingDialog(QDialog):
    """Der Dialog, der während der 'Backend'-Analyse angezeigt wird."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Loading")
        self.setFixedSize(400, 200)
        self.setStyleSheet(f"background-color: {COLOR_WHITE}; border-radius: 16px;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setAlignment(Qt.AlignCenter)

        # Status Text
        self.lbl_status = QLabel("HIGGS AI is analyzing data...")
        self.lbl_status.setFont(QFont(FONT_FAMILY, 16, QFont.Bold))
        self.lbl_status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.lbl_status)

        # Progress Bar (Extension)
        self.progress = QProgressBar()
        self.progress.setStyleSheet(f"""
            QProgressBar {{ border: 2px solid {COLOR_GREY}; border-radius: 8px; text-align: center; }}
            QProgressBar::chunk {{ background-color: {COLOR_GREEN}; border-radius: 6px; }}
        """)
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        # Timer für die Simulation der KI-Berechnung
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.step = 0

    def start_loading(self):
        self.step = 0
        self.progress.setValue(0)
        self.timer.start(30) # Alle 30ms updaten

    def update_progress(self):
        self.step += 1
        self.progress.setValue(self.step)
        if self.step >= 100:
            self.timer.stop()
            self.accept() # Schließt den Dialog erfolgreich