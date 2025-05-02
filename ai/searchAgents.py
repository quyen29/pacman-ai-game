import time

from characters.pacman import *
from ai.utilities import SearchProblem, manhattanDistance
from ai.search_alrogithms import *

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
    
class BlinkySearchProblem(SearchProblem):
    def __init__(self, start, goal, game_state, ghost_index=1):
        self.start = start
        self.goal = goal
        self.game_state = game_state
        self.ghost_index = ghost_index

    def getStartState(self):
        return self.start
    
    def isGoalState(self, state):
        return state == self.goal
    
    def getSuccessors(self, state):
        successors = []
        directions = {
            'North': (0, 1),
            'South': (0, -1),
            'East': (1, 0),
            'West': (-1, 0)
        }

        for action, (dx, dy) in directions.items():
            next_x, next_y = int(state[0] + dx), int(state[1] + dy)
            if not self.game_state.hasWall(next_x, next_y):
                successors.append(((next_x, next_y), action, 1))
            
        return successors

    def getCostOfActions(self, actions):
        return len(actions)
    

