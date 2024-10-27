from typing import Any, Dict, List, Optional
from CSP import Assignment, BinaryConstraint, Problem, UnaryConstraint
from helpers.utils import NotImplemented

# This function applies 1-Consistency to the problem.
# In other words, it modifies the domains to only include values that satisfy their variables' unary constraints.
# Then all unary constraints are removed from the problem (they are no longer needed).
# The function returns False if any domain becomes empty. Otherwise, it returns True.
def one_consistency(problem: Problem) -> bool:
    remaining_constraints = []
    solvable = True
    for constraint in problem.constraints:
        if not isinstance(constraint, UnaryConstraint):
            remaining_constraints.append(constraint)
            continue
        variable = constraint.variable
        new_domain = {value for value in problem.domains[variable] if constraint.condition(value)}
        if not new_domain:
            solvable = False
        problem.domains[variable] = new_domain
    problem.constraints = remaining_constraints
    return solvable

# This function returns the variable that should be picked based on the MRV heuristic.
# NOTE: We don't use the domains inside the problem, we use the ones given by the "domains" argument 
#       since they contain the current domains of unassigned variables only.
# NOTE: If multiple variables have the same priority given the MRV heuristic, 
#       we order them in the same order in which they appear in "problem.variables".
def minimum_remaining_values(problem: Problem, domains: Dict[str, set]) -> str:
    _, _, variable = min((len(domains[variable]), index, variable) for index, variable in enumerate(problem.variables) if variable in domains)
    return variable

# This function should implement forward checking
# The function is given the problem, the variable that has been assigned and its assigned value and the domains of the unassigned values
# The function should return False if it is impossible to solve the problem after the given assignment, and True otherwise.
# In general, the function should do the following:
#   - For each binary constraints that involve the assigned variable:
#       - Get the other involved variable.
#       - If the other variable has no domain (in other words, it is already assigned), skip this constraint.
#       - Update the other variable's domain to only include the values that satisfy the binary constraint with the assigned variable.
#   - If any variable's domain becomes empty, return False. Otherwise, return True.
# IMPORTANT: Don't use the domains inside the problem, use and modify the ones given by the "domains" argument 
#            since they contain the current domains of unassigned variables only.
def forward_checking(problem: Problem, assigned_variable: str, assigned_value: Any, domains: Dict[str, set]) -> bool:
    for constraint in problem.constraints:
        if isinstance(constraint, BinaryConstraint) and assigned_variable in constraint.variables:
            other_variable = constraint.variables[0] if constraint.variables[1] == assigned_variable else constraint.variables[1]
            if not domains.get(other_variable):
                continue
            new_domain = {value for value in domains.get(other_variable) if constraint.is_satisfied({assigned_variable: assigned_value, other_variable: value})}
            domains[other_variable] = new_domain
            if not domains.get(other_variable):
                return False
    return True

# This function should return the domain of the given variable order based on the "least restraining value" heuristic.
# IMPORTANT: This function should not modify any of the given arguments.
# Generally, this function is very similar to the forward checking function, but it differs as follows:
#   - You are not given a value for the given variable, since you should do the process for every value in the variable's
#     domain to see how much it will restrain the neigbors domain
#   - Here, you do not modify the given domains. But you can create and modify a copy.
# IMPORTANT: If multiple values have the same priority given the "least restraining value" heuristic, 
#            order them in ascending order (from the lowest to the highest value).
# IMPORTANT: Don't use the domains inside the problem, use and modify the ones given by the "domains" argument 
#            since they contain the current domains of unassigned variables only.
def least_restraining_values(problem: Problem, variable_to_assign: str, domains: Dict[str, set]) -> List[Any]:
    values_counts = []
    for value in domains.get(variable_to_assign):
        count = 0
        for constraint in problem.constraints:
            if isinstance(constraint, BinaryConstraint) and variable_to_assign in constraint.variables:
                other_var = constraint.variables[0] if constraint.variables[1] == variable_to_assign else constraint.variables[1]
                if not domains.get(other_var):
                    continue
                for other_value in domains.get(other_var):
                    if not constraint.is_satisfied({variable_to_assign: value, other_var: other_value}):
                        count += 1
        values_counts.append([value, count])
    values_counts.sort(key=lambda x: (x[1], x[0]))
    sorted_values = [value for value, _ in values_counts]
    return sorted_values

def backtrack(problem: Problem, assignment: Assignment, domains: Dict[str, set]) -> Optional[Assignment]:
    if problem.is_complete(assignment):
        return assignment
    
    variable = minimum_remaining_values(problem, domains)
    listOfLCV = least_restraining_values(problem, variable, domains)
    domains.pop(variable)
    
    for value in listOfLCV:
        copiedDomain = domains.copy()
        assignment[variable] = value
        
        if forward_checking(problem, variable, value, copiedDomain):
            result = backtrack(problem, assignment, copiedDomain)
            if result:
                return result
        
        assignment.pop(variable)
    
    return None

# This function should solve CSP problems using backtracking search with forward checking.
# The variable ordering should be decided by the MRV heuristic.
# The value ordering should be decided by the "least restraining value" heurisitc.
# Unary constraints should be handled using 1-Consistency before starting the backtracking search.
# This function should return the first solution it finds (a complete assignment that satisfies the problem constraints).
# If no solution was found, it should return None.
# IMPORTANT: To get the correct result for the explored nodes, you should check if the assignment is complete only once using "problem.is_complete"
#            for every assignment including the initial empty assignment, EXCEPT for the assignments pruned by the forward checking.
#            Also, if 1-Consistency deems the whole problem unsolvable, you shouldn't call "problem.is_complete" at all.
def solve(problem: Problem) -> Optional[Assignment]:
    if not one_consistency(problem):
        return None
    return backtrack(problem, {}, problem.domains)
