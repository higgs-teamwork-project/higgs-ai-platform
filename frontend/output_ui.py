import sys
import csv
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, 
                             QPushButton, QHeaderView, QFileDialog, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class MatchmakingResultWindow(QMainWindow):
    def __init__(self, donor_name="Jane Doe", match_count=12):
        super().__init__()
        
        self.donor_name = donor_name
        self.match_count = match_count
        
        # Setup Main Window
        self.setWindowTitle("Donors Speed Dating - Match Results")
        self.setGeometry(100, 100, 1400, 1024) # Desktop size from Figma guidelines
        self.setStyleSheet("background-color: #E9E8E8;") # Grey background
        
        # Main Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(50, 50, 50, 50)
        self.main_layout.setSpacing(30)
        
        self.setup_ui()
        self.load_dummy_data()

    def setup_ui(self):
        # 1. Heading
        heading_text = f"{self.match_count} NGOs are matched for {self.donor_name}"
        self.heading_label = QLabel(heading_text)
        self.heading_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        self.heading_label.setStyleSheet("color: #E52C4E; margin-bottom: 20px;") # Accent Red
        self.heading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.heading_label)

        # 2. Scrollable Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Seq No.", "NGO Name", "NGO Strategy", "AI Match Score", "Possible Reasons"
        ])
        
        # Table Styling (White foreground, black text, Arial font, rounded corners)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #FFFFFF;
                color: #000000;
                font-family: Arial;
                font-size: 14px;
                border-radius: 16px; /* Nested rounded corners guideline */
                padding: 10px;
                border: none;
            }
            QHeaderView::section {
                background-color: #FFFFFF;
                color: #E52C4E; /* Red headers for accent */
                font-weight: bold;
                font-size: 16px;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #E9E8E8;
            }
            QTableWidget::item {
                border-bottom: 1px solid #E9E8E8;
                padding: 5px;
            }
        """)
        
        # Adjust column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers) # Read-only
        self.main_layout.addWidget(self.table)

        # 3. Interaction Buttons Layout
        self.button_layout = QHBoxLayout()
        self.button_layout.setSpacing(24)
        
        # Button Stylesheet (Red outlines, white background, Arial, multiples of 8 radii)
        button_style = """
            QPushButton {
                background-color: #FFFFFF;
                color: #E52C4E;
                font-family: Arial;
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #E52C4E;
                border-radius: 8px; 
                padding: 12px 24px;
            }
            QPushButton:hover {
                background-color: #E52C4E;
                color: #FFFFFF;
            }
        """

        # Back Button
        self.back_btn = QPushButton("Back to Matchmaking")
        self.back_btn.setStyleSheet(button_style)
        self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_btn.clicked.connect(self.go_back)
        
        # Spacer to push buttons to the sides or keep them centered
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.back_btn)

        # Download/Export Button
        self.export_btn = QPushButton("Download / Export (.csv)")
        self.export_btn.setStyleSheet(button_style)
        self.export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.export_btn.clicked.connect(self.export_to_csv)
        self.button_layout.addWidget(self.export_btn)
        self.button_layout.addStretch()

        self.main_layout.addLayout(self.button_layout)

    def load_dummy_data(self):
        # Mock data (Unsorted)
        raw_data = [
            {"name": "Green Earth", "strategy": "Reforestation", "score": 85, "reason": "High interest in climate"},
            {"name": "EduForAll", "strategy": "Building Schools", "score": 92, "reason": "Matches past education donations"},
            {"name": "Ocean Cleanup", "strategy": "Plastic Removal", "score": 98, "reason": "Perfect alignment with marine focus"},
            {"name": "Food Bank Inc", "strategy": "Urban Hunger Relief", "score": 74, "reason": "Secondary interest matched"},
        ]
        
        # Sort data in descending order of AI Match Score
        sorted_data = sorted(raw_data, key=lambda x: x["score"], reverse=True)
        
        self.table.setRowCount(len(sorted_data))
        
        # Populate Table
        for row_idx, data in enumerate(sorted_data):
            seq_item = QTableWidgetItem(str(row_idx + 1))
            seq_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            name_item = QTableWidgetItem(data["name"])
            strategy_item = QTableWidgetItem(data["strategy"])
            
            score_item = QTableWidgetItem(f"{data['score']}%")
            score_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            reason_item = QTableWidgetItem(data["reason"])
            
            self.table.setItem(row_idx, 0, seq_item)
            self.table.setItem(row_idx, 1, name_item)
            self.table.setItem(row_idx, 2, strategy_item)
            self.table.setItem(row_idx, 3, score_item)
            self.table.setItem(row_idx, 4, reason_item)

    def go_back(self):
        # Placeholder for navigation logic
        print("Navigating back to the matchmaking page...")
        QMessageBox.information(self, "Navigation", "Going back to the previous page!")

    def export_to_csv(self):
        # Open file dialog to choose save location
        path, _ = QFileDialog.getSaveFileName(self, "Save Match Results", "", "CSV Files (*.csv)")
        
        if path:
            try:
                with open(path, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    # Write headers
                    headers = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())]
                    writer.writerow(headers)
                    
                    # Write data rows
                    for row in range(self.table.rowCount()):
                        row_data = []
                        for col in range(self.table.columnCount()):
                            item = self.table.item(row, col)
                            row_data.append(item.text() if item else "")
                        writer.writerow(row_data)
                
                QMessageBox.information(self, "Success", f"Data successfully exported to {path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not export file: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MatchmakingResultWindow()
    window.show()
    sys.exit(app.exec())