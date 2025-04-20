from characters.ghost import Ghost

class Inky(Ghost):
    def __init__(self, x, y):
        super().__init__('inky', x, y)
        self.mode = 'chase'
