# Variance for your own classes

In this tutorial, I will explain how to customize variance for your own types.

## Invariance: `Box`

Let's take a look at a generic class we made earlier:

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
```

By default, a type variable is _invariant_. In other words, `Box[Child]` is not a subtype or
supertype of `Box[Parent]`. Is this the right thing for our `Box`?

A `Box` is very close to a 1-element list, so the reasoning is very similar to `list`. Consider
this function:

```py
class Parent:
    pass

class ChildA(Parent):
    pass

class ChildB(Parent):
    pass

def do_something(box: Box[Parent]) -> None:
    box.put(ChildA())
```

This is a reasonable function to make. So if we were to call `do_something` with a `Box[ChildB]`,
we would have gotten a very unpleasant surprise. So `Box` can't be _covariant_.

Similarly, `Box` can't be contravariant either:
```py
def something_else(box: Box[ChildA]) -> None:
    assert isinstance(box.get(), ChildA)


parent_box = Box(Parent())
something_else(parent_box)  # Error
```

So our `Box` class should stay covariant.


## How to make the `Box` covariant?

Let's take a look at a different version of the `Box` class:

```py
from typing import Generic, TypeVar

T = TypeVar("T")

class Box(Generic[T]):
    def __init__(self, value: T) -> None:
        self._value = value

    def get(self) -> T:
        return self._value

    def display(self) -> None:
        print(self._value)
```

Now that we can't `set` a value, we can make `Box` covariant. To do this, we need to set the
`covariant` flag to `True` on our type variable.

```py
from typing import Generic, TypeVar

T = TypeVar("T", covariant=True)

class Box(Generic[T]):
    def __init__(self, value: T) -> None:
        self._value = value

    def get(self) -> T:
        return self._value

    def display(self) -> None:
        print(self._value)
```

Let's see if it works.

```py
class Parent:
    pass

class Child(Parent):
    pass

child_box: Box[Child] = Box(Child())
parent_box: Box[Parent] = child_box
```

No errors, so it looks like we've succeeded.


## Contravariance example

Making a class contravariant is similar to making it covariant: you switch a flag on a type variable.

```py
from typing import Generic, TypeVar

T = TypeVar("T", contravariant=True)

class EventSink(Generic[T]):
    def __init__(
        self,
        queue: SomeMessageQueue,
        to_json: Callable[[T], object],
    ) -> None:
        self._queue = queue
        self._to_json = to_json

    def push(self, event: T) -> None:
        json_event = self._to_json(event)
        self._queue.publish({
            "error": False,
            "data": json_event,
        })

    def push_error(self, code: str, message: str) -> None:
        self._queue.publish({
            "error": True,
            "code": code,
            "message": message,
        })
```

## Two type variables

You can mix and match different variances for different type variables. For example:

```py
from typing import Generic, TypeVar

In = TypeVar("In", contravariant=True)
Out = TypeVar("Out", covariant=True)

class EventSink(Generic[In, Out]):
    def __init__(
        self,
        queue: SomeMessageQueue,
        in_to_json: Callable[[In], object],
        json_to_out: Callable[[object], Out],
    ) -> None:
        self._queue = queue
        self._in_to_json = in_to_json
        self._json_to_out = json_to_out

    def push(self, event: In) -> Out:
        json_event = self._in_to_json(event)
        json_resp = self._queue.publish({
            "error": False,
            "data": json_event,
        })
        return self._json_to_out(json_resp)

    def push_error(self, code: str, message: str) -> None:
        self._queue.publish({
            "error": True,
            "code": code,
            "message": message,
        })
```


## Do I need to do this reasoning every time I make a generic class?

Thankfully, no!

The type checker will report an error if you mistakenly make a class co/contravariant.

```py
from typing import Generic, TypeVar

T = TypeVar("T", covariant=True)

class Box(Generic[T]):
    def __init__(self, value: T) -> None:
        self._value = value

    def get(self) -> T:
        return self._value

    def put(self, new_value: T) -> None:
        #                   ^^^
        # Covariant type variable cannot be used in parameter
        self._value = new_value
```
