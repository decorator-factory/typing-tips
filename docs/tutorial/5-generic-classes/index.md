# Generic classes

!!! warning "This article is a draft"

Generic classes are classes that can be parameterized by one or more types.
The most notable examples of generic classes you've seen are probably
`list` and `dict`: you can write `list[int]` no denote a list with just integers,
and you can write `dict[str, int]` to denote a dictionary where the keys are
strings and the values are integers.

This parameterization is not reserved for built-in types: you and the libraries you
use can define their own classes with parameters.
This chapter teaches you how to do that.

---

You might already have an intuition as to why configuring a class with
another type is useful.
Imagine for a moment that the `list` class does not accept parameters and
can only be used as is in type annotations:

```py {title="(fake python without generics)"}
numbers = [1, 2, 3]
reveal_type(numbers)  # list

first = numbers[0]
reveal_type(first)  # what is this? `object`? `Any`?

first + 42  # is this allowed? why?
len(first)  # is this allowed? why?
```

A lot of programming is concerned with processing collections.
Either accessing the elements of a collection would not really be type checked
(since elements would be inferred as `Any` or something similar);
or accessing the elements of a collection would require extra conditionals,
leading to very silly code that checks if e.g. `first` is an `int` here.
This would be such a bad experience that adding type annotations to code would
rarely be worth the hassle.

## Basic syntax

To make a class generic, add square brackets after the class name and list
one or more names that will acts as _type parameters_.

```py
class ClassName[T]:
    ...

class ChainMap[K, V]:
    ...

class Generator[Yield, Send, Return]:
    ...
```

!!!tip "Naming type parameters"

    For collections and iterators (like `list`, `dict`, `set`,
    `collections.ChainMap`, classes from `itertools`), and in other cases where
    the subject matter is very abstract, it is common to use one-letter names for
    type variables, like `T`; `T, U, V`; `A, B`; `K, V` (for "key" and "value").

    However, if you can think of a better name, use that instead.
    It will help with understanding their purpose when reading the code.

    ```py {title="Bad"}
    class Middleware[X: ASGIApplication, Y]:
    ```

    ```py {title="Good"}
    class Middleware[App: ASGIApplication, Config]:
    ```

Just like in generic functions (see [Chapter 3](../3-generic-functions/index.md)),
you can then use the type parameters in type annotations.

```py {title="non-generic class", linenums="1"}
class Box:
    def __init__(self, value: object) -> None:
        self._value = value

    def put(self, new_value: object) -> None:
        self._value = new_value

    def get(self) -> object:
        return self._value

box = Box(42)
reveal_type(box)  # Box

answer = box.get()
reveal_type(answer)  # object
print(answer * 10)  # type checking error :(

box.put(1000)  # ok
box.put(True)  # ok
box.put("banana")  # ok :(
```


```py {title="generic class", linenums="1"}
class Box[T]:
    def __init__(self, value: T) -> None:
        self._value = value

    def put(self, new_value: T) -> None:
        self._value = new_value

    def get(self) -> T:
        return self._value

box = Box[int](42)
reveal_type(box)  # Box[int]

answer = box.get()
reveal_type(answer)  # int
print(answer * 10)  # ok 🎉

box.put(1000)  # ok
box.put(True)  # ok (bool is a subclass of int)
box.put("banana")  # type checking error 🎉
```

Here, we created a `Box` class that accepts one type parameter, representing
the type of the value it's storing.
Then, on line 11, we created an instance of `Box[int]`.
You can think of `Box[int]` as a copy-pasted version of `Box` where
every instance `T` is replaced by an `int`:
```py
class IntBox:
    def __init__(self, value: int) -> None:
        self._value = value

    def put(self, new_value: int) -> None:
        self._value = new_value

    def get(self) -> int:
        return self._value
```


### Instantiating a generic class

You don't have to call the generic class like the above, you can also use
a variable annotation:
```py
box: Box[int] = Box(42)
reveal_type(box)  # Box[int]
```
However, very often you can omit the annotation entirely, if `T` can be inferred from
the arguments to `__init__`:
```py
box = Box(42)
reveal_type(box)  # Box[int]
```
**Use this where possible**.
Do not add annotations when they are unnecessary.


