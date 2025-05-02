from characters.agents import Agent
from ai.searchAgents import BlinkySearchProblem
from ai.search_alrogithms import pacmanASS
from ai.utilities import manhattanDistance
from ultils.prng import PRNG

class Blinky(Agent):
    def __init__(self, index=1):
        super().__init__(index)
        self.mode = 'chase'
        self.prng = PRNG(seed=12345)

    def set_mode(self, mode):
        self.mode = mode

    def getAction(self, state):
        blinky_state = state.getGhostState(self.index)
        blinky_pos = blinky_state.getPosition()

        if self.mode == 'frightened' or blinky_state.scaredTimer > 0:
            legal = state.getLegalActions(self.index)
            legal = [a for a in legal if a != 'Stop']
            if not legal:
                return 'Stop'
            index = self.prng.next() % len(legal)
            return legal[index]
        elif self.mode == 'scatter':
            goal = (0, state.getWalls().width - 1)
        else:
            goal = state.getPacmanPosition()
        
        problem = BlinkySearchProblem(blinky_pos, goal, state)
        path = pacmanASS(problem, heuristic=manhattanDistance)

        return path[0] if path else 'Stop'
    