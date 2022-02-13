# Intro

This tutorial series introduces two important, closely related concepts:

- Type variables (`TypeVar`s)
- Generic classes

_Type variables_ let you "link" two types together. For example, they let you express a function that filters a list
of elements, while preserving the element type:

```py
evens = filter_list(lambda x: x % 2 == 0, [1, 2, 3, 4, 5, 6])
# evens: Iterable[int]

numeric = filter_list(str.isdigit, ["abc", "123", "", "abc3.14"])
# numeric: Iterable[str]

```

_Generic classes_ are classes that can be parametrized with other types. There's a good chance you've worked
with generic classes from the standard library, such as `list` and `dict`.
