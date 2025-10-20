# Generic functions

The following few chapters introduce _type variables_, _generic functions_
and _generic classes_.
These are pretty advanced concepts, and you will probably not define your own generic
functions and classes very often.
However, you will use generic functions and classes made by other people, and
understanding them will help you understand why type checkers complain about certain things.

## How to define a generic function

Suppose that you have this function:
```py
from typing import reveal_type
import random

def pick_option(option1: str, option2: str) -> str:
    if random.random() > 0.5:
        return option1
    else:
        return option2

fruit = pick_option("apple", "banana")
reveal_type(fruit)  # str
```

It's a fine function, but you might want to make it more flexible.
`pick_option` would work just as well with options other than strings, but it's
artificially limited to accept and return `str` by the type signature. How can we
make it work with other objects? We could use `object`:
```py
def pick_option(option1: object, option2: object) -> object:
    if random.random() > 0.5:
        return option1
    else:
        return option2

fruit = pick_option("apple", "banana")
reveal_type(fruit)  # object

number = pick_option(42, 57)
reveal_type(number)  # object

numbers = pick_option([1, 2, 3], [4, 5])
reveal_type(numbers)  # object
```
Unfortunately, `fruit`, `number`, and `numbers` are all inferred to be `object`.
This is annoying, because doing `fruit + "!"` or `numbers[0]` will produce a
type checking error, even though you know it's fine at runtime.
That's because type checkers don't understand that the types of `option1`, `option2`
and the returned value are linked in some way.

You can solve this by introducing a _type variable_ to the function signature:
```py
def pick_option[Opt](option1: Opt, option2: Opt) -> Opt:
    if random.random() > 0.5:
        return option1
    else:
        return option2

fruit = pick_option("apple", "banana")
reveal_type(fruit)  # str

number = pick_option(42, 57)
reveal_type(number)  # int

numbers = pick_option([1, 2, 3], [4, 5])
reveal_type(numbers)  # list[int]
```
In this snippet, `Opt` is a type variable scoped to the `pick_option` function.
The purpose of a type variable is to link the type of different values together.
Inside the function, the type variable can be used whenever a normal type can be used:
```py
def pick_option[Opt](option1: Opt, option2: Opt) -> Opt | None:
    selected_option: Opt | None = None

    if random.random() > 0.33:
        selected_option = option1
    elif random.random() > 0.5:
        selected_option = option2

    return selected_option
```
A function containing type variables in the signature is called a _generic function_.


## Using a type variable as a type parameter

You can use a type variable instead of a concrete type when parameterizing generic types
like `list`, `dict`, `Iterable` and so on:

```py
def pick_options[Opt](option1: Opt, option2: Opt, *, count: int) -> list[Opt]:
    options: list[Opt] = []
    for _ in range(count):
        options.append(random.choice([option1, option2]))
    return options

fruits = pick_options("apple", "banana", count=10)
reveal_type(fruits)  # list[str]

numbers = pick_options(42, 57, count=5)
reveal_type(numbers)  # list[int]
```

You can use this to type functions that operate on e.g. lists but don't care what's inside
the list:

```py
def every_second_element[T](items: list[T]) -> list[T]:
    return items[1::2]
```


## Callables and collections

As you may know, Python has first-class functions: you can pass functions as arguments
to other functions, or use a function as a return value.
That's supported by most modern programming languages.

`Callable` a special form in the `collections.abc` module that allows expressing the
type of a _callable object_.
User-defined functions are callable, but so are built-in functions, classes,
`functools.partial` objects and other user-defined classes with the special `__call__` method.

`Callable` accepts two type arguments: a list of argument types and a return type. Here's an example:
```py
from collections.abc import Callable

def calculate(fn: Callable[[int, int], float]) -> None:
    print(fn(2, 1))
    print(fn(3, 4))
    print(fn(42, 57))
    print(fn(False, True))

def divide(x: int, y: int) -> float:
    return x / y

def add(x: int, /, y: int) -> float:
    # slash (/) in the signature means that x is a positional-only parameter
    return float(x + y)

calculate(divide)
calculate(add)
```

`fn: Callable[[int, int], float]` means that `fn` must be a callable accepting
two arguments of type `int` and returning a `float`.

