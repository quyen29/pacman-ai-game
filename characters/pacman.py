import pygame.transform


class Pacman:
    def __init__(self, x, y, speed=2):
        self.x = x
        self.y = y
        self.speed =speed
        self.direction = 0
        self.images = [pygame.transform.scale(pygame.image.load(f'assets/pacman_images/{i}.png'), (30, 20)) for i in range(1, 5)]

    def move(self):
        pass

    def update(self):
        pass

    def reset(self):
        pass
