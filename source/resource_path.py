import os
import sys

#credit for this file goes to this stack overflow answer: http://stackoverflow.com/questions/7674790/bundling-data-files-with-pyinstaller-onefile accessed 6/22/15

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)