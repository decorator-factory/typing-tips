# Subtyping

To move forward, we'll need a quick interlude about _subtyping_.

Subtyping is a generalization of subclassing. If you're familiar with set theory,
subtyping is very similar to one set being a subset of another.

## Definition

A type `Child` is a subtype of type `Parent` if a value of type `Child` can be assigned to
a variable of type `Parent`

## Examples

- `Dog` is a _subclass_ of `Animal`, so `Dog` is also a _subtype_ of `Animal`
```py
class Animal:
    pass

class Dog(Animal):
    pass

pet: Animal = Dog()
```

- `int` and `str` are subtypes of `Union[int, str]`
```py
x: Union[int, str] = "hello"
y: Union[int, str] = 42
```

- Any type is a subtype of itself
```py
class Foo:
    pass

foo: Foo = Foo()
```

- `Literal["nice"]` is a subtype of `str`
```py
nice: Literal["nice"] = "nice"
word: str = nice
```

- A type is a subtype of a protocol if it satisfies it
```py
class Reader(Protocol):
    def read_chunk(self, max_size: int) -> str: ...

class StringReader:
    def __init__(self, initial: str) -> None:
        self._buffer = initial

    def read_chunk(self, max_size: int) -> str:
        max_size = max(max_size, 0)
        chunk = self._buffer[:max_size]
        self._buffer = self._buffer[max_size:]
        return chunk

reader: Reader = StringReader("Hello, world!")
```

- `tuple[int, ...]` is a subtype of `tuple[Union[int, str], ...]`
```py
ints: tuple[int, ...] = (1, 2, 3, 4)
ints_or_strings: tuple[Union[int, str], ...] = ints
```

- `Callable[[Animal], int]` is a subtype of `Callable[[Dog], Union[int, str]]`

- `list[int]` is **not** a subtype of `list[Union[int, str]]`

    > Wait, what?

    You'll see why later in the series!
