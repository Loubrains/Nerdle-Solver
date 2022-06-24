from dataclasses import dataclass
from typing import Iterable
from itertools import product, chain


class LHS:
    def evaluate(self):
        to_eval = self.as_string()
        result = eval(to_eval)
        if isinstance(result, float) and result.is_integer():
            return f"{to_eval}={int(result)}", result
        else:
            return f"{to_eval}={result}", result



@dataclass
class TwoPartExpressions(LHS):
    num1: int
    operator: str
    num2: int

    def as_string(self):
        return f"{self.num1}{self.operator}{self.num2}"


@dataclass
class ThreePartExpressions(LHS):
    num1: int
    operator1: str
    num2: int
    operator2: str
    num3: int

    def as_string(self):
        return f"{self.num1}{self.operator1}{self.num2}{self.operator2}{self.num3}"


def one_digit():
    return range(1, 10)


def two_digit():
    return range(10, 100)


def three_digit():
    return range(100, 1000)


operators = list('+-*/')


def valid_lhs() -> Iterable[LHS]:
    three_parters = chain(
        product(two_digit(), operators, one_digit(), operators, one_digit()),
        product(one_digit(), operators, two_digit(), operators, one_digit()),
        product(one_digit(), operators, one_digit(), operators, two_digit()),
        product(one_digit(), operators, one_digit(), operators, one_digit()),
    )

    for (n1, op1, n2, op2, n3) in three_parters:
        yield ThreePartExpressions(n1, op1, n2, op2, n3)

    two_parters = chain(
        product(three_digit(), operators, one_digit()),
        product(one_digit(), operators, three_digit()),
        product(three_digit(), operators, two_digit()),
        product(two_digit(), operators, three_digit()),
        product(two_digit(), operators, two_digit()),
        product(two_digit(), operators, one_digit()),
        product(one_digit(), operators, two_digit()),
    )

    for (n1, op1, n2) in two_parters:
        yield TwoPartExpressions(n1, op1, n2)


def valid_expressions():
    for lhs in valid_lhs():
        expression, result = lhs.evaluate()
        if len(expression) != 8:
            continue
        if isinstance(result, float) and not result.is_integer():
            continue
        if result < 0:
            continue
        yield expression


def write_to_file():
    results = list(x + "\n" for x in valid_expressions())

    with open("precalculated_permutations.txt", "w") as f:
        f.writelines(results)