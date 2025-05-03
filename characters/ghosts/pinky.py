from characters.agents import Agent, Actions
from characters.ghosts.blinky import BlinkySearchProblem
from ai.search_algorithms import pacmanASS
from ai.utilities import manhattanDistance
import random

class Pinky(Agent):
    def __init__(self, index=3):
        super().__init__(index)
        self.mode = "chase"

    def set_mode(self, mode):
        self.mode = mode

    def getAction(self, state):
        ghost_state = state.getGhostState(self.index)
        pacman_state = state.getPacmanState()
        ghost_pos = ghost_state.getPosition()
        pacman_pos = pacman_state.getPosition()

        if self.mode == 'frightened' or ghost_state.scaredTimer > 0:
            legal = state.getLegalActions(self.index)
            legal = [a for a in legal if a != 'Stop']
            if not legal:
                return 'Stop'
            return random.choice(legal)

        if self.mode == 'scatter':
            goal = (0, 0)  # Góc trên trái
        elif self.mode == 'chase':
            dx, dy = Actions.directionToVector(pacman_state.getDirection(), 1)
            goal = (int(pacman_pos[0] + 4 * dx), int(pacman_pos[1] + 4 * dy))
        else:
            return 'Stop'

        problem = BlinkySearchProblem(ghost_pos, goal, state)
        path = pacmanASS(problem, heuristic=manhattanDistance)
        return path[0] if path else 'Stop'
    