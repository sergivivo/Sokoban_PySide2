from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *

from level import Level

class LevelView(QGraphicsView):
    keymapping = {Qt.Key_Right: 0, Qt.Key_Up: 1, Qt.Key_Left: 2, Qt.Key_Down: 3}
    cellsize = 50
    def __init__(self, parent=None):
        super(LevelView, self).__init__()
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setRenderHint(QPainter.Antialiasing)

    def generateLevel(self, level):
        self.level = level
        self.rows, self.columns = self.level.getMapRect()
        xsize = self.columns * self.cellsize
        ysize = self.rows * self.cellsize

        self.scene = QGraphicsScene(parent=self)
        self.scene.setSceneRect(0,0,xsize,ysize)
        brush = QBrush(QColor(38,34,10,255))
        self.scene.setBackgroundBrush(brush)

        self.setScene(self.scene)
        self.resetMatrix()

        self._setScreen()

    def restartLevel(self):
        self.level.restartLevel()
        self._setScreen()

    def undoMove(self):
        self.level.undoMove()
        self._updateScreen()

    def redoMove(self):
        self.level.redoMove()
        self._updateScreen()

    def _setScreen(self):
        self.scene.clear()

        player_pos = self.level.getPlayer()
        walls = self.level.getWalls()
        goals = self.level.getGoalSquares()
        boxes = self.level.getBoxes()

        # Floor
        brush = QBrush(QColor(149,115,59,255))
        accessible = self._getAccessible(player_pos[0], player_pos[1], walls)
        for e in accessible:
            if e not in goals:
                accs_x = e[1] * self.cellsize
                accs_y = e[0] * self.cellsize
                self.scene.addRect(accs_x, accs_y, self.cellsize, self.cellsize, brush=brush)

        # Goal squares
        brush = QBrush(QColor(200,155,80,255))
        for e in goals:
            goal_x = e[1] * self.cellsize
            goal_y = e[0] * self.cellsize
            self.scene.addRect(goal_x, goal_y, self.cellsize, self.cellsize, brush=brush)

        # Boxes
        brush = QBrush(QColor(193,120,0,255))
        shrink = 3/4
        gap = self.cellsize * (1 - shrink) / 2
        gapsize = self.cellsize - gap * 2
        self.boxes = []
        for e in boxes:
            box_x = e[1] * self.cellsize + gap
            box_y = e[0] * self.cellsize + gap
            self.boxes.append(self.scene.addRect(box_x, box_y, gapsize, gapsize, brush=brush))

        # Player
        brush = QBrush(QColor(255,255,255,255))
        player_x = player_pos[1] * self.cellsize + gap
        player_y = player_pos[0] * self.cellsize + gap
        self.player = self.scene.addEllipse(player_x, player_y, gapsize, gapsize, brush=brush)

        # Walls
        brush = QBrush(QColor(97,68,20,255))
        for e in walls:
            wall_x = e[1] * self.cellsize
            wall_y = e[0] * self.cellsize
            self.scene.addRect(wall_x, wall_y, self.cellsize, self.cellsize, brush=brush)

        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def _updateScreen(self):
        mod = self.level.getModified()
        if len(mod) > 0:
            xpos1 = mod[0][1] * self.cellsize + self.cellsize / 2
            ypos1 = mod[0][0] * self.cellsize + self.cellsize / 2
            xpos2 = mod[1][1] * self.cellsize + self.cellsize / 2
            ypos2 = mod[1][0] * self.cellsize + self.cellsize / 2
            xinc = (xpos2 - xpos1)
            yinc = (ypos2 - ypos1)
            if len(mod) == 3:
                item = self.scene.itemAt(xpos2, ypos2, QTransform())
                item.moveBy(xinc, yinc)
            item = self.scene.itemAt(xpos1, ypos1, QTransform())
            item.moveBy(xinc, yinc)

    def _getAdjacent(self, row, column):
        return [(i,j) for i in range(max(row-1   , 0), min(row+2   , self.rows))
                      for j in range(max(column-1, 0), min(column+2, self.columns))
                      if (i + j) % 2 != (row + column) % 2]

    def _getAccessible(self, row, column, walls):
        # Will store adjacent connected floor
        tocheck = [(row,column)]
        checked = []

        while len(tocheck) > 0:
            checking = tocheck.pop()

            adjacent = self._getAdjacent(checking[0], checking[1])
            nowall = [x for x in adjacent if x not in walls]
            tocheck += [x for x in nowall if x not in checked+tocheck]

            checked.append(checking)

        return checked

    def keyPressEvent(self, event):
        if not self.level.checkSolved() and event.key() in self.keymapping:
            self.level.move(self.keymapping[event.key()])
            self._updateScreen()
        elif event.key() == Qt.Key_U:
            self.undoMove()
        elif event.key() == Qt.Key_R:
            self.redoMove()

    def resizeEvent(self, event):
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

