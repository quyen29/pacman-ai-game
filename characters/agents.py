from abc import ABC, abstractmethod
import random
import time
import traceback
import copy

from game.board import boards
from ai.utilities import manhattanDistance

def gameMaze():
    import main
    classicMaze = []
    for i in range(0, len(boards)):
        row = []
        for j in range(0, len(boards[0])):
            if 3 <= boards[i][j] <= 8:
                row.append("%")
            elif boards[i][j] == 0 or boards[i][j] == 9:
                row.append(" ")
            elif boards[i][j] == 1:
                row.append(".")
            elif boards[i][j] == 2:
                row.append("o")
        classicMaze.append(row)
    classicMaze[int((main.pacman_y / 20) - 3)][int(main.pacman_x / 20)] = "P"
    classicMaze[int((main.blinky_y / 20) - 3)][int(main.blinky_x / 20)] = "G"
    classicMaze[int((main.pinky_y / 20) - 3)][int(main.pinky_x / 20)] = "G"
    classicMaze[int((main.inky_y / 20) - 3)][int(main.inky_x / 20)] = "G"
    classicMaze[int((main.clyde_y / 20) - 3)][int(main.clyde_x / 20)] = "G"
    return classicMaze

class Agent(ABC):
    def __init__(self, index = 0):
        self.index = index
        
    @abstractmethod
    def getAction(self, gameState):  #Biến gameState có kiểu dữ liệu là GameState
        pass

class Directions:
    NORTH = "North"
    SOUTH = "South"
    EAST = "East"
    WEST = "West"
    STOP = "Stop"

#Lớp quản lý hành động di chuyển
class Actions:
    #Hướng NORTH, SOUTH là trục x, hướng EAST, WEST là trục y với trục x hướng xuống và trục y hướng sang phải (Theo chiều của mảng 2 chiều)
    directions = {Directions.NORTH: (-1, 0),
                  Directions.SOUTH: (1, 0),
                  Directions.EAST: (0, 1),
                  Directions.WEST: (0, -1),
                  Directions.STOP: (0, 0)}
    directionsAsList = directions.items()  #Tránh gọi lại generator, tối ưu hóa về mặt tốc độ

    #Di chuyển ngược lại, phương thức này có thể gọi trực tiếp từ class, không cần dùng new để tạo instance thì mới gọi được
    @staticmethod
    def reverseDirection(action):
        if action == Directions.NORTH:
            return Directions.SOUTH
        if action == Directions.SOUTH:
            return Directions.NORTH
        if action == Directions.EAST:
            return Directions.WEST
        if action == Directions.WEST:
            return Directions.EAST
        return action
    
    #Chuyển từ vector (dx, dy) sang dạng hướng (NORTH, SOUTH, WEST, EAST)
    @staticmethod
    def vectorToDirection(vector):
        dx, dy = vector
        if dx < 0:
            return Directions.NORTH
        if dx > 0:
            return Directions.SOUTH
        if dy > 0:
            return Directions.EAST
        if dy < 0:
            return Directions.WEST
        return Directions.STOP

    #Chuyển từ hướng sang vector và speed cho biết di chuyển bao nhiêu ô theo hướng đó
    @staticmethod
    def directionToVector(direction, speed = 1.0):
        dx, dy =  Actions.directions[direction]
        return (dx * speed, dy * speed)

    #Đưa ra những hướng di chuyển cho agent từ Configuration hiện tại
    @staticmethod
    def getPossibleActions(config, walls, agentIndex):
        possible = []
        x, y = config.pos  #config có kiểu dữ liệu là Configuration
        
        #Đưa ra các hướng có thể đi được
        for dir, vec in Actions.directionsAsList:
            dx, dy = vec
            next_x = x + dx 
            next_y = y + dy
            
            if next_y > 29:
                next_y = 0
            elif next_y < 0:
                next_y = 29

            if agentIndex == 0:
                if not walls[int(next_x)][int(next_y)] and (int(next_x), int(next_y)) not in [(13, 14), (13, 15)]:
                    possible.append(dir)
            else:
                if not walls[int(next_x)][int(next_y)]:
                    possible.append(dir)
        return possible
    
    #Trả về vị trí sau khi di chuyển theo action nào đó
    @staticmethod
    def getSuccessor(position, action):
        dx, dy = Actions.directionToVector(action)
        x, y = position
        if y == 29 and action == Directions.EAST:
            return (x + dx, 0)
        elif y == 0 and action == Directions.WEST:
            return(x + dx, 29)
        return (x + dx, y + dy)
    #Tính toán 4 bước tiếp theo của pacman
    def get_ahead_position(pos, direction, steps=4):
        x, y = pos
        if direction == 'UP':
            return (x, y - steps)
        elif direction == 'DOWN':
            return (x, y + steps)
        elif direction == 'LEFT':
            return (x - steps, y)
        elif direction == 'RIGHT':
            return (x + steps, y)
        return pos

