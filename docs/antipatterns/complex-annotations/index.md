# Complex annotations


## Summary

!!! abstract "Smell"

    A deeply nested type annotation, especially involving collections

!!! bug "Why is it bad?"

    - Complex expressions are hard to read and understand
    - If you're passing complicated things between your functions, you might have decomposed
      the solution badly
    - If the annotation is complicated, the thing it _represents_ is also pretty complicated
    - There's a good chance that you've missed some important invariant in the annotation.
      Make it more precise, and it will become simpler.

!!! success "Solution"

    - Extract a type alias
    - Create proper classes for your data
    - Decompose the solution differently


## Example

Suppose that you're working with an external service that returns you a list of movies, as a JSON:
```py
{
    "movies": [
            {
                "name": "Dependency Injection in Brainfuck",
                "director": "Alice Alpha",
                "year": 2014,
                "genres": [
                    "comedy",
                    "horror",
                ],
            },
            {
                "name": "The Legacy of the Ancients (the previous team)",
                "director": "Bob Beta",
                "year": 2002,
                "genre": "adventure",
            },
            # ...
    ]
}
```

You wrote a function that calls the external service and returns the data from it.

```py
def fetch_movies() -> dict[str, list[dict[str, Union[str, int, list[str]]]]]:
    resp = requests.get("https://movies.example.com/v2/movies")
    return resp.json()
```

The return type annotation is really complex. I would probably spend a minute reading it, and a few more
minutes understanding what the function actually returns.

## Improvements

Let's extract a type alias - the type of a single movie.

```py
Movie = dict[str, Union[str, int, list[str]]]

def fetch_movies() -> dict[str, list[Movie]]:
    resp = requests.get("https://movies.example.com/v2/movies")
    return resp.json()
```

This is better. But the underlying problem is still there: this function returns some
complex structure, and it's not very clear how to work with it.

We could use `TypedDict`s to make the keys more precise:
```py
from typing import TypedDict


class _MovieOptional(TypedDict, total=False):
    # exactly one of:
    genre: str
    genres: list[str]


class Movie(_Movie):
    name: str
    director: str
    year: int


class MoviesResponse(TypedDict):
    movies: list[Movie]


def fetch_movies() -> MoviesResponse:
    resp = requests.get("https://movies.example.com/v2/movies")
    return resp.json()
```

This is also better. Now it's clear what kind of structure we're dealing with.
However, there's still something wrong.

- It doesn't capture the possible states correctly
- It's not convenient to work with: namely, the genres of a movie are represented either as a string
  or as a list of strings. External APIs sometimes return inconvenient data (because of backwards compatibility,
  or just because they're weirdos). But we don't want to force our callers to deal with this accidental
  complexity.
- More importantly, this annotation **is a lie**! You don't really know what the API returns. You could've read the
  API documentation incorrectly, or the documentation diverges from the actual response. We never validate
  our assumptions about the external service.


## Solution

Validate the response you're getting. You can use an existing validation library such as `pydantic`,
`marshmallow` or `dataclass_factory`.


```py
from collections.abc import Collection
from dataclasses import dataclass
from typing import Optional

import dataclass_factory


@dataclass(frozen=True)
class Movie:
    name: str
    director: str
    year: int
    genres: Collection[str]


def parse_raw_movies_response(raw: object) -> list[Movie]:
    factory = dataclass_factory.Factory()
    raw_movies = factory.load(raw, _RawMovies)
    return list(map(_parse_raw_movie, raw_movies.movies))


###


@dataclass
class _RawMovie:
    name: str
    director: str
    year: int
    genres: Optional[list[str]] = None
    genre: Optional[str] = None


@dataclass
class _RawMovies:
    movies: list[_RawMovies]


def _parse_raw_movie(raw: _RawMovie) -> Movie:
    if raw.genres is None:
        if raw.genre is None:
            raise ValueError
        genres = [raw.genre]
    else:
        if raw.genre is not None:
            raise ValueError
        genres = raw.genres

    return Movie(raw.name, raw.director, raw.year, genres)
```
