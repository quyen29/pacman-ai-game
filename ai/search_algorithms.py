from ai.utilities import *
def pacmanDFS(problem):
    frontier = Stack()
    frontier.push(problem.getStartState())
    visited = []
    path = []
    explore = []

    while not frontier.isEmpty():
        currState = frontier.pop()
        if len(explore) > 0:
            path = explore.pop()

        if problem.isGoalState(currState):
            return path

        if currState not in visited:
            visited.append(currState)
            successors = problem.getSuccessors(currState)
            for child, direction, cost in successors:
                frontier.push(child)
                tempPath = path + [direction]
                explore.append(tempPath)  #Thêm đường đi mới vào
    return []

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

def pacmanUCS(problem):
    frontier = PriorityQueue()
    frontier.push(problem.getStartState(), 0)
    visited = []
    path = []
    explore = PriorityQueue()
    while not frontier.isEmpty():
        currState = frontier.pop()
        if len(explore) > 0:
            path = explore.pop()

        if problem.isGoalState(currState):
            return path
        
        if currState not in visited:
            visited.append(currState)
            successors = problem.getSuccessors(currState)
            for child, direction, cost in successors:
                tempPath = path + [direction]
                costToGo = problem.getCostOfActions(tempPath)
                if child not in visited:
                    frontier.push(child, costToGo)
                    explore.push(tempPath, costToGo)
    return []

#Dùng trong trường hợp dùng thuật toán A* nhưng không có hàm heuristic thực tế
def pacmanNullHeuristic(static, problem = None):
    return 0

def pacmanASS(problem, heuristic = pacmanNullHeuristic):
    frontier = PriorityQueue()
    frontier.push(problem.getStartState(), 0)
    visited = []
    path = []
    explore = PriorityQueue()
    explore.push([], 0)
    while not frontier.isEmpty():
        currState = frontier.pop()
        if len(explore) > 0:
            path = explore.pop()

        if problem.isGoalState(currState):
            return path
        
        if currState not in visited:
            visited.append(currState)
            successors = problem.getSuccessors(currState)
            for child, direction, cost in successors:
                tempPath = path + [direction]
                costToGo = problem.getCostOfActions(tempPath) + heuristic(child, problem)
                if child not in visited:
                    frontier.push(child, costToGo)
                    explore.push(tempPath, costToGo)
    return []

def a_star_search(problem: SearchProblem, heuristic):
    frontier = PriorityQueue()
    start = problem.getStartState()
    frontier.push((start, [], 0), heuristic(start, problem))
    visited = set()

    while not frontier.isEmpty():
        curr_state, path, cost_so_far = frontier.pop()

        if problem.isGoalState(curr_state):
            return path
        if curr_state in visited:
            continue
        visited.add(curr_state)

        for next_state, action, step_cost in problem.getSuccessors(curr_state):
            if next_state not in visited:
                new_path = path + [action]
                new_cost = cost_so_far + step_cost
                priority = new_cost + heuristic(next_state, problem)
                frontier.push((next_state, new_path, new_cost), priority)
        
    return []