You've already seen a common case where this is not an option though &mdash;
when creating an empty collection:
```py
d = defaultdict[str, set[int]](set)
# or:
d: defaultdict[str, set[int]] = defaultdict(set)
```
One reason to avoid the former style is that it has a runtime cost [^generic-inst-slow].


## More examples

### `Pair`

An example with more than one type variable:

```py
class Pair[L, R]:
    def __init__(self, left: L, right: R, /) -> None:
        self._left = left
        self._right = right

    @property
    def left(self) -> L:
        return self._left

    @property
    def right(self) -> R:
        return self._right


pair = Pair("red", 42)
reveal_type(pair)        # Pair[str, int]
reveal_type(pair.left)   # str
reveal_type(pair.right)  # int
```

You can also add an explicit annotation where the type can be inferred, but it's not the
type you wanted:
```py
from typing import Literal

type Color = Literal["red", "blue"]

pair2: Pair[Color, int] = Pair("red", 42)
pair3: Pair[str, list[int]] = Pair("red", [True, True, False])
```


### `Stack`

```py
from collections.abc import Iterable, Iterator
from typing import reveal_type

class Stack[T]:
    def __init__(self, items: Iterable[T] = (), /) -> None:
        self._items = list(items)

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[T]:
        return iter(self._items)

    def push(self, item: T, /) -> None:
        self._items.append(item)

    def pop(self, /) -> T:
        return self._items.pop()

int_stack = Stack([1, 2, 3])
reveal_type(int_stack)  # `Stack[int]`

stack_idk = Stack()
reveal_type(stack_idk)  # mypy, ty, pyrefly say: `Stack[Any]`
                        # pyright says: `Stack[Never]` (see explanation)

stack_explicit: Stack[int] = Stack()
reveal_type(stack_explicit)  # `Stack[int]`

str_stack = Stack(["a", "b", "c"])
reveal_type(str_stack)        # `Stack[str]`
str_stack.push("something")   # ok
reveal_type(str_stack.pop())  # `str`
str_stack.push(42)            # type checking error
```

Type checkers don't agree on what to do with `stack_idk`.
`mypy`, `pyrefly` and `ty` all say that it's `Stack[Any]` (or something close),
because they don't have any clues as to what `T` in `Iterable[T]` stands for.

However, `pyright` infers it as `Stack[Never]`.
We haven't seen `typing.Never` before, but it will probably appear in a later chapter.
It is an unusual special type that contains no values at all.
For example, if `x: list[Never]` then `x` is always empty.
`pyright` sees that `()` is empty, which means that it's a `tuple[Never, ...]`
and therefore an `Iterable[Never]`, so it solves that `T = Never`.

Some type checkers have configuration options to catch situations where you
accidentally make a value with a partially unknown type (meaning that it has
`Any` as a parameter without you explicitly writing it).

