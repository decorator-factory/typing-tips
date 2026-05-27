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

4. Assignability and variance &mdash; a more theory-heavy chapter. Understanding what "A is assignable
    to B" means and all the concepts that lead up to it is crucial to solving type checking problems.
    Variance is introduced, but only explained on existing types like `list` and `Callable`, because
    generic classes are not introduced yet.

5. (Draft) Generic classes &mdash; defining your own generic classes; variance of your own classes.
    This one should also have a lot of examples, because variance is notoriously hard to teach IME.

6. (TODO) Generic protocols. Reinforcing distinction between class-level typevars and method-level
    typevars.

7. (TODO) Type aliases. Seemingly innocent topic, but Python has at least 3 ways of defining a
    type alias, and it's kinda complicated.

8. (TODO) Type checking in practice &mdash; debugging issues; configuring type checkers (_a_ type checker?);
    tradeoffs in type checking (e.g.: when to give up and use `# type: ignore`); type narrowing;
    tricks and bugs; unsoundness of Python's type system. Should include a list of things on
    `typing.python.org` you should read (e.g.: packaging type information).

9. (TODO) `typing.Self`

10. (TODO) Special items &mdash; miscellaneous stuff like `*TypeVarTuple`, `**ParamSpec`, `typing.overload`,
    type aliases (`type` statement), `typing.Final`,  `typing.final`; often needed to understand library stubs


Some ideas for one-off guides:

- Typing decorators. Need to do research on the method decorator situation.
- Inspecting type hints at runtime. I'll need to do a lot of research on this (there's a new stdlib module for this). Probably show examples of libraries that use it (like `msgspec`)
- `enum.Enum` vs `Literal`
- Transforming cowboy-style dynamic Python into military grade statically analyzed enerprise code.
    (trying to steal the vibes from [Transforming Code into Beautiful, Idiomatic Python](https://www.youtube.com/watch?v=OSGv2VnC0go) but it does end up sounding a bit depressing)
- `TypedDict`
- type guards
- things to avoid in statically typed Python code
