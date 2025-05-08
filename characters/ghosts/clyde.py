from characters.agents import Agent
from characters.agents import Directions,Actions
import random
class Clyde(Agent):
    def __init__(self, index=4):
        super().__init__(index)
    def getAction(self, state):
        walls = state.getWalls()
        legal = state.getLegalActions(self.index)
        legal = [a for a in legal if a != Directions.STOP]  # Bỏ qua hành động đứng yên
        if legal:
            return random.choice(legal)
        return Directions.STOP