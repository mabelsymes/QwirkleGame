from Game import Game
import random
import tkinter as tk
from tkinter import *
from tkinter import messagebox
from Database import Database
from User import User
from itertools import product
from PIL import Image, ImageTk
import time
import sys

class GameUi():

    def __init__(self):
        pass

    def _getStartingPlayerAndMoves(self, players, playerTiles):
        startingPlayer = None
        tilesToPlace = []
        positionsToPlace = []
        longest = 0
        for pos in range(len(players)):
            tileCombs = Game.getHandTileCombinations(playerTiles[pos])
            if len(tileCombs[-1]) > longest:
                longest = len(tileCombs[-1])
                startingPlayer = players[pos]
                tilesToPlace, positionsToPlace = Game.getTilesAndPositionsForEmptyBoard(tileCombs)
        return startingPlayer, tilesToPlace, positionsToPlace
    
    def _getPlayerById(self, id, players):
        for player in players:
            if player.getUserId() == id:
                return player
        return None
    
    def _getNextPlayer(self, players, currentPlayer):
        returnNext = False
        for player in players:
            if returnNext == True:
                return player
            if player.getUserId() == currentPlayer.getUserId():
                returnNext = True
        return players[0]
    
class GameGui(GameUi):

    __EMPTY = "     "
    __CENTRE = "  *  "

    # INIT -----------------------------------------------------------------------------------------------------------------------------------------
    def __clearWindow(self):
        for widget in self.__root.winfo_children():
            widget.destroy()

    def __init__(self, players, gameName, userId, master, loadGame, gameDetails=None):

        # VARIABLES --------------------------------------------------------------------------------------------------------------------------------
        self.__players = players
        self.__userId = userId
        random.shuffle(self.__players)
        self.__currentPlayer = self.__players[0]
        self.__root = master
        self.__root.title("Qwirkle - Game")
        self.__root.geometry("1200x700")
        self.__game = Game(self.__players, gameName)
        dim = self.__game.getBoardDimensions()
        self.__centre = self.__game.getBoardCentre()
        self.__currentTileVal = GameGui.__EMPTY
        self.__replaceTiles = False
        self.__usedTileVals = []
        self.__usedTilePositions = []
        self.__tilesSelected = []
        self.__usedPlayerTilePos = None
        button = tk.Button(self.__root, text='Hello')
        self.__DEFAULT_BUTTON_COLOR = button['bg']
        self.__minimumTilesToPlace = 1
        self.__hintSelected = False
        self.__hintTiles = []
        self.__hintPositions = []
        # END VARIABLES ----------------------------------------------------------------------------------------------------------------------------

        self.__clearWindow()
        
        # TITLE LABEL ------------------------------------------------------------------------------------------------------------------------------
        titleLabel = tk.Label(self.__root, text="Qwirkle")
        titleLabel.grid(row=0, column=0, padx=5, pady=5)
        offset1 = 1
        # END TITLE LABEL --------------------------------------------------------------------------------------------------------------------------

        # BOARD BUTTONS ----------------------------------------------------------------------------------------------------------------------------
        self.__boardButtons = [[None for _ in range(dim)] for _ in range(dim)]

        for col,row in product(range(dim),range(dim)):
            startImage = self.__getTileImage("empty")
            cmd = lambda r=row,c=col: self.__placeTileTemp(c,r)

            string = GameGui.__EMPTY
            if (col,row) == self.__centre:
                string = GameGui.__CENTRE
                startImage = self.__getTileImage("centre")
            button = self.__createButton(self.__root, col+offset1, row+offset1, string, startImage, cmd)
            button.image = startImage

            self.__boardButtons[row][col] = button

        # END BOARD BUTTONS ------------------------------------------------------------------------------------------------------------------------

        offset2 = offset1 + dim + 1

        # PLAYER LABELS ----------------------------------------------------------------------------------------------------------------------------
        self.__currentPlayerLabel = tk.Label(self.__root, text="Current Player: " + self.__currentPlayer.getUserName())
        self.__currentPlayerLabel.grid(row=1,column=offset2,sticky=N + S + E)
        self.__playerScores = []
        for player in self.__players:
            self.__playerScores.append(tk.Label(self.__root, text=player.getUserName() + ": " + str(self.__game.getPlayerScore(player.getUserId()))))
        for i in range(len(self.__playerScores)):
            self.__playerScores[i].grid(row=i+5,column=offset2,sticky=N + S + E)
        # END PLAYER LABELS-------------------------------------------------------------------------------------------------------------------------

        # PLAYER BUTTONS ---------------------------------------------------------------------------------------------------------------------------
        buttonFrame = tk.Frame(self.__root, width=200, height=50, bd=1, relief=tk.SOLID)
        buttonFrame.grid(row=3,column=offset2,sticky=N + S + E)
        yourTilesLabel = tk.Label(buttonFrame, text="Your Tiles:")
        yourTilesLabel.grid(row=0,column=0,sticky=N + S + E)

        self.__playerTiles = self.__game.getPlayerTiles(self.__userId)
        numberOfPlayerTiles = len(self.__playerTiles)
        self.__playerButtons = []
        for i in range(numberOfPlayerTiles):
            image = self.__getTileImage(self.__playerTiles[i])
            b = StringVar()
            b.set(self.__playerTiles[i])
            cmd = lambda i=i: self.__playerTileSelected(i)
            button = self.__createButton(buttonFrame, i+1, 0, self.__playerTiles[i], image, cmd)
            button.image = image
            self.__playerButtons.append(button)
        # END PLAYER BUTTONS -----------------------------------------------------------------------------------------------------------------------

        # OPTION BUTTONS ---------------------------------------------------------------------------------------------------------------------------
        optionFrame = tk.Frame(self.__root, width=200, height=50, bd=1, relief=tk.SOLID)
        optionFrame.grid(row=4,column=offset2,sticky=N + S + E)
        yourOptionsLabel = tk.Label(optionFrame, text="Options:")
        yourOptionsLabel.grid(row=0,column=0,sticky=N + S + E)
        returnTilesButton = tk.Button(optionFrame, text="Return Tiles", command=self.__returnTiles)
        returnTilesButton.grid(row=0,column=1,sticky=N + S + E)
        self.__replaceTilesButton = tk.Button(optionFrame, text="Replace Tiles", command=self.__replaceTilesButtonSelected)
        self.__replaceTilesButton.grid(row=0,column=2,sticky=N + E)
        finishTurnButton = tk.Button(optionFrame, text="Finish Turn", command=self.__finishTurn)
        finishTurnButton.grid(row=0,column=3,sticky=N + S + E)
        self.__hintButton = tk.Button(optionFrame, text="Hint", command=self.__hintButtonSelected)
        self.__hintButton.grid(row=0,column=4,sticky=N + E)
        # END OPTION BUTTONS -----------------------------------------------------------------------------------------------------------------------

        # TILES LEFT LABEL -------------------------------------------------------------------------------------------------------------------------
        self.__tilesLeftLabel = tk.Label(self.__root, text="Tiles Left: " + str(self.__game.getNumberOfTilesRemaining()))
        self.__tilesLeftLabel.grid(row=10,column=offset2, sticky=E)
        # END TILES LEFT LABEL ---------------------------------------------------------------------------------------------------------------------
       
        # END GAME AND PAUSE GAME BUTTONS ---------------------------------------------------------------------------------------------------------
        endGameButton = tk.Button(self.__root, text="End Game", command=self.__endGameAbruptly)
        endGameButton.grid(row=12,column=offset2,sticky=N + S + E)
        pauseGameButton = tk.Button(self.__root, text="Pause Game", command=self.__pauseGame)
        pauseGameButton.grid(row=13,column=offset2,sticky=N + S + E)
        # END END GAME AND PAUSE GAME BUTTONS -----------------------------------------------------------------------------------------------------
        
        # LOAD GAME OR PLAY FIRST MOVE -------------------------------------------------------------------------------------------------------------
        if loadGame == True:
            self.__loadGame(gameDetails)
        else:
            playerTiles = []
            for p in self.__players:
                playerTiles.append(self.__game.getPlayerTiles(p.getUserId()))
            startingPlayer, tilesToPlace, positionsToPlace = super()._getStartingPlayerAndMoves(self.__players, playerTiles)
            self.__currentPlayer = startingPlayer
            if self.__currentPlayer.getUserType() == "Computer":
                self.__executeComputerTurn()
            else:
                self.__minimumTilesToPlace = len(tilesToPlace)
        # END LOAD GAME OR PLAY FIRST MOVE ---------------------------------------------------------------------------------------------------------

        if self.__currentPlayer.getUserType() == "Computer":
            self.__executeComputerTurn() 

    # END INIT -------------------------------------------------------------------------------------------------------------------------------------

    # GET ------------------------------------------------------------------------------------------------------------------------------------------ 
    def __getTileImage(self,tile):
        try:
            open(f"images/{tile}.png")
            image = Image.open(f"images/{tile}.png")
            image = image.resize((20,20), Image.ANTIALIAS)
            image = ImageTk.PhotoImage(image)
            return image
        except FileNotFoundError:
            return None
    # END GET --------------------------------------------------------------------------------------------------------------------------------------

    # BUTTON-RELATED METHODS --------------------------------------------------------------------------------------------------------------------------------
    def __createButton(self, parent, column, row, text, image, command):
        button = tk.Button(parent, text=text, image=image, command=command)
        button.grid(column=column, row=row, sticky=N + S + E + W)
        return button
    
    def __clearPlayerTileColours(self):
        for pos in range(len(self.__playerButtons)):
            self.__playerButtons[pos].config(background=self.__DEFAULT_BUTTON_COLOR)

    def __setBoardButton(self, col, row, t):
        try:
            if t == GameGui.__EMPTY:
                imageToUse = self.__getTileImage("empty")
            elif t == GameGui.__CENTRE:
                imageToUse = self.__getTileImage("centre")
            else:
                imageToUse = self.__getTileImage(t)
            self.__boardButtons[row][col].config(text=t, image=imageToUse)
            self.__boardButtons[row][col].image = imageToUse
        except:
            pass

    def __setPlayerButton(self, pos, t):
        try:
            imageToUse = self.__getTileImage(t)
            if imageToUse == None:
                imageToUse = self.__getTileImage("empty")
        except:
            imageToUse = self.__getTileImage("empty")
        try:
            self.__playerButtons[pos].config(text=t, image=imageToUse)
            self.__playerButtons[pos].image = imageToUse
        except:
            pass

    def __setPlayerHand(self):
        for pos in range(len(self.__playerButtons)):
            self.__setPlayerButton(pos, self.__playerTiles[pos])

    def __returnTileToPlayerHand(self,col,row):
        tileVal = self.__boardButtons[row][col].cget('text')
        if (col,row) == self.__centre:
            self.__setBoardButton(col,row,GameGui.__CENTRE)
        else:
            self.__setBoardButton(col,row,GameGui.__EMPTY)
        for pos in range(len(self.__playerButtons)):
            if self.__playerTiles[pos] == tileVal and self.__playerButtons[pos].cget('text') == GameGui.__EMPTY:
                self.__setPlayerButton(pos, tileVal)
                break
    
    def __reverseMovesAndResetTileValsAndPositions(self):
        self.__currentTileVal = GameGui.__EMPTY
        for pos in self.__usedTilePositions:
            r = pos[1]
            c = pos[0]
            self.__returnTileToPlayerHand(c,r)
        self.__usedTileVals = []
        self.__usedTilePositions = []
        self.__tilesSelected = []
        self.__usedPlayerTilePos = None

    def __updatePlayerTilesAndButtons(self):
        newPlayerTiles = self.__game.getPlayerTiles(self.__currentPlayer.getUserId())
        for i in range(len(self.__playerButtons)):
            if i >= len(newPlayerTiles):
                self.__setPlayerButton(i, GameGui.__EMPTY)
            else:
                self.__setPlayerButton(i, newPlayerTiles[i])
        self.__playerTiles = newPlayerTiles.copy()
    # END BUTTON-RELATED METHODS ----------------------------------------------------------------------------------------------------------------------------

    # UPDATE SCORES AND CURRENT PLAYER ---------------------------------------------------------------------------------------------------------------------
    def __updateScoresAndCurrentPlayer(self):
        self.__playerScores[self.__players.index(self.__currentPlayer)].config(text=self.__currentPlayer.getUserName() + ": " + str(self.__game.getPlayerScore(self.__currentPlayer.getUserId())))
        self.__currentPlayer = super()._getNextPlayer(self.__players, self.__currentPlayer)
        self.__currentPlayerLabel.config(text="Current Player: " + self.__currentPlayer.getUserName())
        self.__tilesLeftLabel.config(text="Tiles Left: " + str(self.__game.getNumberOfTilesRemaining()))
    # END UPDATE SCORES AND CURRENT PLAYER -----------------------------------------------------------------------------------------------------------------

    # BUTTON COMMANDS ------------------------------------------------------------------------------------------------------------------------------
    
    def __hintButtonSelected(self):
        if self.__currentPlayer.getUserId() == self.__userId:
            self.__reverseMovesAndResetTileValsAndPositions()
            if self.__hintSelected:
                self.__hintSelected = False
                self.__hintButton.config(background=self.__DEFAULT_BUTTON_COLOR)
                if len(self.__hintTiles) != 0:
                    for pos in range(len(self.__hintPositions)):
                        row = self.__hintPositions[pos][1]
                        col = self.__hintPositions[pos][0]
                        if (col,row) == self.__centre:
                            self.__setBoardButton(col,row,GameGui.__CENTRE)
                        else:
                            self.__setBoardButton(col,row,GameGui.__EMPTY)
                        self.__boardButtons[row][col].config(background=self.__DEFAULT_BUTTON_COLOR)
                self.__hintTiles = []
                self.__hintPositions = []
            else:
                self.__hintSelected = True
                self.__hintButton.config(background="lawngreen")
                playerTiles = self.__game.getPlayerTiles(self.__currentPlayer.getUserId())
                tiles, positions = self.__game.getSuggestedMove(self.__game.getBoard(),playerTiles,3)
                if tiles == None:
                    messagebox.showinfo("showinfo", "No move available. You should replace your tiles.")
                    self.__hintSelected = False
                    self.__hintButton.config(background=self.__DEFAULT_BUTTON_COLOR)
                else:
                    for pos in range(len(positions)):
                        row = positions[pos][1]
                        col = positions[pos][0]
                        self.__setBoardButton(col,row,tiles[pos])
                        self.__boardButtons[row][col].config(background="lawngreen")
                    self.__hintTiles = tiles
                    self.__hintPositions = positions

    # Return Tiles Button Selected
    def __returnTiles(self):
        if self.__currentPlayer.getUserId() == self.__userId and self.__hintSelected == False:
            self.__reverseMovesAndResetTileValsAndPositions()
            self.__clearPlayerTileColours()

    # Replace Tiles Button Selected
    def __replaceTilesButtonSelected(self):
        if self.__currentPlayer.getUserId() == self.__userId and self.__hintSelected == False:
            self.__replaceTiles = not self.__replaceTiles
            if self.__replaceTiles == True:
                self.__replaceTilesButton.config(background="lawngreen")
            else:
                self.__replaceTilesButton.config(background=self.__DEFAULT_BUTTON_COLOR)

    # Board Button Selected
    def __placeTileTemp(self, col, row):
        if self.__currentPlayer.getUserId() == self.__userId and self.__hintSelected == False:

            if (col,row) in self.__usedTilePositions:
                tempUsedTileVals = self.__usedTileVals.copy()
                tempUsedTilePositions = self.__usedTilePositions.copy()
                index = tempUsedTilePositions.index((col,row))
                tempUsedTileVals.pop(index)
                tempUsedTilePositions.pop(index)
                if self.__game.isAddingTilesValid(tempUsedTileVals, tempUsedTilePositions) or len(tempUsedTileVals) == 0:
                    self.__returnTileToPlayerHand(col,row)
                    self.__usedTileVals.pop(index)
                    self.__usedTilePositions.pop(index)
                else:
                    messagebox.showerror("showerror", "Invalid Move")

            elif self.__currentTileVal != GameGui.__EMPTY:

                # Check move is valid
                tempTileVals = self.__usedTileVals.copy()
                tempTileVals.append(self.__currentTileVal)
                tempTilePositions = self.__usedTilePositions.copy()
                tempTilePositions.append((col,row))
                if not self.__game.isAddingTilesValid(tempTileVals, tempTilePositions):
                    messagebox.showerror("showerror", "Invalid Move")
                    return
                # End check move is valid

                # Makes sure existing tiles are not overwritten
                if self.__boardButtons[row][col].cget('text') in [GameGui.__EMPTY, GameGui.__CENTRE]: 

                    self.__setBoardButton(col,row,self.__currentTileVal)
                    self.__setPlayerButton(self.__usedPlayerTilePos, GameGui.__EMPTY)

                    self.__usedTileVals.append(self.__currentTileVal)
                    self.__usedTilePositions.append((col,row))
                    self.__currentTileVal = GameGui.__EMPTY
                    self.__clearPlayerTileColours()
                    self.__tilesSelected = []
                    self.__usedPlayerTilePos = None 

    # Player Tile Selected
    def __playerTileSelected(self, pos):
        if self.__currentPlayer.getUserId() == self.__userId:
            if self.__hintSelected == False:
                if self.__playerTiles[pos] != GameGui.__EMPTY:
                    if self.__playerTiles[pos] not in self.__tilesSelected and self.__playerButtons[pos].cget('text') != GameGui.__EMPTY:
                        self.__tilesSelected.append(self.__playerTiles[pos])
                        self.__usedPlayerTilePos = pos
                        self.__playerButtons[pos].config(background="lawngreen")
                    else:
                        if self.__playerTiles[pos] in self.__tilesSelected:
                            self.__tilesSelected.remove(self.__playerTiles[pos])
                            self.__usedPlayerTilePos = None
                            self.__playerButtons[pos].config(background=self.__DEFAULT_BUTTON_COLOR)
                    if self.__playerTiles[pos] not in self.__usedTileVals:
                        self.__currentTileVal = self.__playerTiles[pos]
            else:
                messagebox.showerror("showerror", "You cannot select tiles when a hint is selected.")

    # Finish Turn Button Selected
    def __finishTurn(self):
        if self.__currentPlayer.getUserId() == self.__userId:
            
            if self.__hintSelected == False:

                error = False

                # tiles are replaced
                if self.__replaceTiles == True and len(self.__tilesSelected) != 0:
                    if len(self.__tilesSelected) > self.__game.getNumberOfTilesRemaining():
                        messagebox.showerror("showerror", "You cannot replace more tiles than are left in the bag.")
                        error = True
                    elif self.__minimumTilesToPlace > 1:
                        messagebox.showerror("showerror", "You cannot replace tiles on your first turn. Please place the longest string of tiles you have on the board.")
                        error = True
                    else:
                        self.__game.replacePlayerHand(self.__currentPlayer.getUserId(), self.__tilesSelected)
                    self.__updatePlayerTilesAndButtons()
                    self.__replaceTiles = False
                    self.__replaceTilesButton.config(background=self.__DEFAULT_BUTTON_COLOR)
                    self.__reverseMovesAndResetTileValsAndPositions()

                # tiles are placed
                elif len(self.__usedTileVals) != 0:

                    if len(self.__usedTileVals) < self.__minimumTilesToPlace:
                        messagebox.showerror("showerror", "You must place the longest string of tiles you have on the board.")
                        self.__reverseMovesAndResetTileValsAndPositions()
                        error = True
                    else:
                        if self.__game.isAddingTilesValid(self.__usedTileVals, self.__usedTilePositions):
                            qwirkle = self.__game.addTilesAndChangeUserScoreAndGetIfQwirkle(self.__currentPlayer.getUserId(), self.__usedTileVals, self.__usedTilePositions)
                            if qwirkle == True:
                                messagebox.showinfo("showinfo", "Qwirkle!")
                            self.__updatePlayerTilesAndButtons()
                        else:
                            print("Invalid Move")
                            messagebox.showerror("showerror", "Invalid Move")
                            self.__reverseMovesAndResetTileValsAndPositions()
                            error = True

                        # minimumTilesToPlace only relevant for first move
                        if self.__minimumTilesToPlace > 1:
                            self.__minimumTilesToPlace = 1
                else:
                    print("You must select at least one tile")
                    messagebox.showerror("showerror", "Use at least one tile")
                    error = True
                
                if self.__game.isGameFinished():
                    self.__endGame()
                self.__usedTileVals = []
                self.__usedPlayerTilePos = None
                self.__usedTilePositions = []
                self.__clearPlayerTileColours()
                
                if error == False:
                    # game is continued provided there is no error
                    self.__updateScoresAndCurrentPlayer()
                    if self.__currentPlayer.getUserType() == "Computer":
                        self.__executeComputerTurn()

            else:
                messagebox.showerror("showerror", "You cannot finish your turn when a hint is selected.")

    # END BUTTON COMMANDS --------------------------------------------------------------------------------------------------------------------------
    
    # COMPUTER TURN --------------------------------------------------------------------------------------------------------------------------------

    def __executeComputerTurn(self):
        while True and self.__game.isGameFinished() == False:

            computerHand = self.__game.getPlayerTiles(self.__currentPlayer.getUserId())

            tiles, positions = self.__currentPlayer.getMove(self.__game.getBoard(), computerHand)
            if tiles == None:
                self.__game.replacePlayerHand(self.__currentPlayer.getUserId(),[self.__game.getPlayerTiles(self.__currentPlayer.getUserId())[0]])
            else:
                qwirkle = self.__game.addTilesAndChangeUserScoreAndGetIfQwirkle(self.__currentPlayer.getUserId(), tiles, positions)
                if qwirkle == True:
                    messagebox.showinfo("showinfo", f"{self.__currentPlayer.getUserName()} got a Qwirkle!")

                for pos in range(len(tiles)):
                    row = positions[pos][1]
                    col = positions[pos][0]
                    self.__setBoardButton(col,row,tiles[pos])

                self.__minimumTilesToPlace = 1

            self.__updateScoresAndCurrentPlayer() 
            if self.__currentPlayer.getUserType() == "Human":
                break 

        if self.__game.isGameFinished():
            self.__endGame()

        if self.__game.doesPlayerHaveMove(self.__currentPlayer.getUserId()) == False:
            messagebox.showinfo("showinfo", f"{self.__currentPlayer.getUserName()} has no moves so passes their turn.")
            self.__updateScoresAndCurrentPlayer()
            if self.__currentPlayer.getUserType() == "Computer":
                self.__executeComputerTurn()
        
    # END COMPUTER TURN ---------------------------------------------------------------------------------------------------------------------------

    # END, LOAD AND PAUSE GAME ------------------------------------------------------------------------------------------------------------------------------------

    def __endGame(self):
        self.__game.saveGame(True, self.__currentPlayer.getUserId(), self.__userId)
        messagebox.showinfo("showinfo", "Game is finished")
        winningPlayerIds, highestScore = self.__game.getWinnerIdsAndHighestScore()
        winningPlayers = []
        for id in winningPlayerIds:
            winningPlayers.append(super()._getPlayerById(id, self.__players))
        for w in winningPlayers:
            messagebox.showinfo("showinfo", f"{w.getUserName()} won with {highestScore} points")
        self.__root.destroy()

    def __endGameAbruptly(self):
        messagebox.showinfo("showinfo", "Game has ended early and has not been saved.")
        self.__root.destroy()

    def __pauseGame(self):
        self.__game.saveGame(False, self.__currentPlayer.getUserId(), self.__userId)
        messagebox.showinfo("showinfo", "Game has been paused and saved.")
        self.__root.destroy()

    def __loadGame(self, gameDetails):

        self.__game.loadGame(gameDetails)
        for p in self.__players:
            if p.getUserId() == gameDetails['currentPlayerId']:
                self.__currentPlayer = p
        self.__currentPlayerLabel.config(text="Current Player: " + self.__currentPlayer.getUserName())
        self.__playerTiles = self.__game.getPlayerTiles(self.__userId)
        self.__setPlayerHand()

        db = Database()
        db.deleteGame(gameDetails['gameId'])

        loadedBoard = self.__game.getBoard()
        empty = self.__game.getEmpty()
        for col,row in product(range(self.__game.getBoardDimensions()),range(self.__game.getBoardDimensions())):
            if loadedBoard[row][col] != empty:
                self.__setBoardButton(col,row,loadedBoard[row][col])
        for p in self.__players:
            self.__playerScores[self.__players.index(p)].config(text=p.getUserName() + ": " + str(self.__game.getPlayerScore(p.getUserId())))
        self.__tilesLeftLabel.config(text="Tiles Left: " + str(self.__game.getNumberOfTilesRemaining()))
        

    # END END, LOAD AND PAUSE GAME --------------------------------------------------------------------------------------------------------------------------------        
 
