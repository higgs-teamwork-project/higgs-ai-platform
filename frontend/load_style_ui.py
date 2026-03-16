import os
from pathlib import Path

"""
Using the style sheet
style sheet file: stylesheet.qss

Works like css. Use Qt reference to add styles & for syntax.
The property 'styling' of a widget will add a style from the stylesheet to it.
Adding styles:
QWidget[styling="mystyle"]{
....
}
On the corresponding widget, say myWidget = QWidget()
Set the property: myWidget.setProperty("styling", "mystyle")
If style doesn't load it is due to style inheritance hierarchy. Layout widgets cannot be styled.
"""


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