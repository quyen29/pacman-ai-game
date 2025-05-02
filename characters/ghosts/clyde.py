from characters.agents import Agent, Actions
from ai.searchAgents import BlinkySearchProblem
from ai.search_alrogithms import pacmanASS
from ai.utilities import manhattanDistance
from ultils.prng import PRNG

class Clyde(Agent):
    def __init__(self, index=4):
        super().__init__(index)
        self.mode = 'chase'
        self.prng = PRNG(seed=12345)

    def setMode(self, mode):
        self.mode = mode
    
    def getAction(self, state):
        clyde_state = state.getGhostState(self.index)
        clyde_pos = clyde_state.getPosition()
        pacman_pos = state.getPacmanPosition()

        if self.mode == 'frightened' or clyde_state.scaredTimer > 0:
            legal = state.getLegalActions(self.index)
            legal = [a for a in legal if a !=  'Stop']
            if not legal:
                return 'Stop'
            index = self.prng.next() % len(legal)
            return legal[index]
        elif self.mode == 'scatter':
            goal = (state.getWalls().height - 1, 0)
        elif self.mode == 'chase':
            dist = manhattanDistance(clyde_pos, pacman_pos)
            if dist > 8:
                goal = pacman_pos
            else:
                goal = (state.getWalls().height - 1, 0)
        else:
            return 'Stop'
        
        problem = BlinkySearchProblem(clyde_pos, goal, state)
        path = pacmanASS(problem, heuristic=manhattanDistance)

        return path[0] if path else 'Stop'
    