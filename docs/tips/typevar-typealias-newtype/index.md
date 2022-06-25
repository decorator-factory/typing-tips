# Type variables vs type aliases vs `NewType`

This article covers the difference between:

- type aliases
- type variables (`TypeVar`)
- `NewType`

They have similar names, but they are all quite different.


## Type aliases

A type alias is just a type saved to a global constant.

### Example: repeating callback type

Suppose that you're using `Callable[[Node, datetime], Awaitable[None]]` in a few places.

```py
class NodeWatcher:
    async def before_update(
        self,
        callback: Callable[[Node, datetime], Awaitable[None]]
    ) -> None:
        ...

    async def after_update(
        self,
        callback: Callable[[Node, datetime], Awaitable[None]]
    ) -> None:
        ...

    async def before_removal(
        self,
        callback: Callable[[Node, datetime], Awaitable[None]]
    ) -> None:
        ...
```

This can get unwieldy, and if you want to change this you'll have to change it in 10 places.
Instead of repeating the same type, extract it to a type alias.


```py
NodeCallback = Callable[[Node, datetime], Awaitable[None]]


class NodeWatcher:
    async def before_update(self, callback: NodeCallback) -> None:
        ...

    async def after_update(self, callback: NodeCallback) -> None:
        ...

    async def before_removal(self, callback: NodeCallback) -> None:
        ...
```

Note that this doesn't create a new type: users of this class will be able to provide plain old functions.



## Type variables

A `TypeVar` is very different from a type alias. `TypeVar`s let you link two types together.

A type variables is not a type alias: it doesn't just let you name a type, or keep your types DRY.
It exists specifically to make generic functions and generic classes.

For a more complete explanation, see the [tutorial on type variables](../../tutorials/generics/type-vars).

### Example: filtering an iterable

```py
from collections.abc import Iterable, Iterator, Callable
from typing import TypeVar


T = TypeVar("T")


def filter_it(predicate: Callable[[T], bool], iterable: Iterable[T]) -> Iterator[T]:
    for item in iterable:
        if predicate(item):
            yield item
```


## NewType

`NewType` lets you create a wrapper type around an existing type. For example:

```py
import re
from typing import NewType


_EMAIL_REGEX = re.compile(r"[^@]+@[^@.]+\.[^@]+")


Email = NewType("Email", str)


def parse_email(string: str) -> Email:
    if _EMAIL_REGEX.fullmatch(string) is None:
        raise ValueError("Invalid email")
    return Email(string)


def send_message(email: Email, message: str) -> None:
    ...
```

Now if you call just `send_message("a@a.com", "Hi there, A!")`, you will get an error because a string is not
an `Email`. This will work though:
```py
email = parse_email("a@a.com")
send_message(email, "Hi there, A!")
```
At runtime `email` will be just a `str` object, but type checkers will know to track it as `Email`.
It can prevent some silly mistakes such as:
```py
send_message("Hi there, A!", email)
```


This can be useful when you pass around values with some specific restrictions and _semantics_:
IDs, units, currency, emails, IP addresses, URLs, hosts, paths, and so on.

However, if you're using this `Email` or `Host` a lot, consider creating a proper class for it.
