import pygame
from ultils.prng import PRNG
from game.state import State

class Ghost:
    def __init__(self, name, x, y, img_path, direction, speed=2):
        self.x = x
        self.y = y
        self.speed = speed
        self.mode = 'chase'
        self.target = State.p
        self.direction = direction
        self.image = pygame.transform.scale(pygame.image.load(img_path), (30, 30))

    def draw(self):
        if (not)

    def set_mode(self, mode):
        self.mode = mode
        if mode == 'frightened':
            self.speed = 1
        else:
            self.speed = 2
    def move(self, pacman_pos, level):
        if self.mode == 'scatter':
            self.target = self.scatter_target()
        elif self.mode == 'chase':
            self.mode = pacman_pos
        elif self.mode == 'frightened':
            self.mode = self.random_move()

    def scatter_target(self):
        return (0, 0)

    def random_move(self):
        prng = PRNG(seed=12345)
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        index = prng.next() % len(directions)
        return directions[index]
