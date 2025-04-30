from characters.ghost import Ghost
from ai.search_algorithms import a_star

class Blinky(Ghost):
    def __init__(self, x, y, speed=2):
        super().__init__('blinky', x, y, f'assets/ghost_images/red.png', speed)

    def move(self, pacman_pos, level):
        start = (self.x // 20, self.y // 20)
        goal = (pacman_pos[0] // 20, pacman_pos[1] // 20)
        if not (0 <= goal[0] < len(level[0]) and 0 <= goal[1] < len(level)):
            return
        path = a_star(level, start, goal)
        if path:
            next_step = path[0]
            dx = next_step[0] - start[0]
            dy = next_step[1] - start[1]

            if dx > 0:
                self.direction = 0
            elif dx < 0:
                self.direction = 1
            elif dy < 0:
                self.direction = 2
            elif dy > 0:
                self.direction = 3

            self.x = next_step[0] * 20
            self.y = next_step[1] * 20
        else:
            print("Blinky không tìm thấy đường đi")