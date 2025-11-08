# Assignability and variance

!!! warning "This article is a draft"

Suppose that you have a function accepting an argument of type `OuterType`
and a variable referring to a value of type `InnerType`:

```py
def func(arg: OuterType) -> None:
    ...

var: InnerType = ...
```

If one is allowed to call `func(var)`, then we say that `InnerType` is
_assignable to_ `OuterType`.

What decides whether one type is assignable to another?
The best way to think about it is in terms of allowed operations.
If there's an operation on `OuterType` that would be illegal on
`InnerType`, then `InnerType` is not assignable to `OuterType`.

Here are some straightforward examples:

- `int` is assignable to `int` (they're the same type!)
- `bool` is assignable to `int` (`bool` is a subclass of `int`)
- `str` is assignable to `int | str`
- `str | bytes` is assignable to `int | str | bytes`
- `int | str` is **not** assignable to `str`
- if a class `Foo` implements a protocol `FooProto`,
    then `Foo` is assignable to `FooProto`
- if a class `Bar` also implements a protocol `BarProto`,
    then `Foo | Bar` is assignable to `FooProto | BarProto`
- `tuple[str, str]` is assignable to `tuple[str, ...]`
- `tuple[str, ...]` is assignable to `tuple[object, ...]`

These should be pretty obvious, but there are more complex cases
where "A is not assignable to B" errors can stump new type checking users.

## Where it's found

Assignability is involved whenever you have an object being provided to a receiver.
This includes:

- assignment into a variable (local or module-level), as the name suggests
- passing an argument into a function
- returning a value from a function
- yielding a value from a generator
- assigning a value to an attribute of an object

A lot of things in Python work sort of like assignment [^nedbat-names-values],
like bindings from `with` and `for` statements, so they are also
in the "assignment into a variable" category.


## Union with `None`

In general, type checkers are conservative: if they think that `InnerType`
could hold a value that doesn't fit `OuterType`, then `InnerType` is not
assignable to `OuterType`.
A common example you'll encounter is that `T | None` is not allowed where
only `T` is expected.

```py
def find_first_email(source: str) -> re.Match[str]:
    return re.search(r"+", source)
    # error: re.Match[str] | None is not assignable to re.Match[str]

def find_first_number(source: str) -> int:
    match = re.search(r"[0-9]+", source)
    return int(match[0])
    # error: cannot subscript `None`
```

Some statically typed languages are not like that: they allow an empty value,
typically called `nil` or `null`, to be passed when a reference is expected.
That will not work here.
If you're using Python with a type checker, you'll need to add an explicit check
before you use a "nullable" value as if it's present:

```py
# option 1: narrow the value with an `if`
def find_first_number(source: str) -> int:
    match = re.search(r"[0-9]+", source)
    if match is None:
        raise ValueError("No value find")
    reveal_type(match)  # shows: re.Match[str]
    return int(match[0])  # ok

# option 2: use `assert`
def find_first_number(source: str) -> int:
    match = re.search(r"[0-9]+", source)
    assert match is not None  # true because: *insert reasoning*
    reveal_type(match)  # shows: re.Match[str]
    return int(match[0])  # ok

# option 3: suppress the type checker
def find_first_number(source: str) -> int:
    match: re.Match[str] = re.search(r"[0-9]+", source)  # pyright: ignore[reportAssignmentType]
    # should never be None because: *insert reasoning*
    return int(match[0])  # ok
```

Handling sometimes-missing values can quickly get annoying when you _know_
something is present, but the type checker is clueless.
Unfortunately, we don't have convenient tools
(like Rust's `Option::unwrap` and `Option::expect`) for this.
You have to brute-force your way by using `assert` statements or just silencing your type checker.

Some people would say that using `None` extensively is a sign of poor software design.
You can often replace `None` with a different construct and make the code more friendly
to static analysis.

For example, rather than having several optional attributes where some of them
are always either present or missing together, you can split the class into several
cases:

```py
@dataclass
class Node
    is_folder: bool
    name: str
    created_at: datetime
    edited_at: datetime | None

    # *thoughtful comment explaining which combinations of attributes exist*
    # (one would hope...)

    mime_type: str | None
    size_bytes: int | None
    children: list[Node] | None
    error: str | None

# ->

@dataclass
class FileKind:
    mime_type: str
    size_bytes: int

@dataclass
class FolderKind:
    children: list[Node]

@dataclass
class BrokenKind:
    error: str

@dataclass
class Node
    name: str
    created_at: datetime
    edited_at: datetime | None
    kind: FileKind | FolderKind | BrokenKind
```

This removed the need for a comment to understand the design, making the code more self-documenting;
it also follows the philosophy of [making illegal states unrepresentable](
https://fsharpforfunandprofit.com/posts/designing-with-types-making-illegal-states-unrepresentable/).


If you have a class with two-step initialization, change it to one-step initialization:

```py
class Thingy:
    def __init__(self) -> None:
        self._connected = False
        self._connection: Connection | None = None
        self._address: Addr | None = None

    async def connect(self, addr: Addr) -> None:
        assert not self._connected
        self._connection = await aiosomething.connect(addr.as_str())
        self._address = addr

thingy = Thingy()
thingy._connection  # Connection | None
await thingy.connect(some_addr)
thingy._connection  # still Connection | None

# ->

class Thingy:
    def __init__(self, conn: Connection, addr: Addr) -> None:
        self._connection = conn
        self._address = addr

    @classmethod
    @contextlib.asynccontextmanager
    async def connect(cls, addr: Addr) -> AsyncGenerator[Thingy]:
        async with aiosomething.connect_ctx(addr.as_str()) as conn:
            yield Thingy(conn, addr)

async with Thingy.connect(some_addr) as thingy:
    thingy._connection  # always a Connection
```

You can also use the _Null Object_ or the more general _Special Case_ pattern[^null-object]
to replace `None` checks with polymorphism:

> Provide something for nothing: a class that conforms to the interface required of
> the object reference, implementing all of its methods to do nothing,
> or to return suitable default values.
> Use an instance of this class, a so-called 'null object,' when the object reference
> would otherwise have been null.

```py
class Route:
    def __init__(self, matcher: Matcher, handler: Handler | None = None) -> None:
        self._matcher = matcher
        self._handler = handler

    def invoke(self, request: Request) -> Response | None:
        if not self._matcher.matches(request):
            return None
        if self._handler is None:
            return Response(status=501)
        return self._handler.process(request)

# ->

class Route:
    def __init__(self, matcher: Matcher, handler: Handler | None = None) -> None:
        self._matcher = matcher
        self._handler: Handler = handler or NotImplementedHandler()

    def invoke(self, request: Request) -> Response | None:
        if not self._matcher.matches(request):
            return None
        return self._handler.process(request)
```

Again, that's a general design choice that should be evaluated regardless of type checking.
You shouldn't indiscriminately replace all your `X | None`s with dummy `X`s.
Sometimes the fact that an `X` is missing is important, so that would
obscure mistakes and make the code harder to read and write, not easier.

> `Null Object` should not, however, be used indiscriminately as a replacement for null references.
> If the absence of an object is significant to the code’s logic and results in
> fundamentally different behavior, using a `Null Object` is inappropriate.

Returning `None` from the `invoke` method is meaningful: we need to signal whether the
request was intended for our route or whether the caller should try other routes.

If you're using a type checker, it will help you ensure that you will not mistakenly
access a possibly `None` value as if it was present.


## Callables are backwards!

Suppose that ou're adding type annotations to an existing application that
powers a bot on a text messaging platform.

```py
class ChatBot:
    ...

    def add_event_handler(self, event_type, handler):
        ...

class Event: ...
class UserJoined(Event): ...
class UserLeft(Event): ...
class NewMessage(Event): ...

bot = ChatBot()

def on_new_message(event):
    if event.author_id == bot.user_id:
        return  # don't respond to our own

    if "apples" in event.text.casefold():
        bot.ban(event.author_id, reason="You are not allowed to talk about apples")

bot.add_event_handler(NewMessage, on_new_message)
```

How do you type the `add_event_handler` method?
Your first guess might be this:

```py
from collections.abc import Callable

class ChatBot:
    user_id: str = ""
    def ban(self, user_id: str, reason: str) -> None: ...

    def add_event_handler(self, event_type: type[Event], handler: Callable[[Event], None]) -> None:
        ...

class Event: ...
class UserJoined(Event): ...
class UserLeft(Event): ...
class NewMessage(Event): ...

bot = ChatBot()

def on_new_message(event: NewMessage) -> None:
    if event.author_id == bot.user_id:
        return  # don't respond to our own

    if "apples" in event.text.casefold():
        bot.ban(event.author_id, reason="You are not allowed to talk about apples")

bot.add_event_handler(NewMessage, on_new_message)
```

However, your type checker (`pyright` in this case) complains about the call to
`bot.add_event_handler`:

```
Argument of type "(event: NewMessage) -> None" cannot be assigned to parameter "handler" of type "(Event) -> None" in function "add_event_handler"
  Type "(event: NewMessage) -> None" is not assignable to type "(Event) -> None"
    Parameter 1: type "Event" is incompatible with type "NewMessage"
      "Event" is not assignable to "NewMessage"
```

This seems backwards...
Surely, a function accepting `NewMessage` as the first argument is a kind of
`Callable[[Event], None]`, since `NewMessage` is an `Event`?
Well, no, and it makes sense if you think in terms of allowed operations.

The main, and the only interesting, operation that a `handler: Callable[[Event], None]`
_must support_ is: being called with an argument of type `Event`.
It's legal (from a type checking perspective) to call `handler(Event())`
and `handler(UserJoined())`.
Our `on_new_message` imposes an extra requirement that the argument must be a `NewMessage`.

Here's a more synthetic demonstration:

```py
from collections.abc import Callable

class Animal: pass

class Cat(Animal):
    def meow(self): print("meow")

class Duck(Animal):
    def quack(self): print("quack")

def apply_callable(fn: Callable[[Animal], None]) -> None:
    fn(Cat())
    fn(Duck())

def handle_duck(duck: Duck) -> None:
    for _ in range(3): duck.quack()

apply_callable(handle_duck)  # this is not allowed
```

In other words, the signature of `ChatBot.add_event_handler` is saying: give me an event class,
and then a function that must be happy to work with arbitrary `Event`s.
This is clearly not what we want: we only need that the handler knows how to work with events
of the supplied class.
We can do this by making the method generic:
```py
class ChatBot:
    def add_event_handler[E: Event](self, event_type: type[E], handler: Callable[[E], None]) -> None:
        ...
```
Now, when you call `bot.add_event_handler(NewMessage, on_new_message)`, `E` is resolved as
`NewMessage`, and the type checker is happy: `NewMessage` is assignable to `event_type: type[NewMessage]`,
and `on_new_message` is assignable to `handler: Callable[[NewMessage], None]`.

And now for something completely different: what if the argument type is broader than expected?
```py
def generic_handler(event: Event) -> None:
    print("something happened:", event)

bot.add_event_handler(UserJoined, generic_handler)
bot.add_event_handler(UserLeft, generic_handler)
```
This is fine: `Callable[[Event], None]` is assignable to `Callable[[UserJoined], None]` because
it supports all the operations required by `Callable[[UserJoined], None]`.
It knows how to handle any `Event`, and that includes `UserJoined`.

So, as a general rule:

1. if `A` is assignable to `B`, then `Callable[[B], X]` is assignable to `Callable[[A], X]`,
    not (necessarily) the other way around.
    Parameters are "backwards" in this way, because they describe receiving something,
    not providing it.
2. if `A` is assignable to `B`, then `Callable[[X], A]` is assignable to `Callable[[X], B]`,
    as you would normally expect.

The technical way to describe this is that `Callable` is **contravariant** in its parameters and
**covariant** in the return type.

"Covariant" uses the Latin prefix "co" meaning "alongside something" or "close to something",
and "contravariant" uses the Latin prefix "contra", meaning "against something" or "opposite".
Both of these adjectives describe the **variance** of a generic type: how the assignability
of type arguments impacts the assignability of the whole type.

For another example, `tuple[T, ...]` is covariant in `T`, because e.g. `tuple[Dog, ...]` is
assignable to `tuple[Animal, ...]`, and `tuple[Animal, ...]` is assignable to `tuple[object, ...]`.

## `list`s don't vary either way

The following is a very common error people run into when adopting type checking:

```py
class Fruit: pass
class Apple(Fruit): pass
class Banana(Fruit): pass


def look_at_fruits(fruits: list[Fruit]) -> None:
    for fruit in fruits:
        print(f"What a beautiful fruit this is: {fruit}")

apples: list[Apple] = [Apple(), Apple(), Apple()]

look_at_fruits(apples)
#              ^^^^^^
# Argument of type "list[Apple]" cannot be assigned to parameter "fruits" of type "list[Fruit]" in function "look_at_fruits"
#  "list[Apple]" is not assignable to "list[Fruit]"
#    Type parameter "_T@list" is invariant, but "Apple" is not the same as "Fruit"
#    Consider switching from "list" to "Sequence" which is covariant
```

`list[Apple]` is not assignable to `list[Fruit]`?
What nonsense, you may say: the function is expecting fruits, and you're
giving it apples, surely that's allowed.
That's Polymorphism 101!

What you might be overlooking is that `list`s are mutable: a `list[Fruit]` allows
appending any `Fruit` to it, which would be bad for our list of apples:

```py
def look_at_fruits(fruits: list[Fruit]) -> None:
    for fruit in fruits:
        print(f"What a beautiful fruit this is: {fruit}")

    fruits.append(Banana())  # complimentary gift for such decent fruits

apples: list[Apple] = [Apple(), Apple(), Apple()]
look_at_fruits(apples)
```

Assigning `list[Apple]` to `list[Fruit]` would invalidate the type of `apples`,
because there is now something that's not an `Apple` among them.
In other words, if we once again consider the allowed operations on types:
`x: list[Fruit]` allows `x.append(Fruit())` or `x.append(Banana())`, while
`x: list[Apple]` does not, so `list[Apple]` is not assignable to `list[Fruit]`.

Obviously, `list[Fruit]` is not assignable to `list[Apple]` either.
So `list` is very inflexible: if you want to assign `list[X]` to `list[Y]`,
you gotta make sure that `X = Y`[^any-assignability].
We say that `list` is **invariant** ("in" is a prefix meaning "not", as in "intolerant"),
because it doesn't have an "assignable to" relation in either direction.

Is there a structured way of knowing which types are _covariant_, _contravariant_ and _invariant_?
Yes, it will be discussed in a later chapter, after we cover making our own generic classes.
But, for a back of the napkin draft of the full truth, consider this rule:

!!! note "Napkin Rule"

    1. If a type `SomeType[T]` has any methods where `T` is in the output position
        (like `def method(self) -> T`), then it is **not** _contravariant_ in `T`
        (i.e.: `SomeType[Fruit]` is not assignable to `SomeType[Apple]`)
    2. If a type `SomeType[T]` has any methods where `T` is in the input position
        (`def method(self, arg: T) -> None`), then it is **not** _covariant_ in `T`
        (i.e.: `SomeType[Apple]` is not assignable to `SomeType[Fruit]`)

    If none of the bullet points apply, the type is a mystery (both `mypy` and `pyright`
    consider it _covariant_).

    If both of the bullet points apply, the type is _invariant_.

    T being "in the output position" and "in the input position" is quite misleading.
    For example, if `SomeType[T]`'s only method is `def method(self) -> Callable[[T], None]`,
    then `SomeType` is contravariant; if the method is `def method(self, fn: Callable[[T], None])`,
    then it is covariant; and if the method is `def method(self) -> list[T]` then it is invariant.
    The margins of this napkin are too narrow, so stay tuned for the next chapter.


## Using _covariant_ collection types

Since accepting `list[Apple]` in place of `list[Fruit]` is only problematic because of mutation,
we can express that we'll only be using the argument in a read-only way.
For that, we can use abstract base classes found in the `collections.abc` module:

```py
from collections.abc import Sequence

class Fruit: pass
class Apple(Fruit): pass
class Banana(Fruit): pass

def look_at_fruits(fruits: Sequence[Fruit]) -> None:
    for fruit in fruits:
        print(f"What a beautiful fruit this is: {fruit}")

    # cannot add `Banana()` to `fruits`, because `Sequence[Fruit]` doesn't have
    # any mutating methods

apples: list[Apple] = [Apple(), Apple(), Apple()]

look_at_fruits(apples)
```

`Sequence`, `Collection`, `Iterable`, and `Iterator`  are all _covariant_.
It means that `Sequence[Apple]` is assignable to `Sequence[Fruit]`, and
`Iterable[Banana]` is assignable to `Iterable[Fruit]`; while `Sequence[Fruit]`
is not assignable to `Sequence[Apple]`.

Here's how the assignability chain works:

1. `list[Apple]` is assignable to `Sequence[Apple]` because `list` is a subclass of `Sequence`[^list-subclass-sequence]
1. `Sequence[Apple]` is assignable to `Sequence[Fruit]`

You can find the type definition of `Sequence` in the
[typeshed source code](https://github.com/python/typeshed/blob/1d548aa88911297f676017f4cc82a120916cae8e/stdlib/typing.pyi#L652-L664).

You can also check out the [`collections.abc` documentation](https://docs.python.org/3/library/collections.abc.html).
For type parameters and their variance, you will need to see the documentation for
[typing.Sequence](https://docs.python.org/3/library/typing.html#typing.Sequence)
(which is deprecated, don't use it!), and for the meaning of `Sequence`'s methods
(like `__getitem__` and `__len__`), you will need to see the [data model](https://docs.python.org/3/reference/datamodel.html)
page.


## `Any` goes both ways {any-goes-both-ways}

`Any` is assignable to every type, and every type is assignable to `Any`.
For example:

- `str` is assignable to `Any`, and `Any` is assignable to `str`
- `tuple[int, str]` is assignable to `tuple[Any, Any]`
- `tuple[int, Any, bool]` is assignable to `tuple[int, str, Any]`
- `list[Any]` is assignable to `list[int]`, and `list[int]` is assignable to `list[Any]`

This does not hold for `object`: `list[int]` is not assignable to `list[object]`
for the reasons described earlier (`list[object]` allows appending any object to it).

This highlights the purpose of `Any`: `Any` does not simply mean "every object will work";
instead, it means "some type that I, the function (or class) author cannot or do not
want to express; it's up to the user to make sure the types connect".
For example, this is the signature of the built-in `setattr` function:
```py
def setattr(obj: object, name: str, value: Any, /) -> None: ...
```
Why is `obj` annotated as `object`, but `value` as `Any`?
After all, it makes no difference to the caller.

The `obj` parameter really can take on every possible object, that's why it's
annotated with `object`.
However, the set of objects that `value` is allowed to take on cannot be expressed as a
type hint.
It's not literally every object: you are not allowed to do e.g. `setattr(point, "x", "banana")`
if `point.x` is an integer attribute; so the allowed set of `value`s depends on the runtime values of `obj` and `name`.

Theoretically, you _could_ describe this function better if type hints were more powerful.
In TypeScript, you can type Python's `setattr`!
```typescript
function setAttr<S extends string, T>(obj: Record<S, T>, name: S, value: T) {
    obj[name] = value;
}

const point = { x: 42, y: 57 };

setAttr(point, "x", 69);  // ok

setAttr(point, "y", "banana"); // error
// Argument of type 'string' is not assignable to parameter of type 'number'.

setAttr(point, "z", 420);  // error
// Argument of type '{ x: number; y: number; }' is not assignable to parameter of type 'Record<"z", number>'.
//   Property 'z' is missing in type '{ x: number; y: number; }' but required in type 'Record<"z", number>'.
```


<!-- Footnotes -->
[^nedbat-names-values]: [Facts and myths about Python names and values](https://nedbatchelder.com/text/names.html)
[^any-assignability]: There's an exception for `Any`, which is discussed [later in the chapter!](#any-goes-both-ways)
[^list-subclass-sequence]: At runtime, `list.mro()` is just `[list, object]`, so `list` doesn't have real
    base classes besides `object`.
    However, `ABC`s like `Sequence` support "virtual subclassing" by registering a class
    with the ABC.
    That way, `isinstance([1, 2, 3], collections.abc.Sequence)` is actually true.
    Registering classes with `ABC`s is not supported by type checkers, so the typeshed
    stubs just pretend that e.g. `list[T]` actually inherits from `Sequence[T]`
[^null-object]: See "Null Object" in "Pattern-Oriented Software Architecture, volume 4";
    also see [Special Case](https://martinfowler.com/eaaCatalog/specialCase.html) from Martin Fowler's
    "Patterns of Enterprise Architecture" and the [Nothing is Something](https://www.youtube.com/watch?v=OMPfEXIlTVE)
    talk by Sandi Metz.


