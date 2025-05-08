import copy

from characters.agents import Configuration, Directions
from game.logic import TIME_PENALTY, GhostRules, PacmanRules


class AgentState:
    def __init__(self, startConfiguration, isPacman):
        self.start = startConfiguration  #Trạng thái ban đầu của agent
        self.configuration = startConfiguration  #Trạng thái hiện tại của agent 
        self.isPacman = isPacman  #Agent có phải là pacman hay không
        self.scaredTimer = 0  #Thời gian mà ghost ở trạng thái hoảng sợ
        self.inPen = not isPacman # Pacman ngoài pen và các ghost trong pen

    def __str__(self):
        if self.isPacman:
            return "Pacman: " + str(self.configuration)
        else:
            return "Ghost: " + str(self.configuration) 
        
    def __eq__(self, other):
        if other == None:
            return False
        if self.configuration == other.configuration and self.scaredTimer == other.scaredTimer:
            return True
        else:
            return False
        
    def __hash__(self):
        x = hash(self.configuration)
        y = hash(self.scaredTimer)
        return hash(x + 123 * y)
    
    #Tạo bản sao của trạng thái ban đầu để thử các bước đi, nếu không tạo bản sao thì khó quay lại trạng thái ban đầu để thử các bước đi khác
    def copy(self):
        state = AgentState(self.start, self.isPacman)
        state.configuration = self.configuration
        state.scaredTimer = self.scaredTimer
        state.inPen = self.inPen
        return state
        
    def getPosition(self):
        if self.configuration == None: 
            return None
        return self.configuration.getPosition()

    def getDirection(self):
        if self.configuration == None: 
            return None
        return self.configuration.getDirection()
    
class GameStateData:
    def __init__(self, prevState = None):
        if prevState != None:
            self.food = prevState.food.shallowCopy()  #Là mảng 2 chiều đánh dấu vị trí có food là True, không có food là False
            self.bonusFruit = prevState.bonusFruit
            self.bonusTime = prevState.bonusTime
            self.energizer = prevState.energizer[:]  #Là danh sách vị trí của các energizer
            self.agentStates = self.copyAgentStates(prevState.agentStates)  #Là danh sách trạng thái của tất cả các agent
            self.layout = prevState.layout  #Là mê cung ban đầu, không thay đổi trong suốt các lượt chơi
            self.eaten = prevState.eaten  #Là danh sách đánh dấu agent nào bị ăn trong lượt chơi trước
            self.score = prevState.score  #Là tổng số điểm hiện tại của game
            self.chance = prevState.chance
        
        self.foodEaten = None  #Là vị trí food đã ăn
        self.energizerEaten = None  #Là vị trí của energizer bị ăn trong lượt hiện tại
        self.agentMoved = None  #Là index của agent di chuyển trong lượt hiện tại
        self.lose = False  #Là trạng thái thắng thua của game
        self.win = False
        self.reset = False
        self.scoreChange = 0  #Là số điểm mà pacman kiếm thêm được trong lượt hiện tại
    
    #Tạo bản sao của trạng thái hiện tại
    def deepCopy(self):
        state = GameStateData(self)
        state.food = self.food.deepCopy()
        state.bonusFruit = self.bonusFruit
        state.bonusTime = self.bonusTime
        state.energizer = copy.deepcopy(self.energizer)
        state.agentStates = self.copyAgentStates(self.agentStates)
        state.layout = self.layout.deepCopy()
        state.eaten = copy.deepcopy(self.eaten[:])
        state.score = self.score
        state.agentMoved = self.agentMoved
        state.foodEaten = self.foodEaten
        state.energizerEaten = self.energizerEaten
        state.lose = self.lose
        state.win = self.win
        state.scoreChange = self.scoreChange
        state.chance = self.chance
        state.reset = self.reset
        return state
    
    #Tạo bản sao danh sách trạng thái của tất cả các agent
    def copyAgentStates(self, agentStates):
        copiedStates = []
        for agentState in agentStates:
            copiedStates.append(agentState.copy())
        return copiedStates
    
    def __eq__(self, other):
        if other == None:
            return False
        if not self.agentStates == other.agentStates:  #Gọi eq trong class AgentState -> gọi eq trong class Configuration
            return False
        if not self.food == other.food:  #Gọi eq của class Grid
            return False
        if not self.energizer == other.energizer:
            return False
        if not self.score == other.score:
            return False
        return True
    
    #Tạo key
    def __hash__(self):
        hashAgentStates = hash(tuple(self.agentStates))
        hashFood = hash(self.food)
        hashEnergizer = hash(tuple(self.energizer))
        hashScore = hash(self.score)
        return int((hashAgentStates + 13 * hashFood + 113 * hashEnergizer + 7 * hashScore) % 1048575)
        """
        hash(self.food) gọi hash trong class Grid
        hash(tuple(self.agentStates)):
            + Chuyển self.agentStates thành tuple
            + Từng phần tử gọi hash trong class AgentState
            + Kết quả sẽ có dạng (hashAgent1, hashAgent2,...)
            + Python hash kết quả này
        """

    def __str__(self):
        return f"Agent: {self.agentMoved}\nScore Change: {self.scoreChange}\nScore: {self.score}\nPosition: {self.agentStates[self.agentMoved].getPosition()}"
    
    def initialize(self, layout, numGhostAgents):
        self.food = layout.food.deepCopy()
        self.energizer = layout.energizer[:]
        self.layout = layout
        self.score = 0
        self.scoreChange = 0
        self.bonusFruit = None
        self.bonusTime = 0
        self.chance = 3

        self.agentStates = []
        numGhosts = 0
        for isPacman, pos in layout.agentPositions:
            #Cho phép cài đặt game có bao nhiêu ghost bằng cách gán giá trị cho biến numGhostAgents
            if not isPacman:
                if numGhosts == numGhostAgents:
                    continue
                else:
                    numGhosts += 1
            self.agentStates.append(AgentState(Configuration(pos, Directions.STOP), isPacman))
        self.eaten = []
        for i in range(0, len(self.agentStates)):
            self.eaten.append(False)
            if i == 1:
                self.agentStates[i].inPen = False

