import os
from pathlib import Path

def loadstylesheet():
    try: 
        PATH = Path(__file__).parent
        STYLESHEET = PATH / "stylesheet.qss"

        with open(STYLESHEET, "r") as f:
            style = f.read()
        return style
    except Exception as e:
        print(f"Error: style sheet not loaded, {e}")
        return None