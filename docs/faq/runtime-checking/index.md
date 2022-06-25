# How to enforce type annotations at runtime?

!!! question

    I have this function:
    ```py
    def foo(bar: Bar, baz: Callable[[], Baz], answers: list[int]) -> Fizz | Buzz:
        ...
    ```
    How can I automatically raise an exception if the function receives an incorrect argument?

You can do this for simple types, but not in the general case. There are some tools that help, but
it depends on what you want to check.

## Why would you need it?

Static typing in Python isn't perfect, and you might end up with the wrong type somewhere. Not everyone uses
static type checking. Some things are just not expressable in the type system. You still want your contracts
to be upheld and provide reasonable error messages, preferably at the first opportunity of catching a mistake.

Nobody likes to read "`AttributeError: 'NoneType' object has no attribute 'quack`" and then go through a nasty
traceback, or spend 15 minutes debugging your library.

## Is it even possible?

Suppose that we have a special `check_types` decorator that checks all input and output contracts.

```py
@check_types
def foo(bar: Bar, baz: Callable[[], Baz], answers: list[int]) -> Fizz | Buzz:
    ...
```

How would you implement it?

- For simple types, like `Bar`, you can just use `isinstance`.
- For union types, you'll have to traverse the variants of the union and check each one of them.
    This is definitely possible.
- For `tuple[X, ...]`, you can go over each element of a tuple. This might be costly at runtime if
    the tuple is large.
- For `list[X]`, it's tricky. You might think that you can just check the list as with `tuple`, but
    not quite. Consider this:

    ```py
    things: list[str] = []

    foo(some_bar, some_baz, answers=things)

    things.append("hey!")
    ```
    The decorator checked that all the elements are strings. Maybe it saved the list somewhere, and now
    there's a string in there. Worse, now there might be integers in the alleged list of strings.

    Or this:
    ```py
    things: list[bool] = [False, True, True]

    foo(some_bar, some_baz, answers=things)
    ```
    Here the decorator ensures that all the elements are indeed `int`s. But it doesn't mean that the list
    is assignable to `list[int]`! Now there might be `42` in the alleged list of booleans.

    But apart from that, you can make a reasonable tradeoff and just repeat the tuple algorithm.
    You probably want to accept a `Sequence[X]` that you turn into a `list` anyway.
- For very dynamic types like `Callable[[str], int]` or `Iterator[int]`, there really isn't anything
    you can check. The best you can do is to embed the types in some wrapper that will check every call
    (for a callable) or every `__next__` invocation (for an iterator). This still buries the type checking
    deep within the call stack.
- For custom generic classes, it is generally impossible to do the check. Example:
    [`aiohttp.web.AppKey`](https://docs.aiohttp.org/en/latest/web_reference.html#appkey).


## So we don't really have static typing?

The point of static typing is to find errors _before_ running the code, not at runtime. Statically typed
languages specifically don't do runtime checks on all the values, they know that the code won't
compile if the types don't match.

With _dynamic typing_, you don't know all the types in advance, so you might want to check them at
interface boundaries so that errors don't propagate too deep.

## Are there tools that can help?

??? info "`typeguard`"

    [`typeguard`](https://github.com/agronholm/typeguard)
    implements the aforementioned magic decorator! Of course, all the previous caveats apply.

    As for callables, it seems to inspect some metadata on `Callable` objects, which should work
    well in most cases.


??? info "`pydantic`"

    [`pydantic`](https://pydantic-docs.helpmanual.io/) provides a class-building framework similar to
    `attrs`, but with automagic validation using type annotations. It's used in FastAPI and some other
    web frameworks for validation, which sounds like a good use case.

??? info "`beartype`"
    [`beartype`](https://github.com/beartype/beartype)

    Beartype is like `typeguard`, but with non-deterministic checking. That is, to check a nested list of
    lists, it will check one random element from the list.


    ```py
    >>> @beartype
    ... def do_stuff(things: list[list[int]]) -> str:
    ...     return "ok"
    ...
    >>> do_stuff([[1, 2], [3, "boom!"]])
    "ok"
    >>> do_stuff([[1, 2], [3, "boom!"]])
    "ok"
    >>> do_stuff([[1, 2], [3, "boom!"]])
    # Exception!
    >>> do_stuff([[1, 2], [3, "boom!"]])
    "ok"
    ```

    Sorry, but I don't get the point.
