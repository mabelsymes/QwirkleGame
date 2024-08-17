from GameUi import GameTerminal, GameGui
from User import User
from ComputerPlayer import EasyPlayer, MediumPlayer, HardPlayer
from Database import Database
import sys
from Stack import Stack
import tkinter as tk
from tkinter import ttk, messagebox, StringVar, OptionMenu, Label, Button, Entry


class MenuUi():
    
    def _isPwdValid(self, pwd):
        if len(pwd) < 8:
            return False
        elif pwd.isalnum():
            return False
        elif pwd.islower():
            return False
        return True
    
    def _getRules():

        rules = """Welcome to Qwirkle!!!\n\n\nIn this game, there are 108 tiles in total. \nEach has one of six colours and shapes and there are three of each tile. \nYou are given 6 tiles at the start of the game. \nAfter each turn, these tiles will be replenished (unless there are no more in the bag). \nThe number of tiles left in the bag is displayed on the right.\n\nThe aim of the game is to place tiles on the board to score points. \nOn a turn, you can place tiles in a row or column, but every tile in a consecutive row/column must have the same colour/shape and there must be no duplicates.\nAlternatively, you can spend your turn replacing tiles. \nTo do this, select them (they will be highlighted in green) and select the 'Replace Tiles' button. \nAfter you have placed tiles on the board or chosen tiles to replace, select the 'Finish Turn' button. \nOn the first player's turn, they must place the longest consecutive sequence of tiles that they can.\n\nThe number of points you score after a turn is equal to the number of tiles in the rows/columns you placed the tile in.\nIf you place a tile to finish a row/column of six tiles (the maximum) then it is a Qwirkle!!! You get 6 extra points.\n\nThe game is over once a player has finished all their tiles, and that player also gets a bonus 6 points.\nThe player with the highest score wins.\n\n\nHave fun!!!"""

        return rules
    
    # DATABASE INTERACTION -------------------------------------------------------------------------------

    def _registerUser(self, database, userName, pwd):
        
        if self._isPwdValid(pwd):
            if database.isUsernameTaken(userName):
                return False,"Username already taken."
            database.registerUser(userName, pwd)
            return True,""
        
        return False,"Invalid password. Password must contain at least 8 characters, an uppercase letter, and a symbol."
    
    def _loginUser(self, database, userName, pwd):
        if database.isLoginValid(userName, pwd):
            userId = database.getUserId(userName)
            return userId
        else:
            return False
        
    def __convertPlayerIdsToPlayerNames(self, database, playerIds, playerDifficulties):

        computerDict = {1: EasyPlayer().getUserName(), 2: MediumPlayer().getUserName(), 3: HardPlayer().getUserName()}

        playerNames = []
        for pos in range(len(playerIds)):
            id = playerIds[pos]
            if id < 0:
                playerNames.append(computerDict[playerDifficulties[pos]])
            else:
                playerNames.append(database.getUserNameById(id))

        return playerNames
    
    def _getGameSummary(self, database, userGame):
        gameId, gameName, dateCreated, numberOfPlayers, playerIds, playerDifficulties, playerScores, winnerIds = userGame['gameId'], userGame['gameName'], userGame['dateCreated'], userGame['numberOfPlayers'], userGame['playerIds'], userGame['playerDifficulties'], userGame['playerScores'], userGame['winnerIds']
        
        playerNames = self.__convertPlayerIdsToPlayerNames(database, playerIds, playerDifficulties)
        winnerNames = self.__convertPlayerIdsToPlayerNames(database, winnerIds, playerDifficulties)
        
        summary = "\n--------------------------------------------\n"
        summary += "Game name: " + gameName + "\n"
        summary += "Date created: " + dateCreated + "\n"
        summary += "Number of players: " + str(numberOfPlayers) + "\n"
        summary += "Player scores:" + "\n"
        for p in range(len(playerNames)):
            summary += "--> " + playerNames[p] + ": " + str(playerScores[p]) + "\n"
        if len(winnerNames) > 0:
            summary += "Winner(s):" + "\n"
            for winner in winnerNames:
                summary += "--> " + winner + "\n"
        summary += "--------------------------------------------\n"

        return summary
    
    def _getPlayersAndGameDetailsFromPausedGame(self, gameId, database, userName, userId):

        gameDetails = database.getGameDetails(gameId)

        gamePlayers = []
        playerIds = gameDetails['playerIds']
        playerDifficulties = gameDetails['playerDifficulties']
        for pos in range(len(playerIds)):
            p = playerIds[pos]
            if p == userId:
                gamePlayers.append(User(userName, userId, "Human", None))
            else:
                if playerDifficulties[pos] == 1:
                    computerPlayer = EasyPlayer()
                elif playerDifficulties[pos] == 2:
                    computerPlayer = MediumPlayer()
                elif playerDifficulties[pos] == 3:
                    computerPlayer = HardPlayer()
                computerPlayer.setUserId(p)
                gamePlayers.append(computerPlayer)

        return gamePlayers, gameDetails['gameName'], gameDetails
    
    def _deleteGame(self, database, gameId):
        database.deleteGame(gameId)

    # END DATABASE INTERACTION ---------------------------------------------------------------------------

