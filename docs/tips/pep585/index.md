# Use new-style annotations

Before Python 3.9, you had to import stuff from `typing` for some annotations:

```py
from typing import List, Dict, Iterator, ContextManager

def foo(things: List[int]) -> ContextManager[Iterator[Dict[str, object]]]:
    ...
```

After [PEP 585](https://peps.python.org/pep-0585/) was implemented, already existing classes
from the standard library are now generic:

```py
from collections.abc import Iterator
from contextlib import AbstractContextManager

def foo(things: list[int]) -> AbstractContextManager[Iterator[dict[str, object]]]:
    ...
```

You should be using the new imports instead of the `typing` ones. It's more convenient to use
already available types, but more importantly, these exports from `typing` are deprecated,
and will be removed some day.

If you want to enforce this in your build pipeline, there's a flake8 plugin:
[flake8-pep585](https://github.com/decorator-factory/flake8-pep585).

The complete list of deprecated symbols can be found
[as text in PEP 585](https://peps.python.org/pep-0585/#implementation)
or
[as a Python dictionary on GitHub](https://github.com/decorator-factory/flake8-pep585/blob/0c359adc8c56647c2fa336e4217422a977f20fdc/flake8_pep585/rules.py#L7-L46).
