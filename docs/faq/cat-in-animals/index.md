# Why can I put a cat in a list of animals?

!!! question

    If `list`s are [invariant](../../tutorials/generics/variance/index.md#example-2-lists),
    how come it's legal to `append` a `Cat` to a `list[Animal]`?

    ```py
    class Animal:
        def speak(self) -> None:
            print("*generic animal noises*")

    class Cat(Animal):
        def speak(self) -> None:
            super().speak()
            print("also: meow")

    animals: list[Animal] = [Animal(), Animal()]
    animals.append(Cat())
    ```

    Doesn't this require `list` to be covariant?

A `list` being invariant only means that you can't put _a list of cats_ into a variable which stores
_a list of animals_ (or vice versa).

It's still legal to put _a cat_ into a variable which stores _an animal_:
```py
cat: Cat = Cat()
animal: Animal = cat
```
and this is roughly what happens when you call `animals.append(Cat())`: `animals.append` expects
_an animal_, and _a cat_ is a perfectly fine animal:
```py
cat: Cat = Cat()
animal: Animal = cat

animals.append(animal)
```

## Does this break anything?

`list` is invariant because if it weren't, bad things could happen:

```py
def add_pets(animals: list[Animal]) -> None:
    animals.append(Dog())
    animals.append(Dragon())

cats: list[Cat] = []
animals: list[Animal] = cats  # this is illegal!
add_pets(animals)  # ...because this would make the cats very uncomfortable
```

But if you put a `Cat` into a list of `Animals`, everything will be fine. You can only extract
an `Animal` from the list, and a `Cat` will work whenever an `Animal` works (at least it [should](https://en.wikipedia.org/wiki/Liskov_substitution_principle)).
