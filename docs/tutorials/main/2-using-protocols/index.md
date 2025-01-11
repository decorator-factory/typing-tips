# Using Protocols

If you're only using classes to group values together, with the occasional helper method, you're programming in a
_procedural style_ (or possibly _functional_, if you're limiting the use of side effects and I/O to the edge of your program). The real power of classes comes from _polymorphism_ &mdash; the ability to handle objects of different types because they have the same shape.

You may have used a protocol before without realizing it. `Sized, `Iterable` and `Mapping` from `collections.abc` are protocols.
They define what methods an object needs to have, but don't restrict what specific class it needs to be.

## The prelude

We'll be making a simple toolkit for making ASCII art

???+ note "The code so far"

    ```py
    from collections.abc import Iterable
    import warnings


    class Block:
        def __init__(self, text: str) -> None:
            self._text = text

        def render(self, width: int) -> Iterable[str]:
            for i in range(len(self._text) // width + 1):
                yield self._text[i * width : (i + 1) * width]


    class Guard:
        def __init__(self, wrapped) -> None:
            self._wrapped = wrapped

        def render(self, width: int) -> Iterable[str]:
            for line in self._wrapped.render(width):
                if len(line) > width:
                    warnings.warn(f"Line length ({len(line)}) exceeds supplied width ({width})")
                    yield line[:width]
                else:
                    yield line + " " * (width - len(line))


    class Pad:
        def __init__(self, char: str, wrapped) -> None:
            if len(char) != 1:
                raise ValueError("Expected a single character for padding")
            self._char = char
            self._wrapped = wrapped

        def render(self, width: int) -> Iterable[str]:
            yield self._char * width
            if width > 2:
                for line in self._wrapped.render(width - 2):
                    yield self._char + line + self._char
            yield self._char * width


    scene = \
        Pad("*",
            Guard(
                Block("Hello, world! Lorem Ipsum Dolor Sit Amet, or so I've been told.")))
    for line in scene.render(12):
        print(line)

    ```

The program outputs:
```
************
*Hello, wor*
*ld! Lorem *
*Ipsum Dolo*
*r Sit Amet*
*, or so I'*
*ve been to*
*ld.       *
************
```
Note that if not for the `Guard` widget, the `*ld.       *` line would be `*ld.*`, which is not what we want &mdash; we extracted the padding functionality so that we don't have to trim the line in every widget's `render`.

This is a classic example of the [Decorator pattern](https://en.wikipedia.org/wiki/Decorator_pattern): one object wraps another object with a well-known interface (the `render` method here) and presents the same interface in return. That way, you can add functionality to widgets of potentially different classes and retain their widget-ness.

## Defining a protocol

Right now we have an unwritten contract for all the `widgets`: they must have a `render` method, accepting a `width` parameter that is an `int`, and returning an iterable of strings. We can formalize this contract with a _protocol class_:

```py
from collections.abc import Iterable
from typing import Protocol


class Widget(Protocol):
    def render(self, width: int, /) -> Iterable[str]:
        ...
```

!!! note

    The `...` here doesn't imply something's missing: leave the method body as `...`, the ellipsis object. I'll use `# <...>` when I really mean to skip something.

This protocol defines the methods an object needs to support to _be_ a `Widget`. We can now add annotations to our `wrapped` parameters:

```py
    class Guard:
        def __init__(self, wrapped: Widget) -> None:
    # <...>

    class Pad:
        def __init__(self, char: str, wrapped: Widget) -> None:
    # <...>
```

Now if you try to call `Guard("some text")`, your type checker will complain:

```
Argument of type "Literal['some text']" cannot be assigned to parameter "wrapped" of type "Widget" in function "__init__"
  "Literal['some text']" is incompatible with protocol "Widget"
    "render" is not present
```

!!! note "Slash (`/`) in the protocol definition"

    A `/` in a function definition means that all the parameters before it can only be provided with positional arguments (see [PEP 570](https://peps.python.org/pep-0570/)).
    This will be common in protocols: if you just said `def render(self, width: int)`, it would mean that to implement this protocol you must name your parameter `width` exactly.
    But we're only going to pass the width as a positional argument, and it would be silly to reject something from being a `Widget` just because its `render` parameter is called `w` or `max_width`.

In addition to `...`, you can provide a docstring for the method, documenting its purpose and potentially other contract requirements:
```py
class Widget(Protocol):
    def render(self, width: int, /) -> Iterable[str]:
        """
        Yield a finite amount of text lines.

        Every line must be at most `width` characters long.
        """
        ...
```

## Attributes

A protocol class may also define attributes:

```py
class Labelled(Protocol):
    label: str
```

This requires that the attribute is both readable and writable. So the following is allowed:

```py
def just_read(thing: Labelled) -> None:
    print(thing.label)

def calm_down(thing: Labelled) -> None:
    thing.label = thing.label.replace("!", "")
```

More often you'll want a read-only attribute. You can do this by defining a property in the protocol class:
```py
class Labelled(Protocol):
    @property
    def label(self) -> str:
        ...
```

With this definition of `Labelled`, `calm_down` will not be accepted by a type checker.
Note that this doesn't require a `Labelled` object to have an actual _property_, it could be a regular attribute as well:

```py
@dataclass
class Node:
    x: int
    y: int
    label: str

just_read(Node(420, 69, "my secret"))
```

Now, back to our `Widget`s. If we want to do more complex layouts, we might need to know how wide a widget wants to be:

```py
class Widget(Protocol):
    def render(self, width: int, /) -> Iterable[str]:
        ...

    @property
    def desired_width(self) -> int:
        """
        If I had unlimited width, how much would I want to grow?
        """
        ...
```

Now we're getting red squiggles in the `scene = ...` line because our `Guard` and `Block` aren't widgets anymore. Let's fix that:

??? note "Code with `desired_width`"

    ```py
    from collections.abc import Iterable
    from typing import Protocol
    import warnings


    class Widget(Protocol):
        def render(self, width: int, /) -> Iterable[str]:
            ...

        @property
        def desired_width(self) -> int:
            ...


    class Block:
        def __init__(self, text: str) -> None:
            self._text = text

        @property
        def desired_width(self) -> int:
            return len(self._text)

        def render(self, width: int) -> Iterable[str]:
            for i in range(len(self._text) // width + 1):
                yield self._text[i * width : (i + 1) * width]


    class Guard:
        def __init__(self, wrapped: Widget) -> None:
            self._wrapped = wrapped

        @property
        def desired_width(self) -> int:
            return self._wrapped.desired_width

        def render(self, width: int) -> Iterable[str]:
            for line in self._wrapped.render(width):
                if len(line) > width:
                    warnings.warn(f"Line length ({len(line)}) exceeds supplied width ({width})")
                    yield line[:width]
                else:
                    yield line + " " * (width - len(line))


    class Pad:
        def __init__(self, char: str, wrapped: Widget) -> None:
            if len(char) != 1:
                raise ValueError("Expected a single character for padding")
            self._char = char
            self._wrapped = wrapped

        @property
        def desired_width(self) -> int:
            return self._wrapped.desired_width + 2

        def render(self, width: int) -> Iterable[str]:
            yield self._char * width
            if width > 2:
                for line in self._wrapped.render(width - 2):
                    yield self._char + line + self._char
            yield self._char * width


    scene = \
        Pad("*",
            Guard(
                Block("Hello, world! Lorem Ipsum Dolor Sit Amet, or so I've been told.")))
    for line in scene.render(12):
        print(line)
    ```

Now we can add classes that handle horizontal and flexible layout!

??? note "Advanced layout"

    This is a lot of code, so if you don't want to read all of it, note:

    - `DesireWidth` has a plain `desired_width` attribute
    - other classes have a `desired_width` property
    - all of them work as `Widget`s!

    ```py
    class DesireWidth:
        """
        Override the `desired_width` of a child widget with a fixed value.
        """
        def __init__(self, desired_width: int, wrapped: Widget) -> None:
            self.desired_width = desired_width
            self._wrapped = wrapped

        def render(self, width: int) -> Iterable[str]:
            return self._wrapped.render(width)


    class Vertical:
        """
        Arrange widgets vertically, one after another.
        """
        def __init__(self, items: Iterable[Widget]) -> None:
            self._items = list(items)

        @property
        def desired_width(self) -> int:
            return max(item.desired_width for item in self._items)

        def render(self, width: int) -> Iterable[str]:
            for item in self._items:
                yield from item.render(width)


    class Horizontal:
        """
        Arrange widgets horizontally. You must specify how much horizontal
        space each item occupies.

        If the total of the spaces is bigger than the required width, the
        lines will be cut off from the right.
        """

        def __init__(self, items: Iterable[tuple[int, Widget]]) -> None:
            self._items = list(items)

        @property
        def desired_width(self) -> int:
            return sum(width for (width, _widget) in self._items)

        def render(self, width: int) -> Iterable[str]:
            if not self._items:
                return
            state = [
                (subwidth, iter(Guard(widget).render(subwidth)))
                for (subwidth, widget) in self._items
            ]
            active = len(state)
            while True:
                total_line = ""
                for i, (subwidth, render_iter) in enumerate(state):
                    try:
                        total_line += next(render_iter)
                    except StopIteration:
                        active -= 1
                        if active == 0:
                            return
                        total_line += " " * subwidth
                        # replace iterator with a dummy that always returns a blank line:
                        state[i] = (subwidth, iter(lambda: " " * subwidth, None))
                yield total_line[:width]


    class Flex:
        """
        Arrange items in rows, switching to a new row when the next item
        wouldn't fit according to its `desired_width`.
        """
        def __init__(self, items: Iterable[Widget]) -> None:
            self._items = list(items)

        @property
        def desired_width(self) -> int:
            return sum(item.desired_width for item in self._items)

        def render(self, width: int) -> Iterable[str]:
            rows: list[Horizontal] = []
            row: list[tuple[int, Widget]] = []
            remaining = width
            for item in self._items:
                if remaining < item.desired_width:
                    if row:
                        rows.append(Horizontal(row))
                    row = [(min(width, item.desired_width), item)]
                    remaining = width - item.desired_width
                else:
                    row.append((item.desired_width, item))
                    remaining -= item.desired_width
            if row:
                rows.append(Horizontal(row))
            return Guard(Vertical(rows)).render(width)
    ```

Let's test it:

???+ note "Test program and output"

    ```py
    b1 = Pad("1", Guard(Block("First")))
    b2 = DesireWidth(5, Pad("2", Guard(Block("SecondSecond"))))
    b3 = Pad("3", Guard(Block("The Very Third!!")))
    b4 = DesireWidth(10, Pad("4", Guard(Block("Fourth"))))

    inner = Pad("+", Flex([b1, b2]))
    outer = Pad("*", Flex([inner, b3, b4]))

    for line in outer.render(30):
        print(line)
    print()
    for line in outer.render(40):
        print(line)
    ```

    ```
    ******************************
    *++++++++++++++              *
    *+111111122222+              *
    *+1First12Sec2+              *
    *+1     12ond2+              *
    *+11111112Sec2+              *
    *+       2ond2+              *
    *+       2   2+              *
    *+       22222+              *
    *++++++++++++++              *
    *3333333333333333334444444444*
    *3The Very Third!!34Fourth  4*
    *3                34444444444*
    *333333333333333333          *
    ******************************

    ****************************************
    *++++++++++++++333333333333333333      *
    *+111111122222+3The Very Third!!3      *
    *+1First12Sec2+3                3      *
    *+1     12ond2+333333333333333333      *
    *+11111112Sec2+                        *
    *+       2ond2+                        *
    *+       2   2+                        *
    *+       22222+                        *
    *++++++++++++++                        *
    *4444444444                            *
    *4Fourth  4                            *
    *4444444444                            *
    ****************************************
    ```


## Intermezzo: points, structural and nominal typing

In statically typed languages like Java and C++, you typically need to specify that you're conforming to an interface,
either through dedicated syntax or through inheritance:

```java
class Vertical implements Widget {
```
```cpp
class Vertical : public Widget {
```

That's called _nominal typing_: the implementor must "name" the things it implements. This is opposed to _structural typing_:
if a value has the required structure, it fits the interface. Both have their pros and cons.

- The obvious benefit of structural typing is that you don't need to explicitly refer to the interface you're implementing.
That's how Python has always worked, with dunder methods and other [duck typing](https://docs.python.org/3/glossary.html#term-duck-typing)
techniques.
- Protocols make it easy to type existing contracts without requiring users to inherit from a base class all of a sudden.
- You can't modify something you don't own. But you can make a protocol that just happens to match someone else's type. For example, a protocol with a `status_code: int` property and a `text: str` method matches `requests.Response` and potentially your own class.

- On the other hand, structural typing can make it hard to realize that a particular class implements a particular interface.
    You'll need to know about that interface beforehand to understand that intention.
- The errors for structural types are worse, as they occur at usage time. If one of our widgets had a typoed `desired_widht` property,
    you'd get a nasty error message when passing the widget somewhere else, saying that `"Foo" is not a "Widget"`. This gets worse with
    unions, more complex protocols, and generics.

As a more subtle point, you can _accidentally_ match a protocol, when your class doesn't _semantically_ satisfy it.
```py
class TwoDimensional(Protocol):
    x: float
    y: float

def reset(point: TwoDimensional) -> None:
    point.x = point.y = 0.0

def distance_to_origin(point: TwoDimensional) -> float:
    return (point.x**2 + point.y**2)**0.5

@dataclass
class Point2D:
    x: float
    y: float

assert 4.99 < distance_to_origin(Point2D(3.0, 4.0)) < 5.01
```
This looks fine. But consider a 3-dimensional point:
```py
@dataclass
class Point3D:
    x: float
    y: float
    z: float
```
It does have `x: float` and `y: float` attributes, but `reset` and `distance_to_origin` will give you completely wrong results with a `Point3D`. So if it's vital that a class understands when it implements the contract, don't use a protocol.


## The nominal counterpart to `Protocol`: `ABC`

If you don't want the structural behaviour of protocols, you can define an _abstract base class_:

```py
from abc import ABC, abstractmethod

class Widget(ABC):
    @abstractmethod
    def render(self, width: int, /) -> Iterable[str]:
        raise NotImplementedError

    @property
    @abstractmethod
    def desired_width(self) -> int:
        raise NotImplementedError
```

With this, you'll need to inherit from `Widget` explicitly in order to mark a class as a widget:

```py
class Block(Widget):
    def __init__(self, text: str) -> None:
        self._text = text

    @property
    def desired_width(self) -> int:
        return len(self._text)

    def render(self, width: int) -> Iterable[str]:
        for i in range(len(self._text) // width + 1):
            yield self._text[i * width : (i + 1) * width]
```

You can read more about ABCs in the [documentation for the `abc` module](https://docs.python.org/3/library/abc.html).


## Inheriting from a protocol

We said before that...

> ... structural typing can make it hard to realize that a particular class implements a particular interface.
> You'll need to know about that interface beforehand to understand that intention.

> ... The errors for structural types are worse, as they occur at usage time

If you want to alleviate that without requiring inheritance from your base class, you can just inherit from the protocol!

```py
class Widget(Protocol):
    # <...>

class Block(Widget):
    # <...>
```

If you expect other people to inherit from a `Protocol` class, you should prepare it for the real world a bit:

```py
from abc import abstractmethod
from typing import Protocol

class Widget(Protocol):
    @abstractmethod
    def render(self, width: int, /) -> Iterable[str]:
        raise NotImplementedError

    @property
    @abstractmethod
    def desired_width(self) -> int:
        raise NotImplementedError

    # or provide a sensible default implementation:

    @property
    def desired_width(self) -> int:
        return 1_000_000
```

- Mark the required-to-implement methods with `abstractmethod`. Yes, the item from the `abc` module. With this change, a class that doesn't implement all the items is considered _abstract_, and instantiating it will cause an error at runtime:

    ```py
    class Foo(Protocol):
        @abstractmethod
        def method1(self) -> None: # <...>
        @abstractmethod
        def method2(self) -> None: # <...>

    class Bar(Foo):
        def method1(self): # <...>

    Bar()  # TypeError: Can't instantiate abstract class Bar without an implementation for abstract method 'method2'
    ```

    A type checker should already prevent you from instantiating `Bar()`, but it's good to catch the error at runtime as well.
    If you're making a library, you shouldn't assume that its users are using a type checker. There are also many creative ways
    around type checkers in Python.

- Raise a `NotImplementedError` in the method body. In an ABC, you're allowed to "bottom out" to an abstract method when using
    `super`:

    ```py
    class Foo(ABC):
        @abstractmethod
        def greet(self):
            print("oh no")

    class Bar(Foo):
        def greet(self):
            super().greet()

    Bar().greet()  # oh no
    ```

    Having an abstract method with a default implementation is pretty dubious, but that's a thing `abc.ABC` allows you to do.
    So if you leave the method body to be `...`, a `super().render()` call in a widget could give you a `None`, which is wrong.
    For that reason, you should use `raise NotImplementedError` for the body of abstract methods to catch those mistaken calls &mdash; both in ABCs and (inheritable) protocols.

And yes, that's the secret: `Protocol` is mostly the same as `abc.ABC`[^1], except type checkers understand that it's structural, not nominal.


## A note on "compatibility"

In order to be compatible with a protocol, the method doesn't need to have exactly the same method signatures as the protocol, they just need to be "compatible".
In other words, it should be "at least as good as a protocol": the parameters can be more wide, but the return type can be more narrow.
All these are valid `render` methods for a widget:

```py
def render(self, width: int, /) -> Iterable[str]:  # exactly the same

def render(self, width: int) -> Iterable[str]:  # width can also be a keyword argument

def render(self, width: int, with_unicorn: bool = True) -> Iterable[str]:  # _optional_ extra parameter is fine

def render(self, width: int | str) -> Iterable[str]:  #
def render(self, width: object) -> Iterable[str]:     # wider parameter type is allowed

def render(self, width: int) -> Iterator[str]: #
def render(self, width: int) -> list[str]:     # narrower return type is allowed
```

<!-- TODO: link to subtyping and variance stuff -->

## Conclusion

??? note "Complete program listing"

    ```py
    from abc import abstractmethod
    from collections.abc import Iterable
    from typing import Protocol
    import warnings


    class Widget(Protocol):
        @abstractmethod
        def render(self, width: int, /) -> Iterable[str]:
            raise NotImplementedError

        @property
        @abstractmethod
        def desired_width(self) -> int:
            raise NotImplementedError


    class Block:
        def __init__(self, text: str) -> None:
            self._text = text

        @property
        def desired_width(self) -> int:
            return len(self._text)

        def render(self, width: int) -> Iterable[str]:
            for i in range(len(self._text) // width + 1):
                yield self._text[i * width : (i + 1) * width]


    class Guard:
        def __init__(self, wrapped: Widget) -> None:
            self._wrapped = wrapped

        @property
        def desired_width(self) -> int:
            return self._wrapped.desired_width

        def render(self, width: int) -> Iterable[str]:
            for line in self._wrapped.render(width):
                if len(line) > width:
                    warnings.warn(
                        f"Line length ({len(line)}) exceeds supplied width ({width})"
                    )
                    yield line[:width]
                else:
                    yield line + " " * (width - len(line))


    class Pad:
        def __init__(self, char: str, wrapped: Widget) -> None:
            if len(char) != 1:
                raise ValueError("Expected a single character for padding")
            self._char = char
            self._wrapped = wrapped

        @property
        def desired_width(self) -> int:
            return self._wrapped.desired_width + 2

        def render(self, width: int) -> Iterable[str]:
            yield self._char * width
            if width > 2:
                for line in self._wrapped.render(width - 2):
                    yield self._char + line + self._char
            yield self._char * width


    class DesireWidth:
        """
        Override the `desired_width` of a child widget with a fixed value.
        """

        def __init__(self, desired_width: int, wrapped: Widget) -> None:
            self.desired_width = desired_width
            self._wrapped = wrapped

        def render(self, width: int) -> Iterable[str]:
            return self._wrapped.render(width)


    class Vertical:
        """
        Arrange widgets vertically, one after another.
        """

        def __init__(self, items: Iterable[Widget]) -> None:
            self._items = list(items)

        @property
        def desired_width(self) -> int:
            return max(item.desired_width for item in self._items)

        def render(self, width: int) -> Iterable[str]:
            for item in self._items:
                yield from item.render(width)


    class Horizontal:
        """
        Arrange widgets horizontally. You must specify how much horizontal
        space each item occupies.

        If the total of the spaces is bigger than the required width, the
        lines will be cut off from the right.
        """

        def __init__(self, items: Iterable[tuple[int, Widget]]) -> None:
            self._items = list(items)

        @property
        def desired_width(self) -> int:
            return sum(width for (width, _widget) in self._items)

        def render(self, width: int) -> Iterable[str]:
            if not self._items:
                return
            state = [
                (subwidth, iter(Guard(widget).render(subwidth)))
                for (subwidth, widget) in self._items
            ]
            active = len(state)
            while True:
                total_line = ""
                for i, (subwidth, render_iter) in enumerate(state):
                    try:
                        total_line += next(render_iter)
                    except StopIteration:
                        active -= 1
                        if active == 0:
                            return
                        total_line += " " * subwidth
                        # replace iterator with a dummy that always returns a blank line:
                        state[i] = (subwidth, iter(lambda: " " * subwidth, None))
                yield total_line[:width]


    class Flex:
        """
        Arrange items in rows, switching to a new row when the next item
        wouldn't fit according to its `desired_width`.
        """

        def __init__(self, items: Iterable[Widget]) -> None:
            self._items = list(items)

        @property
        def desired_width(self) -> int:
            return sum(item.desired_width for item in self._items)

        def render(self, width: int) -> Iterable[str]:
            rows: list[Horizontal] = []
            row: list[tuple[int, Widget]] = []
            remaining = width
            for item in self._items:
                if remaining < item.desired_width:
                    if row:
                        rows.append(Horizontal(row))
                    row = [(min(width, item.desired_width), item)]
                    remaining = width - item.desired_width
                else:
                    row.append((item.desired_width, item))
                    remaining -= item.desired_width
            if row:
                rows.append(Horizontal(row))
            return Guard(Vertical(rows)).render(width)


    b1 = Pad("1", Guard(Block("First")))
    b2 = DesireWidth(5, Pad("2", Guard(Block("SecondSecond"))))
    b3 = Pad("3", Guard(Block("The Very Third!!")))
    b4 = DesireWidth(10, Pad("4", Guard(Block("Fourth"))))

    inner = Pad("+", Flex([b1, b2]))
    outer = Pad("*", Flex([inner, b3, b4]))

    for line in outer.render(30):
        print(line)
    print()
    for line in outer.render(40):
        print(line)
    ```


[^1]: `Protocol` has some added machinery to support `typing.get_protocol_members`, but that's very niche