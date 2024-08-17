import sqlite3
import hashlib
import pickle

class Database():

    def __init__(self):
        self.__createDatabase()

    def __createDatabase(self):

        con, cur = self.__connect()
        try: 
            # If database already exists, then return None
            cur.execute("SELECT * FROM User")
            cur.execute("SELECT * FROM Game")
            return None
        except:
            pass

        userSQL = """
        CREATE TABLE User(
        userId INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        pwdhash BLOB NOT NULL
        );"""

        gameSQL = """
        CREATE TABLE Game(
        gameId INTEGER PRIMARY KEY AUTOINCREMENT,
        gameName TEXT NOT NULL,
        dateCreated DATE NOT NULL,
        numberOfPlayers INTEGER NOT NULL,
        currentPlayerId INTEGER NOT NULL,
        playerIds BLOB NOT NULL,
        playerDifficulties BLOB NOT NULL,
        playerScores BLOB NOT NULL,
        playerTiles BLOB NOT NULL,
        winnerIds BLOB NOT NULL,
        board BLOB NOT NULL,
        tilesLeft BLOB NOT NULL,
        gameCompleted BOOLEAN NOT NULL,
        userId INTEGER NOT NULL
        );"""

        tableSQLDict = {"User": userSQL, "Game": gameSQL}
        for tableName, sql in tableSQLDict.items():
            cur.execute(sql)
        con.commit()
        con.close()

    # GET --------------------------------------------------------------------------------------------------------

    def getUserId(self, username):
        con, cur = self.__connect()
        try:
            cur.execute("SELECT userId FROM User WHERE username=?", (username,))
        except sqlite3.OperationalError:
            con.close()
            return None
        result = cur.fetchone()
        con.close()
        return result[0]

    def __getHash(self, string):
        return hashlib.sha256(string.encode()).hexdigest()
    
    def getGameDetails(self, gameId):
        con, cur = self.__connect()
        try:
            cur.execute("SELECT * FROM Game WHERE gameId=?", (gameId,))
        except sqlite3.OperationalError:
            con.close()
            return None
        result = cur.fetchone()
        toReturn = {'gameId': result[0], 'gameName': result[1], 'dateCreated': result[2], 'numberOfPlayers': result[3], 'currentPlayerId': result[4], 'playerIds': pickle.loads(result[5]), 'playerDifficulties': pickle.loads(result[6]), 'playerScores': pickle.loads(result[7]), 'playerTiles': pickle.loads(result[8]), 'winnerIds': pickle.loads(result[9]), 'board': pickle.loads(result[10]), 'tilesLeft': pickle.loads(result[11]), 'gameCompleted': result[12]}
        con.close()
        return toReturn

    def getUserNameById(self, userId):
        con, cur = self.__connect()
        cur.execute("SELECT username FROM User WHERE userId=?", (userId,))
        result = cur.fetchone()
        con.close()
        if result == None:
            return None
        return result[0]
    
    def getUserGameInfo(self, userId, gameCompleted):
        con, cur = self.__connect()
        cur.execute("SELECT gameId, gameName, dateCreated, numberOfPlayers, playerIds, playerDifficulties, playerScores, winnerIds FROM Game WHERE userId=? AND gameCompleted=?", (userId, gameCompleted))
        result = cur.fetchall()
        toReturn = []
        for pos in range(len(result)):
            toReturn.append({'gameId':result[pos][0], 'gameName':result[pos][1], 'dateCreated':result[pos][2], 'numberOfPlayers':result[pos][3], 'playerIds':pickle.loads(result[pos][4]), 'playerDifficulties':pickle.loads(result[pos][5]), 'playerScores':pickle.loads(result[pos][6]), 'winnerIds':pickle.loads(result[pos][7])})
        con.close()
        return toReturn
    
    # END GET ----------------------------------------------------------------------------------------------------`
    
    # IS TRUE / VALID ---------------------------------------------------------------------------------------------
    
    def isUsernameTaken(self, username):
        con, cur = self.__connect()
        cur.execute("SELECT * FROM User WHERE username=?", (username,))
        result = cur.fetchone()
        con.close()
        return result != None
    
    def isLoginValid(self, username, userPwd):
        con, cur = self.__connect()
        try:
            cur.execute("SELECT * FROM User WHERE username=? AND pwdhash=?", (username, self.__getHash(userPwd)))
        except sqlite3.OperationalError:
            con.close()
            return False
        result = cur.fetchone()
        con.close()
        return result != None
    
    # END IS TRUE / VALID -----------------------------------------------------------------------------------------
    
    # REGISTER ---------------------------------------------------------------------------------------------------
    
    def registerUser(self, username, userPwd):
        con, cur = self.__connect()
        cur.execute("INSERT INTO User(username,pwdhash) VALUES(?,?)", (username, self.__getHash(userPwd)))
        con.commit()
        con.close()

    # END REGISTER ------------------------------------------------------------------------------------------------
    
    # SAVE -------------------------------------------------------------------------------------------------------
    
    def saveGame(self, gameName, dateCreated, numberOfPlayers, currentPlayerId, playerIds, playerDifficulties, playerScores, playerTiles, winnerIds, board, tilesLeft, gameCompleted, userId):

        # pickle
        playerIds = pickle.dumps(playerIds)
        playerDifficulties = pickle.dumps(playerDifficulties)
        playerScores = pickle.dumps(playerScores)
        playerTiles = pickle.dumps(playerTiles)
        winnerIds = pickle.dumps(winnerIds)
        board = pickle.dumps(board)
        tilesLeft = pickle.dumps(tilesLeft)
        
        con, cur = self.__connect()
        cur.execute("INSERT INTO Game(gameName,dateCreated,numberOfPlayers,currentPlayerId,playerIds,playerDifficulties,playerScores,playerTiles,winnerIds,board,tilesLeft,gameCompleted,userId) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", (gameName, dateCreated, numberOfPlayers, currentPlayerId, playerIds, playerDifficulties, playerScores, playerTiles, winnerIds, board, tilesLeft, gameCompleted, userId))
        con.commit()
        con.close()

    # END SAVE ---------------------------------------------------------------------------------------------------
    
    # DELETE -----------------------------------------------------------------------------------------------------

    def deleteGame(self, gameId):
        con, cur = self.__connect()
        cur.execute("DELETE FROM Game WHERE gameId=?", (gameId,))
        con.commit()
        con.close()

    # END DELETE -------------------------------------------------------------------------------------------------

    def __connect(self):
        con = sqlite3.connect("Qwirkle.db")
        cur = con.cursor()
        return con, cur
    



