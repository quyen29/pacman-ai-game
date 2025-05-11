from ai.utilities import manhattanDistance, SearchProblem
from ai.search_algorithms import pacmanBFS
from characters.agents import Agent, Directions, Actions

def scoreEvaluationFunction(currentGameState):
    return currentGameState.getScore()

def betterEvaluationFunction(currentGameState):
    pacmanPosition = currentGameState.getPacmanPosition()

    ghostPositions = currentGameState.getGhostPositions()
    ghostStates = currentGameState.getGhostStates()
    
    food = currentGameState.getFood()
    foodList = food.asList()
    bonusFruit = currentGameState.data.bonusFruit
    bonusTime = currentGameState.data.bonusTime
    score = currentGameState.data.rateScore

    problem = PositionSearchProblem(currentGameState)

    #Tránh ghost
    for ghost in range(0, len(ghostStates)):
        x, y = ghostPositions[ghost]
        problem.setGoal(f"Position,{x},{y}")
        distance = len(pacmanBFS(problem)) - 1
        if distance <= 8 and ghostStates[ghost].scaredTimer == 0:
            score -= 500
            score += distance
        elif distance <= 16 and ghostStates[ghost].scaredTimer == 0:
            score -= 300
            score += distance
        elif distance > 16 and ghostStates[ghost].scaredTimer == 0:
            score += distance

    if TARGET_ENERGIZER != None:
        if len(currentGameState.getEnergizer()) > 0:
            if TARGET_ENERGIZER not in currentGameState.getEnergizer():
                score += 100
            else:
                x, y = TARGET_ENERGIZER
                problem.setGoal(f"Position,{x},{y}")
                distanceEnergizer = len(pacmanBFS(problem)) - 1
                score -= distanceEnergizer
        else:
            score += 100

    #Ăn ghost (Dựa vào khoảng cách)
    if TARGET_GHOST != None:
        if ghostStates[TARGET_GHOST[1]].scaredTimer == 0 and currentGameState.data.eaten[TARGET_GHOST[1] + 1] == True:
            score += 100
        else:
            x, y = TARGET_GHOST[0]
            problem.setGoal(f"Position,{x},{y}")
            distanceGhostScared = len(pacmanBFS(problem)) - 1
            score -= distanceGhostScared

    #Ăn bonus fruit (Dựa vào khoảng cách)
    if bonusFruit != None and bonusTime > 0:
        if pacmanPosition == bonusFruit:
            score += 50
        else:
            x, y = bonusFruit
            problem.setGoal(f"Position,{x},{y}")
            distanceBonusFruit = len(pacmanBFS(problem)) - 1
            score -= distanceBonusFruit

    #Ăn dots
    if TARGET_FOOD != None:
        if TARGET_FOOD not in foodList:
            score += 10
        else:
            x, y = TARGET_FOOD
            problem.setGoal(f"Position,{x},{y}")
            score -= (len(pacmanBFS(problem)) - 1)

    return score


PACMAN_STAYED = []
TARGET_ENERGIZER = None
TARGET_FOOD = None
TARGET_GHOST = None

class MultiAgent(Agent):
    def __init__(self, evaluationFunction, depth):
        super().__init__(0)
        self.evaluationFunction = globals()[evaluationFunction]
        self.depth = int(depth)
        """
            - Biến depth là số bước mà pacman được giả định
            - Có nghĩa là khi biến depth bằng 1 thì pacman và các ghost chỉ thực hiện 1 lượt chơi theo thứ tự pacman đến các ghost
            - Khi biến depth bằng 2 thì pacman và các ghost thực hiện 2 lượt chơi theo thứ tự pacman đến các ghost và lặp lại
            - Nếu biến depth càng lớn thì tỉ lệ pacman tìm ra trạng thái tốt nhất càng lớn
            - Tuy nhiên nếu biến depth quá lớn thì thời gian tính toán sẽ mất nhiều thời gian
        """

