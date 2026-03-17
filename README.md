# Typing Tips

URL: https://decorator-factory.github.io/typing-tips/

This is a blob of writing about Python's optional type annotation system, including
a tutorial and some one-off articles.

The Python documentation has recently started adopting the [Diataxis](https://diataxis.fr/)
framework for understanding different documentation genres. Python's type annotation system
is quite deep and complex. The [typing documentation](https://typing.python.org/en/latest/)
site covers the "reference" quadrant well and has some "guide" articles. However,
there isn't a high quality and up to date resource for the "tutorial" quadrant. The purpose
of that would be to introduce the type system to someone who's familiar with Python, but
unfamiliar with static typing and type systems.

My hope for this is to eventually teach all the concepts necessary to understand how typing is
set up for any piece of Python code you find and annotate all of your own code.
You should be able to understand messages from mypy/pyright/ty without the help of a
colleague, even if they contains scary words like "invariant" or "overload".
With how much content is needed for this to work, this is turning from a tutorial series into
a mini-book.


## Plans for the tutorial

The tutorial series is missing a few key pieces to be a complete resource. The goal is not
to explain every single item from `typing`, but to teach concepts that don't come easily from
reading the manual.

This is the current plan for what I want to include:

0. Introduction &mdash; what type annotations are; (very briefly) why they're used;
    how to run a type checker on your code; a few basic constructs to give an idea of what
    you can express with type hints on a novice level; annotating functions. This chapter
    is very important and should be refined a lot, because it's the one most people will read
    and benefit from.
1. Working with classes &mdash; annotating attributes and methods for the most common cases;
    introduction to standard library protocols/ABCs like `Iterable` and `Sequence`; dataclasses.
2. Using protocols &mdash; a walkthrough of using protocols in a real micro-project; abstract
    base classes; a brief discussion of nominal and structural types.
3. Generic functions &mdash; functions with typevars; typevar bounds and constraints; reference
    to the `typeshed`; introduction of `Callable`.
    Lots and lots of examples because it's the first topic that might not click at first
    intuitively. Old-style syntax is explained as an afterthought because it's less
    and less likely to be relevant with time.
4. (Draft) Assignability and variance &mdash; a more theory-heavy chapter. Understanding what "A is assignable
    to B" means and all the concepts that lead up to it is crucial to solving type checking problems.
    Variance is introduced, but only explained on existing types like `list` and `Callable`, because
    generic classes are not introduced yet.
5. (TODO) Generic classes &mdash; defining your own generic classes; variance of your own classes.
    This one should also have a lot of examples, because variance is notoriously hard to teach IME.
6. (TODO) Type checking in practice &mdash; debugging issues; configuring type checkers (_a_ type checker?);
    tradeoffs in type checking (e.g.: when to give up and use `# type: ignore`); type narrowing;
    tricks and bugs; unsoundness of Python's type system. Should include a list of things on
    `typing.python.org` you should read (e.g.: packaging type information).
7. (TODO) Special items &mdash; miscellaneous stuff like `*TypeVarTuple`, `**ParamSpec`, `typing.overload`,
    type aliases (`type` statement), `typing.Final`,  `typing.final`; often needed to understand library stubs

The chapter(s) currently marked "(Draft)" should be alright but haven't received substantial feedback.
I'd appreciate help with that.

Some ideas for one-off guides:

- Typing decorators. Need to do research on the method decorator situation.
- Inspecting type hints at runtime. I'll need to do a lot of research on this (there's a new stdlib module for this). Probably show examples of libraries that use it (like `msgspec`)
- `enum.Enum` vs `Literal`
- Transforming cowboy-style dynamic Python into military grade statically analyzed enerprise code.
    (trying to steal the vibes from [Transforming Code into Beautiful, Idiomatic Python](https://www.youtube.com/watch?v=OSGv2VnC0go) but it does end up sounding a bit depressing)
- `TypedDict`
- type guards
- things to avoid in statically typed Python code


## Contribute

### Feedback

The main thing this project is lacking is feedback. What sort of documentation
or teaching materials are you missing for yourself or your team? Do the articles
in here actually work?

Feel free to open a pull request, issue or discussion on
[GitHub](https://github.com/decorator-factory/typing-tips), or message `decorator_factory` on Discord.

### How to run this locally?

1. Install Python 3.13+
2. Create a new virtual environment and activate it
3. In the virtual environment, run `python -m pip install -r requirements-lock.txt`
4. Run `python -X dev -m mkdocs serve`
5. Visit `http://127.0.0.1:8000/typing-tips/`

### AI policy

This project is an LLM-free zone. Everything in the repository is created by a human.
