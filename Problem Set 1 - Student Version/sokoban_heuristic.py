from sokoban import SokobanProblem, SokobanState
from mathutils import Direction, Point, manhattan_distance
from helpers.utils import NotImplemented

# This heuristic returns the distance between the player and the nearest crate as an estimate for the path cost
# While it is consistent, it does a bad job at estimating the actual cost thus the search will explore a lot of nodes before finding a goal
def weak_heuristic(problem: SokobanProblem, state: SokobanState):
    return min(manhattan_distance(state.player, crate) for crate in state.crates) - 1

#TODO: Import any modules and write any functions you want to use
from typing import List

def ckmin(a: int, b: int) -> bool:
    return min(a,b), b < a

def hungarian(cost_matrix: List[List[float]]) -> int:
    '''
        Given J jobs and W workers, the cost_matrix is a JxW matrix where cost_matrix[j][w] is the cost of assigning job j to worker w.
        The function returns the minimum cost of assigning each job to a worker such that each worker is assigned at most one job.
        Implementation inspired from: https://en.wikipedia.org/wiki/Hungarian_algorithm
    '''
    J = len(cost_matrix)
    W = len(cost_matrix[0])
    # job[w] = job assigned to w-th worker, -1 if not assigned
    # note: a W-th worker was added for convencience
    job = [-1] * (W + 1)
    ys = [0] * (J)
    # -yt[W] will equal the sum of all deltas
    yt = [0] * (W + 1)
    answer = -1
    for j_cur in range(J): # assign j_cur-th job
        w_cur = W
        job[w_cur] = j_cur
        # min reduced cost over edges from Z to worker w
        min_to = [float('inf')] * (W + 1)
        prv = [-1] * (W + 1) # previous woker on alternating path
        in_Z = [False] * (W + 1) # whether worker is in Z
        while job[w_cur] != -1: # runs at most j_cur + 1 times
            in_Z[w_cur] = True
            j = job[w_cur]
            delta = float('inf')
            w_next = None
            for w in range(W):
                if not in_Z[w]:
                    min_to[w], is_smaller = ckmin(min_to[w], cost_matrix[j][w] - ys[j] - yt[w])
                    if is_smaller:
                        prv[w] = w_cur
                    delta, is_smaller = ckmin(delta, min_to[w])
                    if is_smaller:
                        w_next = w
            # delta will always be non-negative
            # except possibly during the first time this loop runs
            # if any entries of cost_matrix[j_cur] are negative
            for w in range(W + 1):
                if in_Z[w]:
                    ys[job[w]] += delta
                    yt[w] -= delta
                else:
                    min_to[w] -= delta
            w_cur = w_next
        # update assignments along alternating path
        w = None
        while w_cur != W:
            w = prv[w_cur]
            job[w_cur] = job[w]
            w_cur = w
        answer = -yt[W]
    return answer


def strong_heuristic(problem: SokobanProblem, state: SokobanState) -> float:
    #TODO: ADD YOUR CODE HERE
    #IMPORTANT: DO NOT USE "problem.get_actions" HERE.
    # Calling it here will mess up the tracking of the expanded nodes count
    # which is the number of get_actions calls during the search
    #NOTE: you can use problem.cache() to get a dictionary in which you can store information that will persist between calls of this function
    # This could be useful if you want to store the results heavy computations that can be cached and used across multiple calls of this function
    
    # Cache pair wise distance between any two points
    if 'distances' not in problem.cache():
        # construct for each of the goals a bfs distance matrix to all tiles in the layout
        # while moving only in the 4 cardinal directions
        # if a tile is not reachable from a goal, the distance is set to infinity
        # if a tile is reachable then you need to check if we took another step
        # from the direction we just came from, does it hit a wall or not (meaning not in walkable)
        # if it does then the distance is set to infinity, if not then the distance is set to the number of steps taken
        distances = {}
        mx = problem.layout.height * problem.layout.width + 1
        for goal in problem.layout.goals:
            distance = [[mx] * problem.layout.height for _ in range(problem.layout.width)]
            distance[goal.x][goal.y] = 0
            queue = [goal]
            while queue:
                current = queue.pop(0)
                for direction in Direction:
                    next_tile = current + direction.to_vector()
                    if next_tile not in problem.layout.walkable:
                        continue
                    if distance[next_tile.x][next_tile.y] == mx:
                        forward_tile = next_tile + direction.to_vector()
                        if forward_tile in problem.layout.walkable:
                            distance[next_tile.x][next_tile.y] = distance[current.x][current.y] + 1
                            queue.append(next_tile)
            distances[goal] = distance
        problem.cache()['distances'] = distances
        problem.cache()['solved_states'] = {}

    # check if the state is already solved by sorting crates and hashing them
    # and check if hash key in problem.cache()['solved_states']

    sorted_crates = sorted(state.crates, key=lambda point: (point.x, point.y))
    state_hash = hash(tuple(sorted_crates))
    if state_hash in problem.cache()['solved_states']:
        return problem.cache()['solved_states'][state_hash]

    cost_matrix = []
    for crate in state.crates:
        row = []
        for goal in problem.layout.goals:
            row.append(problem.cache()['distances'][goal][crate.x][crate.y])
        cost_matrix.append(row)
    
    problem.cache()['solved_states'][state_hash] = hungarian(cost_matrix)
    return problem.cache()['solved_states'][state_hash]