class AlphaBetaAgent(MultiAgent):
    def __init__(self, evaluationFunction = "scoreEvaluationFunction", depth = "1"):
        super().__init__(evaluationFunction, depth)
    
    def getAction(self, gameState):
        global TARGET_ENERGIZER
        global TARGET_FOOD
        global TARGET_GHOST
        def maxLevel(gameState, depth, alpha, beta):
            currDepth = depth + 1  #Mỗi lần pacman di chuyển thì tăng độ sâu

            #Nếu pacman thắng hoặc thua hoặc đạt tới giưới hạn độ sâu thì trả về điểm đánh giá
            if gameState.isWin() or gameState.isLose() or currDepth == self.depth:
                rate = self.evaluationFunction(gameState)
                return rate
            
            maxValue = -999999  #Khởi tạo giá trị lớn nhất có thể, đặt giá trị của biến bằng -999999 là để có thể kiểm tra được mọi giá trị
            actions = gameState.getLegalActions(0)  #Danh sách các hành động hợp lệ của pacman
            alpha1 = alpha

            if Directions.STOP in actions:
                actions.remove(Directions.STOP)

            for action in actions:
                successor = gameState.generateSuccessor(0, action)
                maxValue = max(maxValue, minLevel(successor, currDepth, 1, alpha1, beta))  #Chọn giá trị lớn nhất
                if maxValue > beta:  #Nếu giá trị lớn nhất hiện tại lớn hơn alpha thì chắc chắn rằng các giá trị sau này đều lớn hơn alpha (Vì maxValue luôn luôn nhận giá trị lớn hơn nó) nên không cần xét các nhánh còn lại (Cắt tỉa nhánh)
                    return maxValue
                alpha1 = max(alpha1, maxValue)
            return maxValue

        def minLevel(gameState, depth, agentIndex, alpha, beta):
            minValue = 999999

            if gameState.isWin() or gameState.isLose():
                rate = self.evaluationFunction(gameState)
                return rate
            
            actions = gameState.getLegalActions(agentIndex)  #Danh sách hành động hợp lệ của ghost có index là agentIndex
            beta1 = beta  #Gán giá trị của biến beta vào biến beta1 để tránh ảnh hưởng đến giá trị ban đầu của beta

            if Directions.STOP in actions:
                actions.remove(Directions.STOP)

            #Duyệt từng hành động hợp lệ của ghost
            for action in actions:
                successor = gameState.generateSuccessor(agentIndex, action)  #Tạo trạng thái tiếp theo của toàn bộ game sau khi ghost di chuyển
                #Nếu đã đến ghost cuối cùng thì gọi tiếp hành động của pacman sau khi tất cả các ghost đều đã di chuyển
                if agentIndex == (gameState.getNumAgents() - 1):
                    minValue = min(minValue, maxLevel(successor, depth, alpha, beta1))  #Chọn giá trị nhỏ nhất 
                    if minValue < alpha:  #Nếu giá trị nhỏ nhất hiện tại nhỏ hơn alpha thì chắc chắn rằng các giá trị sau này đều nhỏ hơn alpha (Vì minValue luôn luôn nhận giá trị nhỏ hơn nó) nên không cần xét các nhánh còn lại (Cắt tỉa nhánh)
                        return minValue
                    beta1 = min(beta1, minValue)
                #Nếu không phải ghost cuối cùng thì xét hành động của ghost tiếp theo
                else:
                    minValue = min(minValue, minLevel(successor, depth, agentIndex + 1, alpha, beta1)) 
                    if minValue < alpha:
                        return minValue
                    beta1 = min(beta1, minValue)
            return minValue
        
        actions = gameState.getLegalActions(0)  #Danh sách các hướng đi hợp lệ của pacman
        currScore = -999999
        returnAction = ""
        alpha = -999999
        beta = 999999

        stateWithAction = {Directions.SOUTH: None, Directions.NORTH: None, Directions.EAST: None, Directions.WEST: None}  

        if Directions.STOP in actions:
            actions.remove(Directions.STOP)
            
        problem = PositionSearchProblem(gameState)
        #Chọn energizer
        if len(gameState.getEnergizer()) > 0:
            path = pacmanBFS(problem)
            if len(path) > 0:
                print(f"energizer: {path}")
                TARGET_ENERGIZER = path[len(path) - 1]
            else:
                TARGET_ENERGIZER = None
        else:
            TARGET_ENERGIZER = None

        #Chọn food
        problem.setGoal("Food")
        if len(gameState.getFood().asList()) > 0:
            path = pacmanBFS(problem)
            if len(path) > 0:
                print(f"Food: {path}")
                TARGET_FOOD = path[len(path) - 1]
            else:
                TARGET_FOOD = None
        else:
            TARGET_FOOD = None

        problem.setGoal("Ghost")
        ghostStates = gameState.getGhostStates()
        ghostPositions = gameState.getGhostPositions()
        scaredTime = []
        for ghost in ghostStates:
            scaredTime.append(ghost.scaredTimer)
        if len(set(scaredTime)) == 1 and scaredTime[0] == 0:
            TARGET_GHOST = None
        else:
            path = pacmanBFS(problem)
            if len(path) > 0:
                ghostRoundUp = [(int(x + 0.5), int(y + 0.5)) for (x, y) in ghostPositions]
                ghostRoundDown = [(int(x), int(y)) for (x, y) in ghostPositions]
                ghostIndex = -1
                if path[len(path) - 1] in ghostRoundUp:
                    ghostIndex = ghostRoundUp.index(path[len(path) - 1])
                if ghostIndex == -1:
                    if path[len(path) - 1] in ghostRoundDown:
                        ghostIndex = ghostRoundDown.index(path[len(path) - 1])
                if ghostIndex == -1:
                    minGhostScared = 999999
                    for ghost in range(0, len(ghostStates)):
                        if ghostStates[ghost].scaredTimer > 0:
                            distanceGhostScared = manhattanDistance(gameState.getPacmanPosition(), ghostPositions[ghost])
                            if distanceGhostScared < minGhostScared:
                                minGhostScared = distanceGhostScared
                                TARGET_GHOST = (ghostPositions[0], ghost)
                    if minGhostScared == 999999:
                        TARGET_GHOST = None
                else:
                    TARGET_GHOST = (path[len(path) - 1], ghostIndex)
            else:
                TARGET_GHOST = None

        print(f"Energizer: {TARGET_ENERGIZER}\nFood: {TARGET_FOOD}\nGhost: {TARGET_GHOST}\n")

        if len(PACMAN_STAYED) > 6:
            currPosition = PACMAN_STAYED[-6:]
            if len(set(currPosition)) == 2:
                print("LOOP")
                currDirection = gameState.getPacmanState().getDirection()
                if currDirection in actions:
                    nextState = gameState.generateSuccessor(0, currDirection)
                    PACMAN_STAYED.append(nextState.getPacmanPosition())
                    return currDirection
                else:
                    reverseAction = Actions.reverseDirection(currDirection)
                    actions.remove(reverseAction)
                    if len(actions) == 0:
                        return reverseAction
                    else:
                        return actions[0]

        for action in actions:
            nextState = gameState.generateSuccessor(0, action)  #Tạo trạng thái tiếp theo của toàn bộ game sau khi pacman thực hiện hành động action
            score = minLevel(nextState, 0, 1, alpha, beta)  #Sau khi pacman hành động phải xem ghost hành động như thế nào
            stateWithAction[action] = nextState

            print(f"Hanh dong: {action}, Diem: {score}")
            if score > currScore:
                returnAction = action
                currScore = score
            if score > beta:
                PACMAN_STAYED.append(stateWithAction[returnAction].getPacmanPosition())
                return returnAction
            alpha = max(alpha, score)
        PACMAN_STAYED.append(stateWithAction[returnAction].getPacmanPosition())
        return returnAction
    
