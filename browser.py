import sys
import os
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *

import pickle
from datetime import date

class BrowserTab(QWidget):
    def __init__(self, parent=None):
        super(BrowserTab, self).__init__(parent)
        layout = QVBoxLayout()
        self.browser = QWebEngineView()
        layout.addWidget(self.browser)
        self.setLayout(layout)

class READMEWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Welcome to OIS Browser")
        self.setWindowIcon(QIcon('icons/ois.jpg'))
        self.setGeometry(0, 0, 800, 600)
        self.move(QApplication.desktop().screen().rect().center() - self.rect().center())

        layout = QVBoxLayout()
        self.setLayout(layout)
        
        readme_text = QLabel()
        readme_text.setAlignment(Qt.AlignLeft)
        readme_text.setWordWrap(True)
        readme_text.setOpenExternalLinks(True)
        with open("README.md", "r") as readme_file:
            readme_text.setText(readme_file.read())
        layout.addWidget(readme_text)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(readme_text)
        layout.addWidget(scroll_area)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("OIS Browser")
        self.setMinimumSize(QSize(1350, 750))
        self.setWindowIcon(QIcon('icons/ois.jpg'))
        self.showMaximized()

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)

        navbar = QToolBar()
        self.addToolBar(navbar)

        # Home button
        home_btn = QAction(QIcon("icons/home_icon.png"), 'Home', self)
        home_btn.setStatusTip("Home")
        home_btn.triggered.connect(self.navigate_home)
        navbar.addAction(home_btn)

        # Back button
        back_btn = QAction(QIcon("icons/Arrow_back_left.png"), 'Back', self)
        back_btn.setStatusTip("Back")
        back_btn.triggered.connect(self.navigate_back)
        navbar.addAction(back_btn)

        # Forward button
        forward_btn = QAction(QIcon("icons/Arrow_forward_right.png"), 'Forward', self)
        forward_btn.setStatusTip("Forward")
        forward_btn.triggered.connect(self.navigate_forward)
        navbar.addAction(forward_btn)

        # Reload button
        reload_btn = QAction(QIcon("icons/Button_refresh.png"), 'Refresh', self)
        reload_btn.setStatusTip("Refresh")
        reload_btn.triggered.connect(self.reload_page)
        navbar.addAction(reload_btn)

        # Search button
        search_btn = QAction(QIcon("icons/search_icon.png"), 'Search', self)
        search_btn.setShortcut("Ctrl+F")
        search_btn.setStatusTip("Search")
        search_btn.triggered.connect(self.search_text)
        navbar.addAction(search_btn)

        # Secure/Unsecure site indicator
        self.secure_icon = QLabel()
        secure_pixmap = QPixmap("icons/safe_icon.png")
        self.secure_icon.setPixmap(secure_pixmap)
        self.secure_icon.setToolTip("Secure")
        navbar.addWidget(self.secure_icon)

        # URL bar
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navbar.addWidget(self.url_bar)

        # Add tab button
        add_tab_btn = QAction(QIcon("icons/add_tab_icon.png"), 'Add Tab', self)
        add_tab_btn.setStatusTip("Add Tab")
        add_tab_btn.triggered.connect(self.add_tab)
        navbar.addAction(add_tab_btn)

        # Set icon size for the toolbar
        navbar.setIconSize(QSize(24, 24))

        self.tabs.currentChanged.connect(self.update_current_tab)

        self.add_tab()

    def add_tab(self):
        new_tab = BrowserTab()
        file_path = os.path.join(os.path.dirname(__file__), "search_engine.html")
        new_tab.browser.setUrl(QUrl.fromLocalFile(file_path))
        self.tabs.addTab(new_tab, "New Tab")
        self.tabs.setCurrentWidget(new_tab)


    def current_browser(self):
        current_tab_index = self.tabs.currentIndex()
        current_tab_widget = self.tabs.widget(current_tab_index)
        return current_tab_widget.browser

    def navigate_home(self):
        self.current_browser().setUrl(QUrl("file://" + os.path.abspath("search_engine.html")))

    def navigate_back(self):
        self.current_browser().back()

    def navigate_forward(self):
        self.current_browser().forward()

    def reload_page(self):
        self.current_browser().reload()

    def navigate_to_url(self):
        today = date.today()
        history_location = "history/search_history_" + str(today) + ".dat"
        input_text = self.url_bar.text()
        if not input_text.startswith(("http://", "https://")):
            input_text = "https://www.google.com/search?q=" + input_text + "&hl=en"
            self.current_browser().setUrl(QUrl(input_text))
        else:
            self.current_browser().setUrl(QUrl(input_text))
        with open(history_location, "ab") as history:
            pickle.dump(input_text, history)

    def update_current_tab(self):
        current_tab_index = self.tabs.currentIndex()
        current_tab_widget = self.tabs.widget(current_tab_index)
        current_tab_url = current_tab_widget.browser.url().toString()
        if current_tab_url == "https://www.google.com/?hl=en":
            self.tabs.setTabText(current_tab_index, "New Tab")
        else:
            current_tab_widget.browser.page().titleChanged.connect(
                lambda title: self.tabs.setTabText(current_tab_index, title))

        self.url_bar.setText(current_tab_url)

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            QApplication.quit()

    def search_text(self):
        text, ok = QInputDialog.getText(self, 'Find Text', 'Enter text to find:')
        if ok and text:
            self.current_browser().findText(text)

app = QApplication(sys.argv)

readme_window = READMEWindow()
readme_window.show()

def show_main_window():
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

readme_window.destroyed.connect(show_main_window)
sys.exit(app.exec_())
