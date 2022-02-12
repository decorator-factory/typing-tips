# Generic types

## The problem

Using classes as type annotations is pretty straightforward: you expect an
object of class `Greeting`.

```py
class Greeting:
    def __init__(self, name: str, adjective: str) -> None:
        self.name = name
        self.adjective = adjective

def greet(greeting: Greeting) -> None:
    print("Hello, {0} {1}!".format(greeting.adjective, greeting.name))

greet(Greeting(name="world", adjective="beautiful"))
```

However, there are cases where this is not enough. Consider this `Box` class:

```py
class Box:
    def __init__(self, value: object) -> None:
        self._value = value

    def get(self) -> object:
        return self._value

    def put(self, new_value: object) -> None:
        self._value = new_value


pair = Box(1)

number = pair.get()
reveal_type(number)
# number: object

pair.put("hello")
```

Hm... well, it does what we told it to do. But it's a bummer: we would really like
`number` to be an `int`, and to prohibit putting `"hello"` into the box.


One solution would be to make a new class for each item type:
```py
class IntBox:
    def __init__(self, value: int) -> None:
        self._value = value

    def get(self) -> int:
        return self._value

    def put(self, new_value: int) -> None:
        self._value = new_value

class StrListBox:
    def __init__(self, value: list[str]) -> None:
        self._value = value

    def get(self) -> list[str]:
        return self._value

    def put(self, new_value: list[str]) -> None:
        self._value = new_value

...
```

This has some obvious downsides:

- If you have more than a few methods and a few types, this will be hard to maintain
- You can't write a function that will work with any kind of box
- You can't make a box for a user-provided type


## How do built-in types solve this?

You've probably seen how it's done with standard types like `list` and `dict`:
you can subscript the type to give it some parameters:

```py
ints: list[int] = [1, 2, 3, 4, 5]
points: dict[str, int] = {"alice": 420, "bob": 69}
```

Type checkers take these parameters into account when you do something with the values:
```py
alice_points = points.get("alice")
reveal_type(alice_points)
# alice_points: int | None
```

A type that can be subscripted like that is called a _generic type_ (or _generic class_).

## Introducing `Generic`

You can make your own generic class by using `typing.Generic`. Let's fix our `Box` class:
```py
from typing import Generic, TypeVar

T = TypeVar("T")

class Box(Generic[T]):
    def __init__(self, value: T) -> None:
        self._value = value

    def get(self) -> T:
        return self._value

    def put(self, new_value: T) -> None:
        self._value = new_value


box = Box(1)
reveal_type(box)
# box: Box[int]

number = box.get()
reveal_type(number)
# number: int

box.put("hello")
# error: "Literal['hello']" is incompatible with "int"
```

Seems like we got what we wanted:

- what we get from the `Box` is inferred as `int`
- we can only put an `int` (or a subtype, such as `bool` or `Literal[42]`) into the box


## More than one parameter

You've probably noticed that `dict` takes two arguments instead of one.
You can do this with your own class by passing several type variables to `Generic`:

```py
from typing import Generic, TypeVar

A = TypeVar("A")
B = TypeVar("B")

class Pair(Generic[A, B]):
    def __init__(self, left: A, right: B) -> None:
        self._left = left
        self._right = right

    def left(self) -> A:
        return self._left

    def right(self) -> B:
        return self._right


pair = Pair(3, "hello")
reveal_type(pair)
# pair: Pair[int, str]

left = pair.left()
reveal_type(left)
# left: int

right = pair.right()
reveal_type(right)
# right: str
```
