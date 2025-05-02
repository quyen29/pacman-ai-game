from characters.agents import Agent, Actions
from ai.searchAgents import BlinkySearchProblem
from ai.search_alrogithms import pacmanASS
from ai.utilities import manhattanDistance
import random

class Inky(Agent):
    def __init__(self, index=2):
        super().__init__(index)
        self.mode = "chase"

    def set_mode(self, mode):
        self.mode = mode

    def getAction(self, state):
        ghost_state = state.getGhostState(self.index)
        pacman_state = state.getPacmanState()
        ghost_pos = ghost_state.getPosition()
        pacman_pos = pacman_state.getPosition()
        blinky_pos = state.getGhostState(1).getPosition()  # Blinky = ghost 1

        if self.mode == 'frightened' or ghost_state.scaredTimer > 0:
            legal = state.getLegalActions(self.index)
            legal = [a for a in legal if a != 'Stop']
            if not legal:
                return 'Stop'
            return random.choice(legal)

        if self.mode == 'scatter':
            goal = (state.getWalls().height - 1, state.getWalls().width - 1)  # Góc dưới phải
        elif self.mode == 'chase':
            dx, dy = Actions.directionToVector(pacman_state.getDirection(), 1)
            px, py = pacman_pos
            ahead_pos = (int(px + 2 * dx), int(py + 2 * dy))
            # Vector: Blinky -> ahead → nhân đôi
            vx = ahead_pos[0] - blinky_pos[0]
            vy = ahead_pos[1] - blinky_pos[1]
            goal = (blinky_pos[0] + 2 * vx, blinky_pos[1] + 2 * vy)
        else:
            return 'Stop'

        problem = BlinkySearchProblem(ghost_pos, goal, state)
        path = pacmanASS(problem, heuristic=manhattanDistance)
        return path[0] if path else 'Stop'
