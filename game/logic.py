import math

from Demos.SystemParametersInfo import new_x, new_y
from PIL.ImageColor import colormap


def is_valid_move(level, x, y):
    row = y // 20
    col = x // 20
    if 0 <= row < len(level) and 0 <= col < len(level[0]):
        invalid = [3, 4, 5, 6, 7, 8]
        return level[row][col] not in invalid
    return False

def move_character(level, x, y, direction, speed):
    dx, dy = 0, 0
    if direction == 0: # sang phải
        dx = speed
    elif direction == 1: # sang trái
        dx = -speed
    elif direction == 2: # đi lên
        dy = -speed
    elif direction == 3: # đi xuống
        dy = speed

    new_x = x + dx
    new_y = y + dy
    if is_valid_move(level, new_x, new_y):
        return new_x, new_y
    return x, y

def check_collision(pos_1, pos_2, radius=15):
    dist = math.sqrt((pos_1[0] - pos_2[0]) ** 2 + (pos_1[1] - pos_2[1]) ** 2)
    return dist < radius

def eat_dot(level, x, y):
    row = y // 20
    col = x // 20
    if 0 <= row < len(level) and 0 <= col < len(level[0]):
        if level[row][col] == 1: # dot nhỏ
            level[row][col] = 0
            return "dot", 10
        elif level[row][col] == 2: # energizer
            level[row][col] = 0
            return "energizer", 50
    return None, 0
