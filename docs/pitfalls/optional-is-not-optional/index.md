# `Optional` doesn't mean an optional argument

`Optional` doesn't represent an optional argument to a function. It means "either `<something>` or `None`".
For example, `Optional[int]` means `Union[int, None]`, exactly.

In fact, if you try to print out `Union[int, None]`, you will see `Optional[int]`!

```python-repl
>>> from typing import Union, Optional
>>>
>>> Optional[int]
typing.Optional[int]
>>> Union[int, None]
typing.Optional[int]
>>> Union[int, None] == Optional[int]
True
>>>
```

## Examples

### A function argument that is not mandatory

```py
def set_team_score(team: Team, score: int = 0) -> None:
    database.execute("UPDATE teams SET score = ? WHERE team_uid = ?", (score, team.uid))
```

This is the right way to annotate this function. The `score` argument is not mandatory, but if it is
provided, it must be an `int` &mdash; it cannot be `None`.

So the `score` _argument_ is optional, but the _type of the argument_ isn't `Optional[int]`.

### A function argument that is not mandatory: incorrect version

```py
def set_team_score(team: Team, score: Optional[int] = 0) -> None:
    database.execute("UPDATE teams SET score = ? WHERE team_uid = ?", (score, team.uid))
```

This type means that it's legal to call `set_team_score(some_team, score=None)`, which we probably didn't mean.

### A function argument that is not mandatory and can be `None`

```py
def create_classroom(name: str, mentor: Optional[Mentor] = None) -> None:
    mentor_uid = None if mentor is None else mentor.uid
    client.create_classroom({"name": name, "mentor_uid": mentor_uid})
```

The function can be called in three ways:

- `create_classroom("foo", mentor)` where `mentor` is a `Mentor` object
- `create_classroom("foo")`, in which case `mentor` will be `None`
- `create_classroom("foo", None)`, which is the same as the second call

### A function argument that is not mandatory and can be `None`: incorrect version

```py
def create_classroom(name: str, mentor: Optional[Mentor]) -> None:
    ...
```

In this case, the second argument is **mandatory**, so you can only call it with two arguments:

- `create_classroom("foo", mentor)`, where `mentor` is a `Mentor` object
- `create_classroom("foo", None)`

In general, type annotations don't change how the function works. But the terminology is a bit confusing here:
"optional" already has some meaning for function arguments.

### A function argument that is not mandatory and can be `None`: don't do this

```py
def create_classroom(name: str, mentor: Optional[Union[Mentor, None]] = None) -> None:
    ...
```

`Optional[Mentor]` already means "a `Mentor` object or `None`". There's no need to say it twice.