#Lớp lưu trữ thông tin về vị trí và hướng di chuyển
class Configuration:
    def __init__(self, pos, direction):
        self.pos = pos  #Là tọa độ (x, y) được lưu trữ dưới dạng tuple
        self.direction = direction
    
    def getPosition(self):
        return self.pos
    
    def getDirection(self):
        return self.direction
    
    #So sánh hướng đi và vị trí của 2 agent
    def __eq__(self, other):
        if other is None:
            return False
        if self.pos == other.pos and self.direction == other.direction:
            return True
        else:
            return False
        
    #Hash để tạo key cho direction cho 1 cặp vị trí và hướng đi
    def __hash__(self):
        x = hash(self.pos)
        y = hash(self.direction)
        return hash(x + 123 * y)
    
    def __str__(self):
        return "(x, y) = " + str(self.pos) + ", direction: " + str(self.direction)
    
    #Cập nhật lại vị trí và hướng đi sau khi agent di chuyển
    def generateSuccessor(self, vector, agentIndex):
        x, y = self.pos
        dx, dy = vector
        direction = Actions.vectorToDirection(vector)
        #Nếu direction là STOP thì phải giữ nguyên direction cũ, không được đặt direction là STOP
        if direction == Directions.STOP:
            direction = self.direction
        if y >= 29 and direction == Directions.EAST:
            return Configuration((int(x + dx), 0), direction)
        elif y <= 0 and direction == Directions.WEST:
            return Configuration((int(x + dx), 29), direction)
        if agentIndex == 0:
            return Configuration((int(x + dx), int(y + dy)), direction)
        else:
            return Configuration((x + dx, y + dy), direction)

class Grid:
    #False là ô đi được, True là tường
    def __init__(self, width, height, initialValue = False):
        self.width = width
        self.height = height

        self.data = []
        for i in range(0, height):
            row = []
            for j in range(0, width):
                row.append(copy.deepcopy(initialValue))
            self.data.append(row)

    def __getitem__(self, i):
        return self.data[i]

    def __setitem__(self, key, item):
        self.data[key] = item

    def __str__(self):
        result = ""
        for i in self.data:
            s = " ".join([str(j) for j in i])
            result += f"{s}\n"
        result = result.strip()
        return result
    
    def __eq__(self, other):
        if other == None:
            return False
        if self.data == other.data:
            return True
        else:
            return False
        
    def __hash__(self):
        base = 1
        h = 0
        for i in self.data:
            for j in i:
                if j:
                    h += base
                base *= 2
        return hash(h)
    
    #Tạo bản sao mà khi thay đổi bản sao thì bản gốc không thay đổi
    def deepCopy(self):
        g = Grid(self.width, self.height)
        g.data = [x[:] for x in self.data]
        return g
    
    #Tạo bản sao mà khi thay đổi bản sao thì bản gốc cũng thay đổi
    def shallowCopy(self):
        g = Grid(self.width, self.height)
        g.data = self.data
        return g
    
    #Đếm số lượng item True hoặc False
    def count(self, item = True):
        total = 0
        for i in self.data:
            total += i.count(item)
        return total
    
    #Tạo list lưu tọa độ (x, y) của key
    def asList(self, key = True):
        list = []
        for i in range(0, self.height):
            for j in range(0, self.width):
                if self.data[i][j] == key:
                    list.append((i, j))
        return list

