# Callable protocol

## Problem

`collections.abc.Callable` (formerly `typing.Callable`) lets you specify the type of a callable object:

```py
def stringify_points(
    points: Iterable[Point],
    fn: Callable[[int, int], str],
) -> str:
    return "\n".join(fn(p.x, p.y) for p in points)
```

However, `Callable` doesn't cover all cases when you need a callable.

- With more than one parameter, it's often unclear what the two parameters stand
  for. What do you do with `Callable[[int, str], None]`?
- `Callable` only lets you specify positional-only parameters
- `Callable` can't describe generic functions (functions that use `TypeVar`s)
- `Callable` doesn't support overloaded functions

## Solution

The solution to all these problems is to define a _Callable Protocol_.
It's a [protocol](https://mypy.readthedocs.io/en/stable/protocols.html) class that defines a
[`__call__` method](https://docs.python.org/3/reference/datamodel.html#object.__call__) and nothing else.


<!--
    TODO: add caveat that named parameters' names actually matter unless you `/` them
    mypy also doesn't enforce this, which of course makes life so much more fun and adventurous
-->

```py
from typing import Protocol


# keyword-able arguments
class PointCallback(Protocol):
    def __call__(self, x: int, y: int) -> None:
        ...


# overloads (note that the usual 'implementation' declaration is not needed)
class WeirdCallback(Protocol):
    @overload
    def __call__(self, thing: int) -> None:
        ...

    @overload
    def __call__(self, thing: int, thong: str) -> str:
        ...
```

<!--
    TODO: give examples of generic functions and generic callable protocol
    (hint: see previous commit)
-->


## Comparison with `Callable`

### Pros

- More flexible than the `Callable` syntax
- Even if you don't need the bells and whistles, naming arguments helps make your API more self-explanatory

### Cons

- More verbose. It simply takes up more space than a simple `Callable[...]`
- Can't be anonymous, unlike a `Callable`
- Requires users to be familiar with `Protocol`s
- When hovering over an element using a protocol as annotation, you might have to jump through some hoops
  to get to its definition

## Applicability

If you need some features a `Callable[...]` doesn't support, such as keyword arguments, this is probably the way to go.

If you need to clarify the purpose of each parameter of a callback with names, consider using this pattern.

If you need a very simple callback with one or two parameters, you likely don't need this pattern.
