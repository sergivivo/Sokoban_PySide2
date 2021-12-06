import sys
import os
import threading

from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *

# Custom
from level import Level
from levelview import LevelView

class MainWindow(QMainWindow):
    lvlfolder = os.path.join(os.path.dirname(__file__), "levels")
    def __init__(self):
        super(MainWindow, self).__init__()

        # MENU BAR
        # ----------------------------------------------------------------------
        game = self.menuBar().addMenu("Game")
        load = QAction("Load levels", self)
        load.triggered.connect(self.searchFile)
        game.addAction(load)

        # LEVEL VIEW WIDGET
        # ----------------------------------------------------------------------
        self.level = LevelView(parent=self)
        self.curpath = os.path.join(self.lvlfolder, "microban.txt")
        self.loadLevelSet()

        # LEVEL CONTROL WIDGET
        # ----------------------------------------------------------------------
        control = QWidget(parent=self)

        # Control buttons
        self.undo = QPushButton("Undo", parent=self)
        self.restart = QPushButton("Restart", parent=self)
        self.redo = QPushButton("Redo", parent=self)
        self.undo.clicked.connect(self.level.undoMove)
        self.restart.clicked.connect(self.level.restartLevel)
        self.redo.clicked.connect(self.level.redoMove)

        # NAVIGATION BAR
        # ----------------------------------------------------------------------
        navbar = QWidget(parent=self)

        # Level navigation buttons
        self.left = QPushButton("<<", parent=self)
        self.right = QPushButton(">>", parent=self)
        self.left.clicked.connect(self.prevLevel)
        self.right.clicked.connect(self.nextLevel)

        # Level number display
        self.number = QLabel(parent=self)
        self.number.setText("{}/{}".format(self.curlvl + 1, len(self.levels)))
        self.number.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter)

        # LAYOUTS
        # ----------------------------------------------------------------------
        vlayout = QVBoxLayout()
        hlayout1 = QHBoxLayout()
        hlayout2 = QHBoxLayout()

        # Control bar layout
        hlayout1.addWidget(self.undo)
        hlayout1.addWidget(self.restart)
        hlayout1.addWidget(self.redo)
        control.setLayout(hlayout1)

        # Navigation bar layout
        hlayout2.addWidget(self.left)
        hlayout2.addWidget(self.number)
        hlayout2.addWidget(self.right)
        navbar.setLayout(hlayout2)

        # Vertical layout
        vlayout.addWidget(control)
        vlayout.addWidget(self.level)
        vlayout.addWidget(navbar)

        # CENTRAL WIDGET
        # ----------------------------------------------------------------------
        cwidget = QWidget(parent=self)
        cwidget.setLayout(vlayout)
        self.setCentralWidget(cwidget)
        self.resize(500,500)

    def nextLevel(self):
        self.curlvl = (self.curlvl + 1) % len(self.levels)
        self.number.setText("{}/{}".format(self.curlvl + 1, len(self.levels)))
        self.loadLevel()

    def prevLevel(self):
        self.curlvl = (self.curlvl - 1) % len(self.levels)
        self.number.setText("{}/{}".format(self.curlvl + 1, len(self.levels)))
        self.loadLevel()

    def searchFile(self):
        dirName = QFileDialog.getOpenFileName(self, "Abrir Archivo",
                self.lvlfolder, "Text Files (*.txt);;")
        if dirName[0] != "":
            self.curpath = dirName[0]
            self.loadLevelSet()

    def loadLevel(self):
        self.level.generateLevel(self.levels[self.curlvl])

    def loadLevelSet(self):
        self.levels = []
        with open(self.curpath, "r") as f:
            lines = f.read().splitlines()
        try:
            prev = 0
            while True:
                nxt = lines[prev:].index("")
                nxt += prev
                self.levels.append(Level(lines[prev:nxt-1]))
                prev = nxt+1
        except ValueError:
            self.curlvl = 0
            self.level.generateLevel(self.levels[self.curlvl])

if __name__ == "__main__":
    application = QApplication([])

    window = MainWindow()
    window.show()

    sys.exit(application.exec_())
