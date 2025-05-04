from characters.agents import Actions, Agent, Directions
from ai.search_algorithms import pacmanASS
from ai.utilities import manhattanDistance
from game.state import GameState
from ultils.prng import PRNG

class Blinky(Agent):
    def __init__(self, index=1):
        super().__init__(index)
        self.mode = 'chase'
        self.prng = PRNG(seed=12345)
        self.scattertarget = (27, 0) # Quay về góc trên phải

    def getAction(self, state: GameState):
        blinky_state = state.getGhostState(self.index)
        pacman_pos = state.getPacmanPosition()

        if blinky_state.scaredTimer > 0:
            legal = state.getLegalActions(self.index)
            legal = [a for a in legal if a != Directions.STOP]
            if not legal:
                return Directions.STOP
            
            direction_priority = [Directions.NORTH, Directions.WEST, Directions.SOUTH, Directions.EAST]
            choice = self.prng.next() % len(direction_priority)
            preferred = direction_priority[choice]

            if preferred in legal:
                return preferred
            for direction in direction_priority:
                if direction in legal:
                    return direction
            return Directions.STOP
    
        if hasattr(state, 'isInChaseMode') and state.isInChaseMode():
            target = pacman_pos
        else:
            target = self.scattertarget
        
        problem = BlinkySearchProblem(state, target, self.index)
        path = pacmanASS(problem, heuristic=lambda pos, _: manhattanDistance(pos, target))
        if path:
            return path[0]
        return Directions.STOP

class BlinkySearchProblem():
    def __init__(self, state: GameState, goal, ghost_index=1):
        self.start = state.getGhostState(ghost_index).getPosition()
        self.goal = goal
        self.ghost_index = ghost_index
        self.walls = state.getWalls()
        self.directions = [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]

    def getStartState(self):
        return self.start
    
    def isGoalState(self, state):
        return state == self.goal
    
    def getSuccessors(self, state):
        successors = []
        for action in self.directions:
            dx, dy = Actions.directionToVector(action)
            next_x, next_y = int(state[0] + dx), int(state[1] + dy)
            if 0 <= next_x < self.walls.getWidth() and 0 <= next_y < self.walls.getHeight() and not self.walls[next_x][next_y]:
                successors.append(((next_x, next_y), action, 1))
            
        return successors

    def getCostOfActions(self, actions):
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
    