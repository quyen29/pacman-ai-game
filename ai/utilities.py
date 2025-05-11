import heapq
from abc import ABC, abstractmethod

class Queue:
    def __init__(self):
        self.list = []
    
    def push(self, item):
        self.list.insert(0, item)

    def pop(self):
        return self.list.pop()  #Xóa và trả về phần tử cuối cùng trong list
    
    def isEmpty(self):
        if len(self.list) == 0:
            return True
        else:
            return False

#Gán trực tiếp giá trị ưu tiên       
class PriorityQueue:
    def __init__(self):
        self.heap = []
        self.count = 0

    def push(self, item, priority):
        entry = (priority, self.count,  item)  #Lần lượt sắp xếp tăng dần theo các tiêu chí priority -> count
        heapq.heappush(self.heap, entry)
        self.count += 1
    
    def pop(self):
        (_, _, item) = heapq.heappop(self.heap)
        return item
    
    def isEmpty(self):
        if len(self.heap) == 0:
            return True
        else:
            return False

def manhattanDistance(xy1, xy2):
    return abs(xy1[0] - xy2[0]) + abs(xy1[1] - xy2[1])

def nearestPoint(pos):
    nearRow = int(pos[0] + 0.5)
    nearCol = int(pos[1] + 0.5)
    return (nearRow, nearCol)

class SearchProblem(ABC):
    @abstractmethod
    def getStartState(self):
        #Trả về trạng thái ban đầu của agent
        pass

    @abstractmethod
    def isGoalState(self, state):
        #Trả về True nếu state là trạng thái mục tiêu, ngược lại là False
        pass

    @abstractmethod
    def getSuccessors(self, state):
        #Nhận trạng thái hiện tại và trả về danh sách các trạng thái kế tiếp
        #Danh sách trạng thái kế tiếp sẽ chứa các tuple mỗi tuple sẽ có dạng (successor, action, stepCost)
        #Ví dụ: ((1, 2), Direction.NORTH, 1)
        pass

    @abstractmethod
    def getCostOfActions(self, actions):
        #Nhận danh sách các hành động và tính toán, sau đó trả về chi phí thực hiện chuỗi hànhd động đó
        pass
    
class GhostSearchProblem(SearchProblem):
    def __init__(self, state, goal, ghost_index):
        from characters.agents import Directions
        super().__init__()
        self.start = state.getGhostState(ghost_index).getPosition()
        self.goal = goal
        self.ghost_index = ghost_index
        self.walls = state.getWalls()
        self.directions = [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST, Directions. STOP]

    def getStartState(self):
        return self.start

    def isGoalState(self, state):
        return state == self.goal

    def getSuccessors(self, state):
        from characters.agents import Actions
        
        successors = []
        for action in self.directions:
            dx, dy = Actions.directionToVector(action)
            next_x, next_y = int(state[0] + dx), int(state[1] + dy)
            if 0 <= next_x < self.walls.height and 0 <= next_y < self.walls.width:
                if not self.walls[next_x][next_y]:
                    successors.append(((next_x, next_y), action, 1))
                
        return successors

    def getCostOfActions(self, actions):
        from characters.agents import Actions
        
        if actions is None:
            return float('inf')
        x, y = self.start
        cost = 0
        for action in actions:
            dx, dy = Actions.directionToVector(action)
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]:
                return float('inf')
            cost += 1
        return cost
    