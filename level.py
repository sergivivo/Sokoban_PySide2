class Level:
    def __init__(self, unprocessed):
        self.model = unprocessed
        self.walls = []
        self.boxes = []
        self.goal_squares = []
        for i in range(len(unprocessed)):
            for j in range(len(unprocessed[i])):
                if unprocessed[i][j] == '#':
                    self.walls.append((i,j))
                elif unprocessed[i][j] == '@':
                    self.player = (i,j)
                elif unprocessed[i][j] == '+':
                    self.player = (i,j)
                    self.goal_squares.append((i,j))
                elif unprocessed[i][j] == '$':
                    self.boxes.append((i,j))
                elif unprocessed[i][j] == '*':
                    self.boxes.append((i,j))
                    self.goal_squares.append((i,j))
                elif unprocessed[i][j] == '.':
                    self.goal_squares.append((i,j))

        self.modified = []
        self.history = []
        self.moves = 0

    def restartLevel(self):
        self.__init__(self.model)

    def move(self, direction, fromHistory=False):
        # Find increment given direction of move
        increments = ((0,1), (-1,0), (0,-1), (1,0))
        iinc = increments[direction][0]
        jinc = increments[direction][1]

        # Get coordinates for the two following positions
        nxtpos  = (self.player[0]+iinc,   self.player[1]+jinc  )
        nxtpos2 = (self.player[0]+iinc*2, self.player[1]+jinc*2)

        if nxtpos not in self.walls:
            if nxtpos in self.boxes:
                # Box in place, check if it can be pushed
                if nxtpos2 not in self.boxes + self.walls:
                    # No box or wall next to pushing box
                    self.modified = [self.player, nxtpos, nxtpos2]
                    self.boxes.remove(nxtpos)
                    self.boxes.append(nxtpos2)
                    self.player = nxtpos

                    # Update history of moves
                    if not fromHistory:
                        self.history = self.history[:self.moves]
                        self.history.append(direction-4)
                        self.moves += 1
                else:
                    self.modified = []
            else:
                # Empty place to move for player
                self.modified = [self.player, nxtpos]
                self.player = nxtpos

                # Update history of moves
                if not fromHistory:
                    self.history = self.history[:self.moves]
                    self.history.append(direction)
                    self.moves += 1
        else:
            self.modified = []

    def undoMove(self):
        if self.moves > 0:
            self.moves -= 1
            direction = self.history[self.moves]
            rev_dir = (direction+2)%4
            self.move(rev_dir, True)
            if direction < 0:
                # Revert pushed box
                increments = ((0,1), (-1,0), (0,-1), (1,0))
                iinc = increments[direction][0]
                jinc = increments[direction][1]

                # Get coordinates for the two following positions
                nxtpos  = (self.player[0]+iinc,   self.player[1]+jinc  )
                nxtpos2 = (self.player[0]+iinc*2, self.player[1]+jinc*2)

                self.boxes.remove(nxtpos2)
                self.boxes.append(nxtpos)

                self.modified.insert(0,nxtpos2)
        else:
            self.modified = []

    def redoMove(self):
        if self.moves < len(self.history):
            direction = self.history[self.moves]
            self.move(direction, True)
            self.moves += 1
        else:
            self.modified = []

    def checkSolved(self):
        for e in self.goal_squares:
            if e not in self.boxes:
                return False
        return True

    def getMapRect(self):
        transposed = list(zip(*self.walls))
        rows = max(transposed[0]) + 1
        columns = max(transposed[1]) + 1
        return rows, columns

    def getWalls(self):
        return self.walls

    def getPlayer(self):
        return self.player

    def getGoalSquares(self):
        return self.goal_squares

    def getBoxes(self):
        return self.boxes

    def getModified(self):
        return self.modified

    def __str__(self):
        transposed = list(zip(*self.walls))
        rows = max(transposed[0]) + 1
        columns = max(transposed[1]) + 1
        s = ""
        for i in range(rows):
            for j in range(columns):
                if (i,j) in self.walls:
                    s += "██"
                elif (i,j) == self.player:
                    if (i,j) in self.goal_squares:
                        s += "움"
                    else:
                        s += "웃"
                elif (i,j) in self.boxes:
                    if (i,j) in self.goal_squares:
                        s += "回"
                    else:
                        s += "口"
                elif (i,j) in self.goal_squares:
                    s += "ㅁ"
                else:
                    s += "  "
            s += "\r\n"
        return s