class PositionSearchProblem(SearchProblem):
    def __init__(self, gameState, goal = "Energizer"):
        self.gameState = gameState
        self.walls = gameState.getWalls()
        self.startState = gameState.getPacmanPosition()
        self.goal = goal

    def setGoal(self, goal):
        self.goal = goal

    def getStartState(self):
        return self.startState
    
    def isGoalState(self, state):
        if self.goal == "Food":
            return state in self.gameState.getFood().asList()
        elif self.goal == "Energizer":
            return state in self.gameState.getEnergizer()
        elif self.goal == "Ghost":
            ghostStates = self.gameState.getGhostStates()
            for ghost in ghostStates:
                x, y = ghost.getPosition()
                positionUp = (int(x + 0.5), int(y + 0.5))
                positionDown = (int(x), int(y))
                if (state == positionUp and ghost.scaredTimer > 0) or (state == positionDown and ghost.scaredTimer > 0):
                    return True
            return False
        elif "Position" in self.goal:
            parts = self.goal.split(",")
            x = int(float(parts[1]))
            y = int(float(parts[2]))
            position = (x, y)
            if state == position:
                return True
            else:
                return False
    
    def getSuccessors(self, state):
        successors = []
        for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            x, y = state
            dx, dy = Actions.directionToVector(action)
            nextx = int(x + dx) 
            nexty = int(y + dy)
            
            if nexty > 29:
                nexty = 0
            elif nexty < 0:
                nexty = 29

            if not self.walls[nextx][nexty]:
                nextState = (nextx, nexty)
                cost = 1
                successors.append((nextState, action, cost))
        return successors
    
    def getCostOfActions(self, actions):
        return 1