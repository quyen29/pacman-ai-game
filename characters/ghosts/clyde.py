from characters.agents import Agent, Directions
from characters.ghosts.blinky import BlinkySearchProblem
from ai.search_algorithms import pacmanASS
from ai.utilities import manhattanDistance
from ultils.prng import PRNG
from math import sqrt

class Clyde(Agent):
    def __init__(self, index=4):
        super().__init__(index)
        self.mode = 'chase'
        self.prng = PRNG(seed=12345)
        self.scatter_target = (28, 2) # Góc dưới trái

    def setMode(self, mode):
        self.mode = mode
    
    def getAction(self, state):
        clyde_state = state.getGhostState(self.index)
        clyde_pos = clyde_state.getPosition()
        pacman_pos = state.getPacmanPosition()

        if self.mode == 'frightened' or clyde_state.scaredTimer > 0:
            legal = state.getLegalActions(self.index)
            legal = [a for a in legal if a !=  Directions.STOP]
            if not legal:
                return Directions.STOP
            index = self.prng.next() % len(legal)
            return legal[index]
        elif self.mode == 'scatter':
            goal = self.scatter_target
        elif self.mode == 'chase':
            dist = self.euclideanDistance(clyde_pos, pacman_pos)
            if dist > 8:
                goal = pacman_pos
            else:
                goal = self.scatter_target
        else:
            return Directions.STOP
        
        problem = BlinkySearchProblem(state, goal, self.index)
        path = pacmanASS(problem, heuristic=lambda pos, _: manhattanDistance(pos, goal))

        print(f"Clyde legal actions: {state.getLegalActions(self.index)}")
        print(f"Clyde planned path: {path}")
        legal = state.getLegalActions(self.index)
        legal = state.getLegalActions(self.index)
        legal = [a for a in legal if a != Directions.STOP]

        if path:
            for move in path:
                if move in legal:
                    return move

        if legal:
            return legal[0]  # hoặc random.choice(legal)
        return Directions.STOP

    @staticmethod
    def euclideanDistance(pos_1, pos_2):
        return sqrt((pos_1[0] - pos_2[0]) ** 2 + (pos_1[1] - pos_2[1]) ** 2)
    