class Layout:
    def __init__(self, layoutText):
        self.width = len(layoutText[0])
        self.height = len(layoutText)
        self.walls = Grid(self.width, self.height, False)
        self.food = Grid(self.width, self.height, False)
        self.energizer = []
        self.agentPositions = []
        self.numGhosts = 0
        self.processLayoutText(layoutText)
        self.layoutText = layoutText
        self.totalFood = len(self.food.asList())
    
    def getNumGhosts(self):
        return self.numGhosts
    
    def __str__(self):
        return "\n".join(self.layoutText)
    
    def deepCopy(self):
        return Layout(self.layoutText[:])
    
    def processLayoutChar(self, x, y, layoutChar):
        if layoutChar == "%":
            self.walls[x][y] = True
        elif layoutChar == ".":
            self.food[x][y] = True
        elif layoutChar == "o":
            self.energizer.append((x, y))
        elif layoutChar == "P":
            self.agentPositions.append((0, (x, y)))
        elif layoutChar == "G":
            self.agentPositions.append((1, (x, y)))
            self.numGhosts += 1
        elif layoutChar in  ['1', '2', '3', '4']:
            self.agentPositions.append((int(layoutChar), (x, y)))
            self.numGhosts += 1

    def processLayoutText(self, layoutText):
        for x in range(0, len(layoutText)):
            for y in range(0, len(layoutText[0])):
                layoutChar = layoutText[x][y]
                self.processLayoutChar(x, y, layoutChar)
                
        self.agentPositions.sort()
        boolAgentPosition = []
        for i, pos in self.agentPositions:
            if i == 0:
                boolAgentPosition.append((True, pos))
            else:
                boolAgentPosition.append((False, pos))
        self.agentPositions = boolAgentPosition

class Game:
    def __init__(self, agents, rules, startingIndex = 0):
        self.agentCrashed = False  #Flag đánh dấu có agent bị lỗi
        self.agents = agents  #Danh sách các agent
        self.rules = rules  #Quy tắc của game
        self.startingIndex = startingIndex  #Index của agent bắt đầu lượt chơi đầu tiên
        self.gameOver = False  #Trạng thái của game đang chạy hay kết thúc
        self.moveHistory = []  #Danh sách ghi lại các bước di chuyển trong game
        self.numMoves = 0
        self.agentIndex = self.startingIndex
        self.state = None
        self.initialized = False

    #Kết thúc game và trả về lỗi khi có agent gặp lỗi   
    def agentCrash(self, agentIndex, quiet = False):
        if not quiet: 
            traceback.print_exc()  #In lỗi ra console
        self.gameOver = True
        self.agentCrash = True
        self.rules.agentCrash(self, agentIndex)

    def run(self):
        if self.gameOver:
            return
        
        if not self.initialized:
            print("Khoi tao agent")
            for i in range(0, len(self.agents)):
                agent = self.agents[i]
                if not agent: 
                    print(f"Agent {i} xay ra loi khi load") 
                    self.agentCrash(i, quiet = True)  #Kết thúc game
            self.initialized = True
            print("Khoi tao agent thanh cong")

        agent = self.agents[self.agentIndex]
        observation = self.state.deepCopy()

        try:
            action = agent.getAction(observation)
            if self.agentIndex == 0:
                print(f"Hanh dong: {action}")
        except Exception as e:
            print(f"Agent {self.agentIndex} bi loi: {e}")
            self.agentCrash(self.agentIndex)
            return
        
        self.moveHistory.append((self.agentIndex, action))
        try:
            self.state = self.state.generateSuccessor(self.agentIndex, action)
        except Exception as e:
            print(f"Agent {self.agentIndex} co loi khi di chuyen: {e}")
            self.agentCrash(self.agentIndex)
            return
        self.rules.process(self.state, self)

        if self.agentIndex == len(self.agents) - 1:
            self.numMoves += 1

        self.agentIndex = (self.agentIndex + 1) % len(self.agents)
        if self.agentIndex == 0:
            print(f"Score: {observation.getScore()}")

class Modes:
    CHASE = 'Chase'
    SCATTER = 'Scatter'
    FRIGHTENED = 'Frightened'

class GhostModeController:
    def __init__(self):
        self.mode_times = [(Modes.SCATTER, 7), (Modes.CHASE, 20),
                           (Modes.SCATTER, 7), (Modes.CHASE, 20),
                           (Modes.SCATTER, 5), (Modes.CHASE, 20),
                           (Modes.SCATTER, 5), (Modes.CHASE, float("inf"))]
        self.current_index = 0
        self.current_mode = self.mode_times[0][0]
        self.start_time = time.time()

    def update(self):
        elapsed = time.time() - self.start_time
        total = 0
        for i, (mode, duration) in enumerate(self.mode_times):
            total += duration
            if elapsed < total:
                if self.current_index != i:
                    self.current_index = i
                    self.current_mode = mode
                break

    def get_mode(self, ghostState):
        if ghostState.scaredTimer > 0:
            self.current_mode = Modes.FRIGHTENED
        else:
            self.update()
        return self.current_mode
    
    def reset(self):
        self.current_index = 0
        self.current_mode = self.mode_times[0][0]
        self.start_time = time.time()
        