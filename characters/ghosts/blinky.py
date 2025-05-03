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
        self.scattertarget = (27, 0)

    def getAction(self, state=GameState):
        blinky_state = state.getGhostState(self.index)
        blinky_pos = blinky_state.getPosition()
        pacman_pos = state.getPacmanPosition()

        if blinky_state.scaredTimer > 0:
            legal = state.getLegalActions(self.index)
            legal = [a for a in legal if a != Directions.STOP]
            if not legal:
                return Directions.STOP
            
            direction_priority = [Directions.NORTH, Directions.WEST, Directions.SOUTH, Directions.EAST]
            seed_index = self.prng.next() % len(direction_priority)
            preferred = direction_priority[seed_index]

            if preferred in legal:
                return preferred
            for direction in direction_priority:
                if direction in legal:
                    return direction
            return Directions.STOP
    
        if hasattr(state, 'isInChaseMode') and state.isInChaseMode():
            target = pacman_pos
        elif hasattr(state, 'isInScatterMode') and state.isInScatterMode():
            target = self.scattertarget
        else:
            target = self.scattertarget
        
        problem = BlinkySearchProblem(state, goal=target, ghost_index=self.index)
        path = pacmanASS(problem, heuristic=lambda pos, _: manhattanDistance(pos, target))
        if path:
            return path[0]
        return Directions.STOP

class BlinkySearchProblem():
    def __init__(self, goal, game_state, ghost_index=1):
        self.start = game_state.getGhostState(ghost_index).getPosition()
        self.goal = goal
        self.game_state = game_state
        self.ghost_index = ghost_index
        self.walls = game_state.getWalls()

    def getStartState(self):
        return self.start
    
    def isGoalState(self, state):
        return state == self.goal
    
    def getSuccessors(self, state):
        successors = []
        for action in Directions.DIRECTIONS:
            dx, dy = Actions.directionToVector(action)
            next_x, next_y = int(state[0] + dx), int(state[1] + dy)
            if not self.walls[next_x][next_y]:
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
    