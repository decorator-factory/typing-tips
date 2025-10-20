# Is `object` the same as `Any`?

!!! question

    ```py
    from typing import Any

    def greet(thing: Any) -> str:
        return f"Hello, {thing}!"

    def greet(thing: object) -> str:
        return f"Hello, {thing}!"
    ```

    What's the difference?


## What is `object`?

`object` is a base class for all classes in Python.
Whatever you have &mdash; a string, a number, a function, a chess piece &mdash; it's an `object`.
If a function accepts `object` for a parameter, you can supply anything as the argument.

```py
def greet(target: object) -> None:
    print(f"Hello, {target}!")

greet("World")
greet(42)
```

For type checking purposes, `object` is not treated specially.
It behaves like an ordinary class:

1. If you have a value of type `object`, you can only do things with it that are appropriate
    for any object.
    Operations that only some objects might support are not allowed.

    ```py
    def greet(target: object) -> None:
        print(f"Hello, {target}!")  # ok
        print(target is None)  # also ok
        print(target.name())  # ERROR
        print(target + 50)  # ERROR
        number: int = target  # ERROR
    ```

 1. Variance works as expected.
    <!-- TODO link tutorial about variance -->
    ```py
    foo: tuple[int, ...] = (1, 2, 3)
    bar: tuple[object, ...] = foo  # ok

    foo: list[int] = [1, 2, 3]
    bar: list[object] = foo  # ERROR

    def fizz(a: object) -> None:
        ...
    buzz1: Callable[[int], None] = fizz # ok
    buzz2: Callable[[int], object] = fizz # ok
    buzz3: Callable[[object], object] = fizz # ok

    def quack(loudness: int) -> str:
        ...
    duck1: Callable[[int], object] = quack  # ok
    duck2: Callable[[object], str] = quack  # ERROR
    ```

If you want to narrow an `object` to a more specific type, you can do an `isinstance` check:

```py
def fizz(a: object) -> None:
    if isinstance(a, int):
        print("The answer differential:", a - 42)
    else:
        print("Interestingly:", a)
```

## What is `Any`?

Marking a value as `Any` tells the type checker to trust anything you do with the object:

```py
def greet(thing: Any) -> str:
    name = thing.name()
    mysterious = thing + 42
    return f"{mysterious} {name}"
```

We cover `Any` in more detail on ["Avoid `Any`"](../avoid-any/index.md)

## What's the difference?

If you have a value of type `Any`, you are allowed to perform any operation on that value.

If you have a value of type `object`, you are only allowed to perform operations on it that are valid for _every_ `object`.

Let's look at the original example:
```py
def greet(thing: Any) -> str:
    return f"Hello, {thing}!"

def greet(thing: object) -> str:
    return f"Hello, {thing}!"
```
In the `Any` version of `greet`, the type checker will not complain if you use `thing.name()` instead of `thing`,
or `"Hello, " + thing` instead of `f"Hello, {thing}"`.
In the `object` version of `greet`, it would.
In this case, we don't care what `thing` is, but we need to turn it into a string.
All objects support that, so `object` is the correct choice here.

`object` is generally what you should use if you don't care what the type is, or if the type is unknown.
However, there are some use cases for `Any` which we described in ["Avoid `Any`"](../avoid-any/index.md).

!!! note "For TypeScript users"

    `typing.Any` is similar to `any` in TypeScript, and `object` is similar to `unknown` in TypeScript.
    As of writing this, there's no equivalent to `void` in Python.