- In `mypy` will complain that `stack_idk` needs an annotation without any settings
- In `pyrefly`, enable the [`implicit-any`](https://pyrefly.org/en/docs/error-kinds/#implicit-any)
    configuration option
- In `pyright` or `basedpyright`, enable the `reportUnknownMemberType`, `reportUnknownVariableType`
    and all the other `^reportUnknown.*` options.
    Alternative, set the `typeCheckingMode` to `strict`, which changes the defaults to these options.

If you don't want to accept an initial iterable in the `__init__`, you can explicitly annotate
the attribute in the `__init__` or the class body:
```py
class Stack[T]:
    def __init__(self) -> None:
        self._items: list[T] = []
# or:
class Stack[T]:
    _items: list[T]

    def __init__(self) -> None:
        self._items = []
```


### `map`

```py {.annotate}
from collections.abc import Callable, Iterator, Iterable

class MapIter[Src, Dest]:
    def __init__(self,
        source: Iterable[Src],
        fn: Callable[[Src], Dest],
    /) -> None:
        self._it = iter(source)  # self._it inferred as: Iterator[Src]
        self._fn = fn

    def __iter__(self) -> Iterator[Dest]:# (1)!
        return self

    def __next__(self) -> Dest:
        return self._fn(next(self._it))
```

1. `typing.Self` might be more appropriate here, but we haven't introduced it yet,
    but `Iterator[Dest]` or `MapIter[Src, Dest]` are perfectly fine.

What's interesting here is that once you instantiate `MapIter`, none of the
public interface of the class mentions `Src`.
It only matters inside of the class body: inside of `__next__`,
`self._it` is of type `Iterator[Src]`, `next(self._it)` is of type `Src`,
 and `self._fn` is of type `Callable[[Src], Dst]`.

### TODO: more examples


## Difference between method-level and class-level type variables

In [Chapter 3's "Generic methods" section](../3-generic-functions/index.md#generic-methods)
we showed an example of a generic method with its own type variable.
That's not the same as the whole class being generic.
It's crucial to understand the difference.

Let's look at the example from chapter 3:
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


times = Times(10)
reveal_type(times)  # Times
                    # ^^^^^ no parameter!

strings = times.repeat("banana")
reveal_type(strings)  # list[str]

numbers = times.repeat(42)
reveal_type(numbers)  # list[int]

hundreds = times.do(lambda x: x * 1.5)
reveal_type(hundreds)  # Iterator[float]
```

The `Times` class is not generic, you cannot parameterize it.
All of its attributes are also of a non-generic type.
The `repeat` method is a self-contained generic function,
and the `do` method is also a self-contained generic function.
They do not have some shared `T` type when you call those methods on the same instance.

To further illustrate the difference, here's a _generic class_ that also has a _generic method_:

```py hl_lines="1 19-32"
from collections.abc import Iterable, Iterator, Callable

class Stack[T]:
    def __init__(self, items: Iterable[T] = (), /) -> None:
        self._items = list(items)

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[T]:
        return iter(self._items)

    def push(self, item: T, /) -> None:
        self._items.append(item)

    def pop(self, /) -> T:
        return self._items.pop()

    def map[U](self, func: Callable[[T], U], /) -> Stack[U]:
        return Stack(map(func, self._items))

strings = Stack(["apple", "banana", "cherry"])
reveal_type(strings)  # Stack[str]

lengths = strings.map(len)
reveal_type(lengths)  # Stack[int]

encoded = strings.map(lambda s: s.encode())
reveal_type(encoded)  # Stack[bytes]

first_letters = strings.map(lambda s: s[:1])
reveal_type(first_letters)  # Stack[str]
```

Here, the `T` type variable is scoped at the class level, and the `U`
type variable is scoped to the `map` method.
`T` describes variation that applies to the a particular `Stack` instance, while
`U` describes variation that applies to a particular call of `map`.

## Inheriting from a generic class

### Scenario 1: continuing the same generic vibe

**TODO** (example: `class ReversibleStack[T](Stack[T])`)

### Scenario 2: inheriting from a parameterized class

**TODO** (example: `class LowerCaseStack(Stack[str])`)

### Scenario 3: inheriting with a transformed parameter

**TODO** (example: `class MultiDict[K, V](Mapping[K, list[V]])`?)

## Variance of generic classes

In [Chapter 4](../4-assignability/index.md) we introduced the concepts of
_assignability_ and _variance_, and mentioned some rough rules for figuring
out the variance of a class.
Now that you know how to define your own generic classes, we'll make it more rigorous.

### Recap

As a reminder, variance describes how assignability of a type parameter impacts
the assignability on the generic class as a whole.
Assuming that `Banana` is assignable to `Fruit` (perhaps a subclass of `Fruit`),
`Class[T]` is:

- **covariant** if `Class[Banana]` is assignable to `Class[Fruit]`
- **contravariant** if `Class[Fruit]` is assignable to `Class[Banana]`
- **invariant** if neither is true (`Class[Fruit]` and `Class[Banana]` are not assignable to each other)

A _covariant_ class parameterized by `T` is a pure "producer" of `T`s.
It's safe to assign `a: Producer[Banana]` to `b: Producer[Fruit]` because
you can only interact with `b` by getting some `Fruit` out of it.
And since you should be okay with getting a `Banana` as part of that, that's okay.

Immutable collections are typically covariant.

![Conveyor belt delivering fruits to a funnel labeled 'Belt[Fruit]',
and a conveyor belt delivering bananas labeled 'Belt[Bananas]' shown as assignable to it,
but not the other way around](./covariance_belt_illustration.png)
/// caption
`Belt[T]` is covariant in `T`
///

A _contravariant_ class parameterized by `T` is a pure "consumer" of `T`s.
It's safe to assign `a: Consumer[Fruit]` to `b: Consumer[Banana]` because
the only way to interact with `a` is to give it `Fruit`s, and `Banana` is
a kind of fruit, so `a` must be capable of handling them too.

"Handlers" of things (events, requests, etc.) are typically contravariant.

![Funnel accepting any fruits from a conveyor belt labeled 'Funnel[Fruit]',
and a funnel with a banana-shaped hole and a warning saying 'Banana only!' with type 'Funnel[Banana]'.
The fruit funnel is assignable to the banana funnel, but not the other way around.](
./contravariance_belt_illustration.png)
/// caption
`Funnel[T]` is contravariant in `T`
///

An _invariant_  class parameterized by `T` has ways to interact with it that
get a `T` from it as well as give it `T`s.
Flexing the parameter either way will land you in trouble: if you assign `a: Both[Banana]`
to `b: Both[Fruit]`, you risk someone handing `b` an `Apple`, which it cannot handle;
and if you assign `a: Both[Fruit]` to `b: Both[Banana]`, you risk `b` producing something
which is not a banana.

Mutable collections are typically invariant.

![Tank that accepts bananas and produces banana juice on the left labeled 'Tank[Banana]'.
Tank that accepts any fruits and produces multifruit juice on the right labeled 'Tank[Fruit]'.
They are not interchangeable](./invariance_belt_illustration.png)
/// caption
`Tank[T]` is invariant in `T`
///

### The algorithm

This is the series of steps you need to take to figure out the variance of a class.
It might be a bit complex, but we'll break down the steps in more detail.

1. If there are any _public_ (not `_underscored` or `__mangled`) attributes in `Class`
    that depend on `T`, then `Class` is invariant in `T` [^attr-invariant].

2. Imagine that `Banana` is assignable to `Fruit`, but not the other way around.
    Construct two versions of the class, `Class[Banana]` and `Class[Fruit]`.

3. Check the compatibility of private attributes.
    For each attribute `_attr`:

    - If `Class[Fruit]._attr` is not assignable to `Class[Banana]._attr`,
    then `Class` cannot be _contravariant_ in `T`.
    - If `Class[Banana]._attr` is not assignable to `Class[Fruit]._attr`,
    then `Class` cannot be _covariant_ in `T`.

    In other words: if all the attributes are covariant in `T`, the class is allowed to
    be covariant in `T`; if all the attributes are contravariant in `T`, the class is allowed to
    be contravariant in `T`.

4. Check the compatibility of methods:

    - If `Class[Fruit].method` wouldn't be compatible with `Class[Banana].method`,
    then `Class` cannot be _contravariant_ in `T`.
    - If `Class[Banana].method` wouldn't be compatible with `Class[Fruit].method`,
    then `Class` cannot be _covariant_ in `T`.

    `child_func` is compatible with `parent_func` if, given:
    ```py
    def parent_func(self, arg: OriginalArg) -> OriginalReturn: ...
    def child_func(self, arg: NewArg) -> NewReturn: ...
    ```
    `OriginalArg` is assignable to `NewArg` and `NewReturn` is assignable to `OriginalReturn`.

5. By this point, if both covariance and contravariance are possible, then
    the class is considered covariant.
    If neither of them is possible, it is invariant.


---

This algorithm is phrased in terms of adding restrictions.
We start with the assumption that the class can "flex" in both directions
(co- and contra-) and we try to "cross out" one of the directions on each step.

If this is confusing, think of it this way: if all the elements are pointing in one
direction (e.g.: prohibit contravariance, allowing covariance), then the entire
class is "that direction" (e.g.: covariant).
If the directions are mixed (sometimes we cross out covariance, sometimes cross
out contravariance), then the class is invariant.

---

First, let's look at methods (step 4).

In [Chapter 4](./4-assignability/index.md#rules-for-variance), we introduced a
shortcut: covariant type variables occur in "output positions" (return types),
and contravariant type variables occur in "input positions" (argument types).

Step 4 in the algorithm phrases it more accurately: we check the _assignability_
of argument and return types.

This correctly takes into account cases where argument and return types themselves
are generics parameterized by the class's type parameter.
In a sense, this plays back recursively into assignability.
Let's look at a practical example:

```py
class Belt[T]:
    def get_next(self) -> T: ...
    def on_next(self, callback: Callable[[T], None]) -> None: ...

    def get_many_tuple(self, count: int) -> tuple[T, ...]: ...
    def get_many_list(self, count: int) -> list[T]: ...
```

- `get_next`:

    ```
    Belt[Fruit].get_next:  (self) -> Fruit
    Belt[Banana].get_next: (self) -> Banana
    ```

    `Banana` is assignable to `Fruit`, and there are no arguments, so `Belt[Banana].get_next`
    is compatible with `Belt[Fruit].get_next`.
    But not the other way around: `Fruit` is not assignable to `Banana`, so `Belt[Fruit].get_next`
    is not compatible with `Belt[Banana].get_next`.
    This means `Belt` can still be covariant, but cannot be contravariant.


- `on_next`:

    ```
    Belt[Fruit].on_next:  (self, callback: Callable[[Fruit], None]) -> Fruit
    Belt[Banana].on_next: (self, callback: Callable[[Banana], None]) -> Banana
    ```

    Remember, `Callable` is contravariant in its parameters, so `Callable[[Fruit], None]`
    is assignable to `Callable[[Banana], None]`.
    Therefore, `Belt[Banana].on_next` is compatible with `Belt[Fruit].on_next`.

    As in `get_next`: `Callable[[Banana], None]` is not assignable to `Callable[[Fruit], None]`,
    so this method would prevent `Belt` from being contravariant.

    This illustrates why "input position" and "output position" are a bit misleading.
    `T` is used as an input to a contravariant type, so it's used in the "output position" here.

- `get_many_tuple`:

    ```
    Belt[Fruit].get_many_tuple:  (self) -> tuple[Fruit, ...]
    Belt[Banana].get_many_tuple: (self) -> tuple[Banana, ...]
    ```

    This will be almost the same as in `get_next`:
    `tuple[Banana, ...]` is assignable to `tuple[Fruit, ...`] (because `tuple` is covariant),
    and there are no arguments, so `Belt[Banana].get_next` is compatible with `Belt[Fruit].get_next`.
    Not the other way around, so it's not contravariant.

- `get_many_list`:

    ```
    Belt[Fruit].get_many_list:  (self) -> list[Fruit]
    Belt[Banana].get_many_list: (self) -> list[Banana]
    ```

    `list[Banana]` is not assignable to `list[Fruit]`, and `list[Fruit]` is not assignable to `list[Banana]`.
    Therefore, this method requires `Belt` to be invariant.

    This might be surprising, since you can imagine that the method probably constructs a new a list on the fly,
    since storing a `list[T]` as an attribute would make the class invariant.

    Here's one way you could violate type expectations if `Belt` could be covariant with `get_many_list`:
    ```py
    bananas: list[Banana] = [Banana(), Banana()]

    class BananaBelt(Belt[Banana]):
        def get_many_list(self) -> list[Banana]:
            return bananas

    banana_belt = BananaBelt()
    generic_belt: Belt[Banana] = banana_belt
    #^ allowed because of direct subclassing

    fruit_belt: Belt[Fruit] = generic_belt
    #^ this would be allowed because of covariance

    fruits: list[Fruit] = fruit_belt.get_many_list()
    fruits.append(Apple())
    # now `bananas` contains an `Apple()`
    ```

    /// details | Another example
        type: example

    Here's another example that doesn't involve subclassing `Belt`:

    ```py
    from collections.abc import Iterable, Callable

    class CallbackList[T](list[T]):
        def __init__(
            self,
            iterable: Iterable[T] = (),
            callback: Callable[[T], None] = lambda _: None,
        /) -> None:
            self._callback = callback
            super().__init__(iterable)

        def append(self, o: T, /) -> None:
            self._callback(o)
            super().append(o)

    class Belt[T]:
        def __init__(self, item: T) -> None:
            self._items = (item,) * 100

        def get_first(self) -> T:
            return self._items[0]

        def get_batch(self) -> list[T]:
            def callback(item: T) -> None:
                self._items = (item,) + self._items

            return CallbackList(self._items, callback)

    belt1: Belt[int] = Belt(42)

    belt2: Belt[object] = belt1
    #^ this would be allowed with covariance

    belt2.get_batch().append("a")

    first: int = belt1.get_first()
    #^ ...but first is actually a string!
    ```
    ///

??? tip "Rule of thumb"

    If following the algorithm outlined above feels too difficult, you can follow this simple rule of thumb when mentally evaluating
    a type parameter's variance:

    Start at the generic itself, and step-by-step evaluate the type surrounding it with these rules in mind:

    - By default, assume the generic is covariant
    - When used in a contravariant position, its variance is "swapped" to the other one
    - When used in a covariant position, its variance stays the same
    - When used in an invariant position, stop here.
      The generic is invariant!

    Let's look at some examples:

    ```py
    from collections.abc import Callable

    class A[T]:
        # T is used in a contravariant position - swap from covariant to contravariant
        # verdict: contravariant
        def fn(self, value: T): ...

    class B[T]:
        # 1. T is used in a contravariant position (`Callable[[T], None]`) - swap from covariant to contravariant
        # 2. `Callable[[T], None]` is used in a covariant position - don't swap
        # verdict: contravariant
        def fn(self) -> Callable[[T], None]: ...


    class C[T]:
        # 1. T is used in a contravariant position (`Callable[[T], None]`) - swap to to contravariant
        # 2. `Callable[[T], None]` is used in a contravariant position again - swap back to covariant
        # verdict: covariant
        def fn(self, fn: Callable[[T], None]): ...

    class D[T]:
        # 1. T is used in a contravariant position (`Callable[[T], None]`) - swap to contravariant
        # 2. `Callable[[T], None]` used in a contravariant position (`Callable[[Callable[[T], None]], None]`) - swap back to covariant
        # 3. `Callable[[Callable[[T], None]], None]` used in covariant position - don't swap
        # verdict: covariant
        def fn(self) -> Callable[[Callable[[T], None]], None]: ...

    class E[T]:
        # 1. T is used in a contravariant position (`Callable[[T], None]`) - swap to contravariant
        # 2. `Callable[[T], None]` used in a contravariant position (`Callable[[Callable[[T], None]], None]`) - swap back to covariant
        # 3. `Callable[[Callable[[T], None]], None]` used in contravariant position (`Callable[[Callable[[Callable[[T], None]], None]], None]`) - swap again to contravariant
        # 4. `Callable[[Callable[[Callable[[T], None]], None]], None]` used in covariant position - don't swap
        # verdict: contravariant
        def fn(self) -> Callable[[Callable[[Callable[[T], None]], None]], None]: ...
    ```

    Now let's see some invariant examples:

    ```py
    class F[T]:
        # 1. T is used in an invariant position - stop here
        # verdict: invariant
        def fn(self, value: list[T]): ...

    class G[T]:
        # 1. T is used in a contravariant position (`Callable[[T], None]`) - swap to contravariant
        # 2. `Callable[[T], None]` used in an invariant position (`list[Callable[[T], None]]`) - stop here!
        # verdict: invariant
        def fn(self) -> Callable[[Callable[[list[Callable[[T], None]]], None]], None]: ...
    ```

    Note that once we encounter an invariant position, we don't need to mentally parse the rest of the type, no matter how nested it gets.

    When multiple methods are involved, or if the generic is used in multiple places within the same signature, the result will be invariant
    unless the verdict is the same for each usage.
    Some more examples:

    ```py
    class H[T]:
        # usage 1: contravariant
        def fn(self) -> Callable[[T], None]: ...

        # usage 2: covariant
        def fn2(self) -> T: ...

        # both covariant and contravariant usages - final verdict: invariant

    class I[T]:
        # usage 1: contravariant
        def fn(self) -> Callable[[T], None]: ...

        # usage 2: contravariant
        def fn2(self, value: T) -> None: ...

        # only contravariant usages - final verdict: contravariant


    class J[T]:
        # usage 1: covariant
        # usage 2: contravariant
        def fn(self, value: Callable[[T], None]) -> Callable[[T], None]: ...

        # both covariant and contravariant usages - final verdict: invariant
    ```

---

**TODO: expand on how attributes impact variance, and the role of private attributes**


## Examples of inferring variance

**TODO**


## Debugging variance

**TODO** (show examples for pyright and mypy)


## The Dataclass Disaster

**TODO** (and make a less dramatic title)


## Generic classes before Python 3.12

**TODO**



[^generic-inst-slow]:
    The amount of extra time and the reason for it can be quite surprising.
    Turns out that both creating `Class[Param1, Param2]` _and_ instantiating
    it is slow:

    ```plaintext {title="Python 3.14.5 (IPython 9.14.0)"}
    In [2]: %timeit defaultdict()
    109 ns ± 0.374 ns per loop (mean ± std. dev. of 7 runs, 10,000,000 loops each)

    In [3]: %timeit defaultdict[set, set[int]]()
    653 ns ± 4.85 ns per loop (mean ± std. dev. of 7 runs, 1,000,000 loops each)

    In [4]: %timeit defaultdict[set, set[int]]
    224 ns ± 0.312 ns per loop (mean ± std. dev. of 7 runs, 1,000,000 loops each)

    In [5]: %timeit defaultdict["set", "set[int]"]
    87.8 ns ± 0.497 ns per loop (mean ± std. dev. of 7 runs, 10,000,000 loops each)

    In [6]: d = defaultdict[set, set[int]]

    In [7]: %timeit d()
    403 ns ± 4.06 ns per loop (mean ± std. dev. of 7 runs, 1,000,000 loops each)
    ```

    ```plaintext {title="Python 3.14.5 (IPython 9.14.0)"}
    In [1]: class Custom[T]: pass

    In [2]: %timeit Custom()
    65.9 ns ± 0.0822 ns per loop (mean ± std. dev. of 7 runs, 10,000,000 loops each)

    In [3]: %timeit Custom[int]()
    830 ns ± 2.59 ns per loop (mean ± std. dev. of 7 runs, 1,000,000 loops each)

    In [4]: %timeit Custom[int]
    620 ns ± 5.33 ns per loop (mean ± std. dev. of 7 runs, 1,000,000 loops each)

    In [5]: d = Custom[int]

    In [6]: %timeit d()
    202 ns ± 0.714 ns per loop (mean ± std. dev. of 7 runs, 10,000,000 loops each)
    ```

    One potential reason instantiating a parameterized class is slow is that it
    attaches (or attempts to attaches) some extra metadata to the object:
    ```plaintext
    In [18]: Custom[int]().__orig_class__
    Out[18]: __main__.Custom[int]
    ```

    Of course, this is Python, so there's a limit to how paranoid it makes sense
    to be about achieving optimal performance.
    But I think it's a good to be aware of how expensive common operations are.


[^attr-invariant]:
    This is not quite true.
    The full truth is something like this:

    1. For private attributes, `_attr: X` or `__attr: X` is evaluated as if it was a
        method with a `(self) -> X` signature.

    2. For public attributes, `attr: X` is evaluated as if it was a pair of methods
        (or a property) with the signatures `(self, arg: X) -> None` and
        `(self) -> X`.

    For most cases, this would work the same, but `Any` breaks these rules.
    Here's an example of an edge case where this is different:

    ```py
    from typing import Any

    class FooAttr[T]:
        def __init__(self) -> None:
            self.things: list[T | Any] = []

    class FooMethod[T]:
        def get_things(self) -> list[T | Any]: ...
        def set_things(self, arg: list[T | Any]): ...
    ```

    In both `FooAttr` and `FooMethod`, `list[Fruit | Any]` and `list[Banana | Any]` are
    assignable to each other, so the class is allowed to be both covariant and
    contravariant (as written, it is covariant, since it has no other items).