# ------------------------------------------------------------------------------------------------------------------------------------------------
# END GUI ----------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------------------------------------------------------------
# TERMINAL ----------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------------------------------------------------------------------------------------------

class GameTerminal(GameUi):

    # INIT ----------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self, players, gameName, userId):
        self.__userId = userId
        self.__players = players
        random.shuffle(self.__players)
        self.__currentPlayer = self.__players[0]
        self.__game = Game(self.__players, gameName)
        self.__minimumTilesToPlace = 1
        self.__gameLoaded = False
        
    # END INIT ------------------------------------------------------------------------------------------------------------------------------------

    # MAIN PROGRAM --------------------------------------------------------------------------------------------------------------------------------
    def run(self):

        self.__minimumTilesToPlace = 1

        if self.__game.isSelfBoardEmpty():
            playerTiles = []
            for p in self.__players:
                playerTiles.append(self.__game.getPlayerTiles(p.getUserId()))
            startingPlayer, tilesToPlace, positionsToPlace = super()._getStartingPlayerAndMoves(self.__players, playerTiles)
            if self.__gameLoaded == False:
                if startingPlayer.getUserType() == "Computer":
                    self.__currentPlayer = startingPlayer
                    self.__executeComputerTurn()
                else:
                    self.__minimumTilesToPlace = len(tilesToPlace)
            else:
                self.__minimumTilesToPlace = len(tilesToPlace)

        displayEndGameInfo = True
        while not self.__game.isGameFinished():

            while self.__currentPlayer.getUserType() == "Computer" and not self.__game.isGameFinished():
                self.__executeComputerTurn()

            if self.__game.isGameFinished():
                break

            self.__displayGameInformation()

            gameOver = False
            # Player's turn
            if self.__game.doesPlayerHaveMove(self.__currentPlayer.getUserId()) == False:
                print(f"{self.__currentPlayer.getUserName()} has no moves so passes their turn.")
                self.__updateScoresAndCurrentPlayer()
                if self.__currentPlayer.getUserType() == "Computer":
                    self.__executeComputerTurn()

            while True:
                choice = self.__getPlaceOrSwapOrPauseOrEndOrHintChoice()
                turnFinished = True

                if choice == "E":
                    displayEndGameInfo = False
                    print("Game has ended early and has not been saved.")
                    gameOver = True

                elif choice == "P":
                    displayEndGameInfo = False
                    self.__game.saveGame(False, self.__currentPlayer.getUserId(), self.__userId)
                    print("Game has been paused and saved.")
                    gameOver = True

                elif choice == "p":
                    tileChoices, positionChoices = self.__getTilesAndPositionChoices()
                    qwirkle = self.__game.addTilesAndChangeUserScoreAndGetIfQwirkle(self.__currentPlayer.getUserId(),tileChoices, positionChoices)
                    if qwirkle == True:
                        print("QWIRKLE!!!")
                        time.sleep(3)
                    self.__minimumTilesToPlace = 1

                elif choice == "s":
                    if self.__minimumTilesToPlace > 1:
                        print("You cannot replace tiles on your first turn. Please place the longest string of tiles you have on the board.")
                        continue
                    tilesToSwap = self.__getTilesToSwap()
                    if len(tilesToSwap) > self.__game.getNumberOfTilesRemaining():
                        print("You cannot replace more tiles than are left in the bag.")
                        continue
                    self.__game.replacePlayerHand(self.__currentPlayer.getUserId(), tilesToSwap)

                elif choice == "h":
                    self.__displaySuggestedMove()
                    turnFinished = False

                if turnFinished == True:
                    break

            if gameOver == True:
                break

            self.__currentPlayer = super()._getNextPlayer(self.__players, self.__currentPlayer)
            print()

        if displayEndGameInfo == True:
            self.__displayEndGameInformation()
            self.__game.saveGame(True, self.__currentPlayer.getUserId(), self.__userId)

    # END MAIN PROGRAM ----------------------------------------------------------------------------------------------------------------------------
    
    # GET -----------------------------------------------------------------------------------------------------------------------------------------        
    def __getTilesToSwap(self):
        while True:
            tilesToSwap = set()
            choice = input("Enter the tiles you want to swap, separated by spaces (e.g. a1 c5 b2):> ")
            choice = choice.split()
            if len(choice) == 0:
                print("You must swap at least one tile. Please try again.")
                continue
            tilesValid = True
            for tile in choice:
                if self.__game.isTileInHand(self.__currentPlayer.getUserId(), tile):
                    tilesToSwap.add(tile)
                else:
                    print(f"{tile} is not in your hand. Please try again.")
                    tilesValid = False
            if tilesValid:
                return list(tilesToSwap)
    
    def __getPlaceOrSwapOrPauseOrEndOrHintChoice(self):
        while True:
            choice = input("Do you want to (p)lace some tiles, (s)wap some tiles, get a (h)int, (E)nd the game or (P)ause the game?:> ")
            if choice == 'p':
                return 'p'
            elif choice == 's':
                return 's'
            elif choice == 'h':
                return 'h'
            elif choice == 'E':
                return 'E'
            elif choice == 'P':
                return 'P'
            else:
                print("Invalid choice. Please try again.")

    def __getTilesAndPositionChoices(self):
        tileChoices = []
        positionChoices = []
        tilesChosen = 0
        boardEmpty = self.__game.isSelfBoardEmpty()
        centre = self.__game.getBoardCentre()

        while tilesChosen < self.__game.getTilesPerHand():
            if boardEmpty:
                print(f"You must place at least one tile in the centre of the board ({centre[0]+1},{centre[1]+1}).")
            
            choice = input("Do you want to (p)lace a tile or (e)nd your turn or (r)eturn tiles to hand?:> ")

            if choice == 'p':
                tileChoices.append(self.__getTileChoice(tileChoices))
                while True:
                    positionChoice = self.__getBoardPositionChoice()
                    if positionChoice not in positionChoices:
                        positionChoices.append(positionChoice)
                        break
                    print("You have already placed a tile there. Please try again.")
                tilesChosen += 1 
                if not self.__game.isAddingTilesValid(tileChoices, positionChoices):
                    print("Invalid tile/position choices. Please enter them again.")
                    tileChoices = []
                    positionChoices = []
                    tilesChosen = 0

            elif choice == 'e':
                if tilesChosen < self.__minimumTilesToPlace:
                    print(f"You must place at least {self.__minimumTilesToPlace} tiles.")
                else:
                    if self.__game.isAddingTilesValid(tileChoices, positionChoices):
                        return tileChoices, positionChoices
                    print(f"Invalid tile/position choices. Please try again")
                    print("You will now re-select the tiles you want to place.")
                tileChoices = []
                positionChoices = []

            elif choice == "r":
                tileChoices = []
                positionChoices = []
                tilesChosen = 0
                print("You will now re-select the tiles you want to place.")
                
            else:
                print("Invalid choice. Please try again.")
            
    def __getBoardPositionChoice(self):
        while True:
            choice = input("Which position (x y) do you wish to place this tile? (e.g. 3 4):> ")
            choice = choice.split()

            if len(choice) != 2:
                print("Invalid position. Please try again.")
                continue

            else:
                try:
                    choice = (int(choice[0])-1, int(choice[1])-1)
                    if self.__game.isPositionValid(choice):
                        return choice
                except ValueError:
                    print("Please enter integers.")
                print("Invalid position. Please try again.")

    def __getTileChoice(self, tileChoices):
        while True:
            choice = input("Which tile do you want to play?:> ")
            if self.__game.isTileInHand(self.__currentPlayer.getUserId(), choice):
                if tileChoices.count(choice) + 1 <= self.__game.getPlayerTiles(self.__currentPlayer.getUserId()).count(choice):
                    return choice
                else:
                    print("You can't use that tile again.")
            else:
                print("That tile is not in your hand.")
    
    # END GET -------------------------------------------------------------------------------------------------------------------------------------

    # DISPLAY -------------------------------------------------------------------------------------------------------------------------------------
    def __displayGameInformation(self):
        print(self.__game)
        print()
        print(f"There are {self.__game.getNumberOfTilesRemaining()} tiles left in the bag.")
        print(f"It is {self.__currentPlayer.getUserName()}'s turn to play")
        self.__displayPlayerTiles()
        for player in self.__players:
            score = self.__game.getPlayerScore(player.getUserId())
            print(f"{player.getUserName()}'s score: {score}")
        print()

    def __displayPlayerTiles(self):
        tiles = self.__game.getPlayerTiles(self.__currentPlayer.getUserId())
        print(f"{self.__currentPlayer.getUserName()}'s tiles: {', '.join(tiles)}")

    def __displayEndGameInformation(self):
        print("The game is over. The final scores are:")
        for player in self.__players:
            print(f"{player.getUserName()}: {self.__game.getPlayerScore(player.getUserId())}")
        winningPlayerIds, highestScore = self.__game.getWinnerIdsAndHighestScore()
        winningPlayers = []
        for id in winningPlayerIds:
            winningPlayers.append(super()._getPlayerById(id, self.__players))
        for w in winningPlayers:
            print(f"Well done to the winner: {w.getUserName()} with {highestScore} points")

    def __displaySuggestedMove(self):
        playerTiles = self.__game.getPlayerTiles(self.__currentPlayer.getUserId())
        tiles, positions = self.__game.getSuggestedMove(self.__game.getBoard(),playerTiles,3)
        if tiles == None:
            print("No move available. You should replace your tiles.")
        else:
            print("Suggested move, with (x,y) co-ordinates:")
            for pos in range(len(positions)):
                print(f"{tiles[pos]} at position {positions[pos][0]+1} {positions[pos][1]+1}")
            print("End of suggestion.")
    # END DISPLAY ---------------------------------------------------------------------------------------------------------------------------------
    
    # COMPUTER MOVE -------------------------------------------------------------------------------------------------------------------------------
    def __executeComputerTurn(self):
        tileChoices, positionChoices = self.__currentPlayer.getMove(self.__game.getBoard(), self.__game.getPlayerTiles(self.__currentPlayer.getUserId()))
        if tileChoices == None:
            self.__game.replacePlayerHand(self.__currentPlayer.getUserId(), [self.__game.getPlayerTiles(self.__currentPlayer.getUserId())[0]])
            print(f"{self.__currentPlayer.getUserName()} swapped their tiles")
        else:
            qwirkle = self.__game.addTilesAndChangeUserScoreAndGetIfQwirkle(self.__currentPlayer.getUserId(),tileChoices, positionChoices)
            if qwirkle == True:
                print("QWIRKLE!!!")
                time.sleep(3)
            self.__minimumTilesToPlace = 1
        self.__currentPlayer = super()._getNextPlayer(self.__players, self.__currentPlayer)
        print()
    # END COMPUTER MOVE ---------------------------------------------------------------------------------------------------------------------------

    # LOAD GAME -----------------------------------------------------------------------------------------------------------------------------------

    def loadGame(self, gameDetails):
        self.__game.loadGame(gameDetails)
        for p in self.__players:
            if p.getUserId() == gameDetails['currentPlayerId']:
                self.__currentPlayer = p

        db = Database()
        db.deleteGame(gameDetails['gameId'])
        self.__gameLoaded = True
        
    # END LOAD GAME -------------------------------------------------------------------------------------------------------------------------------