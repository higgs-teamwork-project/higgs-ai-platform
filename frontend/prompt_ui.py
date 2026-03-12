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
                             QMessageBox)
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
    border: 2px solid {COLOR_GREY}; 
    border-radius: 8px; 
    padding: 10px; 
    background-color: {COLOR_WHITE};
    font-family: '{FONT_FAMILY}';
    font-size: 14px;
"""
# Style für leere Pflichtfelder (roter Rand)
INPUT_STYLE_ERROR = f"""
    border: 2px solid {COLOR_RED}; 
    border-radius: 8px; 
    padding: 10px; 
    background-color: {COLOR_WHITE};
    font-family: '{FONT_FAMILY}';
    font-size: 14px;
"""

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
        
        btn_add_ngo = QPushButton("Add NGOs")
        btn_del_ngo = QPushButton("Delete NGOs")
        
        for btn in [btn_add_ngo, btn_del_ngo]:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COLOR_WHITE};
                    color: {COLOR_BLACK};
                    border: 2px solid {COLOR_GREY};
                    border-radius: 8px;
                    padding: 10px;
                    font-weight: bold;
                }}
                QPushButton:hover {{ background-color: {COLOR_GREY}; }}
            """)
            ngo_btn_layout.addWidget(btn)
        
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HIGGSApp()
    window.show()
    sys.exit(app.exec())