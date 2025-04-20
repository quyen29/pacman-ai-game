import pygame
import copy
import math

from game.board import boards  # boards là mảng 2D chứa các số từ 0–9 như bạn mô tả

pygame.init()

# Kích thước cửa sổ
TILE_SIZE = 20
WIDTH = 30 * TILE_SIZE
HEIGHT = 38 * TILE_SIZE

screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption("Pac-Man")
timer = pygame.time.Clock()

# Cấu hình game
fps = 60
font = pygame.font.Font('freesansbold.ttf', 20)
level = copy.deepcopy(boards)
color = 'blue'
PI = math.pi

pacman_x = 14 * TILE_SIZE
pacman_y= 27 * TILE_SIZE
direction = 0

blinky_x = 14 * TILE_SIZE
blinky_y = 15 * TILE_SIZE
blinky_direction = 0

pinky_x = 14 * TILE_SIZE
pinky_y = 18 * TILE_SIZE
pinky_direction = 0

inky_x = 12 * TILE_SIZE
inky_y = 18 * TILE_SIZE
inky_direction = 0

clyde_x = 16 * TILE_SIZE
clyde_y = 18 * TILE_SIZE
clyde_direction = 0


counter = 0
flicker = False


pacman_images = []
for i in range(1, 5):
    pacman_images.append(pygame.transform.scale(pygame.image.load(f'assets/pacman_images/{i}.png'), (30, 30)))

blinky_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/red.png'), (30, 30))
pinky_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/pink.png'), (30, 30))
inky_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/blue.png'), (30, 30))
clyde_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/orange.png'), (30, 30))
scared_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/blue.png'), (30, 30))
dead_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/orange.png'), (30, 30))


def draw_board():
    for row in range(len(level)):
        for col in range(len(level[row])):
            x = col * TILE_SIZE
            y = (row + 3) * TILE_SIZE

            if level[row][col] == 1:  # dot nhỏ
                pygame.draw.circle(screen, 'white', (x + TILE_SIZE // 2, y + TILE_SIZE // 2), 4)
            elif level[row][col] == 2 and not flicker:  # energizer
                pygame.draw.circle(screen, 'white', (x + TILE_SIZE // 2, y + TILE_SIZE // 2), 10)
            elif level[row][col] == 3:  # tường dọc
                pygame.draw.line(screen, color, (x + TILE_SIZE // 2, y), (x + TILE_SIZE // 2, y + TILE_SIZE), 3)
            elif level[row][col] == 4:  # tường ngang
                pygame.draw.line(screen, color, (x, y + TILE_SIZE // 2), (x + TILE_SIZE, y + TILE_SIZE // 2), 3)
            elif level[row][col] == 5:  # góc dưới trái
                pygame.draw.arc(screen, color, [x - TILE_SIZE * 0.4, y + TILE_SIZE * 0.5, TILE_SIZE, TILE_SIZE], 0, PI / 2, 2)
            elif level[row][col] == 6:  # góc dưới phải
                pygame.draw.arc(screen, color, [x + TILE_SIZE * 0.5, y + TILE_SIZE * 0.5, TILE_SIZE, TILE_SIZE], PI / 2, PI, 2)
            elif level[row][col] == 7:  # góc trên phải
                pygame.draw.arc(screen, color, [x + TILE_SIZE * 0.5, y - TILE_SIZE * 0.4, TILE_SIZE, TILE_SIZE], PI, 3 * PI / 2, 2)
            elif level[row][col] == 8:  # góc trên trái
                pygame.draw.arc(screen, color, [x - TILE_SIZE * 0.4, y - TILE_SIZE * 0.4, TILE_SIZE, TILE_SIZE], 3 * PI / 2, 2 * PI, 2)
            elif level[row][col] == 9:  # cửa pen
                pygame.draw.line(screen, 'white', (x, y + TILE_SIZE // 2), (x + TILE_SIZE, y + TILE_SIZE // 2), 3)

def draw_pacman():
    # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
    if direction == 0:
        screen.blit(pacman_images[counter // 5], (pacman_x, pacman_y))
    elif direction == 1:
        screen.blit(pygame.transform.flip(pacman_images[counter // 5], True, False), (pacman_x, pacman_y))
    elif direction == 2:
        screen.blit(pygame.transform.rotate(pacman_images[counter // 5], 90), (pacman_x, pacman_y))
    elif direction == 3:
        screen.blit(pygame.transform.rotate(pacman_images[counter // 5], 270), (pacman_x, pacman_y))

def draw_ghosts():
    screen.blit(blinky_img, (blinky_x, blinky_y))
    screen.blit(pinky_img, (pinky_x, pinky_y))
    screen.blit(inky_img, (inky_x, inky_y))
    screen.blit(clyde_img, (clyde_x, clyde_y))

def main():
    global counter
    global flicker
    run = True
    while run:
        timer.tick(fps)
        if counter < 19:
            counter += 1
            if counter > 5:
                flicker = False
        else:
            counter = 0
            flicker =True

        screen.fill('black')
        draw_board()
        draw_pacman()
        draw_ghosts()
        center_x = pacman_x + 15
        center_y = pacman_y+ 15

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()