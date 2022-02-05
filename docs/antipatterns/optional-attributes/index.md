# `Optional` attribute hell


## Summary

!!! abstract "Smell"

    A class has several optional fields which are linked together

!!! bug "Why is it bad?"

    The class contains invariants that aren't possible to capture at the type level.
    It makes it harder and more error-prone to work with the class. Often these invariants
    aren't explicitly documented, which doesn't help.

!!! success "Solution"

    Represent each of the possible states of the class as its own thing.
    Sometimes inheritance works better, sometimes you're better off with a `Union`.

## Example

Suppose that you need to model an arithmetic expression, such as
```
((x * x) + 2 - y) * 5 + 4
```
And then evaluate it, given a dict mapping variable names to integers.

A straight-forward way to represent an expression is to make a syntax tree:
```
               Add
              /   \
             /     Const(4)
           Sub
          /   \
         /     Var('y')
       Add
       /  \
      /    Const(2)
     Mul
   /     \
Var('x')  Var('x')
```

Suppose then that you come up with this solution:

```py
from enum import Enum
from collections.abc import Mapping
from dataclasses import dataclass


class Operation(Enum):
    add = "add"
    subtract = "subtract"
    multiply = "multiply"


@dataclass
class Node:
    line: int
    column: int
    variable_name: Optional[str]
    constant: Optional[int]
    operation: Optional[Operation]
    left_operand: Optional["Node"]
    right_operand: Optional["Node"]


def evaluate(node: Node, variables: Mapping[str, int]) -> int:
    if node.constant is not None:
        return node.constant

    elif node.variable_name is not None:
        number = variables.get(node.variable_name)
        if number is None:
            raise LookupError(node.variable_name)
        return number

    elif node.operation is not None:
        assert node.left_operand is not None
        assert node.right_operand is not None
        left_result = evaluate(node.left_operand, variables)
        right_result = evaluate(node.right_operand, variables)

        if node.operation is Operation.add:
            return left_result + right_result
        elif node.operation is Operation.subtract:
            return left_result - right_result
        elif node.operation is Operation.multiply:
            return left_result * right_result
        else:
            assert False

    else:
        assert False
```

Nothing about this is right. This `Node` class has some complex invariants that we need to respect:

- At least one of `variable_name`, `constant`, `operation` must be non-`None`
- If `variable_name` is not `None`, `constant` and `operation` must be `None`
- If `constant` is not `None`, `variable_name` and `operation` must be `None`
- If `operation` is not `None`, `variable_name` and `constant` must be `None`
- `left_operand` and `right_operand` are `None` if and only if `operation` is `None`

If we break some invariants (like the first one), we'll get a runtime error.
If we break others (like setting both `constant` and `operation`), the program will be silently wrong.

One benefit of types is that they help us eliminate invalid states. So let's leverage that help.

## Solution

One possible solution is to make a `Node` base class and take advantage of polymorphism.

```py
from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass


Vars = Mapping[str, int]


@dataclass(frozen=True)
class Pos:
    line: int
    column: int


class Node(ABC):
    @property
    @abstractmethod
    def pos(self) -> Pos:
        raise NotImplementedError

    @abstractmethod
    def evaluate(self, variables: Vars) -> int:
        raise NotImplementedError


class Constant(Node):
    def __init__(self, pos: Pos, value: int) -> None:
        self._pos = pos
        self._value = value

    @property
    def pos(self) -> Pos:
        return self._pos

    def evaluate(self, variables: Vars) -> int:
        return self._value


class Variable(Node):
    def __init__(self, pos: Pos, name: str) -> None:
        self._pos = pos
        self._name = name

    @property
    def pos(self) -> Pos:
        return self._pos

    def evaluate(self, variables: Vars) -> int:
        number = variables.get(self._name)
        if number is None:
            raise LookupError(self._name)
        return number


class BinaryOperationNode(Node):
    def __init__(self, pos: Pos, left: Node, right: Node) -> None:
        self._pos = pos
        self._left = left
        self._right = right

    @property
    def pos(self) -> Pos:
        return self._pos

    @abstractmethod
    def _operation(self, left: int, right: int) -> int:
        raise NotImplementedError

    def evaluate(self, variables: Vars) -> int:
        left_result = self._left.evaluate(variables)
        right_result = self._right.evaluate(variables)
        return self._operation(left_result, right_result)


class Add(BinaryOperationNode):
    def _operation(self, left: int, right: int) -> int:
        return left + right


class Sub(BinaryOperationNode):
    def _operation(self, left: int, right: int) -> int:
        return left - right


class Mul(BinaryOperationNode):
    def _operation(self, left: int, right: int) -> int:
        return left * right
```
