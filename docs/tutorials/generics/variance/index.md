# Variance

_Variance_ describes how subtyping works with generics.
Let's take a look at a few examples to set the stage.

## Example 1. Iterables

Suppose that we have this class hierarchy[^1]:

```py
class Animal:
    def __init__(self, name: str) -> None:
        self._name = name

    def name(self) -> str:
        return self._name


class Dog(Animal):
    def bark(self) -> None:
        print("Woof!")
```

And we have this function:
```py
from collections.abc import Iterable


def greet_animals(animals: Iterable[Animal]) -> None:
    for animal in animals:
        print("Hi, {0}!".format(animal.name()))
```

Should this call be allowed?

```py
dogs: Iterable[Dog] = [Dog("alice"), Dog("bob"), Dog("charlie")]
greet_animals(dogs)
```

The answer is yes! All we can do with an `Iterable` is iterate over it.
Every element of the iterable will be a `Dog`, which is a subtype of `Animal`. Our code
can't assume anything else about the elements, so it should work.

So as you can see, `Dog` is a subtype of `Animal`, therefore `Iterable[Dog]` is a subtype of `Iterable[Animal]`.
But that's not true for all generic types.


## Example 2. Lists

Let's take a slightly different function:
```py
def greet_animals(animals: list[Animal]) -> None:
    for animal in animals:
        print("Hi, {0}!".format(animal.name()))
```

Should this call be allowed?

```py
dogs: list[Dog] = [Dog("alice"), Dog("bob"), Dog("charlie")]
greet_animals(dogs)
```

If we run `pyright` on this code, this is what we see:

> Argument of type `"list[Dog]"` cannot be assigned to parameter `"animals"` of type `"list[Animal]"` in function `"greet_animals"`

How so? The call will work fine at runtime, so why not allow it?

Well, for all the type checker knows, `greet_animals` could do this:

```py
class Cat(Animal):
    def meow(self) -> None:
        print("Meow!")


def greet_animals(animals: list[Animal]) -> None:
    animals.append(Cat("dennis"))
    animals[0] = Animal("emily")

    for animal in animals:
        print("Hi, {0}!".format(animal.name()))
```

The contract of `list[Animal]` is that you can push any `Animal` to it.
`list[Dog]` doesn't satisfy this contract: there are `Animal`s you cannot push
into a `list[Dog]`, for example a `Cat` or a plain `Animal` object.

---

This call is also not allowed:

```py
def greet_dogs(dogs: list[Dog]) -> None:
    for dog in dogs:
        print("Hi, {0}!".format(dog.name()))
        dog.bark()

animals: list[Animal] = [Animal("alice"), Cat("bob"), Dog("charlie")]
greet_dogs(animals)
```

A `list[Animal]` can already contain animals that are not
`Dog`s, so the assumptions of the function (namely, the fact that you can call
`bark()` on each element in the list) will be violated.

---

In other words, `list[Dog]` is not a subtype of `list[Animal]`, and `list[Animal]`
is not a subtype of `list[Dog]` either.


## Example 3. Functions

Consider this function:

```py
from collections.abc import Callable

def create_animals(factory: Callable[[str], Animal]) -> tuple[Animal, Animal]:
    return factory("alice"), factory("bob")
```

Which of these functions would work as the `factory`?
```py
class BetterString(str):
    ...

    def to_awesome_case(self) -> str:
        import random
        return "".join(random.choice([char.lower(), char.upper()]) for char in self)


def make_animal(name: str) -> Animal: ...
def make_cat(name: str) -> Cat: ...
def make_cat_or_dog(name: str) -> Cat | Dog: ...
def make_cat2(name_or_id: str | int) -> Cat: ...
def make_cat3(whatever: object) -> Cat: ...
def make_animal2(name: BetterString) -> Animal: ...
def make_animal_of_plant(name: str) -> Animal | Plant: ...
```

- `def make_animal(name: str) -> Animal: ...`

    This function has exactly the type we need - `Callable[[str], Animal]`.
    So yes, it will work

- `def make_cat(name: str) -> Cat: ...`

    This function returns a `Cat` instead of just any animal. But that's fine:
    we need a function that returns an `Animal`, and whatever `make_cat` returns
    is an `Animal`.

    You can think of it in another way: you could make a trivial function that
    transforms this into `(name: str) -> Animal`:
    ```py
    def make_cat_wrapper(name: str) -> Animal:
        animal: Animal = make_cat(name)
        return animal
    ```

- `def make_cat_or_dog(name: str) -> Cat | Dog: ...`

    Same for this function: whatever it returns, it is an `Animal`.

- `def make_cat2(name_or_id: str | int) -> Cat: ...`

    This one is more tricky, but it will still fit: we need a function that
    _accepts_ a string as an argument, and this function satisfies this requirement.

    In other words, `make_cat2` accepts any _subtype_ of `str | int` as an
    argument, and `str` is a subtype of `str | int`.

- `def make_cat3(whatever: object) -> Cat: ...`

    This is also fine. `make_cat3` will work with any object at all, including
    a string.

- `def make_animal2(name: BetterString) -> Animal: ...`

    This one will not fit. We need our `factory` to accept any string,
    but `make_animal2` only accepts `BetterString` objects and can, for example,
    call the `to_awesome_case()` method on the name.

- `def make_animal_of_plant(name: str) -> Animal | Plant: ...`

    This will not work either. The function should always return an `Animal`.


As you can see, there are two rules for functions:

1. If `Child` is a subtype of `Parent`, then `Callable[[X], Child]` is a
    subtype of `Callable[[X], Parent]`
2. If `Child` is a subtype of `Parent`, then `Callable[[Parent], X]`
    is a subtype of `Callable[[Child], X]`


## Definition

Suppose that we have a generic type `F[T]`, and two ordinary types: `Child` and `Parent`, where `Child`
is a subtype of `Parent`.
The _variance_ of `F` describes how `F[Child]` is related to `F[Parent]`.

There are three kinds of _variance_:

1. **Covariance**: `F[Child]` is a subtype of `F[Parent]`

    - example: `tuple[Dog, ...]` is a subtype of `tuple[Animal, ...]`
    - example: `Callable[[str], Dog]` is a subtype of `Callable[[str], Animal]`

2. **Contravariance**: `F[Parent]` is a subtype of `F[Child]`

    - example: `Callable[[Animal], None]` is a subtype of `Callable[[Cat], None]`

3. **Invariance**: `F[Child]` is not related to `F[Parent]`

    - example: `list[Dog]` is not related to `list[Animal]`


When describing a type, replace the "ance" suffix with "ant". For example,
`list` is _invariant_, while `tuple` is _covariant_.


## More than one type variable


Some generic types take in more than one type variable. For example, `Callable` can take
any number of variables for parameters, and then another one for the result type.

In that case, a generic type can have different variance in different type variables.

For example:

- `Callable` is _contravariant in the parameter types_ but _covariant in the return type_
- `Mapping` is _invariant in the key type_ but _covariant in the return type_


[^1]: I know, I hate nonsense examples of inheritance as well. I hope that you forgive me.
