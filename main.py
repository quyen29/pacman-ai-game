import pygame
import copy
import math
import threading

from characters.agents import Layout, gameMaze
from game.board import boards


from characters.pacman import AlphaBetaAgent
from characters.ghosts.blinky import Blinky
from characters.ghosts.pinky import Pinky
from characters.ghosts.inky import Inky
from characters.ghosts.clyde import Clyde
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

#Index = 0
pacman_x = 14 * TILE_SIZE
pacman_y= 27 * TILE_SIZE
direction = 0

#Index = 1
blinky_x = 14 * TILE_SIZE
blinky_y = 15 * TILE_SIZE
blinky_direction = 0

#Index = 2
pinky_x = 14 * TILE_SIZE
pinky_y = 18 * TILE_SIZE
pinky_direction = 0

#Index = 3
inky_x = 12 * TILE_SIZE
inky_y = 18 * TILE_SIZE
inky_direction = 0

#Index = 4
clyde_x = 16 * TILE_SIZE
clyde_y = 18 * TILE_SIZE
clyde_direction = 0

bonusFruit_x = 14 * TILE_SIZE
bonusFruit_y = 21 * TILE_SIZE
bonusFruit_img = pygame.transform.scale(pygame.image.load(f'assets/fruit.png'), (20, 20))

counter = 0
flicker = False

pacman_images = []
for i in range(1, 5):
    pacman_images.append(pygame.transform.scale(pygame.image.load(f'assets/pacman_images/{i}.png'), (30, 30)))

blinky_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/red.png'), (30, 30))
pinky_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/pink.png'), (30, 30))
inky_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/blue.png'), (30, 30))
clyde_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/orange.png'), (30, 30))
scared_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/powerup.png'), (30, 30))
dead_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/dead.png'), (30, 30))

#Sửa kích thước agent thành 20x20
# for i in range(1, 5):
#     pacman_images.append(pygame.transform.scale(pygame.image.load(f'assets/pacman_images/{i}.png'), (20, 20)))

# blinky_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/red.png'), (20, 20))
# pinky_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/pink.png'), (20, 20))
# inky_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/blue.png'), (20, 20))
# clyde_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/orange.png'), (20, 20))
# scared_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/blue.png'), (20, 20))
# dead_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/orange.png'), (20, 20))



