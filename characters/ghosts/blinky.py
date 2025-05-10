from characters.agents import Agent, Directions, Layout, Modes, GhostModeController
from ai.search_algorithms import a_star_search
from ai.utilities import GhostSearchProblem, manhattanDistance
from game.state import GameState
from ultils.prng import PRNG

class Blinky(Agent):
    def __init__(self, index=1):
        super().__init__(index)
        self.prng = PRNG(seed=42)
        self.scatter_target = (2, 26) # Quay về góc trên phải
        self.mode_controller = GhostModeController()

    def getAction(self, state: GameState):
        blinky_state = state.getGhostState(self.index)
        legal = state.getLegalActions(self.index)
        mode = self.mode_controller.get_mode(blinky_state)
        pacman_pos = state.getPacmanPosition()

        walls = state.getWalls()

        if mode == Modes.FRIGHTENED or blinky_state.scaredTimer > 0:
            print(f"Blinky Pos: {blinky_state.getPosition()}, Mode: {mode}")
            if legal:
                return legal[self.prng.next() % len(legal)]
            else:
                return Directions.STOP

        if mode == Modes.CHASE:
            goal = pacman_pos
        elif mode == Modes.SCATTER:
            goal = self.scatter_target
        else:
            goal = pacman_pos # fallback
        if walls[int(goal[0])][int(goal[1])]:
            print(f"Muc tieu {goal} la tuong! Muc tieu chuyen sang goc phan tan")
            goal = self.scatter_target
        
        problem = GhostSearchProblem(state, goal, self.index)
        path = a_star_search(problem, heuristic=lambda pos, _: manhattanDistance(pos, goal))
        print(f"Blinky Pos: {blinky_state.getPosition()}, Goal: {goal}, Mode: {mode}")
        print(f"Cac hanh dong hop le cua Blinky: {state.getLegalActions(self.index)}")
        print(f"Ke hoach duong di cua Blinky: {path}")
        
        if path and path[0] in legal:
            return path[0]
        else:
            if legal:
                return legal[0]
            else:
                return Directions.STOP