class State:
    def __init__(self):
        self.pacman_pos = (14 * 20, 27 * 20)
        self.ghosts_pos = {
            "blinky": (14 * 20, 15 * 20),
            "pinky": (14 * 20, 18 * 20),
            "inky": (12 * 20, 18 * 20),
            "clyde": (16 * 20, 18 * 20)
        }
        self.lives = 3
        self.score = 0
        self.energizer = False

    def update_pacman_pos(self, new_x, new_y):
        self.pacman_pos = (new_x, new_y)

    def update_ghost_pos(self, name, new_x, new_y):
        if name in self.ghosts_pos:
            self.ghosts_pos[name] = (new_x, new_y)

    def activate_energizer(self):
        self.energizer = True

    def deactivate_energizer(self):
        self.energizer = False

    def lose_life(self):
        self.lives -= 1
        if self.lives == 0:
            print("Game Over!")
            