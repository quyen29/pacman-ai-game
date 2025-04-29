import time

from characters.pacman import *
from utilities import *
from search_alrogithms import *

def scoreEvaluationFunction(currentGameState):
    return currentGameState.getScore()

def betterEvaluationFunction(currentGameState):
    """
    - Các đặc điểm của hàm đánh giá này:
        + Ưu tiên ăn các dots
        + Ưu tiên ăn ghosts khi ghosts ở trạng thái hoảng sợ
        + Tránh ghosts
        + Tính khoảng cách manhattan
    """
    

