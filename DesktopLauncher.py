import sys
import os
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView

class TrafficAIWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TRAFFIC CONTROL SYSTEM - Desktop Edition")
        self.resize(1366, 768)
        
        # Initialize Web Engine
        self.browser = QWebEngineView()
        
        # Get path to HTML file
        if getattr(sys, 'frozen', False):
            # If running as EXE, get path from temp folder
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            
        html_path = os.path.join(base_dir, "TrafficSystem3D.html")
        
        # Load the HTML
        local_url = QUrl.fromLocalFile(html_path)
        self.browser.setUrl(local_url)
        
        self.setCentralWidget(self.browser)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TrafficAIWindow()
    window.show()
    sys.exit(app.exec_())
