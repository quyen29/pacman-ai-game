import heapq
from ai.utilities import heuristic
from game.logic import is_valid_move

def a_star(level, start, goal):
    frontier = []
    heapq.heappush(frontier, (0, start))
    parent = {}
    gn = {}

    parent[start] = None
    gn[start] = 0

    while frontier:
        _, current = heapq.heappop(frontier)

        if current == goal:
            break

        x, y = current
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            next_pos = (x + dx, y + dy)

            if is_valid_move(level, next_pos[0] * 20, next_pos[1] * 20):
                new_cost = gn[current] + 1
                if next_pos not in gn or new_cost < gn[next_pos]:
                    gn[next_pos] = new_cost
                    priority = new_cost + heuristic(next_pos, goal)
                    heapq.heappush(frontier, (priority, next_pos))
                    parent[next_pos] = current

    path = []
    current = goal
    if goal not in parent:
        print("Không tìm thấy dường đi")
        return []
    while current != start:
        path.append(current)
        current = parent[current]
    path.reverse()
    return path


