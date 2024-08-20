import sys
import os
import pickle
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from datetime import datetime, date

class CustomWebEnginePage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        log_message = f"JS Console [{level}]: {message} (Line: {lineNumber}, Source: {sourceID})"
        print(log_message)
        # Optionally, write to a log file:
        with open("browser_errors.log", "a") as log_file:
            log_file.write(log_message + "\n")

class BrowserTab(QWidget):
    def __init__(self, parent=None):
        super(BrowserTab, self).__init__(parent)
        layout = QVBoxLayout()
        self.browser = QWebEngineView()
        self.browser.setPage(CustomWebEnginePage(self.browser))  # Use the custom page with overridden method
        layout.addWidget(self.browser)
        self.setLayout(layout)

class READMEWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Welcome to OIS Browser")
        self.setWindowIcon(QIcon('icons/ois.jpg'))
        self.setGeometry(0, 0, 800, 600)
        self.move(QApplication.desktop().screen().rect().center() - self.rect().center())  # Center the window

        layout = QVBoxLayout()
        self.setLayout(layout)
        
        readme_text = QLabel()
        readme_text.setAlignment(Qt.AlignLeft)
        readme_text.setWordWrap(True)
        readme_text.setOpenExternalLinks(True)
        
        # Delay loading README content to speed up initial UI
        QTimer.singleShot(0, lambda: self.load_readme(readme_text))

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(readme_text)
        layout.addWidget(scroll_area)

    def load_readme(self, label):
        with open("README.md", "r") as readme_file:
            label.setText(readme_file.read())

