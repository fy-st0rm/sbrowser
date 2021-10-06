
#-- Qt engine
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

#-- Utils import
import sys
import json
import os


#-----
# Browser app
#----

class Browser(QMainWindow):
    def __init__(self):
        super(Browser, self).__init__()
        
        self.__load_settings()
        self.__load_history()
        self.__load_bookmark()

        # Search bar vars
        self.activate_search = True
        self.nav_bar = None
        self.search_mode = "browse"

        # Setting up browser
        self.home_page = "file://" + os.path.dirname(os.path.abspath(__file__)) + "/.config/" + self.settings["home"]
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl(self.home_page))

        # App stuff
        self.setCentralWidget(self.browser)
        self.showMaximized()

        # Add shortcuts
        self.__add_shortcut()

    #----
    # File Loaders
    #----

    def __load_settings(self):
        with open(os.path.join(".config/config.json"), "r") as r:
            self.settings = json.load(r)

    def __load_history(self):
        with open(os.path.join(".config/.history"), "r") as r:
            data = r.readlines()

        self.history = []
        for i in data:
            self.history.append(i.strip("\n"))
        
    def __append_history(self, new_histroy):
        with open(os.path.join(".config/.history"), "a") as a:
            a.write(new_histroy + "\n")

    def __load_bookmark(self):
        with open(os.path.join(".config/.bookmark"), "r") as r:
            data = r.readlines()

        self.bookmarks = []
        for i in data:
            self.bookmarks.append(i.strip("\n"))
   
    def __append_bookmark(self, new_bookmark):
        with open(os.path.join(".config/.bookmark"), "a") as a:
            a.write(new_bookmark + "\n")

    #----
    # Key handlers
    #----

    def __add_shortcut(self):
        # All shortcut keys

        # To activate search bar
        self.website_search = QShortcut(QKeySequence("o"), self)
        self.website_search.activated.connect(self.__search_website)

        self.bookmark_search = QShortcut(QKeySequence("b"), self)
        self.bookmark_search.activated.connect(self.__search_bookmark)

        self.close_search = QShortcut(QKeySequence("Escape"), self)
        self.close_search.activated.connect(self.__close_search_bar)

        # To add bookmark
        self.add_book_mark = QShortcut(QKeySequence("Ctrl+b"), self)
        self.add_book_mark.activated.connect(self.__bookmark)

        # To refresh the page
        self.refresh = QShortcut(QKeySequence("Ctrl+r"), self)
        self.refresh.activated.connect(self.__refresh)

        # To go to prev page
        self.prev = QShortcut(QKeySequence("Ctrl+left"), self)
        self.prev.activated.connect(self.__back)

        # To go forward
        self.forward = QShortcut(QKeySequence("Ctrl+right"), self)
        self.forward.activated.connect(self.__forward)

        # To go to home
        self.home = QShortcut(QKeySequence("Ctrl+h"), self)
        self.home.activated.connect(self.__home)
 
    #----
    # Cmds refrences
    #----

    # Search bar
    def __load_url(self):
        search = self.search_bar.text()
        
        if search:
            if "http" in search:
                self.browser.load(QUrl(search))
            else:
                search = self.settings["search_engine"] + "/search?q=" + search
                self.browser.load(QUrl(search))
            
            # Saving and reloading history
            if search not in self.history:
                self.__append_history(search)
            self.__load_history()
        
        self.__close_search_bar()

    def __close_search_bar(self):
        self.search_bar.clear()
        self.nav_bar.removeAction(self.action)
        self.removeToolBar(self.nav_bar)

    def __search(self, completer):
        self.search_bar = QLineEdit()
        self.nav_bar = QToolBar()
        
        # Adding search bar
        self.search_bar.setFocusPolicy(Qt.StrongFocus)
        self.action = self.nav_bar.addWidget(self.search_bar)
        self.addToolBar(self.nav_bar)
        
        # Adding auto completer
        self.completer = QCompleter(completer)
        self.search_bar.setCompleter(self.completer)
        
        # Setting the dimension of the completer
        if completer:
            rect = QRect(0, -64, self.size().width(), 100)
            self.completer.complete(rect)
            self.completer.popup().show()

        # Adding focus
        self.search_bar.setFocus()
        self.search_bar.returnPressed.connect(self.__load_url)

    def __search_website(self):
        self.__search(self.history)
    
    def __search_bookmark(self):
        self.__search(self.bookmarks)

    # Bookmark
    def __bookmark(self):
        bookmark = self.browser.url().toString()

        if bookmark not in self.bookmarks:
            self.__append_bookmark(bookmark)
        self.__load_bookmark()

    # Refresh 
    def __refresh(self):
        self.browser.reload()
        self.__load_settings()

    # Back
    def __back(self):
        self.browser.back()

    # Forward
    def __forward(self):
        self.browser.forward()

    # Home
    def __home(self):
        self.browser.setUrl(QUrl(self.home_page))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    QApplication.setApplicationName("Browser")

    browser = Browser()
    app.exec_()

