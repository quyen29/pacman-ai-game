from characters.agents import Agent, Actions, Directions
from characters.ghosts.blinky import BlinkySearchProblem
from ai.search_algorithms import pacmanASS
from ai.utilities import manhattanDistance
import random

class Pinky(Agent):
    def __init__(self, index=2):
        super().__init__(index)
        self.mode = "chase"
        self.scatter_target = (2, 2) # Góc trên trái

    def set_mode(self, mode):
        self.mode = mode

    def getAction(self, state):
        ghost_state = state.getGhostState(self.index)
        pacman_state = state.getPacmanState()
        pacman_pos = pacman_state.getPosition()

        if self.mode == 'frightened' or ghost_state.scaredTimer > 0:
            legal = state.getLegalActions(self.index)
            legal = [a for a in legal if a != Directions.STOP]
            if not legal:
                return Directions.STOP
            return random.choice(legal)

        if self.mode == 'scatter':
            goal = self.scatter_target
        elif self.mode == 'chase':
            dx, dy = Actions.directionToVector(pacman_state.getDirection(), 1)
            goal = (int(pacman_pos[0] + 4 * dx), int(pacman_pos[1] + 4 * dy))
        else:
            return Directions.STOP

        problem = BlinkySearchProblem(state, goal, self.index)
        path = pacmanASS(problem, heuristic=lambda pos, _: manhattanDistance(pos, goal))
        
        print(f"Pinky legal actions: {state.getLegalActions(self.index)}")
        print(f"Pinky planned path: {path}")
        legal = state.getLegalActions(self.index)
        legal = [a for a in legal if a != Directions.STOP]

        if path:
            for move in path:
                if move in legal:
                    return move

        if legal:
            return legal[0]  # hoặc random.choice(legal)
        return Directions.STOP
    