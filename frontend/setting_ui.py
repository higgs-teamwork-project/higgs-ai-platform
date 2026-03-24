# frontend/settings_ui.py
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QPushButton, QSpinBox, QDialog)
from PySide6.QtCore import Qt

class SettingsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("HIGGS AI Platform - Settings")
        self.resize(700, 500)

        # color palette
        self.bg_color = "#F2F2F7"        
        self.card_color = "#FFFFFF"      
        self.tint_color = "#C12250"      
        self.text_color = "#000000"      
        self.value_color = "#8A8A8E"     
        self.separator_color = "#C6C6C8" 

        self.setStyleSheet(f"""
            QWidget {{ 
                background-color: {self.bg_color}; 
                font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; 
            }}
        """)

        central_widget = QWidget()

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 50, 40, 40)
        main_layout.setSpacing(20)

        # page title
        title_label = QLabel("Settings")
        title_label.setStyleSheet(f"font-size: 34px; font-weight: 700; color: {self.text_color}; background: transparent;")
        main_layout.addWidget(title_label)

       
       # card container
        card_widget = QWidget()
        card_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {self.card_color};
                border-radius: 12px;
            }}
        """)
        card_layout = QVBoxLayout(card_widget)
        card_layout.setContentsMargins(0, 0, 0, 0) 
        card_layout.setSpacing(0)

        # options row 1: Max AI Recommendations
        row1 = QWidget()
        row1_layout = QHBoxLayout(row1)
        row1_layout.setContentsMargins(20, 16, 20, 16)
        
        lbl1 = QLabel("Max AI Recommendations")
        lbl1.setStyleSheet("font-size: 17px; background: transparent; color: black;")
        
        self.recs_spinbox = QSpinBox()
        self.recs_spinbox.setRange(1, 15)  # set a limited range for recommendations：1-15
        self.recs_spinbox.setValue(3)  # default value is 3
        self._style_ios_spinbox(self.recs_spinbox, show_buttons=True) #allows up/down arrows
        
        row1_layout.addWidget(lbl1)
        row1_layout.addStretch()
        row1_layout.addWidget(self.recs_spinbox)

        # separator line
        sep = QWidget()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {self.separator_color}; margin-left: 20px;")

        # options row 2: Meeting Duration Constraints
        row2 = QWidget()
        row2_layout = QHBoxLayout(row2)
        row2_layout.setContentsMargins(20, 16, 20, 16)
        
        lbl2 = QLabel("Meeting Duration Constraints")
        lbl2.setStyleSheet("font-size: 17px; background: transparent; color: black;")
        
        self.mins_spinbox = QSpinBox()
        self.mins_spinbox.setRange(1, 1440) 
        self.mins_spinbox.setValue(15)
        self.mins_spinbox.setSuffix(" mins") # unit suffix for clarity
        self._style_ios_spinbox(self.mins_spinbox, show_buttons=False)
        
        row2_layout.addWidget(lbl2)
        row2_layout.addStretch()
        row2_layout.addWidget(self.mins_spinbox)

        card_layout.addWidget(row1)
        card_layout.addWidget(sep)
        card_layout.addWidget(row2)

        main_layout.addWidget(card_widget)

       # save button
        self.save_btn = QPushButton("Save Settings")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.tint_color};
                color: white;
                font-size: 17px;
                font-weight: 600;
                border-radius: 14px; 
                padding: 14px;
                margin-top: 15px;
            }}
            QPushButton:hover {{ background-color: #A01B40; }}
        """)
        self.save_btn.clicked.connect(self.save_settings)
        main_layout.addWidget(self.save_btn)

        main_layout.addStretch()

       # back to dashboard button
        self.back_btn = QPushButton("Back to Dashboard")
        self.back_btn.setCursor(Qt.PointingHandCursor)
        self.back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {self.tint_color};
                font-size: 16px;
                font-weight: 500;
                border: none;
            }}
            QPushButton:hover {{ text-decoration: underline; }}
        """)
        self.back_btn.clicked.connect(self.go_back)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.back_btn, alignment=Qt.AlignCenter)
        main_layout.addLayout(bottom_layout)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
  
    # styling spinboxes
    def _style_ios_spinbox(self, spinbox, show_buttons=False):
        spinbox.setCursor(Qt.PointingHandCursor)
        
        if show_buttons:
            spinbox.setButtonSymbols(QSpinBox.UpDownArrows)
            border_style = "border: 1px solid #E5E5EA; border-radius: 6px; padding: 2px 4px;"
            width_style = "width: 70px;"
        else:
            spinbox.setButtonSymbols(QSpinBox.NoButtons)
            border_style = "border: none;"
            width_style = "width: 100px;"
            
        spinbox.setAlignment(Qt.AlignRight | Qt.AlignVCenter) 
        spinbox.setStyleSheet(f"""
            QSpinBox {{
                background-color: transparent;
                color: {self.value_color};
                font-size: 17px;
                {border_style}
                {width_style}
            }}
            QSpinBox::focus {{ color: {self.tint_color}; }} 
        """)

    # save settings and show custom success dialog
    def save_settings(self):
        payload = {
            "max_recommendations": self.recs_spinbox.value(),
            "session_duration_minutes": self.mins_spinbox.value()
        }
        print("Hook -> Sending Settings Payload:", payload)
        
        # create and show a custom styled dialog to confirm settings are saved
        msg_dialog = QDialog(self)
        msg_dialog.setWindowTitle("Saved")
        msg_dialog.setFixedSize(380, 150) 
        msg_dialog.setStyleSheet(f"QDialog {{ background-color: {self.card_color}; }}")
        
        dialog_layout = QVBoxLayout(msg_dialog)
        dialog_layout.setContentsMargins(20, 30, 20, 20)
        
        # layout for icon + text
        text_layout = QHBoxLayout()
        text_layout.setAlignment(Qt.AlignCenter) 
        
        # 1.red exclamation bubble icon
        icon_bubble = QLabel("!")
        icon_bubble.setFixedSize(22, 22) 
        icon_bubble.setAlignment(Qt.AlignCenter)
        icon_bubble.setStyleSheet(f"""
            QLabel {{
                background-color: {self.tint_color}; 
                color: white; 
                border-radius: 11px; 
                font-weight: 900; 
                font-size: 14px;
            }}
        """)
        
        # 2. success text
        text_label = QLabel("System settings saved successfully")
        text_label.setStyleSheet(f"color: {self.tint_color}; font-size: 16px; font-weight: bold; background: transparent;")
        
        # combine icon and text into one line
        text_layout.addWidget(icon_bubble)
        text_layout.addSpacing(8) 
        text_layout.addWidget(text_label)
        
       
        dialog_layout.addLayout(text_layout)       
        dialog_layout.addStretch() 
        
        # button layout
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.setCursor(Qt.PointingHandCursor)
        ok_btn.setFixedSize(120, 36)
        ok_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.tint_color};
                color: white;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
            }}
            QPushButton:hover {{ background-color: #A01B40; }}
        """)
        ok_btn.clicked.connect(msg_dialog.accept)
        
        btn_layout.addWidget(ok_btn, alignment=Qt.AlignCenter)
        dialog_layout.addLayout(btn_layout)
        
        msg_dialog.exec()

    def go_back(self):
        from dashboard_ui import DashboardWindow
        self.hide()
        dashboard = DashboardWindow()
        dashboard.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SettingsWindow() 
    window.show()
    sys.exit(app.exec())