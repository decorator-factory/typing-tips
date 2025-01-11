# Avoid `Any`

## TL;DR

Avoid using `Any`, because it turns off all type-checking and somewhat defeats the purpose of static typing.
Often you can use union types, `object` or generics instead. But don't get too hung up on this: Python is a dynamically
typed language, and its "type system" has limited expressive power, so sometimes `Any` is just what you need.

## What is `Any`?

`Any` is a special form that essentially marks a value as dynamically typed. You can do whatever you want with it, and
`mypy` won't bat an eye. For example:

```py
def do_something(mystery_object: Any) -> None
    mystery_object.quack()  # ok
    mystery_object += 1  # ok
    carefully_typed_value: int = mystery_object  # ok
    mystery_object(mystery_object)  # ok!
```

Values produced from an `Any` are also `Any`, in a "viral" way:

```py
def do_something(mystery_object: Any) -> None
    x = mystery_object.foo(answer=42)
    reveal_type(x)  # Any
```

## What's bad about `Any`?

`Any` turns off all type checks. That's basically why it's "bad".

1. If you make a typo, the type checker won't help you

2. You lose editor integration. This is not just a typing aid: features like "Go To Definition"
    or "Go To Reference" will no longer work. This will make refactoring harder.

3. If you "leak" an `Any` that you didn't check propely, you might end up with a "typed value that's not the right type at runtime.
    For example, you might accidentally pass a `None` where it's never expected.

4. (perhaps a subtle and controversial point) It encourages devlopers to "trust" dynamic values, skipping validation where
    it would be beneficial.

    For example, it's common in Python programs to make a request to some remote API, deserialize its
    response as JSON and do some things to it. If the remote service has a bug, or the programmer misunderstood the
    documentation, this could cause a bug that's hard to catch. Or worse, a security issue: see
    [CWE-20: Improper Input Validation](https://cwe.mitre.org/data/definitions/20.html).

5. Finally, `Any` is viral: if you do something to it, you get a new `Any`. If you're getting some things from a
    `settings: dict[str, Any]`, soon you'll be juggling a dozen of `Any`s.

## Why would you use `Any`?

Generally, people use `Any` if it's not possible to express something in the type system. Or, perhaps, expressing
something would require a big refactoring, which you don't have time to do, or which would make the code less readable.

Python's type system is not designed to find all bugs or to write mathematically correct programs.
Sometimes practicality beats purity, and a bit of slack is accepted in a trade-off between
safety and complexity.

For example, when talking to a statically typed database such as PostgreSQL, you might get back a `Record`. The interface
a `Record` presents is similar to a `dict[str, Any]`. Even though your query is `SELECT 42 AS foo`, it's unreasonable to expect
the type checker to know that the record has the shape of `{"foo": int}`. There are tools like
[Prisma](https://prisma-client-py.readthedocs.io/en/stable/) that help somewhat, but there's no universal solution.


## Tips

Here are some steps you can take to reduce the number of `Any`s in your code:

1. If you're using `mypy`, you can [generate a report](https://mypy.readthedocs.io/en/stable/command_line.html#report-generation)
    that measures how much of your code is untyped.

2. Learn about type variables and generics (TODO: link generics tutorial). Whenever you see a function or a class where two values
    are linked together and are marked as `Any`, see if you can use a `TypeVar`.

3. Search for external inputs, such as configuration or network requests, and decide if they need stricter validation.

4. Consider if you can use a [union type](https://docs.python.org/3/library/typing.html#typing.Union).

5. If you really want "any value", see if using `object` makes sense. See ["Is `object` the same as `Any`?"](../object-vs-any/index.md) for more details.


## More on this topic

- ["No, dynamic type systems are not inherently more open"](https://lexi-lambda.github.io/blog/2020/01/19/no-dynamic-type-systems-are-not-inherently-more-open/) by Alexis King
- ["typing.Any vs object?"](https://stackoverflow.com/q/39817081/10295729) on StackOverflow

