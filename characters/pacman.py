from ai.utilities import manhattanDistance
from characters.agents import Agent, Directions, Actions

def scoreEvaluationFunction(currentGameState):
    return currentGameState.getScore()

def betterEvaluationFunction(currentGameState):
    pacmanPosition = currentGameState.getPacmanPosition()

    ghostPositions = currentGameState.getGhostPositions()
    ghostStates = currentGameState.getGhostStates()

    layout = currentGameState.data.layout
    food = currentGameState.getFood()
    foodList = food.asList()
    bonusFruit = currentGameState.data.bonusFruit
    bonusTime = currentGameState.data.bonusTime
    score = currentGameState.data.rateScore

    #Tránh ghost
    for ghost in ghostStates:
        distance = manhattanDistance(ghost.getPosition(), pacmanPosition)
        if distance <= 8 and ghost.scaredTimer == 0:
            score -= 500

    #Ăn energizer
    if len(currentGameState.getEnergizer()) > 0:
        score += 100
        distanceEnergizer = manhattanDistance(pacmanPosition, TARGET_ENERGIZER)
        score -= distanceEnergizer

    #Ăn ghost (Dựa vào khoảng cách)
    if TARGET_GHOST != None:
        score += 100
        distanceGhostScared = manhattanDistance(pacmanPosition, TARGET_GHOST)
        score -= distanceGhostScared

    #Ăn bonus fruit (Dựa vào khoảng cách)
    if bonusFruit != None and bonusTime > 0:
        distanceBonusFruit = manhattanDistance(pacmanPosition, bonusFruit)
        if distanceBonusFruit < bonusTime:
            score += 50
            score -= distanceBonusFruit
    
    #Ăn dots
    if TARGET_FOOD != None:
        score -= manhattanDistance(pacmanPosition, TARGET_FOOD)

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
    def __init__(self, evaluationFunction = "scoreEvaluationFunction", depth = "2"):
        super().__init__(evaluationFunction, depth)
    
    def getAction(self, gameState):
        global TARGET_ENERGIZER
        global TARGET_FOOD
        global TARGET_GHOST
        def maxLevel(gameState, depth, alpha, beta):
            currDepth = depth + 1  #Mỗi lần pacman di chuyển thì tăng độ sâu

            #Nếu pacman thắng hoặc thua hoặc đạt tới giưới hạn độ sâu thì trả về điểm đánh giá
            if gameState.isWin() or gameState.isLose() or currDepth == self.depth:
                return self.evaluationFunction(gameState)
            
            maxValue = -999999  #Khởi tạo giá trị lớn nhất có thể, đặt giá trị của biến bằng -999999 là để có thể kiểm tra được mọi giá trị
            actions = gameState.getLegalActions(0)  #Danh sách các hành động hợp lệ của pacman
            alpha1 = alpha
            for action in actions:
                successor = gameState.generateSuccessor(0, action)
                maxValue = max(maxValue, minLevel(successor, currDepth, 1, alpha1, beta))
                if maxValue > beta:
                    return maxValue
                alpha1 = max(alpha1, maxValue)
            return maxValue

        def minLevel(gameState, depth, agentIndex, alpha, beta):
            minValue = 999999
            if gameState.isWin() or gameState.isLose():
                return self.evaluationFunction(gameState)
            actions = gameState.getLegalActions(agentIndex)  #Danh sách hành động hợp lệ của ghost có index là agentIndex
            beta1 = beta  #Gán giá trị của biến beta vào biến beta1 để tránh ảnh hưởng đến giá trị ban đầu của beta

            #Duyệt từng hành động hợp lệ của ghost
            for action in actions:
                successor = gameState.generateSuccessor(agentIndex, action)  #Tạo trạng thái tiếp theo của toàn bộ game sau khi ghost di chuyển
                
                #Nếu đã đến ghost cuối cùng thì gọi tiếp hành động của pacman sau khi tất cả các ghost đều đã di chuyển
                if agentIndex == (gameState.getNumAgents() - 1):
                    minValue = min(minValue, maxLevel(successor, depth, alpha, beta1))
                    if minValue < alpha:
                        return minValue
                    beta1 = min(beta1, minValue)
                #Nếu không phải ghost cuối cùng thì xét hành động của ghost tiếp theo
                else:
                    minValue = min(minValue, minLevel(successor, depth, agentIndex + 1, alpha, beta1))  #Lấy ra giá trị nhỏ nhất giữa 2 giá trị là giá trị nhỏ nhất hiện tại và giá trị sau khi ghost tiếp theo di chuyển
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
        print(actions)

        #Chọn energizer
        minDistanceEnergizer = 999
        if len(gameState.getEnergizer()) > 0:
            for energizer in gameState.getEnergizer():
                distance = manhattanDistance(gameState.getPacmanPosition(), energizer)
                if distance < minDistanceEnergizer:
                    minDistanceEnergizer = distance
                    TARGET_ENERGIZER = energizer
        else:
            TARGET_ENERGIZER = None

        #Chọn food
        minDistanceFood = 999
        foodList = gameState.getFood().asList()
        if len(foodList) > 0:
            for food in foodList:
                distance = manhattanDistance(gameState.getPacmanPosition(), food)
                if distance < minDistanceFood:
                    minDistanceFood = distance
                    TARGET_FOOD = food
        else:
            TARGET_FOOD = None

        minDistanceGhost = 999
        ghostStates = gameState.getGhostStates()
        scaredTime = []
        for ghost in ghostStates:
            scaredTime.append(ghost.scaredTimer)
        if len(set(scaredTime)) == 1 and scaredTime[0] == 0:
            TARGET_GHOST = None
        else:
            for i in range(0, len(ghostStates)):
                if scaredTime[i] > 0:
                    distance = manhattanDistance(gameState.getPacmanPosition(), ghostStates[i].getPosition())
                    if distance < minDistanceGhost:
                        TARGET_GHOST = ghostStates[i].getPosition()
        print(f"Target ghost: {TARGET_GHOST}")

        #Duyệt từng hành động hợp lệ của pacman
        for action in actions:
            nextState = gameState.generateSuccessor(0, action)  #Tạo trạng thái tiếp theo của toàn bộ game sau khi pacman thực hiện hành động action
            score = minLevel(nextState, 0, 1, alpha, beta)  #Sau khi pacman hành động phải xem ghost hành động như thế nào
            stateWithAction[action] = nextState
            print(f"Hanh dong: {action}, Diem: {score}")
            if score > currScore:
                returnAction = action
                currScore = score
            if score > beta:
                print(f"Score change: {gameState.data.scoreChange}")
                PACMAN_STAYED.append(stateWithAction[returnAction].getPacmanPosition())
                return returnAction
            alpha = max(alpha, score)
        print(f"Score change: {gameState.data.scoreChange}")
        PACMAN_STAYED.append(stateWithAction[returnAction].getPacmanPosition())
        return returnAction