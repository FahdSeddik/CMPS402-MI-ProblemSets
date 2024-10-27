from typing import Tuple
import re
from CSP import Assignment, Problem, UnaryConstraint, BinaryConstraint

#TODO (Optional): Import any builtin library or define any helper function you want to use
# class BinaryConstraint(Constraint):
#     variables: Tuple[str, str]  # The name of the two variables that are in the constraint.
#     condition: Callable[[Any, Any], bool] # A function that takes the variables' values and returns whether they satisfies the constraint or not.

#     def __init__(self, variables: Tuple[str, str], condition: Callable[[Any, Any], bool]) -> None:
#         super().__init__()
#         self.variables = variables
#         self.condition = condition
# class UnaryConstraint(Constraint):
#     variable: str  # The name of the variable that is in the constraint.
#     condition: Callable[[Any], bool] # A function that takes the variable's value and returns whether it satisfies the constraint or not.

#     def __init__(self, variable: str, condition: Callable[[Any], bool]) -> None:
#         super().__init__()
#         self.variable = variable
#         self.condition = condition


# This is a class to define for cryptarithmetic puzzles as CSPs
class CryptArithmeticProblem(Problem):
    LHS: Tuple[str, str]
    RHS: str

    # Convert an assignment into a string (so that is can be printed).
    def format_assignment(self, assignment: Assignment) -> str:
        LHS0, LHS1 = self.LHS
        RHS = self.RHS
        letters = set(LHS0 + LHS1 + RHS)
        formula = f"{LHS0} + {LHS1} = {RHS}"
        postfix = []
        valid_values = list(range(10))
        for letter in letters:
            value = assignment.get(letter)
            if value is None: continue
            if value not in valid_values:
                postfix.append(f"{letter}={value}")
            else:
                formula = formula.replace(letter, str(value))
        if postfix:
            formula = formula + " (" + ", ".join(postfix) +  ")" 
        return formula

    @staticmethod
    def from_text(text: str) -> 'CryptArithmeticProblem':
        # Given a text in the format "LHS0 + LHS1 = RHS", the following regex
        # matches and extracts LHS0, LHS1 & RHS
        # For example, it would parse "SEND + MORE = MONEY" and extract the
        # terms such that LHS0 = "SEND", LHS1 = "MORE" and RHS = "MONEY"
        pattern = r"\s*([a-zA-Z]+)\s*\+\s*([a-zA-Z]+)\s*=\s*([a-zA-Z]+)\s*"
        match = re.match(pattern, text)
        if not match: raise Exception("Failed to parse:" + text)
        LHS0, LHS1, RHS = [match.group(i+1).upper() for i in range(3)]

        problem = CryptArithmeticProblem()
        problem.LHS = (LHS0, LHS1)
        problem.RHS = RHS

        #TODO Edit and complete the rest of this function
        # problem.variables:    should contain a list of variables where each variable is string (the variable name)
        # problem.domains:      should be dictionary that maps each variable (str) to its domain (set of values)
        #                       For the letters, the domain can only contain integers in the range [0,9].
        # problem.constaints:   should contain a list of constraint (either unary or binary constraints).
        problem.variables = list(set(LHS0 + LHS1 + RHS))
        lenMax = max(len(LHS0), len(LHS1))
        
        problem.domains = {letter: set(range(1, 10)) if letter in [LHS0[0], LHS1[0], RHS[0]] else set(range(10)) for letter in problem.variables}

        problem.constraints = [
            UnaryConstraint(LHS0[0], lambda x: x != 0),
            UnaryConstraint(LHS1[0], lambda x: x != 0),
            UnaryConstraint(RHS[0], lambda x: x != 0)
        ]

        problem.constraints.extend([
            BinaryConstraint([letter, letter2], lambda x, y: x != y) for letter in problem.variables for letter2 in problem.variables if letter != letter2
        ])

        carryList = [f"C{i}" for i in range(lenMax)]
        problem.variables.extend(carryList)
        problem.domains.update({carry: set(range(2)) for carry in carryList})

        if len(RHS) > lenMax:
            problem.domains[RHS[0]] = {1}
            problem.domains[carryList[-1]] = {1}

        def domain2var(x, y):
            return [(i, j) for i in x for j in y]

        def domain3var(x, y, z):
            return [(i, j, k) for i in x for j in y for k in z]

        for i in range(lenMax):
            if i == 0:
                auxLeft = LHS0[-1] + LHS1[-1]
                auxRight = RHS[-1] + "C0"
                problem.variables.extend([auxLeft, auxRight])
                problem.domains[auxLeft] = domain2var(problem.domains[LHS0[-1]], problem.domains[LHS1[-1]])
                problem.domains[auxRight] = domain2var(problem.domains[RHS[-1]], problem.domains["C0"])
                problem.constraints.extend([
                    BinaryConstraint([auxLeft, LHS0[-1]], lambda auxleft, lhs0: auxleft[0] == lhs0),
                    BinaryConstraint([auxLeft, LHS1[-1]], lambda auxleft, lhs1: auxleft[1] == lhs1),
                    BinaryConstraint([auxRight, RHS[-1]], lambda auxright, rhs: auxright[0] == rhs),
                    BinaryConstraint([auxRight, "C0"], lambda auxright, c0: auxright[1] == c0),
                    BinaryConstraint([auxLeft, auxRight], lambda auxleft, auxright: auxleft[0] + auxleft[1] == auxright[0] + 10*auxright[1])
                ])
            elif i < (min(len(LHS0), len(LHS1))):
                auxLeft = LHS0[-(i+1)] + LHS1[-(i+1)] + carryList[i-1]
                auxRight = RHS[-(i+1)] + carryList[i]
                problem.variables.extend([auxLeft, auxRight])
                problem.domains[auxLeft] = domain3var(problem.domains[LHS0[-(i+1)]], problem.domains[LHS1[-(i+1)]], problem.domains[carryList[i-1]])
                problem.domains[auxRight] = domain2var(problem.domains[RHS[-(i+1)]], problem.domains[carryList[i]])
                problem.constraints.extend([
                    BinaryConstraint([auxLeft, LHS0[-(i+1)]], lambda auxleft, lhs0: auxleft[0] == lhs0),
                    BinaryConstraint([auxLeft, LHS1[-(i+1)]], lambda auxleft, lhs1: auxleft[1] == lhs1),
                    BinaryConstraint([auxLeft, carryList[i-1]], lambda auxleft, c: auxleft[2] == c),
                    BinaryConstraint([auxRight, RHS[-(i+1)]], lambda auxright, rhs: auxright[0] == rhs),
                    BinaryConstraint([auxRight, carryList[i]], lambda auxright, c: auxright[1] == c),
                    BinaryConstraint([auxLeft, auxRight], lambda auxleft, auxrigh: auxleft[0] + auxleft[1] + auxleft[2] == auxrigh[0] + 10*auxrigh[1])
                ])
            else:
                auxLeft = LHS0[-(i+1)] + carryList[i-1]
                auxRight = RHS[-(i+1)] + carryList[i]
                problem.variables.extend([auxLeft, auxRight])
                problem.domains[auxLeft] = domain2var(problem.domains[LHS0[-(i+1)]], problem.domains[carryList[i-1]])
                problem.domains[auxRight] = domain2var(problem.domains[RHS[-(i+1)]], problem.domains[carryList[i]])
                problem.constraints.extend([
                    BinaryConstraint([auxLeft, LHS0[-(i+1)]], lambda auxleft, lhs0: auxleft[0] == lhs0),
                    BinaryConstraint([auxLeft, carryList[i-1]], lambda auxleft, c: auxleft[1] == c),
                    BinaryConstraint([auxRight, RHS[-(i+1)]], lambda auxright, rhs: auxright[0] == rhs),
                    BinaryConstraint([auxRight, carryList[i]], lambda auxright, c: auxright[1] == c),
                    BinaryConstraint([auxLeft, auxRight], lambda auxleft, auxrigh: auxleft[0] + auxleft[1] == auxrigh[0] + 10*auxrigh[1])
                ])

        return problem

    # Read a cryptarithmetic puzzle from a file
    @staticmethod
    def from_file(path: str) -> "CryptArithmeticProblem":
        with open(path, 'r') as f:
            return CryptArithmeticProblem.from_text(f.read())