from characters.ghost import Ghost

class Inky(Ghost):
    def __init__(self, x, y, speed=2):
        super().__init__('inky', x, y, f'assets/ghost_images/blue.png', speed)
        self.mode = 'chase'
