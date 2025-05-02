import heapq
from abc import ABC, abstractmethod
import random

class Stack:
    def __init__(self):
        self.list = []
    
    def push(self, item):
        self.list.append(item)

    def pop(self):
        return self.list.pop()  #Xóa và trả về phần tử cuối cùng trong list
    
    def isEmpty(self):
        if len(self.list) == 0:
            return True
        else:
            return False

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
    
#Dùng hàm để tính toán độ ưu tiên
class PriorityQueueWithFunction(PriorityQueue):
    def __init__(self, priorityFunction):
        self.priorityFunction = priorityFunction
        super().__init__(self)
    
    def push(self, item):
        super().push(self, item, self.priorityFunction(item))

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