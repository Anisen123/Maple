#Displays GUI window which contains all widgets from 'Widgets' class

import sys

from Widgets import Widgets
from PyQt5.QtWidgets import QApplication, QMainWindow

class MainWindow(QMainWindow): 
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.widget = Widgets(self) 
        self.setCentralWidget(self.widget)   
        self.setGeometry(300,400,1200,900)   
        self.setWindowTitle('Maple GUI')     
                                             
    #def getApp(self):
    #    return app

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show() 
    sys.exit(app.exec_())
    