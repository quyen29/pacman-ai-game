from characters.agents import Agent
import random

class Pacman(Agent):
    def __init__(self, index=0):
        super().__init__(index)

    def getAction(self, state):
        legal_actions = state.getLegalActions(self.index)
        legal_actions = [a for a in legal_actions if a != 'Stop']
        if not legal_actions:
            return 'Stop'
        return random.choice(legal_actions)
