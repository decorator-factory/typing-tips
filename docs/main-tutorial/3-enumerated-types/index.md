# Enumerated Types

## Motivation

Sometimes you want to represent that a value should only be one of a set of specific, predefined values, like the `mode` parameter in the builtin [``open()``](https://docs.python.org/3/library/functions.html#open) function: although it is a string, it shouldnt be any ``str`` - only some specific ones.

For that, there are 2 choices: [``typing.Literal``](https://docs.python.org/3/library/typing.html#typing.Literal) and [``enum.Enum``](https://docs.python.org/3/library/enum.html#enum.Enum).

There are some differences between them, though. 

## `Literal`

``Literal`` is the simpler one, that can be used for:

- ``int``eger literals (**not ``float``s**, though)
- ``str``ing literals
- ``bytes`` literals
- ``bool``ean literals (``False, True``)
- the ``None`` singleton
- enum members, which will be explained later

``Literal[42]`` would mean a type, for which only the integer literal ``42`` is valid (or, other ways of writing an integer literal that would mean the same value, like a hex literal - ``0x2a``)

Literals can have multiple "variants" - separated with ``,``, e.g. ``Literal[1, 2]`` would mean "either the 1 literal, or the 2 literal" - no need for ``Literal[1] | Literal[2]``.

## `Enum`

``Enum``s are a bit more complex and require the user to access the members rather than just passing a value, but they can be used for non-literals and other types too, as they are
a set of names bound to (unique) values, rather than just the values themselves.

The usual way to define an enum is by defining a class and inheriting from the [``enum.Enum``](https://docs.python.org/3/library/enum.html#enum.Enum) base class, like so:

```python
from enum import Enum

class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3
```

The ``RED, GREEN, BLUE`` are called the **members** of the enum.

What does that enum mean when used as a typehint? lets say, in:

```python
def draw_circle(x: int, y: int, color: Color) -> None:
    ...
```

It means that you can only pass it a member of the ``Color`` enum, that is: ``Color.RED``, ``Color.GREEN``, ``Color.BLUE``. You cant pass just a ``1`` or a ``2`` or a ``3``, though.

The members of such an enum are somewhat special. They are not just literally the values you defined for them, if you, lets say, if you try to add ``Color.RED`` and ``Color.GREEN`` you wont get ``3`` - you will get a type error.

```python-repl
>>> from enum import Enum
>>> class Color(Enum):
...     RED = 1
...     GREEN = 2
...     BLUE = 3
...
>>> Color.RED + Color.GREEN
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: unsupported operand type(s) for +: 'Color' and 'Color'
```

If you want members of the enum to be a subclass of some type - inherit from that type too, alongside the base ``Enum`` class, or use one of the predefined base classes for some of the builtin types like ``IntEnum``, ``StrEnum``.

```python-repl
>>> class Color(int, Enum):
...     RED = 1
...     GREEN = 2
...     BLUE = 3
...
>>> Color.RED + Color.GREEN
3
```

Here members of the ``Color`` enum are subclasses of ``int``.

Enums also act as a mapping (like a dict) - if you have the name of the member as a string, you can do ``Enum[name]`` to get the member, e.g.:

```python-repl
>>> Color["RED"]
<Color.RED: 1>
```

You can also use ``Enum``s for your own classes - the class you inherit from doesnt have to be a builtin one. Then, you'd declare the members by writing the arguments to be passed to the class constructor (in the previous example, it actually did call the constructor too, so theoretically we could have written something like ``RED = "1"`` and ``Enum`` would take care of calling ``int`` on that)

Something like:

```python-repl
>>> from dataclasses import dataclass
>>> @dataclass
... class Color:
...     r: int
...     g: int
...     b: int
...
>>> class Colors(Color, Enum):
...     RED = (255, 0, 0)
...     GREEN = (0, 255, 0)
...     BLUE = (0, 0, 255)
...
>>> Colors.RED
<Colors.RED: r=255, g=0, b=0>
>>> Colors.RED.r # yep, its still usable as a `Color`, even though looks different from it
255
```

Though, you might want to say something like: dont we want to "make invalid state unrepresentable", why make the ``r, g, b`` parameters arbitrary ints? shouldnt they be in a range of 0 - 255?
And, well, you'd be right here. But, at the moment of writing, the type system is not expressive enough for us to easily implement something like this. The only thing we could do is generate a big ``Literal`` with all 256 ints in the range of 0 to 255,
thats somewhat of a limitation of types that represent specific values, even though something might easily be formulated with words - it might not necessary be easy to express with types in a programming language.

### ``auto``

``auto`` is sort of a magical class that can be called to define a value of an ``Enum`` member, its behaviour differs based on the type of the enum.

- For ``Enum`` and ``IntEnum`` it will produce a value of the last value plus one (1 if its the first one)
- For ``Flag`` and ``IntFlag`` it will produce the first power of two greater than the previous highest value (1 if its the first one)
- For ``StrEnum`` it will produce the lower-cased version of the member's name

### ``Flag``

``Flag`` is a special kind of ``Enum``, for which the members support bitwise operators (``&`` (AND), ``|`` (OR), ``^`` (XOR), and ``~`` (INVERT)), and the result of those operations will be a member of that enum too, rather than just dropping to the value type. Usually the members of such enums are ``int``s, for which, like with ``Enum`` there is a ``IntEnum`` - there is ``IntFlag``.

They can be useful for something like unix filesystem permissions - the members would then be: ``READ, WRITE, EXECUTE``.

Combinations of them would then be produced using said bitwise operators, so, something like a "read and write" permission would be ``READ | WRITE`` - so, both the ``READ`` and ``WRITE`` flag are "on", which could be checked with ``&`` (AND), e.g. ``(READ | WRITE) & READ`` is ``READ`` (which is, as a non-zero ``int``, truthy, so could be used in an ``if`` or something like that).

```python-repl
>>> from enum import IntFlag, auto
>>> class Permission(IntFlag):
...     READ = auto()
...     WRITE = auto()
...     EXECUTE = auto()
...
>>> Permission.READ, Permission.WRITE, Permission.EXECUTE
(<Permission.READ: 1>, <Permission.WRITE: 2>, <Permission.EXECUTE: 4>)
>>> Permission.READ | Permission.WRITE
<Permission.READ|WRITE: 3>
>>> (Permission.READ | Permission.WRITE) & Permission.READ
<Permission.READ: 1>
```