class HistoryTab(BrowserTab):
    def __init__(self, parent=None):
        super(HistoryTab, self).__init__(parent)
        self.browser.setHtml(self.generate_history_html())

    def generate_history_html(self):
        history_dir = "history"
        html_content = "<html><body><h1>History</h1><ul>"

        if not os.path.exists(history_dir):
            html_content += "<li>No history found.</li>"
        else:
            for history_file in sorted(os.listdir(history_dir), reverse=True):
                if history_file.endswith(".dat"):
                    html_content += f"<h2>{history_file.replace('search_history_', '').replace('.dat', '')}</h2>"
                    with open(os.path.join(history_dir, history_file), "rb") as history:
                        while True:
                            try:
                                entry = pickle.load(history)
                                if isinstance(entry, tuple) and len(entry) == 2:
                                    url, timestamp = entry
                                    if isinstance(timestamp, int):
                                        formatted_time = datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")
                                        html_content += f"<li>{formatted_time}: <a href='{url}'>{url}</a></li>"
                                    else:
                                        html_content += f"<li>Invalid timestamp format in {history_file}</li>"
                                else:
                                    html_content += f"<li>Invalid entry format in {history_file}</li>"
                            except EOFError:
                                break
                            except Exception as e:
                                html_content += f"<li>Error reading entry from {history_file}: {str(e)}</li>"

        html_content += "</ul></body></html>"
        return html_content

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("OIS Browser")
        self.setMinimumSize(QSize(1350, 750))
        self.setWindowIcon(QIcon('icons/ois.jpg'))
        self.showMaximized()

        self.bookmarks = {}  # Initialize bookmarks as a dictionary
        self.load_bookmarks()  # Load bookmarks

        # Main Toolbar
        navbar = QToolBar()
        self.addToolBar(navbar)

        home_btn = QAction(QIcon("icons/home_icon.png"), 'Home', self)
        home_btn.setStatusTip("Home")
        home_btn.triggered.connect(self.navigate_home)
        navbar.addAction(home_btn)

        back_btn = QAction(QIcon("icons/Arrow_back_left.png"), 'Back', self)
        back_btn.setStatusTip("Back")
        back_btn.triggered.connect(self.navigate_back)
        navbar.addAction(back_btn)

        forward_btn = QAction(QIcon("icons/Arrow_forward_right.png"), 'Forward', self)
        forward_btn.setStatusTip("Forward")
        forward_btn.triggered.connect(self.navigate_forward)
        navbar.addAction(forward_btn)

        reload_btn = QAction(QIcon("icons/Button_refresh.png"), 'Refresh', self)
        reload_btn.setStatusTip("Refresh")
        reload_btn.triggered.connect(self.reload_page)
        navbar.addAction(reload_btn)

        search_btn = QAction(QIcon("icons/search_icon.png"), 'Search', self)
        search_btn.setShortcut("Ctrl+F")  # Mimics Ctrl+F
        search_btn.setStatusTip("Search")
        search_btn.triggered.connect(self.search_text)
        navbar.addAction(search_btn)

        self.secure_icon = QLabel()
        secure_pixmap = QPixmap("icons/safe_icon.png")
        self.secure_icon.setPixmap(secure_pixmap)
        self.secure_icon.setToolTip("Secure")
        navbar.addWidget(self.secure_icon)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navbar.addWidget(self.url_bar)

        add_tab_btn = QAction(QIcon("icons/add_tab_icon.png"), 'Add Tab', self)
        add_tab_btn.setStatusTip("Add Tab")
        add_tab_btn.triggered.connect(self.add_tab)
        navbar.addAction(add_tab_btn)

        add_bookmark_btn = QAction(QIcon("icons/bookmark_add.png"), 'Add Bookmark', self)
        add_bookmark_btn.setStatusTip("Add Bookmark")
        add_bookmark_btn.triggered.connect(self.add_bookmark_prompt)
        navbar.addAction(add_bookmark_btn)

        dots_menu_btn = QAction(QIcon("icons/dots.png"), 'More Options', self)
        dots_menu_btn.setStatusTip("More Options")
        dots_menu_btn.triggered.connect(self.show_more_options)
        navbar.addAction(dots_menu_btn)

        navbar.setIconSize(QSize(24, 24))

        # Add bookmarks bar below the main toolbar
        self.bookmarks_toolbar = QToolBar("Bookmarks")
        self.addToolBar(Qt.BottomToolBarArea, self.bookmarks_toolbar)
        self.update_bookmarks_bar()

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)

        self.tabs.currentChanged.connect(self.update_current_tab)
        self.add_tab()

    def update_bookmarks_bar(self):
        self.bookmarks_toolbar.clear()
        for name, url in self.bookmarks.items():
            bookmark_action = QAction(name, self)
            bookmark_action.setData(url)
            bookmark_action.triggered.connect(lambda checked, url=url: self.current_browser().setUrl(QUrl(url)))
            self.bookmarks_toolbar.addAction(bookmark_action)

    def add_tab(self):
        new_tab = BrowserTab()
        self.tabs.addTab(new_tab, "New Tab")
        self.tabs.setCurrentWidget(new_tab)
        QTimer.singleShot(0, lambda: new_tab.browser.setUrl(QUrl("https://www.google.com/?hl=en")))

    def current_browser(self):
        current_tab_index = self.tabs.currentIndex()
        current_tab_widget = self.tabs.widget(current_tab_index)
        return current_tab_widget.browser

    def navigate_home(self):
        self.current_browser().setUrl(QUrl("https://www.google.com/?hl=en"))

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
            if "." not in input_text:
                input_text = "https://www.google.com/search?q=" + input_text + "&hl=en"
            else:
                input_text = "http://" + input_text
        self.current_browser().setUrl(QUrl(input_text))
        with open(history_location, "ab") as history:
            pickle.dump((input_text, int(datetime.now().timestamp())), history)

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
            self.current_browser().setUrl(QUrl("about:blank"))

    def add_bookmark_prompt(self):
        current_url = self.current_browser().url().toString()
        bookmark_name, ok = QInputDialog.getText(self, 'Bookmark Name', 'Enter a name for the bookmark:')
        if ok and bookmark_name:
            self.bookmarks[bookmark_name] = current_url
            self.save_bookmarks()
            self.update_bookmarks_bar()

    def save_bookmarks(self):
        with open("bookmarks.dat", "wb") as file:
            pickle.dump(self.bookmarks, file)

    def load_bookmarks(self):
        if os.path.exists("bookmarks.dat"):
            with open("bookmarks.dat", "rb") as file:
                self.bookmarks = pickle.load(file)

    def search_text(self):
        text, ok = QInputDialog.getText(self, 'Find Text', 'Enter text to find:')
        if ok and text:
            self.current_browser().findText(text)

    def show_more_options(self):
        menu = QMenu()
        history_action = QAction('History', self)
        history_action.triggered.connect(self.show_history_tab)
        menu.addAction(history_action)

        zoom_in_action = QAction('Zoom In', self)
        zoom_in_action.triggered.connect(self.zoom_in)
        menu.addAction(zoom_in_action)

        zoom_out_action = QAction('Zoom Out', self)
        zoom_out_action.triggered.connect(self.zoom_out)
        menu.addAction(zoom_out_action)

        show_bookmarks_bar_action = QAction('Show Bookmarks Bar', self, checkable=True)
        show_bookmarks_bar_action.setChecked(self.bookmarks_toolbar.isVisible())
        show_bookmarks_bar_action.toggled.connect(self.toggle_bookmarks_bar)
        menu.addAction(show_bookmarks_bar_action)

        menu.exec_(QCursor.pos())

    def show_history_tab(self):
        history_tab = HistoryTab()
        self.tabs.addTab(history_tab, "History")
        self.tabs.setCurrentWidget(history_tab)

    def zoom_in(self):
        self.current_browser().setZoomFactor(self.current_browser().zoomFactor() + 0.1)

    def zoom_out(self):
        self.current_browser().setZoomFactor(self.current_browser().zoomFactor() - 0.1)

    def toggle_bookmarks_bar(self, checked):
        self.bookmarks_toolbar.setVisible(checked)

def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    # Show the welcome window first
    welcome_window = READMEWindow()
    welcome_window.show()
    app.exec_()

if __name__ == "__main__":
    main()
