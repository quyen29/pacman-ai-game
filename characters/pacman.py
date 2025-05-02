from ai.utilities import manhattanDistance
from characters.agents import Agent

def scoreEvaluationFunction(currentGameState):
    return currentGameState.getScore()

def betterEvaluationFunction(currentGameState):
    """
    - Các đặc điểm của hàm đánh giá này:
        + Ưu tiên ăn các dots
        + Ưu tiên ăn ghosts khi ghosts ở trạng thái hoảng sợ
        + Tránh ghosts
        + Tính khoảng cách manhattan
    """
    #Biến currentGameState có kiểu dữ liệu là GameState. Biến này là trạng thái giả định của game nếu agent thực hiện một hành động nào đó
    newPos = currentGameState.getPacmanPosition() 
    newFood = currentGameState.getFood()  #(Grid) bản đồ food
    newGhostStates = currentGameState.getGhostStates()  #(list[AgentState]) danh sách trạng thái của ghost
    newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]  #(list[int]) danh sách thời gian hoảng sợ của ghost

    foodList = newFood.asList()  #Lấy danh sách các vị trí có food
    #Tính khoảng cách của pacman đến các dots nhỏ trong mê cung
    foodDistance = []
    for pos in foodList:
        foodDistance.append(manhattanDistance(newPos, pos))
    
    #Tính khoảng cách của pacman đến các ghost
    ghostPos = []  #Danh sách vị trí của các ghost
    for ghost in newGhostStates:
        ghostPos.append(ghost.getPosition())
    ghostDistance = []
    for pos in ghostPos:
        ghostDistance.append(manhattanDistance(newPos, pos))

    numberOfEnergizer = len(currentGameState.getEnergizer())
    score = 0
    numberOfNoFoods = len(newFood.asList(False))
    sumScaredTimes = sum(newScaredTimes)
    sumGhostDistance = sum(ghostDistance)
    reciprocalFoodDistance = 0 
    """
        - Tính nghịch đảo khoảng cách của pacman đến food
        - Nghĩa là khi khoảng cách càng nhỏ thì điểm phải càng lớn nên cần phải tính nghich đảo
        - Chỉ được dùng nghịch đảo cho food vì nghịch đảo nhạy hơn các phép tính khác mà pacman cần ưu tiên ăn food
        - Không được dùng phép trừ vì khoảng cách điểm giữa các trạng thái sẽ không rõ ràng như dùng nghịch đảo
    """
    if sum(foodDistance) > 0:
        reciprocalFoodDistance = 1 / sum(foodDistance)

    score += currentGameState.getScore() + reciprocalFoodDistance + numberOfNoFoods
    """
        - Khi chọn di chuyển theo hướng này, pacman ăn được càng nhiều food thì số lượng vị trí không có food sẽ càng tăng
        - Vì vậy cộng biến numberOfNoFood để đánh gía khả năng ăn food của trạng trạng thái đó
    """

    if sumScaredTimes > 0:
        score += sumScaredTimes + (-1 * numberOfEnergizer) + (-1 * sumGhostDistance)
        """
            - Thời gian ghost ở trong trạng thái hoảng sợ càng cao thì điểm càng cao để khuyến khích pacman đến ăn ghost
            - Phải trừ khoảng cách đến ghost vì khoảng cách càng xa điểm càng nhỏ
            - Phải trừ số lượng energizer vì cần khuyến khích pacman ăn các energizer để duy trì trạng thái hoảng sợ của ghost lâu hơn, để pacman tận dụng hết tài nguyên
        """
    else:
        score += sumGhostDistance + numberOfEnergizer
        """
            - Khi ghost không ở trạng thái hoảng sợ thì cần tránh xa ghost vì vậy càng xa ghost thì điểm càng tăng
            - Pacman cần chờ thời điểm thích hợp để ăn energizer, vì vậy khi ghost không ở trạng thái hoảng sợ thì còn càng nhiều energizer thì điểm càng cao
        """
    return score

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

        #Duyệt từng hành động hợp lệ của pacman
        for action in actions:
            nextState = gameState.generateSuccessor(0, action)  #Tạo trạng thái tiếp theo của toàn bộ game sau khi pacman thực hiện hành động action
            score = minLevel(nextState, 0, 1, alpha, beta)  #Sau khi pacman hành động phải xem ghost hành động như thế nào
            if score > currScore:
                returnAction = action
                currScore = score
            if score > beta:
                return returnAction
            alpha = max(alpha, score)
        return returnAction

class Pacman():
    def __init___(self, x, y):
        self.x = x
        self.y = y
        self.direction = 0
        self.score = 0
        self.lives = 3

    def move(self):
        pass

    def update(self):
        pass

    def reset(self):
        pass
