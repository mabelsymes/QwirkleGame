from string import ascii_lowercase as ascii_l
import random
import datetime
from Database import Database
from itertools import combinations, permutations
import time

class Player():

    # INIT -----------------------------------------------------------------------------------------------------------
    def __init__(self, playerId, playerDifficulty):
        self.__playerDifficulty = playerDifficulty
        self.__playerId = playerId
        self.__score = 0
        self.__tiles = []
    # END INIT -------------------------------------------------------------------------------------------------------

    # GET ------------------------------------------------------------------------------------------------------------
    def getPlayerId(self):
        return self.__playerId

    def getScore(self):
        return self.__score
    
    def getTiles(self):
        return self.__tiles
    
    def getPlayerDifficulty(self):
        return self.__playerDifficulty
    # END GET --------------------------------------------------------------------------------------------------------
    
    # SET ------------------------------------------------------------------------------------------------------------
    def setScore(self, sScore):
        self.__score = sScore

    def setTiles(self, sTiles):
        self.__tiles = sTiles
    # END SET --------------------------------------------------------------------------------------------------------

    # TILES ----------------------------------------------------------------------------------------------------------
    def removeTile(self, tile):
        if tile in self.__tiles:
            self.__tiles.remove(tile)

    def addTile(self, tile):
        self.__tiles.append(tile)
    # END TILES ------------------------------------------------------------------------------------------------------

