class User():

    __UserNumber = -1

    def __init__(self, userName, id, userType, difficulty):
        if userType == "Computer":
            self._userType = "Computer"
            self._userId = User.__UserNumber
            User.__UserNumber -= 1
        else:
            self._userType = "Human"
            self._userId = id
        self._userDifficulty = difficulty
        self._userName = userName
        
    def getUserType(self):
        return self._userType
    
    def getUserId(self):
        return self._userId
    
    def getUserName(self):
        return self._userName
    
    def getUserDifficulty(self):
        return self._userDifficulty   