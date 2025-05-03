from abc import ABC, abstractmethod
import random
import traceback

from game.board import boards
from ai.utilities import manhattanDistance

def gameMaze():
    import main
    classicMaze = []
    for i in range(0, len(boards)):
        row = []
        for j in range(0, len(boards[0])):
            if 3 <= boards[i][j] <= 9:
                row.append("%")
            elif boards[i][j] == 0:
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

    LEFT = {NORTH: WEST,
            SOUTH: EAST,
            EAST: NORTH,
            WEST: SOUTH,
            STOP: STOP}
    RIGHT = dict([(y, x) for x, y in LEFT.items()])
    REVERSE = {NORTH: SOUTH,
               SOUTH: NORTH,
               EAST: WEST,
               WEST: EAST,
               STOP: STOP}

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
            return Directions.WEST
        if dy < 0:
            return Directions.EAST
        return Directions.STOP

    #Chuyển từ hướng sang vector và speed cho biết di chuyển bao nhiêu ô theo hướng đó
    @staticmethod
    def directionToVector(direction, speed = 1.0):
        dx, dy =  Actions.directions[direction]
        return (dx * speed, dy * speed)

    #Đưa ra những hướng di chuyển cho agent từ Configuration hiện tại
    @staticmethod
    def getPossibleActions(config, walls, speed):
        possible = []
        x, y = config.pos  #config có kiểu dữ liệu là Configuration
        
        #Đưa ra các hướng có thể đi được
        for dir, vec in Actions.directionsAsList:
            dx, dy = vec
            next_x = x + (dx * speed)
            next_y = y + (dy * speed)

            if next_x > 29:
                next_x = 0
            elif next_x < 0:
                next_x = 29

            if speed == 0.5:
                if dir == Directions.WEST or dir == Directions.NORTH:
                    if not walls[int(next_x)][int(next_y)]:
                        possible.append(dir)
                else:
                    if not walls[int(next_x + 0.5)][int(next_y + 0.5)]:
                        possible.append(dir)
            else:
                if not walls[int(next_x)][int(next_y)]:
                    possible.append(dir)
        return possible

    #Trả về các ô hàng xóm có thể đi tới mà không bị tường chặn
    @staticmethod
    def getLegalNeighbors(position, walls):
        x, y = position
        x_int, y_int = int(x + 0.5), int(y + 0.5)
        neighbors = []

        #Duyệt qua tất cả các hướng để tìm hàng xóm
        for dir, vec in Actions.directionsAsList:
            dx, dy = vec

            #Nếu vị trí tiếp theo ở ngoài bản đồ thì duyệt hướng khác
            next_x = x_int + dx
            if next_x < 0 or next_x == walls.height: 
                continue
            next_y = y_int + dy
            if next_y < 0 or next_y == walls.width: 
                continue

            #Nếu vị trí tiếp theo không phải là tường thì thêm vào neighbors
            if not walls[next_x][next_y]:
                neighbors.append((next_x, next_y))
        return neighbors
    
    #Trả về vị trí sau khi di chuyển theo action nào đó
    @staticmethod
    def getSuccessor(position, action):
        dx, dy = Actions.directionToVector(action)
        x, y = position
        if x == 29 and action == Directions.EAST:
            return (0, y + dy)
        elif x == 0 and action == Directions.WEST:
            return(29, y + dy)
        return (x + dx, y + dy)

#Lớp lưu trữ thông tin về vị trí và hướng di chuyển
class Configuration:
    def __init__(self, pos, direction):
        self.pos = pos  #Là tọa độ (x, y) được lưu trữ dưới dạng tuple
        self.direction = direction
    
    def getPosition(self):
        return self.pos
    
    def getDirection(self):
        return self.direction
    
    #Kiểm tra agent (Pacman hoặc ghost) đang đứng trong 1 ô hay đứng giữa 2 ô
    def isInteger(self):
        x, y = self.pos
        if x == int(x) and y == int(y):
            return True
        else:
            return False
    
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
    def generateSuccessor(self, vector):
        x, y = self.pos
        dx, dy = vector
        direction = Actions.vectorToDirection(vector)
        #Nếu direction là STOP thì phải giữ nguyên direction cũ, không được đặt direction là STOP
        if direction == Directions.STOP:
            direction = self.direction
        if x == 29 and direction == Directions.EAST:
            return Configuration((0, y + dy), direction)
        elif x == 0 and direction == Directions.WEST:
            return Configuration((29, y + dy), direction)
        return Configuration((x + dx, y + dy), direction)

