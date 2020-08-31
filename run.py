from novelreader.controllers.mainapp import MainApp
from pathlib import Path

if __name__ == "__main__":
    app = MainApp()
    app.title = 'Novel Reader'
    app.run()