"""
Split pane
LHS: table of donors
RHS: 2 tabs
RHS TAB1: matches, in table unordered
RHS TAB2: schedule

"""


from PySide6.QtCore import (Qt,
                            QAbstractTableModel)

from PySide6.QtWidgets import (QWidget,
                               QSplitter,
                               QMainWindow,
                               QApplication,
                               QVBoxLayout,
                               QHBoxLayout,
                               QPushButton)

import requests
from load_style_ui import loadstylesheet
from list_donors_table_ui import DonorsTableModel   

