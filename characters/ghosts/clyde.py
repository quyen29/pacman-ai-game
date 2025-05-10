from characters.agents import Agent, Directions, Modes, GhostModeController
from ai.search_algorithms import a_star_search
from ai.utilities import GhostSearchProblem, manhattanDistance
from game.state import GameState
from ultils.prng import PRNG
from math import sqrt

class Clyde(Agent):
    def __init__(self, index=4):
        super().__init__(index)
        self.prng = PRNG(seed=12345)
        self.scatter_target = (28, 2) # Góc dưới trái
        self.mode_controller = GhostModeController()
    
    def getAction(self, state: GameState):
        legal = state.getLegalActions(self.index)
        clyde_state = state.getGhostState(self.index)
        clyde_pos = clyde_state.getPosition()
        pacman_pos = state.getPacmanPosition()
        dist = manhattanDistance(pacman_pos, clyde_pos)

        mode = self.mode_controller.get_mode(clyde_state)
        if mode == Modes.FRIGHTENED or clyde_state.scaredTimer > 0:
            print(f"Blinky Pos: {clyde_state.getPosition()}, Mode: {mode}")
            if legal:
                return legal[self.prng.next()% len(legal)]
            else:
                return Directions.STOP
        if dist <= 8 or mode == Modes.SCATTER:
            goal = self.scatter_target
        elif dist > 8 or mode == Modes.CHASE:
            goal = pacman_pos
        else:
            goal = self.scatter_target

        walls = state.getWalls()
        if walls[int(goal[0])][int(goal[1])]:
            goal = self.scatter_target
        
        problem = GhostSearchProblem(state, goal, self.index)
        path = a_star_search(problem, heuristic=lambda pos, _: self.euclideanDistance(pos, goal))
        print(f"Clyde. Pos: {clyde_state.getPosition()}, Goal: {goal}, Mode: {mode}")
        print(f"Cac hanh dong hop le cua Clyde: {state.getLegalActions(self.index)}")
        print(f"Ke hoach duong di cua Clyde: {path}")
        
        if path and path[0] in legal:
            return path[0]
        else:
            if legal:
                return legal[0]
            else:
                return Directions.STOP

    @staticmethod
    def euclideanDistance(pos_1, pos_2):
        return sqrt((pos_1[0] - pos_2[0]) ** 2 + (pos_1[1] - pos_2[1]) ** 2)
    