class Grid:
    #False là ô đi được, True là tường
    def __init__(self, width, height, initialValue = False, bitRepresentation = None):
        self.CELLS_PER_INT = 30 #Dùng 30 giá trị True và False trong grid để nén thành 1 số nguyên

        self.width = width
        self.height = height

        #Nếu bitRepresentation có dữ liệu thì giải nén
        if bitRepresentation:
            self.data = self.unpackBits(bitRepresentation)
        else:
            self.data = []
            for i in range(0, height):
                row = []
                for j in range(0, width):
                    row.append(initialValue)
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

    def cellIndexToPosition(self, index):
        x = index / self.width
        y = index % self.width
        return int(x), int(y)
    
    #Nén mảng 2 chiều thành mảng 1 chiều
    def packBits(self):
        bits = [self.width, self.height]
        currentInt = 0
        s = ""

        for i in range(0, self.width * self.height):
            x, y = self.cellIndexToPosition(i, self.width)  #Chuyển từ chỉ số index thành vị trí trong mảng data
            #Nối giá trị tại các điểm đó thành 1 chuỗi nhị phân
            if self.data[x][y]:
                s += "1"
            else:
                s += "0"

            #Kiểm tra số lượng giá trị đã bằng CELLS_PER_INT chưa
            if (i + 1) % self.CELLS_PER_INT == 0:
                currentInt = int(s, 2)  #Chuỗi chuỗi nhị phân thành số nguyên
                bits.append(currentInt)  #Thêm giá trị vào biến bits
                s = ""
                currentInt = 0

        #Kiểm tra để thêm giá trị nén cuối cùng vào biến bits
        if self.width % self.CELLS_PER_INT != 0:
            s = s + "0" * (self.CELLS_PER_INT - len(s))
            currentInt = int (s, 2)
            bits.append(currentInt)
        return tuple(bits)

    #Giải nén
    def unpackBits(self, bits):
        result = []
        strBit = ""

        for i in bits:
            bit = bin(i)[2:]  #Bỏ phần 0b ở đầu giá trị
            bit = bit.zfill(self.CELLS_PER_INT)  #Thêm vào các bit 0 để đạt đủ chiều dài, tránh mất dữ liệu
            strBit += bit  #Nối tất cả thành chuỗi nhị phân

        atomic = []
        for i in range(0, self.width * self.height):
            #Kiểm tra từng bit để trả lại giá trị ban đầu
            if strBit[i] == "1":
                atomic.append(True)
            else:
                atomic.append(False)

            #Kiểm tra đã đủ chiều dài chưa
            if (i + 1) % self.width == 0:
                result.append(atomic)
                atomic = []
        return result

VISIBILITY_MATRIX_CACHE = {}

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
    
    def initializeVisibilityMatrix(self):
        global VISIBILITY_MATRIX_CACHE
        if "".join(self.layoutText) not in VISIBILITY_MATRIX_CACHE:
            vecs = [(-1, 0), (1, 0), (0, 1), (0, -1)]
            dirs = [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]
            vis = Grid(self.width, self.height, {Directions.NORTH: set(), Directions.SOUTH: set(), Directions.WEST: set(), Directions.STOP: set()})
            
            for x in range(0, self.height):
                for y in range(0, self.width):
                    #Nếu ở vị trí không phải là tường thì kiểm tra các ô có thể đi đến theo các hướng từ vị trí đó 
                    if not self.walls[x][y]:
                        for vec, dir in zip(vecs, dirs):
                            dx, dy = vec
                            nextx, nexty = x + dx, y + dy
                            while not self.walls[nextx][nexty]:
                                vis[x][y][dir].add((nextx, nexty))
                                nextx, nexty = nextx + dx, nexty + dy
            self.visibility = vis
            VISIBILITY_MATRIX_CACHE["".join(self.layoutText)] = vis
        else:
            self.visibility = VISIBILITY_MATRIX_CACHE["".join(self.layoutText)]
        
    def isWall(self, pos):
        x, y = pos
        return self.walls[x][y]
    
    #Random vị trí mà không phải tường
    def getRandomLegalPosition(self):
        x = random.choice(range(0, self.height))
        y = random.choice(range(0, self.width))
        while self.isWall((x, y)):
            x = random.choice(range(0, self.height))
            y = random.choice(range(0, self.width))
        return (x, y)
    
    #Random 1 góc trong mê cung
    def getRandomCorner(self):
        corners = [(2, 2), (2, 27), (30, 2), (30, 27)]
        return random.choice(corners)
    
    #Lấy góc xa nhất so với vị trí của pacman
    def getFurthestCorner(self, pacPos):
        corners = [(2, 2), (2, 27), (30, 2), (30, 27)]
        max = -1
        furthestCorner = (-1, -1)
        for corner in corners:
            distance = manhattanDistance(corners, pacPos)
            if distance >= max:
                max = distance
                furthestCorner = corner
        return furthestCorner
    
    #Kiểm tra ghost có trong tầm nhìn của pacman theo một hướng nào đó không
    def isVisibleFrom(self, ghostPos, pacPos, pacDirection):
        row = pacPos[0]
        col = pacPos[1]
        return ghostPos in self.visibility[row][col][pacDirection]
    
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
    
    #Trả về tiến độ của game
    def getProgress(self):
        if self.gameOver:
            return 1.0
        else:
            return self.rules.getProgress(self)

    #Kết thúc game và trả về lỗi khi có agent gặp lỗi   
    def agentCrash(self, agentIndex, quiet = False):
        if not quiet: 
            traceback.print_exc()  #In lỗi ra console
        self.gameOver = True
        self.agentCrash = True
        self.rules.agentCrash(self, agentIndex)

    def run(self):
        nameAgent = ["Pacman", "Blinky", "Pinky", "Inky", "Clyde"]
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
            print(f"{nameAgent[self.agentIndex]} dang lay hanh dong...")
            action = agent.getAction(observation)
            print(f"{nameAgent[self.agentIndex]} lay hanh dong thanh cong")
        except Exception as e:
            print(f"Agent {self.agentIndex} bi loi: {e}")
            self.agentCrash(self.agentIndex)
            return
        
        print(f"{nameAgent[self.agentIndex]} them hanh dong vao lich su")
        self.moveHistory.append((self.agentIndex, action))
        try:
            print(f"{nameAgent[self.agentIndex]} tao lai trang thai cua game sau khi di chuyen")
            self.state = self.state.generateSuccessor(self.agentIndex, action)
        except Exception as e:
            print(f"Agent {self.agentIndex} co loi khi di chuyen: {e}")
            self.agentCrash(self.agentIndex)
            return
        self.rules.process(self.state, self)

        if self.agentIndex == len(self.agents) - 1:
            self.numMoves += 1

        self.agentIndex = (self.agentIndex + 1) % len(self.agents)
        print(f"Score: {observation.getScore()}")