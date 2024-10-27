from typing import Tuple
from game import HeuristicFunction, Game, S, A
from helpers.utils import NotImplemented

#TODO: Import any modules you want to use

# All search functions take a problem, a state, a heuristic function and the maximum search depth.
# If the maximum search depth is -1, then there should be no depth cutoff (The expansion should not stop before reaching a terminal state) 

# All the search functions should return the expected tree value and the best action to take based on the search results

# This is a simple search function that looks 1-step ahead and returns the action that lead to highest heuristic value.
# This algorithm is bad if the heuristic function is weak. That is why we use minimax search to look ahead for many steps.
def greedy(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    agent = game.get_turn(state)
    
    terminal, values = game.is_terminal(state)
    if terminal: return values[agent], None

    actions_states = [(action, game.get_successor(state, action)) for action in game.get_actions(state)]
    value, _, action = max((heuristic(game, state, agent), -index, action) for index, (action , state) in enumerate(actions_states))
    return value, action

# Apply Minimax search and return the game tree value and the best action
# Hint: There may be more than one player, and in all the testcases, it is guaranteed that 
# game.get_turn(state) will return 0 (which means it is the turn of the player). All the other players
# (turn > 0) will be enemies. So for any state "s", if the game.get_turn(s) == 0, it should a max node,
# and if it is > 0, it should be a min node. Also remember that game.is_terminal(s), returns the values
# for all the agents. So to get the value for the player (which acts at the max nodes), you need to
# get values[0].
def minimax(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    player = game.get_turn(state)
    isTerminalState, terminateValues = game.is_terminal(state)
    if isTerminalState:
        return terminateValues[0], None
    if max_depth == 0:
        return heuristic(game, state, 0), None
    
    best_value = -float('inf') if player == 0 else float('inf')
    best_action = None
    
    for action in game.get_actions(state):
        child = game.get_successor(state, action)
        returnedValue = minimax(game, child, heuristic, max_depth - 1)
        
        if player == 0 and returnedValue[0] > best_value:
            best_value = returnedValue[0]
            best_action = action
        elif player != 0 and returnedValue[0] < best_value:
            best_value = returnedValue[0]
            best_action = action
    
    return best_value, best_action

# Apply Alpha Beta pruning and return the tree value and the best action
# Hint: Read the hint for minimax.
def alphabeta(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    alpha = -float('inf')
    beta = float('inf')
    value, action = recursiveAlphaBeta(game, state, heuristic, max_depth, alpha, beta)
    return value, action

def recursiveAlphaBeta(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1, alpha=-float('inf'), beta=float('inf')) -> Tuple[float, A]:
    player = game.get_turn(state)
    isTerminalState, terminateValues = game.is_terminal(state)
    if isTerminalState:
        return terminateValues[0], None
    if max_depth == 0:
        return heuristic(game, state, 0), None
    
    best_value = -float('inf') if player == 0 else float('inf')
    best_action = None
    
    for action in game.get_actions(state):
        child = game.get_successor(state, action)
        returnedValue = recursiveAlphaBeta(game, child, heuristic, max_depth - 1, alpha, beta)
        if (player == 0 and returnedValue[0] > best_value) or (player != 0 and returnedValue[0] < best_value):
            best_value = returnedValue[0]
            best_action = action
            if player == 0:
                alpha = max(alpha, best_value)
                if alpha >= beta:
                    break
            else:
                beta = min(beta, best_value)
                if beta <= alpha:
                    break
    
    return best_value, best_action


# Apply Alpha Beta pruning with move ordering and return the tree value and the best action
# Hint: Read the hint for minimax.
def alphabeta_with_move_ordering(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    alpha = -float('inf')
    beta = float('inf')
    value, action = recursiveAlphaBetaWithOrder(game, state, heuristic, max_depth, alpha, beta)
    return value, action

def recursiveAlphaBetaWithOrder(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1, alpha=-float('inf'), beta=float('inf')) -> Tuple[float, A]:
    player = game.get_turn(state)
    isTerminalState, terminateValues = game.is_terminal(state)
    if isTerminalState:
        return terminateValues[0], None
    if max_depth == 0:
        return heuristic(game, state, 0), None
    
    childrenAndActions = [(game.get_successor(state, action), action, heuristic(game, game.get_successor(state, action), 0)) for action in game.get_actions(state)]
    childrenAndActions.sort(key=lambda m: m[2], reverse=player==0)
    
    best_value = -float('inf') if player == 0 else float('inf')
    best_action = None
    
    for child, action, _ in childrenAndActions:
        returnedValue = recursiveAlphaBetaWithOrder(game, child, heuristic, max_depth - 1, alpha, beta)
        if (player == 0 and returnedValue[0] > best_value) or (player != 0 and returnedValue[0] < best_value):
            best_value = returnedValue[0]
            best_action = action
            if player == 0:
                alpha = max(alpha, best_value)
                if alpha >= beta:
                    break
            else:
                beta = min(beta, best_value)
                if beta <= alpha:
                    break
    
    return best_value, best_action


# Apply Expectimax search and return the tree value and the best action
# Hint: Read the hint for minimax, but note that the monsters (turn > 0) do not act as min nodes anymore,
# they now act as chance nodes (they act randomly).
def expectimax(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    player = game.get_turn(state)
    isTerminalState, terminateValues = game.is_terminal(state)
    if isTerminalState:
        return terminateValues[0], None
    if max_depth == 0:
        return heuristic(game, state, 0), None
    
    if player == 0:
        maximum = -float('inf')
        best_action = None
        for action in game.get_actions(state):
            child = game.get_successor(state, action)
            value, _ = expectimax(game, child, heuristic, max_depth - 1)
            if value > maximum:
                maximum = value
                best_action = action
        return maximum, best_action
    else:
        total_value = 0
        for action in game.get_actions(state):
            child = game.get_successor(state, action)
            value, _ = expectimax(game, child, heuristic, max_depth - 1)
            total_value += value
        return total_value / len(game.get_actions(state)), None
