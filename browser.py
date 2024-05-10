import sys
import os
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *


class BrowserTab(QWidget):
    def __init__(self, parent=None):
        super(BrowserTab, self).__init__(parent)
        layout = QVBoxLayout()

        self.browser = QWebEngineView()
        layout.addWidget(self.browser)

        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("OIS Browser")
        self.setMinimumSize(QSize(1350, 750))
        self.setWindowIcon(QIcon('unnamed.png'))
        self.showMaximized()

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)

        self.add_tab()

        navbar = QToolBar()
        self.addToolBar(navbar)

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

        # Home button
        home_btn = QAction(QIcon("icons/home_icon.png"), 'Home', self)
        home_btn.setStatusTip("Home")
        home_btn.triggered.connect(self.navigate_home)
        navbar.addAction(home_btn)

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
        add_tab_btn = QAction(QIcon("icons/Add_tab_icon.png"), 'Add Tab', self)
        add_tab_btn.setStatusTip("Add Tab")
        add_tab_btn.triggered.connect(self.add_tab)
        navbar.addAction(add_tab_btn)

        self.tabs.currentChanged.connect(self.update_current_tab)

    def add_tab(self):
        new_tab = BrowserTab()
        self.tabs.addTab(new_tab, "New Tab")
        self.tabs.setCurrentWidget(new_tab)

    def current_browser(self):
        current_tab_index = self.tabs.currentIndex()
        current_tab_widget = self.tabs.widget(current_tab_index)
        return current_tab_widget.browser

    def navigate_back(self):
        self.current_browser().back()

    def navigate_forward(self):
        self.current_browser().forward()

    def reload_page(self):
        self.current_browser().reload()

    def navigate_home(self):
        self.current_browser().setUrl(QUrl("https://www.google.com/?hl=en"))

    def navigate_to_url(self):
        input_text = self.url_bar.text()
        if not input_text.startswith(("http://", "https://")):
            input_text = "https://www.google.com/search?q=" + input_text + "&hl=en"
            self.current_browser().setUrl(QUrl(input_text))
        else:
            self.current_browser().setUrl(QUrl(input_text))

    def update_current_tab(self):
        current_tab_index = self.tabs.currentIndex()
        current_tab_widget = self.tabs.widget(current_tab_index)
        current_tab_url = current_tab_widget.browser.url().toString()
        self.url_bar.setText(current_tab_url)

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            QApplication.quit()


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
