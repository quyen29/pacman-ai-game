from ai.utilities import *

def pacmanBFS(problem):
    frontier = Queue()
    frontier.push((problem.getStartState(), []))
    visited = []

    while not frontier.isEmpty():
        currState, path = frontier.pop()

        if problem.isGoalState(currState):
            path.append(currState)
            return path

        if currState not in visited:
            visited.append(currState)
            successors = problem.getSuccessors(currState)
            for child, direction, cost in successors:
                newPath = path + [direction]
                frontier.push((child, newPath))
    return []

#Dùng trong trường hợp dùng thuật toán A* nhưng không có hàm heuristic thực tế
def pacmanNullHeuristic(static, problem = None):
    return 0

def pacmanASS(problem, heuristic = pacmanNullHeuristic):
    frontier = PriorityQueue()
    frontier.push(problem.getStartState(), 0)
    visited = set()
    path = []
    explore = PriorityQueue()
    explore.push([], 0)
    while not frontier.isEmpty():
        currState = frontier.pop()
        if not explore.isEmpty():
            path = explore.pop()

        if problem.isGoalState(currState):
            return path
        
        if currState not in visited:
            visited.add(currState)
            successors = problem.getSuccessors(currState)
            for child, direction, cost in successors:
                tempPath = path + [direction]
                costToGo = problem.getCostOfActions(tempPath) + heuristic(child, problem)
                if child not in visited:
                    frontier.push(child, costToGo)
                    explore.push(tempPath, costToGo)
    return []
