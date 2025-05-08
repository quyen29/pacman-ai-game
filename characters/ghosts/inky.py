from characters.agents import Agent, Directions, Modes, GhostModeController, Actions
from ai.search_algorithms import a_star_search
from ai.utilities import GhostSearchProblem, manhattanDistance
from game.state import GameState
from ultils.prng import PRNG

class Inky(Agent):
    def __init__(self, index=3):
        super().__init__(index)
        self.prng = PRNG(seed=67890)  # Seed riêng để đảm bảo hành vi ngẫu nhiên
        self.scatter_target = (28, 27)  # Góc dưới phải của mê cung
        self.mode_controller = GhostModeController()
    
    def getAction(self, state: GameState):
        inky_state = state.getGhostState(self.index)
        legal = state.getLegalActions(self.index)
        mode = self.mode_controller.get_mode()
        pacman_pos = state.getPacmanPosition()
        pacman_direction = state.data.agentStates[0].configuration.direction
        walls = state.getWalls()
        
        # Chế độ sợ hãi (Frightened) hoặc khi scaredTimer > 0
        if inky_state.scaredTimer > 0 or mode == Modes.FRIGHTENED:
            if legal:
                return legal[self.prng.next() % len(legal)]
            return Directions.STOP
        
        # Tính toán mục tiêu
        if mode == Modes.CHASE:
            # Tính vị trí mục tiêu của Inky dựa trên Pac-Man và Blinky
            blinky_pos = state.getGhostPosition(1)  # Blinky là ghost index 1
            # Lấy vị trí phía trước Pac-Man 2 bước
            intermediate_pos = self.get_intermediate_position(pacman_pos, pacman_direction)
            # Tính điểm đối xứng qua Blinky
            goal = self.calculate_symmetric_target(intermediate_pos, blinky_pos)
        else:  # Modes.SCATTER
            goal = self.scatter_target
        
        # Kiểm tra nếu mục tiêu là tường, chuyển sang scatter target
        if walls[int(goal[0])][int(goal[1])]:
            goal = self.scatter_target
        
        # Tìm đường bằng A* search
        problem = GhostSearchProblem(state, goal, self.index)
        path = a_star_search(problem, heuristic=lambda pos, _: manhattanDistance(pos, goal))
        
        print(f"Inky Pos: {inky_state.getPosition()}, Goal: {goal}, Mode: {mode}")
        print(f"Inky legal actions: {legal}")
        print(f"Inky planned path: {path}")
        
        if path and path[0] in legal:
            return path[0]
        if legal:
            return legal[0]
        return Directions.STOP
    
    def get_intermediate_position(self, pacman_pos, pacman_direction):
        """Tính vị trí phía trước Pac-Man 2 bước theo hướng di chuyển."""
        dx, dy = Actions.directionToVector(pacman_direction, speed=2)
        x, y = pacman_pos
        tx, ty = x + dx, y + dy
        # Ràng buộc trong giới hạn bản đồ (dựa trên board.py và state.py)
        tx = max(0, min(tx, 32))  # Chiều cao mê cung
        ty = max(0, min(ty, 29))  # Chiều rộng mê cung
        return (tx, ty)
    
    def calculate_symmetric_target(self, intermediate_pos, blinky_pos):
        """Tính điểm đối xứng của vị trí trung gian qua Blinky."""
        ix, iy = intermediate_pos
        bx, by = blinky_pos
        # Vector từ Blinky đến vị trí trung gian
        dx, dy = ix - bx, iy - by
        # Đối xứng qua Blinky: Blinky + (vector * 2)
        tx, ty = bx + 2 * dx, by + 2 * dy
        # Ràng buộc trong giới hạn bản đồ
        tx = max(0, min(tx, 32))
        ty = max(0, min(ty, 29))
        return (tx, ty)