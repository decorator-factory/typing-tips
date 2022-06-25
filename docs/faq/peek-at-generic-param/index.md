# How do I "peek" at my generic parameter?

!!! question

    At runtime, how can I reference a type parameter of a generic type?

    ```py hl_lines="20"
    from typing import Protocol, TypeVar, Generic


    class Defaultable(Protocol):
        def __init__(self) -> None:
            ...

    D = TypeVar("D", bound=Defaultable)


    class Registry(Generic[D]):
        def __init__(self) -> None:
            self._registry: dict[str, D] = {}

        def put(self, key: str, value: D) -> None:
            self._registry[key] = value

        def fetch(self, key: str) -> D:
            if key not in self._registry:
                self.put(key, D())
            return self._registry[key]


    balance: Registry[int] = Registry()
    ```

    This causes `TypeError: 'TypeVar' object is not callable` at runtime, and the type checker complains
    as well. Is it possible to tell Python to use `int()` in that place?

## Why isn't this possible?

1. The type variable might not resolve to a simple, concrete class. How should `Registry[str | int]` behave? Or, for example, `Registry[Sequence[str]]`?

2. Type annotations don't affect runtime behaviour. You can inspect them, and with a help of a
clever metaclass (or a [`__class_getitem__` method](https://docs.python.org/3.10/reference/datamodel.html#object.__class_getitem__)) you can make this work:
```py
balance = Registry[int]()
```
which is IMO an awkward notation. There isn't really a way to prohibit writing
`balance: Registry[int] = Registry()`, and it's not clear what to do about the previous point.

## Solution: accept a factory function

Very often this can be solved with a factory function:
```py
from collections.abc import Callable
from typing import TypeVar, Generic

T = TypeVar("T")

class Registry(Generic[T]):
    def __init__(self, make_default: Callable[[], T]) -> None:
        self._make_default = make_default
        self._registry: dict[str, T] = {}

    def put(self, key: str, value: T) -> None:
        self._registry[key] = value

    def fetch(self, key: str) -> T:
        if key not in self._registry:
            self.put(key, self._make_default())
        return self._registry[key]

balance = Registry(int)  # inferred as: Registry[int]
```

- this doesn't require metaclasses, [`inspect`](https://docs.python.org/3.10/library/inspect.html), or any other
advanced techniques;
- this will work with more complex types, like unions and abstract base classes;
- this is more flexible: you can tweak the default (e.g. provide `lambda: 42`) without changing the class.

This won't always solve your problem, but very often you can do a similar maneuver: instead of deriving behaviour
from a type, infer the type from the provided behaviour.

??? note "Is deriving behaviour from types a bad idea in general?"

    No, this is a good idea. It works well in languages like Haskell and Rust.
    ```hs
    class Default a where
        pick :: a

    instance Default Integer where
        pick = 0

    instance Default [a] where
        pick = []

    instance (Default a, Default b) => Default (a, b) where
        -- Haskell magic!
        pick = (pick, pick)
    ```
    It's simply not possible in Python. In Python, type annotations are not considered
    when compiling or running the code, beyond adding some metadata.
