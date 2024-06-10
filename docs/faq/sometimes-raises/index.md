# What if my function can raise an exception?

!!! question

    ```py
    def fetch_user(user_id: str) -> User:
        user = database.fetch_user(id=user_id)
        if user is None:
            raise LookupError(user_id)
        return user
    ```

    This function either returns a user or raises an exception. How to annotate it correctly?


## Exception means `NoReturn`, right?

```py
from typing import NoReturn


def fetch_user(user_id: str) -> User | NoReturn:
    user = database.fetch_user(id=user_id)
    if user is None:
        raise LookupError(user_id)
    return user
```
This doesn't break any rules per se, but this means exactly the same as just returning a `User`:
```py
def fetch_user(user_id: str) -> User:
```


## What about `Union` with the exception type?
```py
def fetch_user(user_id: str) -> User | LookupError:
    user = database.users.where(id=user_id, deleted=False)
    if user is None:
        raise LookupError(user_id)
    return user
```
This annotation means that the function can _return_ a `LookupError` object, not raise it. This is not
right, and it doesn't force the caller to handle the exception with a `try-except` block.
```py
user = fetch_user("u:cba43b8f:42")
# user: User | LookupError
```


## How to specify that I'm raising an exception, then?

There isn't a way to mark that a function raises something in Python's type system.
In Python, pretty much anything can raise a variety of exceptions.

If raising an exception is part of the function's contract, note it in the docstring:
```py
def fetch_user(user_id: str) -> User:
    """
    Raises:
        LookupError: If the user is not found
    """
    user = database.users.where(id=user_id, deleted=False)
    if user is None:
        raise LookupError(user_id)
    return user
```

If you want a more type-safe way to handle errors, consider returning an error value.
The simplest example is `None`: if you return a value that can be `None`, the type checker
will force the caller to handle the error case.

If you want something more sophisticated than `None`, perhaps take a look at
the [`returns`](https://returns.readthedocs.io/en/latest/pages/result.html) library.
