from Game import Game
from User import User

class ComputerPlayer(User):

    def __init__(self, username, difficulty):
        super().__init__(username, None, "Computer", difficulty)

    def getMove(self, board, handTiles):
        return Game.getSuggestedMove(board, handTiles, self._userDifficulty)
    
    def setUserId(self, id):
        self._userId = id
    
class EasyPlayer(ComputerPlayer):

    def __init__(self):
        super().__init__("EasyComputer", 1)
    
class MediumPlayer(ComputerPlayer):

    def __init__(self):
        super().__init__("MediumComputer", 2)
    
class HardPlayer(ComputerPlayer):

    def __init__(self):
        super().__init__("HardComputer", 3)
    

    