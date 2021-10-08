#-- Qt engine
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

#-- Utils import
import sys
import json
import os
import platform


PLATFORM = platform.system()


#-----
# Browser app
#----

class Browser(QMainWindow):
    def __init__(self):
        super(Browser, self).__init__()
        
        # Plaform specific stuff
        if PLATFORM == "Linux":
            self.home_dir = os.path.expanduser("~")
        elif PLATFORM == "Windows":
            self.home_dir = os.path.dirname(os.path.abspath(__file__))
      
        # Startups
        self.__generate_files()
        self.__generate_paths()
                
        self.__load_settings()
        self.__load_history()
        self.__load_bookmark()

        # Tags
        self.tags = [":open", ":bookmark"]
        self.cmds = [":cmd q", ":cmd clear_history"]

        # Search bar vars
        self.activate_search = True
        self.nav_bar = None

        # Tab
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.__kill_tab)
        self.tab_widget.setStyleSheet("QTabWidget::pane { border: 0; } QTabBar::tab { height: 10px; width: 100px; }");
        self.tabs = []

        # Setting up browser
        self.__generate_home_page()
        self.__generate_new_tab()

        # App stuff
        self.setCentralWidget(self.tab_widget)
        self.showMaximized()

        # Add shortcuts
        self.__add_shortcut()
    
    #----
    # Startup generations
    #----

    def __generate_home_page(self):
        if PLATFORM == "Windows":
            path = "/.config/"
        elif PLATFORM == "Linux":
            path = "/.config/sbrowser/"
 
        if ".html" in self.settings["home"]:
            self.home_page = "file://" + self.home_dir + path + self.settings["home"]
        else:
            self.home_page = self.settings["home"]

    def __generate_files(self):
        # Generates .history and .bookmark files

        if PLATFORM == "Windows":
            if not os.path.exists(os.path.join(".config")):
                os.mkdir(os.path.join(".config"))
                
            if not os.path.isfile(os.path.join(".config/.history")):
                open(os.path.join(".config/.history"), "w")

            if not os.path.isfile(os.path.join(".config/.bookmark")):
                open(os.path.join(".config/.bookmark"), "w")
        
        elif PLATFORM == "Linux":
            if not os.path.exists(f"{self.home_dir}/.config/sbrowser"):
                os.mkdir(f"{self.home_dir}/.config/sbrowser")

            if not os.path.isfile(f"{self.home_dir}/.config/sbrowser/.history"):
                open(f"{self.home_dir}/.config/sbrowser/.history", "w")

            if not os.path.isfile(f"{self.home_dir}/.config/sbrowser/.bookmark"):
                open(f"{self.home_dir}/.config/sbrowser/.bookmark", "w") 

    def __generate_paths(self):
        if PLATFORM == "Windows":
            self.history_path = os.path.join(".config/.history")
            self.bookmark_path = os.path.join(".config/.bookmark")
            self.settings_path = os.path.join("sbrowser_config.json")

        elif PLATFORM == "Linux":
            self.history_path = f"{self.home_dir}/.config/sbrowser/.history"
            self.bookmark_path = f"{self.home_dir}/.config/sbrowser/.bookmark"
            
            if os.path.isfile(f"{self.home_dir}/.config/sbrowser/sbrowser_config.json"):
                self.settings_path = f"{self.home_dir}/.config/sbrowser/sbrowser_config.json"
            else:
                self.settings_path = os.path.join("sbrowser_config.json")

    #----
    # File Loaders
    #----
    
    # Settings loader
    def __load_settings(self):
        print(self.settings_path)
        with open(self.settings_path, "r") as r:
            self.settings = json.load(r)
    
    # History loader
    def __load_history(self):
        with open(self.history_path, "r") as r:
            data = r.readlines()

        self.history = []
        for i in data:
            self.history.append(":open " + i.strip("\n"))
        
    def __append_history(self, new_histroy):
        with open(self.history_path, "a") as a:
            a.write(new_histroy + "\n")

    # Bookmarks loader
    def __load_bookmark(self):
        with open(self.bookmark_path, "r") as r:
            data = r.readlines()

        self.bookmarks = []
        for i in data:
            self.bookmarks.append(":bookmark " + i.strip("\n"))
   
    def __append_bookmark(self, new_bookmark):
        with open(self.bookmark_path, "a") as a:
            a.write(new_bookmark + "\n")

    def __remove_bookmark(self, to_remove):
        self.bookmarks.remove(":bookmark " + to_remove)
            
        # Getting the bookmarks to resave
        to_save = []
        for i in self.bookmarks:
            to_save.append(i.split(":bookmark")[1] + "\n")
        
        # Saving the bookmarks
        with open(self.bookmark_path, "w") as w:
            for i in to_save:
                w.write(i)
        
        # Reloading the bookmarks
        self.__load_bookmark()

    #----
    # Key handlers
    #----

    def __add_shortcut(self):
        # All shortcut keys
        
        # Enables cmd entry
        self.cmd_search = QShortcut(QKeySequence(":"), self)
        self.cmd_search.activated.connect(self.__search_cmd)

        self.close_search = QShortcut(QKeySequence("Escape"), self)
        self.close_search.activated.connect(self.__close_search_bar)
        
        #-- Webpage util
        
        # To clear history
        self.clear_history = QShortcut(QKeySequence("Shift+h"), self)
        self.clear_history.activated.connect(self.__clear_history)

        # To add bookmark
        self.add_book_mark = QShortcut(QKeySequence("Ctrl+b"), self)
        self.add_book_mark.activated.connect(self.__bookmark)

        # To refresh the page
        self.refresh = QShortcut(QKeySequence("Ctrl+r"), self)
        self.refresh.activated.connect(self.__refresh)

        # To go to prev page
        self.prev = QShortcut(QKeySequence("Ctrl+p"), self)
        self.prev.activated.connect(self.__back)

        # To go forward
        self.forward = QShortcut(QKeySequence("Ctrl+f"), self)
        self.forward.activated.connect(self.__forward)

        # To go to home
        self.home = QShortcut(QKeySequence("Ctrl+h"), self)
        self.home.activated.connect(self.__home)

        #-- Tabs

        # To generate new tab
        self.new_tab = QShortcut(QKeySequence("Ctrl+t"), self)
        self.new_tab.activated.connect(self.__generate_new_tab)

        # To kill tabs
        self.kill_tab = QShortcut(QKeySequence("Ctrl+w"), self)
        self.kill_tab.activated.connect(self.__kill_tab)

        # Tabs movement
        self.move_left = QShortcut(QKeySequence("Ctrl+left"), self)
        self.move_left.activated.connect(self.__tab_left)

        self.move_right = QShortcut(QKeySequence("Ctrl+right"), self)
        self.move_right.activated.connect(self.__tab_right)

    #----
    # Tabs
    #----

    def __generate_new_tab(self):
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl(self.home_page))
        self.tabs.append(self.browser)

        self.tab_widget.addTab(self.browser, "New Tab")
   
    def __kill_tab(self, junk = None):
        index = self.tab_widget.currentIndex()
        self.tabs.pop(index)
        self.tab_widget.removeTab(index)

        if len(self.tabs) == 0:
            self.__generate_new_tab()

    def __tab_left(self):
        index = self.tab_widget.currentIndex()
        if index > 0:
            self.tab_widget.setCurrentIndex(index - 1)
    
    def __tab_right(self):
        index = self.tab_widget.currentIndex()
        if index < len(self.tabs):
            self.tab_widget.setCurrentIndex(index + 1)

    #----
    # Cmds refrences
    #----

    # Search bar
    def __exec_cmd(self):
        search = self.search_bar.text()
        
        if search:
            # Parsing the cmds
            if search == ":q" or search == ":cmd q":
                self.close()

            elif search == ":ch" or search == ":cmd clear_history":
                self.__clear_history()
             
            else: 
                # Extracting search data
                tokens = search.split(" ")
                
                if tokens[0] in self.tags:
                    search = search.split(tokens[0])[1][1:]

                # Searching in default search engine
                if "http" in search:
                    self.tabs[self.tab_widget.currentIndex()].load(QUrl(search))
                else:
                    search = self.settings["search_engine"] + "/search?q=" + search
                    self.tabs[self.tab_widget.currentIndex()].load(QUrl(search))
                
                # Changing the tab name
                self.tab_widget.setTabText(self.tab_widget.currentIndex(), search)
                
                # Saving and reloading history
                if ":open " + search not in self.history:
                    self.__append_history(search)
                self.__load_history()
        
        self.__close_search_bar()

    def __close_search_bar(self):
        if self.nav_bar:
            self.search_bar.clear()
            self.nav_bar.removeAction(self.action)
            self.removeToolBar(self.nav_bar)

    def __search(self, completer, pre_text):
        self.search_bar = QLineEdit()
        self.nav_bar = QToolBar()
        
        # Adding search bar
        self.search_bar.setFocusPolicy(Qt.StrongFocus)
        self.action = self.nav_bar.addWidget(self.search_bar)
        self.addToolBar(Qt.BottomToolBarArea, self.nav_bar)
        
        # Adding auto completer
        self.completer = QCompleter(completer)
        self.search_bar.setCompleter(self.completer)
        self.search_bar.setText(pre_text)

        # Adding focus
        self.search_bar.setFocus()
        self.search_bar.returnPressed.connect(self.__exec_cmd)
    
    def __search_cmd(self):
        all_completion = self.cmds + self.bookmarks + self.history
        self.__search(all_completion, ":")

    # Bookmark
    def __bookmark(self):
        bookmark = self.tabs[self.tab_widget.currentIndex()].url().toString()

        if ":bookmark " + bookmark not in self.bookmarks:
            self.__append_bookmark(bookmark)
        else:
            self.__remove_bookmark(bookmark)
        self.__load_bookmark()

    # History
    def __clear_history(self):
        with open(self.history_path, "w") as w:
            w.write("")
            
        self.__load_history()

    # Refresh 
    def __refresh(self):
        self.tabs[self.tab_widget.currentIndex()].reload()
        self.__load_settings()

    # Back
    def __back(self):
        self.tabs[self.tab_widget.currentIndex()].back()

    # Forward
    def __forward(self):
        self.tabs[self.tab_widget.currentIndex()].forward()

    # Home
    def __home(self):
        self.tabs[self.tab_widget.currentIndex()].setUrl(QUrl(self.home_page))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    QApplication.setApplicationName("Browser")

    browser = Browser()
    app.exec_()

