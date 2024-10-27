from problem import HeuristicFunction, Problem, S, A, Solution
from collections import deque
from helpers.utils import NotImplemented

from queue import PriorityQueue
from typing import List

# All search functions take a problem and a state
# If it is an informed search function, it will also receive a heuristic function
# S and A are used for generic typing where S represents the state type and A represents the action type

# All the search functions should return one of two possible type:
# 1. A list of actions which represent the path from the initial state to the final state
# 2. None if there is no solution

def BreadthFirstSearch(problem: Problem[S, A], initial_state: S) -> Solution:
    queue = deque()
    actions = []
    visited = set()
    queue.append((initial_state, actions))
    while queue:
        state, actions = queue.popleft()
        if problem.is_goal(state):
            return actions
        if state in visited:
            continue
        visited.add(state)
        for action in problem.get_actions(state):
            new_state = problem.get_successor(state, action)
            new_actions = actions + [action]
            if problem.is_goal(new_state):
                return new_actions
            if new_state not in visited:
                queue.append((new_state, new_actions))
    return None

def DFSUtil(problem: Problem[S, A], state: S, visited: set, actions: List[A]) -> Solution:
    if problem.is_goal(state):
        return actions
    if state in visited:
        return None
    visited.add(state)
    for action in problem.get_actions(state):
        new_state = problem.get_successor(state, action)
        new_actions = actions + [action]
        result = DFSUtil(problem, new_state, visited, new_actions)
        if result is not None:
            return result
    return None

def DepthFirstSearch(problem: Problem[S, A], initial_state: S) -> Solution:
    return DFSUtil(problem, initial_state, set(), [])
    

class PQItem:
    def __init__(self, cost: float, state: S, actions: List[A], time: int):
        self.cost = cost
        self.state = state
        self.actions = actions
        self.time = time

    def __lt__(self, other):
        if self.cost == other.cost:
            return self.time < other.time
        return self.cost < other.cost

def UniformCostSearch(problem: Problem[S, A], initial_state: S) -> Solution:
    pq = PriorityQueue()
    time = 0
    pq.put(PQItem(0, initial_state, [], time))
    time += 1
    visited = dict()
    while not pq.empty():
        item = pq.get()
        cost, state, actions = item.cost, item.state, item.actions
        if state in visited and visited[state] <= cost:
            continue
        if problem.is_goal(state):
            return actions
        visited[state] = cost
        for action in problem.get_actions(state):
            new_state = problem.get_successor(state, action)
            new_actions = actions + [action]
            new_cost = cost + problem.get_cost(state, action)
            if new_state not in visited or visited[new_state] > new_cost:
                pq.put(PQItem(new_cost, new_state, new_actions, time))
                time += 1
    return None

def AStarSearch(problem: Problem[S, A], initial_state: S, heuristic: HeuristicFunction) -> Solution:
    pq = PriorityQueue()
    time = 0
    pq.put(PQItem(0, initial_state, [], time))
    time += 1
    visited = dict()
    while not pq.empty():
        item = pq.get()
        cost, state, actions = item.cost, item.state, item.actions
        if state in visited and visited[state] <= cost:
            continue
        if problem.is_goal(state):
            return actions
        visited[state] = cost
        cur_heuristic = heuristic(problem, state)
        for action in problem.get_actions(state):
            new_state = problem.get_successor(state, action)
            new_actions = actions + [action]
            new_cost = cost + problem.get_cost(state, action) + heuristic(problem, new_state) - cur_heuristic
            if new_state not in visited or visited[new_state] > new_cost:
                pq.put(PQItem(new_cost, new_state, new_actions, time))
                time += 1
    return None

def BestFirstSearch(problem: Problem[S, A], initial_state: S, heuristic: HeuristicFunction) -> Solution:
    pq = PriorityQueue()
    time = 0
    pq.put(PQItem(0, initial_state, [], time))
    time += 1
    visited = dict()
    while not pq.empty():
        item = pq.get()
        cost, state, actions = item.cost, item.state, item.actions
        if state in visited and visited[state] <= cost:
            continue
        if problem.is_goal(state):
            return actions
        visited[state] = cost
        for action in reversed(problem.get_actions(state)):
            new_state = problem.get_successor(state, action)
            new_actions = actions + [action]
            new_cost = heuristic(problem, new_state)
            if new_state not in visited or visited[new_state] > new_cost:
                pq.put(PQItem(new_cost, new_state, new_actions, time))
                time += 1
    return None