def draw_board():
    for row in range(len(level)):
        for col in range(len(level[row])):
            x = col * TILE_SIZE
            y = (row + 3) * TILE_SIZE

            if level[row][col] == 1:  # dot nhỏ
                pygame.draw.circle(screen, 'white', (x + TILE_SIZE // 2, y + TILE_SIZE // 2), 4)
            elif level[row][col] == 2 and not flicker:  # energizer
                pygame.draw.circle(screen, 'white', (x + TILE_SIZE // 2, y + TILE_SIZE // 2), 10)

                #Sửa kích thước energizer thành 8
                # pygame.draw.circle(screen, 'white', (x + TILE_SIZE // 2, y + TILE_SIZE // 2), 8)
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
            elif level[row][col] == 10: # bonus fruit
                screen.blit(bonusFruit_img, (bonusFruit_x, bonusFruit_y))

def draw_pacman():
    screen.blit(pacman_images[counter // 5], (pacman_x, pacman_y))
    # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
    # if direction == 0:
    #     screen.blit(pacman_images[counter // 5], (pacman.x, pacman.y))
    # elif direction == 1:
    #     screen.blit(pygame.transform.flip(pacman_images[counter // 5], True, False), (pacman.x, pacman.y))
    # elif direction == 2:
    #     screen.blit(pygame.transform.rotate(pacman_images[counter // 5], 90), (pacman.x, pacman.y))
    # elif direction == 3:
    #     screen.blit(pygame.transform.rotate(pacman_images[counter // 5], 270), (pacman.x, pacman.y))

def draw_ghosts():
    screen.blit(blinky_img, (blinky_x, blinky_y))
    screen.blit(pinky_img, (pinky_x, pinky_y))
    screen.blit(inky_img, (inky_x, inky_y))
    screen.blit(clyde_img, (clyde_x, clyde_y))
    
def runGame():
    from game.logic import ClassicGameRules
    layoutText = gameMaze()
    layout = Layout(layoutText)

    pacman = AlphaBetaAgent("betterEvaluationFunction") #Điền đối tượng pacman vào đây (Đối tượng này được tạo từ abstract class Agent trong file agent.py)

    blinky = Blinky()

    pinky = Pinky()

    inky = Inky()

    clyde = Clyde()

    ghosts = [blinky, pinky, inky, clyde]

    rules = ClassicGameRules()

    game = rules.newGame(layout, pacman, ghosts)

    return game

def updatePositionAgent(game):
    global pacman_x
    global pacman_y
    global blinky_x
    global blinky_y
    global pinky_x
    global pinky_y
    global inky_x
    global inky_y
    global clyde_x
    global clyde_y
    global level
    global blinky_img
    global pinky_img
    global inky_img
    global clyde_img
    #Vẽ pacman
    pacmanState = game.state.data.agentStates[0]
    pacmanPos = pacmanState.getPosition()
    pacman_x = pacmanPos[1] * TILE_SIZE
    pacman_y = (pacmanPos[0] + 3) * TILE_SIZE
    level[pacmanPos[0]][pacmanPos[1]] = 0

    #Vẽ blinky
    blinkyState = game.state.data.agentStates[1]
    blinkyPos = blinkyState.getPosition()
    blinky_x = blinkyPos[1] * TILE_SIZE
    blinky_y = (blinkyPos[0] + 3) * TILE_SIZE

    #Vẽ pinky
    pinkyState = game.state.data.agentStates[2]
    pinkyPos = pinkyState.getPosition()
    pinky_x = pinkyPos[1] * TILE_SIZE
    pinky_y = (pinkyPos[0] + 3) * TILE_SIZE

    #Vẽ inky
    inkyState = game.state.data.agentStates[3]
    inkyPos = inkyState.getPosition()
    inky_x = inkyPos[1] * TILE_SIZE
    inky_y = (inkyPos[0] + 3) * TILE_SIZE

    #Vẽ clyde
    clydeState = game.state.data.agentStates[4]
    clydePos = clydeState.getPosition()
    clyde_x = clydePos[1] * TILE_SIZE
    clyde_y = (clydePos[0] + 3) * TILE_SIZE

    if blinkyState.scaredTimer != 0:
        blinky_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/powerup.png'), (TILE_SIZE, TILE_SIZE))
    else:
        blinky_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/red.png'), (TILE_SIZE, TILE_SIZE))

    if pinkyState.scaredTimer != 0:
        pinky_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/powerup.png'), (TILE_SIZE, TILE_SIZE))
    else:
        pinky_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/pink.png'), (TILE_SIZE, TILE_SIZE))

    if inkyState.scaredTimer != 0:
        inky_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/powerup.png'), (TILE_SIZE, TILE_SIZE))
    else:
        inky_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/blue.png'), (TILE_SIZE, TILE_SIZE))

    if clydeState.scaredTimer != 0:
        clyde_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/powerup.png'), (TILE_SIZE, TILE_SIZE))
    else:
        clyde_img = pygame.transform.scale(pygame.image.load(f'assets/ghost_images/orange.png'), (TILE_SIZE, TILE_SIZE))
    
    print(game.state.data.bonusTime)
    if game.state.data.bonusTime != 0:
        level[18][14] = 10
        
    if game.state.data.bonusTime == 0:
        level[18][14] = 0

def logicFunction(game):
    if game and not game.gameOver:
        game.run()
        updatePositionAgent(game)

def main():
    global counter
    global flicker
    run = True
    game = None
    logicThread = None
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

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    game = runGame()
            
        if game and not game.gameOver:
            if logicThread is None or not logicThread.is_alive():
                logicThread = threading.Thread(target = logicFunction, args = (game,))
                logicThread.start()

        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()