import pygame

from ai.utilities import nearestPoint, manhattanDistance
from characters.agents import Game, Actions, Directions

SCARED_TIME = 40
BONUS_TIME = 40
TIME_PENALTY = 1

class ClassicGameRules:
    def __init__(self, timeout = 20):
        self.timeout = timeout  #Thời gian tối đa để agent đưa ra quyết định, đơn vị là giây

    def newGame(self, layout, pacmanAgent, ghostAgents, quiet = False):
        from game.state import GameState
        agents = [pacmanAgent] + ghostAgents[:layout.getNumGhosts()]
        print("Khoi tao trang thai cua game")
        initState = GameState()
        initState.initialize(layout)
        print("Khoi tao game")
        game = Game(agents, self)
        game.state = initState  #Khởi tạo trạng thái ban đầu của toàn bộ game
        self.initialState = initState.deepCopy()
        self.quiet = quiet
        print("Khoi tao hoan tat")
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
        return Actions.getPossibleActions(state.getPacmanState().configuration, state.data.layout.walls, 0)
    
    #Tính toán điểm số nếu agent di chuyển đến vị trí position ở trạng thái state
    @staticmethod
    def consume(position, state):
        x, y = position
        numFood = state.getNumFood()
        if state.data.food[x][y]:
            state.data.rateScore += 10
            state.data.scoreChange += 10
            state.data.food = state.data.food.deepCopy()
            state.data.food[x][y] = False
            state.data.foodEaten = position
        if numFood == 0 and not state.data.lose:
            state.data.rateScore += 500
            state.data.win = True

        if position in state.getEnergizer():
            state.data.energizer.remove(position)
            state.data.energizerEaten = position
            state.data.scoreChange += 50
            state.data.rateScore += 50
            for i in range(1, len(state.data.agentStates)):
                state.data.agentStates[i].scaredTimer = SCARED_TIME
            for i in range(0, len(state.data.eaten)):
                state.data.eaten[i] = False

        if (240 - numFood) == 70 or (240 - numFood) == 170:
            state.data.numberOfFruit -= 1
            state.data.bonusFruit = (21, 14)
            state.data.bonusTime = BONUS_TIME

        if state.data.bonusFruit != None:
            #Trường hợp pacman ăn bonus fruit
            if position == state.data.bonusFruit and state.data.bonusTime > 0:
                state.data.rateScore += 100
                state.data.scoreChange += 100
                state.data.bonusFruit = None
                state.data.bonusTime = 0
            
            #Trường hợp bonus fruit hết thời gian xuất hiện
            if state.data.bonusTime == 1 and position != state.data.bonusFruit:
                state.data.bonusTime = 0
                state.data.bonusFruit = None

            #Giảm thời gian xuất hiện của bonus fruit sau mỗi lượt đi
            if state.data.bonusTime > 1:
                state.data.bonusFruit = (21, 14)
            state.data.bonusTime = max(0, state.data.bonusTime - 1)
            
    #Thực hiện di chuyển đến một hướng nào đó
    @staticmethod
    def applyAction(state, action):
        legal = PacmanRules.getLegalActions(state)
        if action not in legal:
            raise Exception("Hanh dong khong hop le")
        
        pacmanState = state.data.agentStates[0]  #Biến pacmanState tham chiếu đến state.data.agentStates[0]. Nghĩa là pacmanState thay đổi thì state.data.agentStates[0] cũng thay đổi

        vector = Actions.directionToVector(action)
        pacmanState.configuration = pacmanState.configuration.generateSuccessor(vector, 0)

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
        if ghostState.scaredTimer > 0:
            speed /= 2
        possibleActions = Actions.getPossibleActions(config, state.data.layout.walls, ghostIndex)
        reverse = Actions.reverseDirection(config.direction)

        ghostPosition = state.getGhostPosition(ghostIndex)
        if not ghostState.inPen or (ghostState.inPen and ghostState.scaredTime > 0):
            for action in possibleActions:
                if (ghostPosition + Actions.directionToVector(action)) in [(13, 14), (13, 15)]:
                    possibleActions.remove(action)

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
        if ghostState.scaredTimer > 0:
            speed /= 2
        vector = Actions.directionToVector(action, speed)
        ghostState.configuration = ghostState.configuration.generateSuccessor(vector, ghostIndex)

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
            countGhostEaten = 1
            for agent in state.data.eaten:
                if agent:
                    countGhostEaten += 1
            print(f"So ghost da an: {countGhostEaten}")
            state.data.rateScore += ((2 ** countGhostEaten) * 100)
            state.data.scoreChange += ((2 ** countGhostEaten) * 100)
            GhostRules.placeGhost(state, ghostState)
            ghostState.scaredTimer = 0
            state.data.eaten[agentIndex] = True
        else:
            if state.data.chance == 0:
                if not state.data.win:
                    state.data.rateScore -= 3000
                    state.data.lose = True
            else:
                if not state.data.reset:
                    state.data.rateScore -= 3000
                    state.data.chance -= 1
                    state.data.reset = True

    @staticmethod
    def canKill(pacmanPosition, ghostPosition):
        if manhattanDistance(ghostPosition, pacmanPosition) <= 0.5:
            return True
        
    @staticmethod
    def placeGhost(state, ghostState):
        ghostState.configuration = ghostState.start