import sys
import os
from PyQt5.QtCore import QSize, QUrl, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QToolBar, QAction, QLineEdit, QInputDialog
from PyQt5.QtGui import QIcon

from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineFindFlags

# Functions definition and creation of classes:
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.browser = QWebEngineView()
        self.setWindowTitle("OIS Browser")
        self.setMinimumSize(QSize(1024, 750))
        self.setWindowIcon(QIcon('unnamed.png'))
        self.browser.setUrl(QUrl("https://google.com"))
        self.setCentralWidget(self.browser)
        self.showMaximized()

        # Load search history from file
        self.search_history_file = 'search_history.txt'
        self.load_search_history()

        # Coding for buttons and their functionalities:
        # navbar
        navbar = QToolBar()
        self.addToolBar(navbar)
        back_btn = QAction(QIcon("icons/Arrow_back_left.png"), 'Back', self)
        back_btn.setStatusTip("Back")
        back_btn.triggered.connect(self.browser.back)
        navbar.addAction(back_btn)

        forward_btn = QAction(QIcon("icons/Arrow_forward_right.png"), 'Forward', self)
        forward_btn.setStatusTip("Forward")
        forward_btn.triggered.connect(self.browser.forward)
        navbar.addAction(forward_btn)

        reload_btn = QAction(QIcon("icons/Button_refresh.png"), 'Refresh', self)
        reload_btn.setStatusTip("Refresh")
        reload_btn.triggered.connect(self.browser.reload)
        navbar.addAction(reload_btn)

        home_btn = QAction(QIcon("icons/home_icon.png"), 'Home', self)
        home_btn.setStatusTip("Home")
        home_btn.triggered.connect(self.navigate_home)
        navbar.addAction(home_btn)

        find_action = QAction('Find', self)
        find_action.setShortcut('Ctrl+F')
        find_action.triggered.connect(self.find_text)
        self.addAction(find_action)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navbar.addWidget(self.url_bar)
        self.browser.urlChanged.connect(self.update_url)

    def navigate_home(self):
        self.browser.setUrl(QUrl("https://google.com"))

    def navigate_to_url(self):
        input_text = self.url_bar.text()
        if not input_text.startswith(("http://", "https://")):
            # Construct Google search URL
            search_url = "https://www.google.com/search?q=" + input_text
            self.browser.setUrl(QUrl(search_url))
        else:
            self.browser.setUrl(QUrl(input_text))

        # Add the searched URL to search history
        self.search_history.append(input_text)
        self.save_search_history()

    def update_url(self, q):
        self.url_bar.setText(q.toString())

    def load_search_history(self):
        if os.path.exists(self.search_history_file):
            with open(self.search_history_file, 'r') as file:
                self.search_history = [line.strip() for line in file.readlines()]
        else:
            self.search_history = []

    def save_search_history(self):
        with open(self.search_history_file, 'w') as file:
            for item in self.search_history:
                file.write(item + '\n')

    def __del__(self):
        # Save search history before closing the application
        self.save_search_history()

    def find_text(self):
        text, ok = QInputDialog.getText(self, 'Find Text', 'Enter text to find:')
        if ok and text:
            options = QWebEngineFindFlags()
            options |= QWebEngineFindFlags.FindCaseSensitively  # Case sensitive search
            options |= QWebEngineFindFlags.FindWrapsAroundDocument  # Wrap around document
            options |= QWebEngineFindFlags.FindBackward  # Search backward
            self.browser.findText(text, options)

app = QApplication(sys.argv)
window = MainWindow()
app.exec_()