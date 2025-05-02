import pygame
from ultils.prng import PRNG
from game.logic import GhostRules

class Ghost:
    def __init__(self, x, y, img_path, direction):
        self.x = x
        self.y = y
        self.speed = GhostRules.GHOST_SPEED
        self.mode = 'chase'
        self.direction = direction
        self.image = pygame.transform.scale(pygame.image.load(img_path), (30, 30))

    def set_mode(self, mode):
        self.mode = mode
        if mode == 'frightened':
            self.speed = 0.5
        else:
            self.speed = 1

    def move(self, pacman_pos, level):
        if self.mode == 'scatter':
            self.target = self.scatter_target()
        elif self.mode == 'chase':
            self.mode = pacman_pos
        elif self.mode == 'frightened':
            self.mode = self.random_move()

    def scatter_target(self):
        return (0, 0)
