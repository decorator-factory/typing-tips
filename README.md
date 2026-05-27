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

See [TODO.md](./TODO.md).


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