One common application of generic functions is processing collections of
unknown types.
When doing so, you should almost always accept a general type
like `Iterable` or `Iterator` or `Mapping` instead of concrete classes like
`list` or `dict`.
It makes the function more flexible and clarifies the intent: you
are only intending to read the collection/iterable, not modify it.

Here are some examples of classic functions for processing collections, fully
annotated:

```py
from collections.abc import Callable, Collection, Iterable, Iterator, Mapping
from typing import reveal_type

def filter[T](items: Iterable[T], predicate: Callable[[T], bool]) -> Iterator[T]:
    for item in items:
        if predicate(item):
            yield item

def map[A, B](items: Iterable[A], fn: Callable[[A], B]) -> Iterator[B]:
    for item in items:
        yield fn(item)

def flatten[T](iterables: Iterable[Iterable[T]]) -> Iterator[T]:
    for it in iterables:
        yield from it

def zip[A, B](first: Iterable[A], second: Iterable[B]) -> Iterator[tuple[A, B]]:
    it1, it2 = iter(first), iter(second)
    while True:
        try:
            yield (next(it1), next(it2))
        except StopIteration:
            break

def count[T](items: Iterable[T]) -> dict[T, int]:
    counter: dict[T, int] = {}
    for item in items:
        counter[item] = counter.get(item, 0) + 1
    return counter

def pick[K, V](m: Mapping[K, V], keys: Collection[K]) -> dict[K, V]:
    return {k: v for k, v in m.items() if k in keys}

def filter_none[T](items: Iterable[T | None]) -> Iterator[T]:
    for item in items:
        if item is not None:
            yield item


letters = count("aaaaabbbbabbaabacbbaaabb")
reveal_type(letters)  # dict[str, int]

fruits = pick({"apple": 3.14, "banana": 2.718, "cherry": -0.1}, {"apple", "banana"})
reveal_type(fruits)  # dict[str, float]

flat1 = flatten([[1, 2], [3, 4]])
reveal_type(flat1)  # Iterator[int]

flat2 = flatten([([1, 2], [3, 4]), ([5, 6], [7, 8])])
reveal_type(flat2)  # Iterator[list[int]]

maybe_ints = [1, 2, None, 3, None, 4, 5, None]
reveal_type(maybe_ints)  # list[int | None]
ints = filter_none(maybe_ints)
reveal_type(ints)  # Iterator[int]
```

Let's examine how a generic function works in more detail.
You can always debug what's going on in a function by adding calls to `reveal_type`
and running your type checker.
(If you're using something other than `mypy`, you can also extract a variable and hover
over it to see its inferred type.)
```py
def map[A, B](items: Iterable[A], fn: Callable[[A], B]) -> Iterator[B]:
    for a in items:
        reveal_type(a)
        b = fn(a)
        reveal_type(b)
        yield b
```
You will see something to the effect of "the type of a is A@map" and "the type of b is B@map".

A particularly interesting example is the `filter_none` function.
Instead of the "inner type" of the iterable being extracted and simply copied to the output iterable,
the argument type is matched against the expected `Iterable[T | None]` to figure out what `T` needs to be.

When you call a generic function, you don't explicitly state what value you want to provide for
the type variables.
The type checker needs to figure that out on its own in a process called
"constraint solving".
Essentially, it needs to find a suitable value for `T` (in the `filter_none`
example) such that this would type-check:
```py
type T = ???

def filter_none*(items: Iterable[T | None]) -> Iterator[T]:
    for item in items:
        if item is not None:
            yield item

maybe_ints: list[int | None] = [1, 2, None, 3, None, 4, 5, None]
ints = filter_none*(maybe_ints)
```
If `T` is `int`, the argument type is successfully matched with the parameter type (because `list[int | None]` is-a
`Iterable[int | None]`). However, there are other valid solutions for T:

- T could be `int | None`
- T could be `object`
- T could be `int | socket` (not a serious solution, but it does work out: `list[int | None]` is-a `Iterable[int | socket | None]`)

When there are multiple possible solutions, a type checker will pick one of them,
presumably one that makes the most sense and in a consistent fashion.
The details of constrain solving are not specified and differ between type checkers. To illustrate,
type checkers disagree on the inference here:

