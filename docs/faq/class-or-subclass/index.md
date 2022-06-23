# I want to specify "X or any subclass of X"

!!! question

    ```py
    class Animal:
        def speak(self) -> None:
            print("*generic animal noises*")

    def choose_speaker(speaker1: Animal, speaker2: Animal) -> None:
        if random.random() >= 0.5:
            speaker1.speak()
        else:
            speaker2.speak()
    ```

    How do I specify that `choose_speaker` accepts `Animal` or any subclass of `Animal`?

It already does!

If a function works with objects of class `A`, it also works with subclasses of `A`. (At least it should!) This is called "substitutatbility".

---

Now, in Python land, this is not the only view on inheritance. Inheritance is also a mechanism for code reuse, see
[this talk from Raymond Hettinger](https://www.youtube.com/watch?v=EiOglTERPEo) for an explanation.

What does it look like? Consider a function like this:
```py
def contains_foo(things: dict[str, int]) -> bool:
    try:
        things["foo"]
    except KeyError:
        return False
    else:
        return True
```
and then you might refactor it like this:
```py
def contains_foo(things: dict[str, int]) -> bool:
    return "foo" in things
```
This refactoring relies on some assumptions about how `dict`s work.

The first version will always return `True` for a `defaultdict`, but the second one
will not. `defaultdict` violates some implicit assumptions about dictionaries, which makes it harder
to know if a function that accepts a dictionary (or a `Mapping`) will work correctly
with a `defaultdict`.

Nevertheless, in the typing world, a child class is considered appropriate whenever a parent class is.

---

More on this topic:

- [StackOverflow: "What is an example of the Liskov Substitution Principle?"](https://stackoverflow.com/questions/56860/what-is-an-example-of-the-liskov-substitution-principle)
