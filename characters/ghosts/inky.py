from characters.agents import Agent, Actions, Directions
from characters.ghosts.blinky import BlinkySearchProblem
from ai.search_algorithms import pacmanASS
from ai.utilities import manhattanDistance
import random

class Inky(Agent):
    def __init__(self, index=3):
        super().__init__(index)
        self.mode = "chase"
        self.scatter_target = (28, 26) # Góc dưới phải

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
            legal = [a for a in legal if a != Directions.STOP]
            if not legal:
                return Directions.STOP
            return random.choice(legal)

        if self.mode == 'scatter':
            goal =  self.scatter_target
        elif self.mode == 'chase':
            dx, dy = Actions.directionToVector(pacman_state.getDirection(), 1)
            px, py = pacman_pos
            ahead_pos = (int(px + 2 * dx), int(py + 2 * dy))
            # Vector: Blinky -> ahead → nhân đôi
            vx = ahead_pos[0] - blinky_pos[0]
            vy = ahead_pos[1] - blinky_pos[1]
            goal = (blinky_pos[0] + 2 * vx, blinky_pos[1] + 2 * vy)
        else:
            return Directions.STOP

        problem = BlinkySearchProblem(state, goal, self.index)
        path = pacmanASS(problem, heuristic=lambda pos, _: manhattanDistance(pos, goal))
        
        print(f"Inky legal actions: {state.getLegalActions(self.index)}")
        print(f"Inky planned path: {path}")
        legal = state.getLegalActions(self.index)
        legal = [a for a in legal if a != Directions.STOP]

        if path:
            for move in path:
                if move in legal:
                    return move

        if legal:
            return legal[0]  # hoặc random.choice(legal)
        return Directions.STOP