```py
import random
from typing import reveal_type

def pick_option[Opt](option1: Opt, option2: Opt) -> Opt:
    if random.random() > 0.5:
        return option1
    else:
        return option2

mystery = pick_option("banana", 42)
reveal_type(mystery)
```

- `pyright` says that `mystery` is of type `int | str`
- `mypy` says that `mystery` is of type `object`
- `ty` says that `mystery` is of type `Literal["banana", 42]`
- `pyrefly` rejects this snippet, saying that 42 is not assignable to type `str`

Sometimes you can refactor the signature so that type checkers are in better agreement with each other.
In this case we can do the following:

```py
import random
from typing import reveal_type

def pick_option[A, B](option1: A, option2: B) -> A | B:
    if random.random() > 0.5:
        return option1
    else:
        return option2

reveal_type(pick_option(100, 200))
reveal_type(pick_option("banana", 42))
```


## Type variables with a bound

In a generic function, you cannot assume that a type behind a type variable supports any
particular operation besides what's universal among all objects.

```py
def pick_option[Opt](option1: Opt, option2: Opt) -> Opt:
    print(option1, option2)  # allowed, you can print any objects

    if random.random() > 0.99:
        return option1 + "!!!"  # not allowed: option1 might not support `+` with `str`
    elif random.random() > 0.5:
        return option1
    else:
        return option2
```

Type variables support setting a _bound_, requiring that the solution to the type variable
must fit the bound.
The bound is provided by adding a colon (`:`) and the bounded type
after the type variable:
```py
from collections.abc import Iterable, Iterator
from enum import IntFlag
from typing import reveal_type

def positive_ints_v1(ints: Iterable[int]) -> Iterator[int]:
    for i in ints:
        if i > 0:
            yield i

def positive_ints_v2[T: int](ints: Iterable[T]) -> Iterator[T]:
    for i in ints:
        if i > 0:
            yield i

class OpenMode(IntFlag):
    none = 0
    read = 1
    write = 2
    binary = 4

reveal_type(positive_ints_v1([1, 2, 0, 3, -1, 4]))  # Iterator[int]
reveal_type(positive_ints_v1([True, False, True]))  # Iterator[int]
reveal_type(positive_ints_v1([
    OpenMode.none, OpenMode.read | OpenMode.write]))  # Iterator[int]

reveal_type(positive_ints_v2([1, 2, 0, 3, -1, 4]))  # Iterator[int]
reveal_type(positive_ints_v2([True, False, True]))  # Iterator[bool]
reveal_type(positive_ints_v2([
    OpenMode.none, OpenMode.read | OpenMode.write]))  # Iterator[OpenMode]

positive_ints_v2(["a", "b", "c"])  # type checker complains
positive_ints_v2([1, 2, 3, None])  # type checker complains
```

As you can see, the difference between the two functions is that `positive_ints_v2` preserves
the subclass of `int` that the iterable contains, while `positive_ints_v1` always produces an
`Iterator[int]`.

Try removing the `: int` bound. You should see that your type checker complains about the
`i > 0` comparison.


## Protocol bound

Sometimes you want to constrain a type variable to types that have certain methods
or attributes, even if they don't share a common base class.
This is where `Protocol` comes in handy:

```py
import io
from typing import Protocol, reveal_type
from collections.abc import Iterable, Iterator

class FileLike(Protocol):
    def tell(self) -> int: ...

def files_at_the_start[F: FileLike](files: Iterable[F]) -> Iterator[F]:
    for file in files:
        if file.tell() == 0:
            yield file

with open("apple.txt") as fa, open("banana.txt") as fb:
    reveal_type(files_at_the_start([fa, fb]))
    # Iterator[TextIOWrapper[_WrappedBuffer]]

s1, s2 = io.StringIO(), io.StringIO()
reveal_type(files_at_the_start([s1, s2]))
# Iterator[StringIO]
```

For more information on protocols, check out [the previous chapter](../2-using-protocols/index.md)


## Generic methods

A function doesn't need to be "free-standing" to be generic. Generic methods work very much the same
as generic functions.

