# Callable protocol

## Problem

`collections.abc.Callable` (and `typing.Callable`) lets you specify the type of a callable object:

```py
def stringify_points(points: Iterable[Point], fn: Callable[[int, int], str]) -> str:
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

### Caveats with type variables

How would you make an inline annotation for this function?
```py
from typing import TypeVar

T = TypeVar("T)

def identity(thing: T, /) -> T:
    return thing
```
If you try to do:
```py
Endomorphism = Callable[[T], T]

identity2: Endomorphism = identity
```
it may not produce errors with your type checker, but it doesn't mean what you want it to mean.
`Endomorphism` is a _generic type alias_, a template where you can substitute a parameter:
```py
pay_taxes: Endomorphism[float] = identity  # we do a little fraud!
# same as:
pay_taxes: Callable[[float], float] = identity
pay_taxes = math.floor # ok
```

However, you _can_ describe this with a protocol:
```py
class Identity(Protocol):
    def __call__(self, thing: T, /) -> T:
        ...

identity2: Identity = identity  # ok
identity2 = math.floor  # not ok! this function won't work with strings or lists
```

Which is in turn different from a _generic protocol_:
```py
class Endo(Protocol[T]):
    def __call__(self, thing: T, /) -> T:
        ...
```
which is the same as `Endomorphism` for all intents and purposes.


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