class Game:

    # CONSTANTS ------------------------------------------------------------------------------------------------------

    __EMPTY = "  "
    __DIM = 25
    __TILESPERHAND = 6
    __CENTRE = (int(__DIM//2), int(__DIM//2))

    # END CONSTANTS --------------------------------------------------------------------------------------------------

    # INIT ----------------------------------------------------------------------------------------------------------

    def __init__(self, players, gameName):
        self.__tiles = self.__generateTiles()
        self.__board = self.__generateBoard()
        self.__dateCreated = datetime.datetime.now()
        self.__dateCreated = self.__dateCreated.strftime('%Y-%m-%d %H:%M:%S')
        self.__gameName = gameName
        self.__players = {}
        self.__winnerIds = []
        for p in players:
            playerId = p.getUserId()
            playerDifficulty = p.getUserDifficulty()
            self.__players[playerId] = Player(playerId, playerDifficulty)
            self.__players[playerId].setTiles(self.__getRandomTiles())

    # END INIT ------------------------------------------------------------------------------------------------------

    # GET -----------------------------------------------------------------------------------------------------------

    def getBoardCentre(self):
        return Game.__CENTRE
    
    def getBoardDimensions(self):
        return Game.__DIM
    
    def getNumberOfTilesRemaining(self):
        return len(self.__tiles)

    def getPlayerTiles(self, playerId):
        return self.__players[playerId].getTiles()
    
    def getPlayerScore(self, playerId):
        return self.__players[playerId].getScore()
    
    def getTiles(self):
        return self.__tiles
    
    def getBoard(self):
        return self.__board
    
    def getEmpty(self):
        return Game.__EMPTY
    
    def getTilesPerHand(self):
        return Game.__TILESPERHAND
    
    def __getRandomTiles(self):
        tiles = self.getTiles()
        randomTiles = []
        for i in range(Game.__TILESPERHAND):
            randomTiles.append(tiles.pop(random.randint(0, len(tiles) - 1)))
        self.__setTiles(tiles)
        return randomTiles
    
    def getWinnerIdsAndHighestScore(self):
        winners = []
        highestScore = 0
        for playerId in self.__players:
            if len(winners) == 0:
                winners = [playerId]
                highestScore = self.__players[playerId].getScore()
            elif self.__players[playerId].getScore() > highestScore:
                winners = [playerId]
                highestScore = self.__players[playerId].getScore()
            elif self.__players[playerId].getScore() == highestScore:
                winners.append(playerId)
        self.__winnerIds = winners
        return winners, highestScore
    
    def getHandTileCombinations(handTiles):

        tileCombs = []
        for i in range(1, len(handTiles)+1):
            tileCombs += list(combinations(handTiles, i))

        finalTileCombs = []
        # making sure the combination is valid (at least shape or colour shared)
        for t in tileCombs:
            if t not in finalTileCombs:
                if Game.__isTileCombinationValid(t):
                    finalTileCombs.append(t)
        return finalTileCombs
    
    def getTilesAndPositionsForEmptyBoard(tileCombs):
        centre = Game.__CENTRE
        # returns longest string of tile combinations in centre of board
        finalTiles = list(tileCombs[-1])
        finalPositions = []
        for i in range(len(finalTiles)):
            finalPositions.append((i+centre[0],centre[1]))
        return finalTiles, finalPositions
    
    @staticmethod
    # Recursive function for determining where a given list of tiles can be placed on the board
    # All tiles must be used, and tiles are placed in the order they are given.
    # Used to calculate suggested move
    def __getPossiblePositionsForTilesOnBoard(board, tiles, possiblePositionsForTiles):

        newPossiblePositionsForTiles = []
        tileToAdd = tiles[0]

        if len(possiblePositionsForTiles) == 0:
            # placing first tile

            tempBoard = []
            for row in board:
                tempBoard.append(row.copy())

            for row in range(len(board)):
                for col in range(len(board[row])):
                    if board[row][col] != Game.__EMPTY:
                        continue
                    # Testing out placing tile in that location
                    tempBoard[row][col] = tileToAdd
                    if Game.__isBoardValid(tempBoard):
                        newPossiblePositionsForTiles.append([(tileToAdd, col, row)])
                    # Resetting board
                    tempBoard[row][col] = Game.__EMPTY

            if newPossiblePositionsForTiles == []:
                # no possible positions for first tile
                return []

        # seeing where other tiles can be placed
        else:
            for p in possiblePositionsForTiles:

                # making copy of board
                tempBoard = []
                for row in board:
                    tempBoard.append(row.copy())
                # seeing which row/column the tile can be added
                rowIsSet = False
                colIsSet = False
                cols = [i[1] for i in p]
                rows = [i[2] for i in p]

                minimumRow = max(0, min(rows) - 1)
                while board[minimumRow][cols[0]] != Game.__EMPTY:
                    minimumRow -= 1
                    if minimumRow < 0:
                        minimumRow = 0
                        break
                maximumRow = min(Game.__DIM - 1, max(rows) + 1)
                while board[maximumRow][cols[0]] != Game.__EMPTY:
                    maximumRow += 1
                    if maximumRow > Game.__DIM - 1:
                        maximumRow = Game.__DIM - 1
                        break
                currentRow = p[0][2]

                minimumCol = max(0, min(cols) - 1)
                while board[rows[0]][minimumCol] != Game.__EMPTY:
                    minimumCol -= 1
                    if minimumCol < 0:
                        minimumCol = 0
                        break
                maximumCol = min(Game.__DIM - 1, max(cols) + 1)
                while board[rows[0]][maximumCol] != Game.__EMPTY:
                    maximumCol += 1
                    if maximumCol > Game.__DIM - 1:
                        maximumCol = Game.__DIM - 1
                        break
                currentCol = p[0][1]

                if len(p) >= 2:
                    if p[0][2] == p[1][2]:
                        # at least two tiles have been placed horizontally, so new tile must also be on that row
                        rowIsSet = True
                    elif p[0][1] == p[1][1]:
                        # at least two tiles have been placed vertically, so new tile must also be on that column
                        colIsSet = True

                for tilePlacement in p:
                    # Updates tempBoard with tile placements in this scenario
                    tile, col, row = tilePlacement[0], tilePlacement[1], tilePlacement[2]
                    tempBoard[row][col] = tile

                if not colIsSet:
                    # testing out placing currentTile on either side of the tiles already placed
                    # when col is not set, that means that either there is only one tile placed, or that the tiles are placed horizontally
                    for col in [minimumCol, maximumCol]:
                        if tempBoard[currentRow][col] != Game.__EMPTY:
                            continue
                        tempBoard[currentRow][col] = tileToAdd
                        if Game.__isBoardValid(tempBoard):
                            newPossibility = p.copy()
                            newPossibility.append((tileToAdd, col, currentRow))
                            newPossiblePositionsForTiles.append(newPossibility)
                        # resetting board
                        tempBoard[currentRow][col] = Game.__EMPTY
                if not rowIsSet:
                    # Same but for rows
                    for row in [minimumRow, maximumRow]:
                        if tempBoard[row][currentCol] != Game.__EMPTY:
                            continue
                        tempBoard[row][currentCol] = tileToAdd
                        if Game.__isBoardValid(tempBoard):
                            newPossibility = p.copy()
                            newPossibility.append((tileToAdd, currentCol, row))
                            newPossiblePositionsForTiles.append(newPossibility)
                        # resetting board
                        tempBoard[row][currentCol] = Game.__EMPTY

        if newPossiblePositionsForTiles == []:
            # no possible positions for tile
            return []
        
        if len(tiles) > 1:
            newPossiblePositionsForTiles = Game.__getPossiblePositionsForTilesOnBoard(board, tiles[1:], newPossiblePositionsForTiles)
        
        return newPossiblePositionsForTiles

    @staticmethod
    def getSuggestedMove(board, playerTiles, difficulty):

        tileCombs = Game.getHandTileCombinations(playerTiles)

        if Game.__isBoardEmpty(board):
            return Game.getTilesAndPositionsForEmptyBoard(tileCombs)
        
        if difficulty == 1:
            # reduce possible moves, making computer weaker
            if len(tileCombs) >= 6:
                newTileCombs = []
                for pos in range(0,len(tileCombs),6):
                    newTileCombs.append(tileCombs[pos])
                tileCombs = newTileCombs.copy()

        if difficulty == 2:
            # reduce possible moves, making computer weaker
            if len(tileCombs) >= 3:
                newTileCombs = []
                for pos in range(0,len(tileCombs),3):
                    newTileCombs.append(tileCombs[pos])
                tileCombs = newTileCombs.copy()
                
        if difficulty == 3:
            # adds permutations of all moves to take into account placing tiles in different orders
            newTileCombs = []
            for t in tileCombs:
                newTileCombs += list(permutations(t))
            tileCombs = newTileCombs.copy()

        time1 = time.time()
        possibleMoves = []
        for t in tileCombs:
            possibleMoves += Game.__getPossiblePositionsForTilesOnBoard(board, t, [])
            time2 = time.time()
            if time2 - time1 > 4:
                # Taking too long
                break

        highestScore = 0
        finalTiles = []
        finalPositions = []

        if len(possibleMoves) == 0:
            return (None,None)

        for possibility in possibleMoves:
            tiles = []
            positions = []
            betterMoveFound = False
            for p in possibility:
                # p[0] is tile value, p[1] is column (y), and p[2] is row (x)
                tiles.append(p[0])
                positions.append((p[1], p[2]))
            score, qwirkle = Game.__calculateScoreAndQwirkle(board, tiles, positions)
            if score > highestScore:
                betterMoveFound = True   
            elif score == highestScore:
                # to prevent moves from being skewered in one direction
                x = random.randint(0,1)
                if x == 0:
                    betterMoveFound = True
            if betterMoveFound:
                num = 0
                if difficulty == 1:
                    num = random.randint(0,4)
                elif difficulty == 2:
                    num = random.randint(0,1)
                if num == 0:
                    highestScore = score
                    finalTiles = tiles
                    finalPositions = positions
        if finalTiles == []:
            return (None,None)
        return (finalTiles, finalPositions)

    # END GET --------------------------------------------------------------------------------------------------------

    # SET ------------------------------------------------------------------------------------------------------------

    def __setTiles(self, sTiles):
        self.__tiles = sTiles

    def __placeTile(self, col, row, tile):
        self.__board[row][col] = tile

    # END SET --------------------------------------------------------------------------------------------------------

    # GENERATE -------------------------------------------------------------------------------------------------------
    
    def __generateTiles(self):
        newTiles = []
        for letter in ascii_l[:Game.__TILESPERHAND]:
            for number in list("123456"):
                for _ in range(3):
                    newTiles.append(letter + number)
        return newTiles
    
    def __generateBoard(self):
        newBoard = []
        for i in range(Game.__DIM):
            newBoard.append([])
            for j in range(Game.__DIM):
                newBoard[i].append(Game.__EMPTY)
        return newBoard
    
    # END GENERATE ---------------------------------------------------------------------------------------------------

    # IS TRUE --------------------------------------------------------------------------------------------------------
    
    def isTileInHand(self, playerId, tile):
        tiles = self.__players[playerId].getTiles()
        if tile in tiles:
            return True
        return False

    def isGameFinished(self):
        if len(self.__tiles) != 0:
            False
        for playerId in self.__players:
            if len(self.__players[playerId].getTiles()) == 0:
                self.__players[playerId].setScore(self.__players[playerId].getScore() + 6)
                return True
        # noMovesLeft = True
        # for playerId in self.__players:
        #     move = Game.getSuggestedMove(self.__board, self.__players[playerId].getTiles(), 3)
        #     if move == (None,None):
        #         continue
        #     else:
        #         noMovesLeft = False
        #         break
        # if noMovesLeft:
        #     return True
        return False
    
    def doesPlayerHaveMove(self, playerId):
        if len(self.__tiles) > 0:
            return True
        move = Game.getSuggestedMove(self.__board, self.__players[playerId].getTiles(), 3)
        if move == (None,None):
            return False
        return True
    
    def isSelfBoardEmpty(self):
        for row in self.__board:
            for tile in row:
                if tile != Game.__EMPTY:
                    return False
        return True
    
    def __isTilePresent(self, position):
        if position[0] > Game.__DIM or position[1] > Game.__DIM or position[0] < 0 or position[1] < 0:
            return False
        col = position[0] 
        row = position[1] 
        if self.__board[row][col] == Game.__EMPTY:
            return False
        return True
    
    @staticmethod
    def __isBoardEmpty(board):
        for row in board:
            for tile in row:
                if tile != Game.__EMPTY:
                    return False
        return True
    
    @staticmethod
    def __isTileAdjacentToOtherTiles(board, ncol, nrow):
        dir = [[0, 1], [1, 0], [0, -1], [-1, 0]]
        for d in dir:
            newx = ncol + d[0]
            newy = nrow + d[1]
            if newx < 0 or newx >= Game.__DIM or newy < 0 or newy >= Game.__DIM:
                continue
            if board[newy][newx] != Game.__EMPTY:
                return True
        return False
    
    # END IS TRUE ---------------------------------------------------------------------------------------------------

    # EDIT HAND -----------------------------------------------------------------------------------------------------

    def __fillPlayerHand(self, playerId):
        while len(self.__players[playerId].getTiles()) < Game.__TILESPERHAND:
            if len(self.__tiles) == 0:
                break
            self.__players[playerId].addTile(self.__tiles.pop(random.randint(0, len(self.__tiles) - 1)))

    def replacePlayerHand(self, playerId, tilesToReplace):
        for tile in tilesToReplace:
            self.__tiles.append(tile)
            self.__players[playerId].removeTile(tile)
        newHand = self.getPlayerTiles(playerId)
        while len(self.__tiles) > 0 and len(newHand) < Game.__TILESPERHAND:
            newHand.append(self.__tiles.pop(random.randint(0, len(self.__tiles) - 1)))
        self.__players[playerId].setTiles(newHand)

    # END EDIT HAND -------------------------------------------------------------------------------------------------

    # CALCULATE SCORE -----------------------------------------------------------------------------------------------
    @staticmethod
    def __calcScore(position, horizontal, board):
        if horizontal:
            return Game.__calcScoreHorizontal(position, board)
        return Game.__calcScoreVertical(position, board)

    @staticmethod
    def __calcScoreHorizontal(position, board):
        col = position[0] 
        row = position[1] 
        # Original tile is of length 1
        lengthOfRow = 1
        # Checking to the right of tile
        for i in range(col+1, Game.__DIM):
            if board[row][i] == Game.__EMPTY:
                break
            else:
                lengthOfRow += 1
        # Checking to the left of tile
        for i in range(col-1, -1, -1):
            if board[row][i] == Game.__EMPTY:
                break
            else:
                lengthOfRow += 1
        if lengthOfRow == 6:
            # Six in a row means six additional points (a Qwirkle)
            return 12
        if lengthOfRow == 1:
            # You don't get a point for 1 tile in a row
            return 0
        return lengthOfRow

    @staticmethod
    def __calcScoreVertical(position, board):
        col = position[0] 
        row = position[1] 
        # Original tile is of length 1
        lengthOfColumn = 1
        # Checking below tile
        for i in range(row+1, Game.__DIM):
            if board[i][col] == Game.__EMPTY:
                break
            else:
                lengthOfColumn += 1
        # Checking above tile
        for i in range(row-1, -1, -1):
            if board[i][col] == Game.__EMPTY:
                break
            else:
                lengthOfColumn += 1
        if lengthOfColumn == 6:
            # Six in a row means six additional points (Qwirkle)
            return 12
        if lengthOfColumn == 1:
            # You don't get a point for 1 tile in a row
            return 0
        return lengthOfColumn
    
    # TEMPORARY
    # To be used for computer player to calculate score without changing board
    @staticmethod
    def __calculateScoreAndQwirkle(board, tiles, positions):

        tilesHorizontal = True
        if len(positions) > 1:
            if positions[0][0] == positions[1][0]:
                tilesHorizontal = False

        boardCopy = []
        for row in board:
            boardCopy.append(row.copy())
        for pos in range(len(tiles)):
            col = positions[pos][0] 
            row = positions[pos][1] 
            tile = tiles[pos]
            boardCopy[row][col] = tile
            
        score = 0
        qwirkle = False
        for pos in positions:
            # Calculating scores in the opposite direction to the tileplacement
            score += (result := Game.__calcScore(pos, not tilesHorizontal, boardCopy))
            if result == 12:
                qwirkle = True
        # Calculating score in the same direction as the tile placement
        score += (result := Game.__calcScore(positions[0], tilesHorizontal, boardCopy))
        if result == 12:
            qwirkle = True
        return score, qwirkle

    # END CALCULATE SCORE--------------------------------------------------------------------------------------------

    # CHANGE BOARD --------------------------------------------------------------------------------------------------

    # Permanently changes board
    def addTilesAndChangeUserScoreAndGetIfQwirkle(self, playerId, tiles, positions):

        score, qwirkle = Game.__calculateScoreAndQwirkle(self.__board, tiles, positions)

        for pos in range(len(tiles)):
            col = positions[pos][0]
            row = positions[pos][1]
            tile = tiles[pos]
            self.__placeTile(col, row, tile)
            self.__players[playerId].removeTile(tile)
        
        self.__fillPlayerHand(playerId)
        self.__players[playerId].setScore(self.__players[playerId].getScore() + score)

        return qwirkle
    
    # END CHANGE BOARD ----------------------------------------------------------------------------------------------
    
    # IS VALID ------------------------------------------------------------------------------------------------------

    def isPositionValid(self, position):
        col = position[0]
        row = position[1]
        if col >= 0 and col < Game.__DIM and row >= 0 and row < Game.__DIM:
            if self.__board[row][col] == Game.__EMPTY:
                return True
        return False
    
    @staticmethod
    # Used to get tile combinations for a given hand
    def __isTileCombinationValid(tiles):

        if len(tiles) == 1:
            return True
        
        # checks if any tile is repeated (if so, returns false)
        for tile in tiles:
            if tiles.count(tile) > 1:
                return False

        # checks that all tiles share either shape or colour
        # when first is True, tiles share the value at position 0 (which represents shape)
        # when first is False, tiles share the value at position 1 (which represents colour)
        first = False
        for pos in range(1,len(tiles)):
            if pos == 1:
                if tiles[pos][0] == tiles[pos-1][0]:
                    first = True
                elif tiles[pos][1] == tiles[pos-1][1]:
                    first = False
                else:
                    return False
            else:
                if first:
                    if tiles[pos][0] != tiles[pos-1][0]:
                        return False
                else:
                    if tiles[pos][1] != tiles[pos-1][1]:
                        return False
        return True
    
    # used in isAddingTileValid
    def __arePositionsValid(self, positions):

        # prevents original positions from being changed
        npositions = positions.copy()

        # making sure tiles are on the board
        for p in npositions:
            if Game.isPositionValid(self, p) == False:
                return False
            
        if len(npositions) > 1:
            # making sure tiles are adjacent to each other
            npositions.sort()
            xSame = False
            if npositions[0][0] == npositions[1][0]:
                xSame = True
            for pos in range(len(npositions)-1):
                position1 = npositions[pos]
                position2 = npositions[pos+1]
                if xSame:
                    # the x values must be same and the tiles adjacent in the y direction (unless there are tiles in between)
                    if position1[0] != position2[0]:
                        # x values not same
                        return False
                    elif position1[1] != position2[1] - 1:
                        for ypos in range(position1[1]+1, position2[1]):
                            if self.__isTilePresent((position2[0],ypos)) == False:
                                # y values not adjacent
                                return False
                else:
                    # the y values must be same and the tiles adjacent in the x direction (unless there are tiles in between)
                    if position1[1] != position2[1]:
                        # y values not same
                        return False
                    elif position1[0] != position2[0] - 1:
                        for xpos in range(position1[0]+1, position2[0]):
                            if self.__isTilePresent((xpos,position2[1])) == False:
                                # x values not adjacent
                                return False
                        
        # making sure at least one tile being placed is adjacent to an existing tile
        # unless the board is empty, in which case the tile must be placed in the centre
        if self.isSelfBoardEmpty() == False:
            for pos in npositions:
                if Game.__isTileAdjacentToOtherTiles(self.__board, pos[0], pos[1]):
                    return True
            return False
        else:
            if Game.__CENTRE in npositions:
                return True
            return False

    def isAddingTilesValid(self, tiles, positions):

        if self.__arePositionsValid(positions) == False:
            return False

        boardCopy = []
        for row in self.__board:
            boardCopy.append(row.copy())
        for pos in range(len(tiles)):
            col = positions[pos][0] 
            row = positions[pos][1] 
            tile = tiles[pos]
            boardCopy[row][col] = tile

        # isBoardValid checks that every run of adjacent tiles shares either shape or colour
        if Game.__isBoardValid(boardCopy):
            return True

        return False
    
    @staticmethod
    def __checkConsecutiveBoardTilesValid(board, checkingRow):
        for num1 in range(Game.__DIM):
            currentSeq = []
            toMatch = ""
            for num2 in range(Game.__DIM):
                if checkingRow == False:
                    currentBoardTile = board[num2][num1]
                else:
                    currentBoardTile = board[num1][num2]
                if currentBoardTile == Game.__EMPTY:
                    # the sequence of tiles is over
                    currentSeq = []
                    toMatch = ""
                else:
                    # the sequence of tiles is not over
                    if currentBoardTile in currentSeq:
                        # two tiles of the same type cannot be in a sequence
                        return False
                    if currentSeq == []:
                        currentSeq.append(currentBoardTile)
                    elif len(currentSeq) == 1:
                        # the attribute to match can be decided now that there are two tiles
                        firstSeqTile = currentSeq[0]
                        if firstSeqTile[0] == currentBoardTile[0]:
                            # abcdef are the shapes
                            toMatch = firstSeqTile[0]
                        elif firstSeqTile[1] == currentBoardTile[1]:
                            # 123456 are the colours
                            toMatch = firstSeqTile[1]
                        else:
                            # there is no common attribute, so the tile combination is invalid
                            return False
                        currentSeq.append(currentBoardTile)
                    else:
                        # checking to see if the shape/colour is the same
                        if toMatch == currentBoardTile[0] or toMatch == currentBoardTile[1]:
                            currentSeq.append(currentBoardTile)
                        else:
                            return False
        return True
    
    @staticmethod
    def __isBoardValid(board):

        # Calculating the number of tiles on the board
        tilesOnBoard = 0
        for row in range(Game.__DIM):
            for col in range(Game.__DIM):
                if board[row][col] != Game.__EMPTY:
                    tilesOnBoard += 1

        if tilesOnBoard == 0:
            # Empty board is valid
            return True
        
        if board[Game.__CENTRE[1]][Game.__CENTRE[0]] == Game.__EMPTY:
            # There must be a tile in the centre of the board
            return False
        else:
            if tilesOnBoard == 1:
                # One tile in the centre of the board is a valid board
                return True

        # Checking all tiles are adjacent to at least one other tile
        for row in range(Game.__DIM):
            for col in range(Game.__DIM):
                if board[row][col] != Game.__EMPTY:
                    if Game.__isTileAdjacentToOtherTiles(board, col, row) == False:
                        return False

        # Checking that sequences of tiles are valid (share at least one shape or colour and no duplicates)
        return (Game.__checkConsecutiveBoardTilesValid(board,True) and Game.__checkConsecutiveBoardTilesValid(board,False))
    
    # END IS VALID ---------------------------------------------------------------------------------------------------
    
    # SAVE GAME ------------------------------------------------------------------------------------------------------
    
    def saveGame(self, gameCompleted, currentPlayerId, userId):

        gameName = self.__gameName
        dateCreated = self.__dateCreated
        numberOfPlayers = len(self.__players)
        currentPlayerId = currentPlayerId

        playerIds = list(self.__players.keys())

        playerDifficulties = []
        for player in self.__players.values():
            playerDifficulties.append(player.getPlayerDifficulty())

        playerScores = []
        for player in self.__players.values():
            playerScores.append(player.getScore())

        playerTiles = []
        for player in self.__players.values():
            playerTiles.append(player.getTiles())

        winnerIds = self.__winnerIds
        board = self.__board
        tilesLeft = self.__tiles

        gameCompleted = gameCompleted

        db = Database()
        db.saveGame(gameName, dateCreated, numberOfPlayers, currentPlayerId, playerIds, playerDifficulties, playerScores, playerTiles, winnerIds, board, tilesLeft, gameCompleted, userId)
    
    # END SAVE GAME --------------------------------------------------------------------------------------------------

    # LOAD GAME ------------------------------------------------------------------------------------------------------

    def loadGame(self, gameDetails):
        self.__dateCreated = gameDetails['dateCreated']
        self.__gameName = gameDetails['gameName']
        playerScores = gameDetails['playerScores']
        playerTiles = gameDetails['playerTiles']
        playerIds = gameDetails['playerIds']
        for pos in range(len(playerIds)):
            self.__players[playerIds[pos]].setScore(playerScores[pos])
            self.__players[playerIds[pos]].setTiles(playerTiles[pos])
        self.__board = gameDetails['board']
        for row in range(len(self.__board)):
            for col in range(len(self.__board[row])):
                square = self.__board[row][col]
                if square[0].isalpha() == False and square[1].isnumeric() == False:
                    # If Game.__EMPTY is update, this makes sure it is updated as well
                    self.__board[row][col] = Game.__EMPTY
        self.__tiles = gameDetails['tilesLeft']
    
    # END LOAD GAME --------------------------------------------------------------------------------------------------
    
    # REPR -----------------------------------------------------------------------------------------------------------

    def __repr__(self):
        result = " "
        for i in range(Game.__DIM):
            i = str(i+1)
            if len(i) == 1:
                result += "    " + i
            else:
                result += "   " + i
        for row in range(Game.__DIM):
            if len(str(row+1)) == 1:
                spacing = "   "
            else:
                spacing = "  "
            result += f"\n{row+1}{spacing}" + " | ".join(self.__board[row]) + " |"
            if row != Game.__DIM - 1:
                dashes = "-" * (5 * Game.__DIM)
                result += f"\n  {dashes}"
        return result
    
    # END REPR ------------------------------------------------------------------------------------------------------

    





