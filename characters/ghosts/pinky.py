from characters.ghost import Ghost

class Pinky(Ghost):
    def __init__(self, x, y, speed=2):
        super().__init__('pinky', x, y, f'assets/ghost_images/pink.png', speed)
        self.mode = 'chase'
