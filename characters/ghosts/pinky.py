from heapq import heappush, heappop
from characters.agents import Directions, Actions, Agent, Configuration, Grid
from ai.utilities import manhattanDistance
from collections import deque
from game.state import GhostRules
from queue import PriorityQueue
import random

TILE_SIZE = 20
WIDTH = 30 * TILE_SIZE
HEIGHT = 38 * TILE_SIZE

def getPinkyPosition(state):
    pinkyPos = state.data.agentStates[2].getPosition()
    pinky_x = int(pinkyPos[1] / TILE_SIZE)
    pinky_y = int(pinkyPos[0] / TILE_SIZE) - 3
    return (pinky_x, pinky_y)

class Pinky(Agent):
    def __init__(self, index=2):
        super().__init__(index)
        self.scared_target = None
        self.scared_path = []

    def getAction(self, state):
        scared_timer = state.getGhostState(self.index).scaredTimer
        print("Chế độ:", "sợ" if scared_timer > 0 else "đuổi bắt", "| ScaredTimer =", scared_timer)
        if state.getGhostState(2).scaredTimer == 0:
            self.scared_target = None
            self.scared_path = []
            walls = state.getWalls()
            currentPos = tuple(map(int, state.getGhostPosition(self.index)))
            currentDirection = state.getGhostState(2).configuration.direction
            # Lấy vị trí và hướng di chuyển của Pacman
            pacmanPos = tuple(map(int, state.getPacmanPosition()))
            pacmanDirection = state.data.agentStates[0].configuration.direction  # Lấy hướng di chuyển của Pacman

            # Tính toán điểm mục tiêu mà Pinky muốn đến dựa trên hướng di chuyển của Pacman
            target = self.calculateTarget(pacmanPos, pacmanDirection)
            predicted_target = Actions.get_ahead_position(pacmanPos, pacmanDirection, 4)
           
            if manhattanDistance(currentPos, pacmanPos) < manhattanDistance(currentPos, predicted_target):
                target = pacmanPos
            else:
                target = predicted_target
            x,y = target
            #Tim target hop le
            if 0 <= x <= walls.height and 0 <= y <= walls.width:
                if walls[x][y]:
                    neighbor = Actions.getLegalNeighbors(target, walls)
                    if not neighbor:
                        target = pacmanPos
                    else:
                        closest = min(neighbor, key=lambda p: manhattanDistance(p, currentPos))
                        neighbor.remove(closest)
                        target = closest
            else:
                #print(f"Target ({x},{y}) nằm ngoài bản đồ (max x: {walls.width - 1}, max y: {walls.height - 1})")
                target = pacmanPos
            # Tìm đường đến điểm mục tiêu
            path = self.aStar(currentPos, target, walls,currentDirection)
            if path:
                #đổi hướng cho pinky
                state.getGhostState(2).configuration.direction = path[0]  
                return path[0]
            else: 
                neighbors = Actions.getLegalNeighbors(target, walls)
                for nei in neighbors:
                    #print("Vị trí hàng xóm đang được xét", neighbor)
                    path = self.aStar(currentPos, nei, walls,currentDirection)
                    if path:
                        state.getGhostState(2).configuration.direction = path[0]  # hoặc bất kỳ hướng nào
                
                        return path[0]
                    else:
                        path = self.aStar(currentPos, pacmanPos, walls,currentDirection)
                        if path:
                        
                            state.getGhostState(2).configuration.direction = path[0]  
                            return path[0]
                        else:
                            legal = state.getLegalActions(self.index)
                            legal = [a for a in legal if a != Directions.STOP]  # Bỏ qua hành động đứng yên
                            if legal:
                                return random.choice(legal)
            return Directions.STOP
        # Chế độ scared: tránh xa Pacman
        else:    
            currentPos = tuple(map(int, state.getGhostPosition(self.index)))
            pacmanPos = tuple(map(int, state.getPacmanPosition()))
            walls = state.getWalls()
            currentDirection = state.getGhostState(2).configuration.direction

            if self.scared_target is None:
                print("Khởi tạo lần đầu")
                # Chỉ tính 1 lần khi bắt đầu sợ
                height, width = walls.height, walls.width
                corners = [(2, 2), (height - 3, 2), (2,width - 3), (height - 3,width - 3)]
                valid_corners = [c for c in corners if not walls[c[0]][c[1]]]
                print("các góc hợp lệ",valid_corners)
                if valid_corners:
                    self.scared_target = max(valid_corners, key=lambda p: manhattanDistance(p, pacmanPos))
                    print(f"🎯 Pinky target (scared): {self.scared_target}")
                    self.scared_path = self.aStar(currentPos, self.scared_target, walls, currentDirection)
            if self.scared_target:  
                next_move = self.scared_path.pop(0)
                print("hanh dong bi loi",next_move)
                state.getGhostState(2).configuration.direction = next_move
                legal = GhostRules.getLegalActions(state, self.index) 
                if next_move not in legal:
                    print("hanh dong ko hop le, tim lai duong di phu hop")
                    self.scared_path = self.aStar(currentPos, self.scared_target, walls, random.choice(legal))
                    next_move = self.scared_path.pop(0)
                return next_move
            else:
                self.scared_target = None

    def calculateTarget(self, pacmanPos, pacmanDirection):
        dx, dy = 0, 0
        if pacmanDirection == Directions.NORTH:
            dy = -4
        elif pacmanDirection == Directions.SOUTH:
            dy = 4
        elif pacmanDirection == Directions.EAST:
            dx = 4
        elif pacmanDirection == Directions.WEST:
            dx = -4

        tx = pacmanPos[0] + dx
        ty = pacmanPos[1] + dy

        # Ràng buộc không vượt khỏi giới hạn bản đồ
        tx = max(0, min(tx, 29))
        ty = max(0, min(ty, 32))

        return (tx, ty)

    def aStar(self, start, goal, walls, prevDirection):
        openSet = PriorityQueue()
        openSet.put((0, start, []))
        visited = set()

        opposite = {
        Directions.NORTH: Directions.SOUTH,
        Directions.SOUTH: Directions.NORTH,
        Directions.EAST: Directions.WEST,
        Directions.WEST: Directions.EAST
        }

        while not openSet.empty():
            _, current, path = openSet.get()
            #print("openSet", openSet)
            if current in visited:
                continue
            visited.add(current)

            if current == goal:
                print("a*", path)
                return path

            for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
                nextPos = Actions.getSuccessor(current, direction)
                x, y = int(nextPos[0]), int(nextPos[1])
                if 0 <= x < walls.height and 0 <= y < walls.width and not walls[x][y]:
                    newPath = path + [direction]
                    #print("newPath", newPath)
                    cost = len(newPath) + self.heuristic((x, y), goal)
                    openSet.put((cost, (x, y), newPath))

        return []

    def heuristic(self, pos, goal):
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])
    
    