class GameState:
    def __init__(self, prevState = None):
        if prevState != None:
            self.data = GameStateData(prevState.data)
        else:
            self.data = GameStateData()

    def deepCopy(self):
        state = GameState(self)
        state.data = self.data.deepCopy()
        return state
    
    def __eq__(self, other):
        if other == None:
            return False
        
        if self.data == other.data:
            return True
        else:
            return False

    def __hash__(self):
        return hash(self.data)
    
    def __str__(self):
        return str(self.data)
    
    def initialize(self, layout, numGhostAgents = 4):
        self.data.initialize(layout, numGhostAgents)

    explore = set()  #Danh sách lưu các trạng thái đã xử lý, tránh xử lý lại
    @staticmethod
    def getAndResetExplored():
        tmp = GameState.explore.copy()
        GameState.explore = set()
        return tmp   

    def hasFood(self, x, y):
        return self.data.food[x][y]
    
    def hasWall(self, x, y):
        return self.data.layout.walls[x][y]
    
    def isWin(self):
        return self.data.win
    
    def isLose(self):
        return self.data.lose
    
    def getNumAgents(self):
        return len(self.data.agentStates)
    
    def getScore(self):
        return self.data.score
    
    def getEnergizer(self):
        return self.data.energizer
    
    def getNumFood(self):
        return self.data.food.count()
    
    def getFood(self):
        return self.data.food
    
    def getWalls(self):
        return self.data.layout.walls

    def getLegalActions(self, agentIndex = 0):
        state = GameState(self)
        if self.isWin() or self.isLose():
            return []

        if agentIndex == 0:
            return PacmanRules.getLegalActions(self)
        else:
            return GhostRules.getLegalActions(state, agentIndex)
        
    def getLegalPacmanActions(self):
        return self.getLegalActions(0)
        
    def generateSuccessor(self, agentIndex, action):
        if self.isWin() or self.isLose():
            raise Exception("Khong tao duoc trang thai tiep theo")
        
        state = GameState(self)

        if agentIndex == 0:
            # state.data.eaten = [False for i in range(0, state.getNumAgents())]
            PacmanRules.applyAction(state, action)
        else:
            GhostRules.applyAction(state, action, agentIndex)

        if agentIndex == 0:
            if action == Directions.STOP:
                state.data.scoreChange += -TIME_PENALTY
        else:
            GhostRules.decrementTimer(state, agentIndex)

        GhostRules.checkDeath(state, agentIndex)
        state.data.agentMoved = agentIndex
        state.data.score += state.data.scoreChange
        if state.data.reset:
            state.data.agentStates = []
            for isPacman, pos in state.data.layout.agentPositions:
                state.data.agentStates.append(AgentState(Configuration(pos, Directions.STOP), isPacman))
            state.data.eaten = []
            for i in range(0, len(state.data.agentStates)):
                state.data.eaten.append(False)
        GameState.explore.add(self)
        GameState.explore.add(state)
        return state
    
    def generatePacmanSuccessor(self, action):
        return self.generateSuccessor(0, action)
    
    def getPacmanState(self):
        return self.data.agentStates[0].copy()
    def getGhostStates(self):
        return self.data.agentStates[1:]
    def getGhostState(self, agentIndex):
        if agentIndex == 0 or agentIndex >= self.getNumAgents():
            raise Exception("Agent khong phai ghost")
        return self.data.agentStates[agentIndex]
    
    def getPacmanPosition(self):
        return self.data.agentStates[0].getPosition()
    def getGhostPositions(self):
        ghostPositions = []
        for ghost in self.getGhostStates():
            ghostPositions.append(ghost.getPosition())
        return ghostPositions
    def getGhostPosition(self, agentIndex):
        if agentIndex == 0 or agentIndex >= self.getNumAgents():
            raise Exception("Agent khong phai ghost")
        return self.data.agentStates[agentIndex].getPosition()