```py
from collections.abc import Callable, Iterator

class Times:
    def __init__(self, value: int) -> None:
        self._value = value

    def repeat[T](self, item: T, /) -> list[T]:
        return [item] * self._value

    def do[T](self, fn: Callable[[int], T], /) -> Iterator[T]:
        for i in range(self._value):
            yield fn(i)

    def make_pair[K, V](self, make_key: Callable[[int], K], make_value: Callable[[int], V]) -> tuple[K, V]:
        return make_key(self._value), make_value(self._value)


times = Times(10)
bananas = times.repeat("banana")  # bananas: list[str]
screams = times.do(lambda n: "a" * (n + 1))  # screams: Iterator[str]
k, v = times.make_pair(str, lambda n: n + 100)  # k: str, v: int
```

!!! note "This is not the same as a _class_ being generic"

    Notice that `[T]` and `[K, V]` are scoped to each method and not on the class.
    Generic methods are very different from generic classes (which we'll cover
    in a different chapter), make sure that you don't confuse the two.

    A generic method allows specifying a different `T` every time you call it on the
    same object, whereas an instance of a generic class (like `list[Fruit]`) is itself
    parameterized.
    (A generic class can have a generic method too: for example, `dict[K, V]` has a
    `get` method that depends on K, V, and the type of the default provided)

<!--
I am doing a bit of time travel here, but it's possible that the reader has already
seen generic classes and/or methods.
It's also possible that people read just up to this article and interact with generic
classes anyway -- it's pretty difficult to write Python code without lists or dicts.
-->

## Type variables with constraints

Sometimes you'll encounter type variables that list several types in parentheses:

```py
def concat[S: (str, bytes)](x: S, y: S) -> S:
    return x + y
```

`S` is called a "type variable with constraints".
This is not the same as declaring `S: str | bytes`, and instead it means that `S` can be
solved as just `str` or just `bytes`, not a subtype of `str` or `bytes` like `Literal[b"foo"]`
or a subclass of `enum.StrEnum`, and not a union type like `str | bytes`.

We will not be discussing this feature in detail, instead refer to:

