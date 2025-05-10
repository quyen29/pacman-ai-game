from heapq import heappush, heappop
from characters.agents import Directions, Actions, Agent, GhostModeController,Modes
from ai.utilities import manhattanDistance,GhostSearchProblem
from ai.search_algorithms import pacmanASS
from game.logic import GhostRules
import random
class Pinky(Agent):
    def __init__(self, index=2):
        super().__init__(index)
        self.scatter_corner = (2, 2)
    def getAction(self, state):
        mode = state.data.mode.get_mode(state.getGhostState(self.index))
        walls = state.getWalls()
        currentPos = tuple(map(int, state.getGhostPosition(self.index)))
        pacmanPos = tuple(map(int, state.getPacmanPosition()))
        if mode ==Modes.CHASE:
            pacmanDir = state.data.agentStates[0].configuration.direction
            predicted_target = Actions.get_ahead_position(pacmanPos, pacmanDir, 4)
            target = predicted_target if manhattanDistance(currentPos, predicted_target) > manhattanDistance(currentPos, pacmanPos) else pacmanPos

        elif mode == Modes.SCATTER:
            target = self.scatter_corner

        else: 
            corners = [(2, 2), (walls.height - 3, 2), (2, walls.width - 3), (walls.height - 3, walls.width - 3)]
            valid_corners = [c for c in corners if not walls[c[0]][c[1]]]
            target = max(valid_corners, key=lambda c: manhattanDistance(c, pacmanPos)) if valid_corners else currentPos

        problem = GhostSearchProblem(state, target, self.index)
        path = pacmanASS(problem, heuristic=lambda pos, _: manhattanDistance(pos, target))
        if currentPos == target:
            legal = state.getLegalActions(self.index)
            legal = [a for a in legal if a != Directions.STOP]
            return random.choice(legal) if legal else Directions.STOP
        elif path:
            next_move = path[0]
            legal = GhostRules.getLegalActions(state, self.index) 
            if next_move not in legal:
                legal = state.getLegalActions(self.index)
                legal = [a for a in legal if a != Directions.STOP]
                next_move=random.choice(legal)
            return next_move

        legal = state.getLegalActions(self.index)
        legal = [a for a in legal if a != Directions.STOP]
        return random.choice(legal) if legal else Directions.STOP