class MenuGui(MenuUi):

    __WINDOWDIM = "1000x700"

    def __init__(self, master):
        self.__db = Database()
        self.__root = master
        self.__userId = None
        self.__userName = ""
        self.__stack = Stack()
        self.__userNameEntry = None
        self.__userPwdEntry = None
        self.__createMainMenuPage()

    # CREATE PAGE ----------------------------------------------------------------------------------------------------

    def __createMainMenuPage(self):
        self.__stack.push('main')
        self.__clearWindow()
        self.__root.title("Qwirkle - Main Menu")
        self.__root.geometry(MenuGui.__WINDOWDIM)
        titleLabel = Label(self.__root, text="Welcome to the Qwirkle Menu!")
        titleLabel.grid(row=1, column=1, padx=50, pady=50)
        loginUserButton = Button(self.__root, text="Login", command=self.__createLoginPage)
        loginUserButton.grid(row=2, column=1, padx=50, pady=20)
        registerUserButton = Button(self.__root, text="Register", command=self.__createRegistrationPage)
        registerUserButton.grid(row=3, column=1, padx=50, pady=20)
        quitButton = Button(self.__root, text="Quit Page", command=self.__quitButtonSelected)
        quitButton.grid(row=4, column=1, padx=50, pady=20)


    def __createGameMenuPage(self):
        self.__stack.push('gameMenu')
        self.__clearWindow()
        self.__root.title("Qwirkle - Game Menu")
        self.__root.geometry(MenuGui.__WINDOWDIM)
        titleLabel = Label(self.__root, text=f"{self.__userName}'s Game Menu:")
        titleLabel.grid(row=1, column=1, padx=50, pady=50)
        startNewGameButton = Button(self.__root, text="Start New Game", command=self.__createNewGamePage)
        startNewGameButton.grid(row=2, column=1, padx=50, pady=20)
        viewFinishedGamesButton = Button(self.__root, text="View Finished Games", command=self.__createFinishedGamesPage)
        viewFinishedGamesButton.grid(row=3, column=1, padx=50, pady=20)
        viewPausedGamesButton = Button(self.__root, text="View Paused Games", command=self.__createPausedGamesPage)
        viewPausedGamesButton.grid(row=4, column=1, padx=50, pady=20)
        viewQwirkleRulesButton = Button(self.__root, text="View Qwirkle Rules", command=self.__createQwirkleRulesPage)
        viewQwirkleRulesButton.grid(row=5, column=1, padx=50, pady=20)
        quitButton = Button(self.__root, text="Quit Page", command=self.__quitButtonSelected)
        quitButton.grid(row=6, column=1, padx=50, pady=20)
    
    def __createNewGamePage(self):
        self.__stack.push('newGame')
        self.__clearWindow()
        self.__root.title("Qwirkle - New Game")
        self.__root.geometry(MenuGui.__WINDOWDIM)
        titleLabel = Label(self.__root, text=f"{self.__userName}'s New Game")
        titleLabel.grid(row=1, column=1, padx=50, pady=50)

        gameNameLabel = Label(self.__root, text="Game Name:")
        gameNameLabel.grid(row=2, column=1, padx=50, pady=20)
        gameNameEntry = Entry(self.__root)
        gameNameEntry.grid(row=2, column=2, padx=50, pady=10)

        playerTypesLabel = Label(self.__root, text="Player Types:")
        playerTypesLabel.grid(row=3, column=1, padx=50, pady=20)
        options = ["None", EasyPlayer().getUserName(), MediumPlayer().getUserName(), HardPlayer().getUserName()]
        selected1 = StringVar()
        selected1.set(options[0])
        selected2 = StringVar()
        selected2.set(options[0])
        selected3 = StringVar()
        selected3.set(options[0])
        player1 = OptionMenu( self.__root , selected1 , *options )
        player1.grid(row=4, column=1, padx=50, pady=20)
        player2 = OptionMenu( self.__root , selected2 , *options )
        player2.grid(row=5, column=1, padx=50, pady=20)
        player3 = OptionMenu( self.__root , selected3 , *options )
        player3.grid(row=6, column=1, padx=50, pady=20)

        def __createNewGame():
            playerNames = [selected1.get(), selected2.get(), selected3.get()]
            if playerNames.count("None") == 3:
                messagebox.showinfo("showinfo", "Please select at least one computer player")
                return
            gameName = gameNameEntry.get()
            if gameName == "":
                messagebox.showinfo("showinfo", "Please enter a game name")
                return
            players = []
            players.append(User(self.__userName, self.__userId, "Human", None))
            for p in playerNames:
                if p != "None":
                    if p == EasyPlayer().getUserName():
                        players.append(EasyPlayer())
                    elif p == MediumPlayer().getUserName():
                        players.append(MediumPlayer())
                    elif p == HardPlayer().getUserName():
                        players.append(HardPlayer())
            ui = GameGui(players, gameName, self.__userId, self.__root, False)
            self.__root.mainloop()
            self.__root = tk.Tk()
            self.__quitButtonSelected()
        
        button = Button( self.__root , text = "Submit" , command = __createNewGame)
        button.grid(row=7, column=1, padx=50, pady=20)
        
        quitButton = Button(self.__root, text="Quit Page", command=self.__quitButtonSelected)
        quitButton.grid(row=8, column=1, padx=50, pady=20)

    def __createQwirkleRulesPage(self):
        self.__stack.push('rules')
        self.__clearWindow()
        self.__root.title("Qwirkle - Rules")
        self.__root.geometry(MenuGui.__WINDOWDIM)
        titleLabel = Label(self.__root, text="Qwirkle Rules")
        titleLabel.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        rules = MenuUi._getRules()
        rulesLabel = Label(self.__root, text=rules)
        rulesLabel.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        quitButton = Button(self.__root, text="Quit Page", command=self.__quitButtonSelected)
        quitButton.pack(side=tk.BOTTOM,padx=10, pady=30)

    def __createFinishedGamesPage(self):
        self.__stack.push('finishedGames')
        self.__clearWindow()
        self.__root.title("Qwirkle - Finished Games")
        self.__root.geometry(MenuGui.__WINDOWDIM)
        titleLabel = Label(self.__root, text=f"{self.__userName}'s Finished Games:")
        titleLabel.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        finishedGames = self.__db.getUserGameInfo(self.__userId, 1)

        canvas = tk.Canvas(self.__root, width=500, height=500)
        canvas.pack(side=tk.LEFT, padx=100, pady=10)
        scrollbar = ttk.Scrollbar(self.__root, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.configure(yscrollcommand=scrollbar.set)
        frame = tk.Frame(canvas, width=500, height=500)
        canvas.create_window((0, 0), window=frame, anchor=tk.NW)

        count = 1
        if len(finishedGames) > 0:
            for game in finishedGames:
                gameSummary = super()._getGameSummary(self.__db, game)
                gameSummaryLabel = Label(frame, text=gameSummary)
                gameSummaryLabel.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
                count += 1
        else:
            noGamesLabel = Label(canvas, text="You have no finished games.")
            noGamesLabel.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        def update_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        frame.bind("<Configure>", update_scroll_region)
        
        quitButton = Button(self.__root, text="Quit Page", command=self.__quitButtonSelected)
        quitButton.pack(side=tk.BOTTOM,padx=10, pady=30) 
    
    def __createPausedGamesPage(self):
        self.__stack.push('pausedGames')
        self.__clearWindow()
        self.__root.title("Qwirkle - Paused Games")
        self.__root.geometry(MenuGui.__WINDOWDIM)
        titleLabel = Label(self.__root, text=f"{self.__userName}'s Paused Games:")
        titleLabel.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        pausedGames = self.__db.getUserGameInfo(self.__userId, 0)
        resumeGameButtons = [None for _ in range(len(pausedGames))]
        deleteGameButtons = [None for _ in range(len(pausedGames))]

        canvas = tk.Canvas(self.__root, width=500, height=500)
        canvas.pack(side=tk.LEFT, padx=100, pady=10)
        scrollbar = ttk.Scrollbar(self.__root, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.configure(yscrollcommand=scrollbar.set)
        frame = tk.Frame(canvas, width=500, height=500)
        canvas.create_window((0, 0), window=frame, anchor=tk.NW)
        
        pos = 0
        if len(pausedGames) > 0:
            for pos in range(len(pausedGames)):

                game = pausedGames[pos]
                gameSummary = super()._getGameSummary(self.__db, game)
                gameSummaryLabel = Label(frame, text=gameSummary)
                gameSummaryLabel.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

                b = StringVar()
                b.set("Resume Game")
                resumeCmd = lambda g=game: self.__resumeGame(g['gameId'])

                c = StringVar()
                c.set("Delete Game")
                deleteCmd = lambda g=game: self.__deleteGame(g['gameId'])

                Button(
                    frame,
                    textvariable=b,
                    command=resumeCmd,).pack(side=tk.TOP, padx=10, pady=5)

                Button(
                    frame,
                    textvariable=c,
                    command=deleteCmd,).pack(side=tk.TOP, padx=10, pady=5
                )
                
                resumeGameButtons[pos] = b
                deleteGameButtons[pos] = c
        else:
            noGamesLabel = Label(frame, text="You have no paused games.")
            noGamesLabel.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        def update_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        frame.bind("<Configure>", update_scroll_region)
        
        quitButton = Button(self.__root, text="Quit Page", command=self.__quitButtonSelected)
        quitButton.pack(side=tk.BOTTOM,padx=10, pady=30)  

    def __createLoginPage(self):
        self.__stack.push('login')
        self.__clearWindow()
        self.__root.title("Qwirkle - Login")
        self.__root.geometry(MenuGui.__WINDOWDIM)
        titleLabel = Label(self.__root, text="Login Page")
        titleLabel.grid(row=1, column=1, padx=50, pady=50)
        userNameLabel = Label(self.__root, text="Username:")
        userNameLabel.grid(row=2, column=1, padx=50, pady=20)
        self.__userNameEntry = Entry(self.__root)
        self.__userNameEntry.grid(row=2, column=2, padx=50, pady=10)
        userPwdLabel = Label(self.__root, text="Password:")
        userPwdLabel.grid(row=3, column=1, padx=50, pady=20)
        self.__userPwdEntry = Entry(self.__root)
        self.__userPwdEntry.grid(row=3, column=2, padx=50, pady=10)
        submitUserDetailsButton = Button(self.__root, text="Submit", command=self.__loginUserDetails)
        submitUserDetailsButton.grid(row=4, column=1, padx=50, pady=20)
        quitButton = Button(self.__root, text="Quit Page", command=self.__quitButtonSelected)
        quitButton.grid(row=5, column=1, padx=50, pady=20)

    def __createRegistrationPage(self):
        self.__stack.push('register')
        self.__clearWindow()
        self.__root.title("Qwirkle - Register")
        self.__root.geometry(MenuGui.__WINDOWDIM)
        titleLabel = Label(self.__root, text="Registration Page")
        titleLabel.grid(row=1, column=1, padx=50, pady=50)
        passwordInfoLabel = Label(self.__root, text="Password must contain at least 8 characters, an uppercase letter, and a symbol")
        passwordInfoLabel.grid(row=2, column=1, padx=50, pady=20)
        userNameLabel = Label(self.__root, text="Username:")
        userNameLabel.grid(row=3, column=1, padx=50, pady=20)
        self.__userNameEntry = Entry(self.__root)
        self.__userNameEntry.grid(row=3, column=2, padx=50, pady=10)
        userPwdLabel = Label(self.__root, text="Password:")
        userPwdLabel.grid(row=4, column=1, padx=50, pady=20)
        self.__userPwdEntry = Entry(self.__root)
        self.__userPwdEntry.grid(row=4, column=2, padx=50, pady=10)
        submitUserDetailsButton = Button(self.__root, text="Submit", command=self.__registerUserDetails)
        submitUserDetailsButton.grid(row=5, column=1, padx=50, pady=20)
        quitButton = Button(self.__root, text="Quit Page", command=self.__quitButtonSelected)
        quitButton.grid(row=6, column=1, padx=50, pady=20)
    
    # END CREATE PAGE -----------------------------------------------------------------------------------------------

    # GAME AND USER -------------------------------------------------------------------------------------------------
    
    def __deleteGame(self, gameId):
        super()._deleteGame(self.__db, gameId)
        messagebox.showinfo("showinfo", "Game deleted")
        self.__quitButtonSelected()
        self.__createPausedGamesPage()
    
    def __resumeGame(self, gameId):
        gamePlayers, gameName, gameDetails = super()._getPlayersAndGameDetailsFromPausedGame(gameId, self.__db, self.__userName, self.__userId)
        ui = GameGui(gamePlayers, gameName, self.__userId, self.__root, True, gameDetails)
        self.__root.mainloop()
        self.__root = tk.Tk()
        self.__stack.pop()
        self.__createPausedGamesPage()

    def __loginUserDetails(self):
        userName = self.__userNameEntry.get()
        pwd = self.__userPwdEntry.get()
        userId = super()._loginUser(self.__db, userName, pwd)
        if userId != False:
            self.__userId = userId
            self.__userName = userName
            self.__createGameMenuPage()
        else:
            messagebox.showinfo("showinfo", "Invalid login details")

    def __registerUserDetails(self):
        userName = self.__userNameEntry.get()
        pwd = self.__userPwdEntry.get()
        valid, error = super()._registerUser(self.__db, userName, pwd)
        if valid:
            messagebox.showinfo("showinfo", "Registration successful")
        else:
            messagebox.showinfo("showinfo", f"Registration failed: {error}")

    # END GAME AND USER ----------------------------------------------------------------------------------------------

    # TK WINDOW ------------------------------------------------------------------------------------------------------
    
    def __quitButtonSelected(self):
        pageDict = {'main': self.__createMainMenuPage, 'gameMenu': self.__createGameMenuPage, 'login': self.__createLoginPage, 'register': self.__createRegistrationPage, 'newGame':self.__createNewGamePage, 'finishedGames':self.__createFinishedGamesPage, 'pausedGames':self.__createPausedGamesPage, 'rules':self.__createQwirkleRulesPage}
        current = self.__stack.pop()
        prev = self.__stack.pop()
        if prev != None:
            pageDict[prev]()
        else:
            sys.exit()

    def __clearWindow(self):
        for widget in self.__root.winfo_children():
            widget.destroy()

    # END TK WINDOW -------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------------------------
# END GUI -----------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------------------------
# TERMINAL ----------------------------------------------------------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------
    
class MenuTerminal(MenuUi):

    def __init__(self):
        self.__db = Database()
    
    # RUN ------------------------------------------------------------------------------------------------

    def run(self):
        self.__userId = None
        self.__userName = ""
        while True:
            self.__displayMenu()
            choice = self.__getMenuChoice()
            if choice == 1:
                self.__loginUser()
            elif choice == 2:
                self.__registerUser()
            elif choice == 3:
                self.__quit()
            else:
                print("Inavlid choice")

    def __runGameMenu(self):
        while True:
            self.__displayGameMenu()
            choice = self.__getGameMenuChoice()
            if choice == 1:
                self.__runCreateGameMenu()
            elif choice == 2:
                self.__runFinishedGameMenu()
            elif choice == 3:
                self.__runPausedGameMenu()
            elif choice == 4:
                self.__runRulesPage()
            elif choice == 5:
                self.run()
            elif choice == None:
                break

    def __runCreateGameMenu(self):
        gamePlayers = []
        gamePlayers.append(User(self.__userName, self.__userId, "Human", None))
        numberOfPlayers = self.__getNumberOfPlayersChoice()
        if numberOfPlayers == None:
            return
        for i in range(numberOfPlayers):
            computerDifficulty = self.__getComputerPlayerDifficultyChoice()
            if computerDifficulty == None:
                return
            if computerDifficulty == 1:
                gamePlayers.append(EasyPlayer())
            elif computerDifficulty == 2:
                gamePlayers.append(MediumPlayer())
            elif computerDifficulty == 3:
                gamePlayers.append(HardPlayer())
        for player in gamePlayers:
            print(player.getUserName())
        while True:
            gameName = input("Enter the name of the game:> ")
            if len(gameName) > 0:
                break
            print("Please enter a game name.")
        ui = GameTerminal(gamePlayers, gameName, self.__userId)
        ui.run()

    def __runFinishedGameMenu(self):
        print()
        print("This is the finished game menu")
        finishedGames = self.__db.getUserGameInfo(self.__userId, 1)
        if len(finishedGames) > 0:
            for p in finishedGames:
                self.__displayGameInformation(p)
        else:
            print("No finished games.")

    def __runPausedGameMenu(self):
        print()
        print("This is the paused game menu")
        while True:
            num = 0
            runGame = False
            pausedGames = self.__db.getUserGameInfo(self.__userId, 0)
            if len(pausedGames) > 0:
                count = 1
                print()
                for p in pausedGames:
                    print(f"Game {count}:", end="")
                    self.__displayGameInformation(p)
                    count += 1
                while True:
                    choice = input("Do you want to (r)esume a game, (d)elete a game, or 'quit'?:> ")
                    if self.__checkIfUserQuit(choice) == True:
                        return
                    if choice == 'r':
                        num = input("Enter the number of the game you want to resume (1 is the top game):> ")
                        num = self.__checkChoiceIsIntegerInRange(num, 1, len(pausedGames)+1)
                        if num != None:
                            runGame = True
                            break
                        else:
                            print("Inavlid number.")
                    elif choice == 'd':
                        num = input("Enter the number of the game you want to delete (1 is the top game):> ")
                        num = self.__checkChoiceIsIntegerInRange(num, 1, len(pausedGames)+1)
                        if num != None:
                            super()._deleteGame(self.__db, pausedGames[num-1]['gameId'])
                            print(f"Game {num} has been deleted.")
                            break
                        else:
                            print("Invalid number")
                if runGame == True:
                    gameId = pausedGames[num-1]['gameId']
                    self.__runLoadedGame(gameId)
            else:
                print("No paused games.")
                return

    def __runLoadedGame(self, gameId):

        gamePlayers, gameName, gameDetails = super()._getPlayersAndGameDetailsFromPausedGame(gameId, self.__db, self.__userName, self.__userId)
        ui = GameTerminal(gamePlayers, gameName, self.__userId)
        ui.loadGame(gameDetails)
        ui.run()

    def __runRulesPage(self):
        print()
        print(MenuUi._getRules())
        input("Press enter to continue:> ")

    # END RUN --------------------------------------------------------------------------------------------

    # CHECK ----------------------------------------------------------------------------------------------

    def __checkIfUserQuit(self, choice):
        if choice == 'quit':
            return True
        return False
    
    def __quit(self):
        sys.exit(0)
    
    # END CHECK ------------------------------------------------------------------------------------------
    
    # GET ------------------------------------------------------------------------------------------------
            
    def __getUserName(self):
        choice = input("Enter your username:> ")
        if self.__checkIfUserQuit(choice) == True:
            return None
        return choice
    
    def __getPwd(self):
        while True:
            pwd = input("Enter your password (which must contain at least 8 characters, an uppercase letter, and a symbol):> ")
            if self.__checkIfUserQuit(pwd) == True:
                return None
            if super()._isPwdValid(pwd) == True:
                return pwd
            print("Invalid password.")
            
    def __getMenuChoice(self):
        while True:
            choice = input("Enter your choice (1,2,3):> ")
            choice = self.__checkChoiceIsIntegerInRange(choice, 1, 4)
            if choice != None:
                return choice

    def __getGameMenuChoice(self):
        while True:
            choice = input("Enter your choice (1,2,3,4,5):> ")
            if self.__checkIfUserQuit(choice) == True:
                return None
            choice = self.__checkChoiceIsIntegerInRange(choice, 1, 6)
            if choice != None:
                return choice

    def __getNumberOfPlayersChoice(self):
        while True:
            choice = input("Enter how many computer players you wish to play (1-3):> ")
            if self.__checkIfUserQuit(choice) == True:
                return None
            choice = self.__checkChoiceIsIntegerInRange(choice, 1, 4)
            if choice != None:
                return choice 

    def __getComputerPlayerDifficultyChoice(self):
        while True:
            print("Choose the difficulty of the computer player:")
            print("1. Easy")
            print("2. Medium")
            print("3. Hard")
            choice = input("Enter the difficulty of the computer player (1-3):> ")
            if self.__checkIfUserQuit(choice) == True:
                return None
            choice = self.__checkChoiceIsIntegerInRange(choice, 1, 4)
            if choice != None:
                return choice

    def __checkChoiceIsIntegerInRange(self, choice, lowerBound, upperBound):
        try:
            choice = int(choice)
            if choice in range(lowerBound, upperBound):
                return choice
            else:
                print(f"Please enter an integer between {lowerBound} and {upperBound-1}.")
        except ValueError:
            print("Please enter an integer")
        return None
          
    
    # END GET --------------------------------------------------------------------------------------------
            
    # DISPLAY --------------------------------------------------------------------------------------------
    
    def __displayMenu(self):
        print()
        print("Welcome to Qwirkle!")
        print("1. Log in")
        print("2. Register")
        print("3. Quit Qwirkle")
        print("If you ever want to quit the menu you are in, enter 'quit'.")
        print()

    def __displayGameMenu(self):
        print()
        print("1. Start a new game")
        print("2. View finished games")
        print("3. View paused games")
        print("4. Read Qwirkle rules")
        print("5. Log out")
        print("If you ever want to quit the menu you are in, enter 'quit'.")

    def __displayGameInformation(self, userGame):
        print(super()._getGameSummary(self.__db, userGame))


    # END DISPLAY ----------------------------------------------------------------------------------------
    
    # DATABASE METHODS -------------------------------------------------------------------------------
    def __registerUser(self):
        while True:
            userName = self.__getUserName()
            if userName == None:
                return
            pwd = self.__getPwd()
            if pwd == None:
                return
            
            valid, error = super()._registerUser(self.__db, userName, pwd)
            if valid:
                print("Registration successful!")
                break
            else:
                print("Registration unsuccessful.")
                print(error)
         
    def __loginUser(self):
        while True:
            userName = self.__getUserName()
            if userName == None:
                return
            pwd = self.__getPwd()
            if pwd == None:
                return
            result =  super()._loginUser(self.__db, userName, pwd)
            if result == False:
                print("Invalid username or password, please try again.")
                continue
            self.__userId = result
            self.__userName = userName
            print("Login successful!")
            break
        self.__runGameMenu()

    # END DATABASE METHODS ---------------------------------------------------------------------------

        
    

    
    

    