- [the mypy documentation](https://mypy.readthedocs.io/en/stable/generics.html#type-variables-with-value-restriction)
- [the type system reference](https://typing.pyth   on.org/en/latest/reference/generics.html#type-variables-with-constraints)

This feature is very rarely the best tool for the job, and you'll probably experience
some headache when using it.

## Examples of generic functions in the standard library

Most of the Python standard library code in the reference implementation (CPython)
does not have any type annotations at all.
There are multiple reasons for this:

1. A lot of it is written in C
1. A lot of it was written without consideration for type checkers, so it
    cannot be annotated well without breaking changes or extreme amounts
    of "jank" on top of the actual code.
1. Not everyone working on Python agrees that type annotations are a good idea at all
1. The type system (including the `typing` module) gets new features every year, and
    putting the types in the standard library source code would mean that e.g.
    Python 3.10 users get worse annotations for the standard library than Python 3.14
    users.
1. Type information adds some amount of overhead when importing (and sometimes running)
    the code.

!!! note "For more information, see [this Discourse thread](https://discuss.python.org/t/type-annotations-in-the-stdlib)"


The canonical type information for the standard library, as well as some third-party packages,
is maintained by the [typeshed](https://github.com/python/typeshed) project. It contains
_stub files_ which only describe the interfaces of classes and functions without providing
their implementation.

Let's take a look at how generic functions are used to express some things
from the standard library. It's definitely not an exhaustive list, but it should give an idea
of how type variables are used in practice.

!!! note

    As of writing this in 2025, the typeshed uses [old-style syntax](#old-style-syntax)
    for type variables for compatibility. I translated all the examples to new-style
    syntax to avoid confusion.

### `copy.copy`

[`copy.copy`](https://github.com/python/typeshed/blob/11e7d904b9745bf33fe5b9b64bcd274ff788b189/stdlib/copy.pyi#L19)
uses a type variable in a very straightforward way. Whatever type comes in, the same type comes out.

```py
def copy[T](x: T) -> T:
    ...
```

### `enum`

[`enum.unique`](https://github.com/python/typeshed/blob/11e7d904b9745bf33fe5b9b64bcd274ff788b189/stdlib/enum.pyi#L251)
is a class decorator: it's a function that accepts a class and returns a class. In this case, it returns the same class,
but it must be a subclass of `enum.Enum`.

```py
def unique[E: type[Enum]](enumeration: E) -> E:
    ...
```

`type[Enum]` is something we haven't covered yet.
`type[X]` means the _class_ `X` (as opposed to an _instance_ of the class `X`), or any of its subclasses.
For example, the _values_ `int` and `bool` would both satisfy `type[int]`, but `42` and `object` would not.

```py
@enum.unique  # works fine
class MaybeBool(enum.Enum):
    yes = 1.0
    no = 0.0
    maybe = 0.5

@unique  # type checker will complain: Banana is not a subclass of Enum
class Banana:
    def speak(self) -> None:
        print("*banana noises*")

unique(MaybeBool.yes)  # type checker will complain: MaybeBool.yes is not a class
```

### `multiprocessing.pool.Pool`

The [`map`](https://github.com/python/typeshed/blob/11e7d904b9745bf33fe5b9b64bcd274ff788b189/stdlib/multiprocessing/pool.pyi#L63)
method on `Pool` is very similar to the `map` function that was shown in a previous code sample:

```py
class Pool:
    def map[S, T](
        self,
        func: Callable[[S], T],
        iterable: Iterable[S],
        chunksize: int | None = None,
    ) -> list[T]:
        ...
```

### `concurrent.futures.Executor`

The [`submit`](https://github.com/python/typeshed/blob/11c7821a79a8ab7e1982f3ab506db16f1c4a22a9/stdlib/concurrent/futures/_base.pyi#L55)
method on `Executor` is generic in order to link the type of the provided function with the type
of the returned `Future`:

```py
class Executor:
    def submit[**P, T](
        self, fn: Callable[P, T], /,
        *args: P.args, **kwargs: P.kwargs,
    ) -> Future[T]:
        ...
```

It uses a "parameter specification variable" which we haven't covered yet.
In short, a type variable prefixed with `**` captures the argument part of a function
signature, including all the necessary details like variadic arguments, some arguments
being accepted as positional-only or keyword-only and such.
<!-- TODO: link ParamSpec chapter -->

### `contextlib.closing` and `contextlib.nullcontext`

`contextlib` uses generic classes in the typeshed definition. To avoid time travel within this
tutorial, we can define `nullcontext` and `closing` using
[`contextlib.contextmanager`](https://docs.python.org/3/library/contextlib.html#contextlib.contextmanager)
&mdash; that's probably what you'd use in your own code.

```py
from contextlib import contextmanager
from collections.abc import Generator
from typing import Protocol


class SupportsClose(Protocol):
    def close(self) -> object: ...


@contextmanager
def nullcontext[T](obj: T) -> Generator[T]:
    yield obj


@contextmanager
def closing[T: SupportsClose](obj: T) -> Generator[T]:
    try:
        yield obj
    finally:
        obj.close()
```



## Old-style syntax { #old-style-syntax }

The modern syntax for writing generic functions using square brackets in the `def` statement
is new to Python 3.12. If you're using Python 3.11 or earlier, you need to use more verbose
syntax:

```py
# plain type variable:

## >=3.12
def identity[A](thing: A, /) -> A:
    return thing

## <3.12
_A = TypeVar("_A")

def identity(thing: _A, /) -> _A:
    return thing


# type variable with a bound:

## >=3.12
def positive_ints[B: int](ints: Iterable[B]) -> Iterator[B]:
    for i in ints:
        if i > 0:
            yield i

## <3.12
_B = TypeVar("_B", bound=int)

def positive_ints(ints: Iterable[_B]) -> Iterator[_B]:
    for i in ints:
        if i > 0:
            yield i


# constrained type variables:

## >=3.12
def add_strings[S: (str, bytes)](foo: S, bar: S) -> S:
    return foo + bar

## <3.12
_S = TypeVar("_S", int, str)

def add_strings(foo: _S, bar: _S) -> _S:
    return foo + bar
```

Note that while the TypeVar object is defined as a global variable, it's logically scoped
to the function where it is used. So the semantics are the same between the versions.

Modules typically define all their type variables at the top and reuse them for several
functions.
