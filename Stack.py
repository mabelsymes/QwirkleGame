class Stack():

    def __init__(self):
        self.__stack = []

    def isStackEmpty(self):
        return len(self.__stack) == 0
    
    def push(self, item):
        self.__stack.append(item)

    def pop(self):
        if self.isStackEmpty():
            return None
        return self.__stack.pop()