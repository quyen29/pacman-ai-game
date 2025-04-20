from characters.ghost import Ghost

class Pinky(Ghost):
    def __init__(self, x, y):
        super().__init__('pinky', x, y)
        self.mode = 'chase'
