import os
os.environ["QTWEBENGINEPROCESS_PATH"] = "/usr/lib/qt/libexec/QtWebEngineProcess"

#-- Qt engine
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

#-- Utils import
import sys
import json
import platform
import clipboard

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
        self.__load_colors()

        # Tags
        self.tags = [":open", ":bookmark"]
        self.cmds = [":cmd q", ":cmd clear_history", ":cmd new_tab"]

        # Search bar vars
        self.activate_search = True
        self.nav_bar = None

        # Tab
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.__kill_tab)
        self.tab_widget.setStyleSheet("""QTabWidget::pane 
                                        { 
                                            border: 0; 
                                        } 
                                        QTabBar::tab 
                                        { 
                                            height: 20px; 
                                            background-color: """ + f"rgb({self.tab_bg[0]}, {self.tab_bg[1]}, {self.tab_bg[2]});" + """
                                            color: white; 
                                        }
                                        QTabBar::tab:selected 
                                        {
                                            background-color:""" + f"rgb({self.tab_bg[0]}, {self.tab_bg[1] + 20}, {self.tab_bg[2] + 20});" + """
                                        }"""
                                        );
        self.tab_widget.setPalette(self.palette)
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

    # Color palette loader
    def __load_colors(self):
        self.palette = QPalette()
        
        self.window = self.settings["window"]
        self.entry_bg = self.settings["entry_bg"]
        self.entry_text = self.settings["entry_text"]
        self.tab_bg = self.settings["tab_bg"]

        self.palette.setColor(QPalette.Window, QColor(self.window[0], self.window[1], self.window[2]))
        self.palette.setColor(QPalette.Base, QColor(self.entry_bg[0], self.entry_bg[1], self.entry_bg[2]))
        self.palette.setColor(QPalette.Text, QColor(self.entry_text[0], self.entry_text[1], self.entry_text[2]))
        
        app.setPalette(self.palette)
    
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
        
        # Enables search entry
        self.open_search = QShortcut(QKeySequence("o"), self)
        self.open_search.activated.connect(self.__search_open)

        # Enables bookmark entry
        self.bookmark_search = QShortcut(QKeySequence("b"), self)
        self.bookmark_search.activated.connect(self.__search_bookmark)

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

        # To copy link
        self.copy_link = QShortcut(QKeySequence("Ctrl+l"), self)
        self.copy_link.activated.connect(self.__copy_link)

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
    # Requests
    #----

    def __download_request(self, item):
        print("Downloading: " + item.downloadFileName() + " to " + self.settings["download_dir"])

        item.setPath(self.home_dir + "/" + self.settings["download_dir"] + item.downloadFileName())
        item.accept()

    #----
    # Tabs
    #----

    def __generate_new_tab(self):
        # Creating a new browser instanc
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl(self.home_page))
        self.browser.settings().setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        self.browser.page().fullScreenRequested.connect(lambda request: request.accept())
        self.browser.page().profile().downloadRequested.connect(self.__download_request)

        # Adding it to the tabs
        self.tabs.append(self.browser)

        self.tab_widget.addTab(self.browser, "New Tab")

        # Changing the focus to the new tab
        self.tab_widget.setCurrentIndex(len(self.tabs) - 1)
   
    def __kill_tab(self, index = None):
        if index is not None:
            self.tabs[index].close()
            self.tabs.pop(index)
            self.tab_widget.removeTab(index)
        else:
            index = self.tab_widget.currentIndex()
            self.tabs[index].close()
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

            elif search == ":clear_history" or search == ":cmd clear_history":
                self.__clear_history()

            elif search == ":new_tab" or search == ":cmd new_tab":
                self.__generate_new_tab()
             
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
        self.search_bar.setPalette(self.palette)

        self.nav_bar = QToolBar()
        self.nav_bar.setStyleSheet("QToolBar {border: 0;}")
        
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
    
    def __search_open(self):
        all_completion = self.cmds + self.bookmarks + self.history
        self.__search(all_completion, ":open")

    def __search_bookmark(self):
        all_completion = self.cmds + self.bookmarks + self.history
        self.__search(all_completion, ":bookmark")

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

    # Link
    def __copy_link(self):
        url = self.tabs[self.tab_widget.currentIndex()].url().toString()
        clipboard.copy(url)

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
        self.tab_widget.setTabText(self.tab_widget.currentIndex(), "New Tab")

if __name__ == "__main__":
    app = QApplication(sys.argv)
     
    if PLATFORM == "Linux":
        app.setStyle("Fusion")
    QApplication.setApplicationName("Browser")
    
    browser = Browser()
    app.exec_()

