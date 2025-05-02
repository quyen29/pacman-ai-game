import pygame

from ai.utilities import nearestPoint, manhattanDistance
from characters.agents import Game, Actions, Directions

SCARED_TIME = 40
TIME_PENALTY = 1

class ClassicGameRules:
    def __init__(self, timeout = 30):
        self.timeout = timeout  #Thời gian tối đa để agent đưa ra quyết định, đơn vị là giây

    def newGame(self, layout, pacmanAgent, ghostAgents, quiet = False, catchExceptions = False):
        from game.state import GameState
        agents = [pacmanAgent] + ghostAgents[:layout.getNumGhosts()]
        initState = GameState()
        initState.initialize(layout, len(ghostAgents))
        game = Game(agents, self, catchExceptions = catchExceptions)
        game.state = initState  #Khởi tạo trạng thái ban đầu của toàn bộ game
        self.initialState = initState.deepCopy()
        self.quiet = quiet
        return game
    
    def win(self, state, game):
        if not self.quiet:
            print(f"Pacman thang! Score: {state.data.score}")
        game.gameOver = True

    def lose(self, state, game):
        if not self.quiet:
            print(f"Pacman thua! Score: {state.data.score}")
        game.gameOver = True

    #Kiểm tra và xử lý kết quả từ biến state(GameState) và đặt trạng thái thắng thua cho biến game(Game)
    def process(self, state, game):
        if state.isWin():
            self.win(state, game)
        if state.isLose():
            self.lose(state, game)
    
    def getProgress(self, game):
        return float(game.state.getNumFood()) / self.initialState.getNumFood
    
    def agentCrash(self, game, agentIndex):
        if agentIndex == 0:
            print("Pacman crashed")
        else:
            print("Ghost crasshed")
class PacmanRules:
    PACMAN_SPEED = 1

    #Lấy danh sách các hướng di chuyển hợp lệ
    @staticmethod
    def getLegalActions(state):
        return Actions.getPossibleActions(state.getPacmanState().configuration, state.data.layout.walls, PacmanRules.PACMAN_SPEED)
    
    #Tính toán điểm số nếu agent di chuyển đến vị trí position ở trạng thái state
    @staticmethod
    def consume(position, state):
        x, y = position
        main.pacman_x = y * 20
        main.pacman_y =  (x + 3) * 20
        pygame.draw.rect(main.screen, 'black', (main.pacman_x, main.pacman_y, 20, 20))
        main.draw_pacman()
        if state.data.food[x][y]:
            state.data.scoreChange += 10
            state.data.food = state.data.food.copy()
            state.data.food[x][y] = False
            state.data.foodEaten = position
            numFood = state.getNumFood()
            if numFood == 0 and not state.data.lose:
                state.data.scoreChange += 500
                state.data.win = True

        if position in state.getEnergizer():
            state.data.energizer.remove(position)
            state.data.energizerEaten = position
            for i in range(1, len(state.data.agentStates)):
                state.data.agentStates[i].scaredTimer = SCARED_TIME
            for i in range(0, len(state.data.eaten)):
                state.data.eaten[i] = False

    #Thực hiện di chuyển đến một hướng nào đó
    @staticmethod
    def applyAction(state, action):
        legal = PacmanRules.getLegalActions(state)
        if action not in legal:
            raise Exception("Hanh dong khong hop le")
        
        pacmanState = state.data.agentStates[0]  #Biến pacmanState tham chiếu đến state.data.agentStates[0]. Nghĩa là pacmanState thay đổi thì state.data.agentStates[0] cũng thay đổi

        vector = Actions.directionToVector(action, PacmanRules.PACMAN_SPEED)
        pacmanState.configuration = pacmanState.configuration.generateSuccessor(vector)

        next = pacmanState.configuration.getPosition()
        PacmanRules.consume(next, state)

class GhostRules:
    GHOST_SPEED = 1

    #Lấy danh sách các hướng di chuyển hợp lệ
    @staticmethod
    def getLegalActions(state, ghostIndex):
        config = state.getGhostState(ghostIndex).configuration
        ghostState = state.data.agentStates[ghostIndex]
        speed = GhostRules.GHOST_SPEED
        if ghostState.scaredTiemr > 0:
            speed /= 2
        possibleActions = Actions.getPossibleActions(config, state.data.layout.walls, speed)
        reverse = Actions.reverseDirection(config.direction)

        #Ghost bắt buộc phải di chuyển
        if Directions.STOP in possibleActions:
            possibleActions.remove(Directions.STOP)
        #Ghost không được quay đầu trừ khi ghost di chuyển đến ngõ cụt (Không còn lối đi nào khác)
        if reverse in possibleActions and len(possibleActions) > 1:
            possibleActions.remove(reverse)
        return possibleActions
    
    @staticmethod
    def applyAction(state, action, ghostIndex):
        legal = GhostRules.getLegalActions(state, ghostIndex)
        if action not in legal:
            raise Exception("Hanh dong khong hop le")
        
        ghostState = state.data.agentStates[ghostIndex]
        speed = GhostRules.GHOST_SPEED
        if ghostState.scaredTiemr > 0:
            speed /= 2
        vector = Actions.directionToVector(action, speed)
        ghostState.configuration = ghostState.configuration.generateSuccessor(vector)
        next = ghostState.configuration.getPosition()
        x, y = next
        if ghostIndex == 1:
            main.blinky_x = y * 20
            main.blinky_y = (x + 3) * 20
        elif ghostIndex == 2:
            main.pinky_x = y * 20
            main.pinky_y = (x + 3) * 20
        elif ghostIndex == 3:
            main.inky_x = y * 20
            main.inky_y = (x + 3) * 20
        elif ghostIndex == 4:
            main.clyde_x = y * 20
            main.clyde_y = (x + 3) * 20
        main.draw_ghosts()

    @staticmethod
    def decrementTimer(state, ghostIndex):
        ghostState = state.data.agentStates[ghostIndex]
        timer = ghostState.scaredTimer
        if timer == 1:
            ghostState.configuration.pos = nearestPoint(ghostState.configuration.pos)

        ghostState.scaredTimer = max(0, timer - 1)

    @staticmethod
    def checkDeath(state, agentIndex):
        pacmanPosition = state.getPacmanPosition()
        if agentIndex == 0:
            for i in range(1, len(state.data.agentStates)):
                ghostState = state.data.agentStates[i]
                ghostPosition = ghostState.configuration.getPosition()
                if GhostRules.canKill(pacmanPosition, ghostPosition):
                    GhostRules.collide(state, ghostState, i)
        else:
            ghostState = state.data.agentStates[agentIndex]
            ghostPosition = ghostState.configuration.getPosition()
            if GhostRules.canKill(pacmanPosition, ghostPosition):
                GhostRules.collide(state, ghostState, agentIndex)

    @staticmethod
    def collide(state, ghostState, agentIndex):
        if ghostState.scaredTimer > 0:
            state.data.scoreChange += ((2 ** (len(state.data.eaten) + 1)) * 100)
            GhostRules.placeGhost(state, ghostState)
            ghostState.scaredTimer = 0
            state.data.eaten[agentIndex] = True
        else:
            if not state.data.win:
                state.data.scoreChange -= 500
                state.data.lose = True

    @staticmethod
    def canKill(pacmanPosition, ghostPosition):
        if manhattanDistance(ghostPosition, pacmanPosition) <= 0.5:
            return True
        
    @staticmethod
    def placeGhost(state, ghostState):
        ghostState.configuration = ghostState.start
