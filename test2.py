from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def setupData(self):

        self.lineEdit1 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit1.setObjectName("lineEdit1")
        self.lineEdit1.returnPressed.connect(self.return_pressed)
        self.autocomplete_list = ['a1', 'a2', 'a3', 'a4', 'a5']
        self.completer = QtWidgets.QCompleter(self.autocomplete_list)
        self.lineEdit1.setCompleter(self.completer)


    def return_pressed(self):
        user_input = self.lineEdit1.text()
        updated_list = [x for x in self.autocomplete_list if x not in user_input]
        print(updated_list)
        self.completer = QtWidgets.QCompleter(updated_list)
        self.lineEdit1.setCompleter(self.completer)
        print('Gets to here')


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    ui.setupData()
    MainWindow.show()
    sys.exit(app.exec_())
