# sphinx-exercise

[![Documentation Status][rtd-badge]][rtd-link]
[![Github-CI][github-ci]][github-link]
[![Coverage Status][codecov-badge]][codecov-link]

**An exercise extension for Sphinx**.

This package contains a [Sphinx](http://www.sphinx-doc.org/en/master/) extension
for producing exercise and solution directives.

## Features

- **Automatic numbering** for exercises and solutions
- **Cross-referencing** support with `ref` and `numref` roles
- **Internationalization** support for 27 languages including Chinese, Japanese, Korean, Arabic, Hindi, and more
- **HTML and PDF** output support
- **Gated directive** syntax for including executable code and complex content
- **Customizable styling** with class options and hidden directive support

## Get started

To get started with `sphinx-exercise`, first install it through `pip`:

```
pip install sphinx-exercise
```

then, add `sphinx_exercise` to your sphinx `extensions` in the `conf.py`

```python
...
extensions = ["sphinx_exercise"]
...
```


## Documentation

See the [Sphinx Exercise documentation](https://ebp-sphinx-exercise.readthedocs.io/en/latest/) for more information.


## Contributing

We welcome all contributions! See the [EBP Contributing Guide](https://executablebooks.org/en/latest/contributing.html) for general details, and below for guidance specific to sphinx-exercise.


[rtd-badge]: https://readthedocs.org/projects/ebp-sphinx-exercise/badge/?version=latest
[rtd-link]: https://ebp-sphinx-exercise.readthedocs.io/en/latest/?badge=latest
[github-ci]: https://github.com/executablebooks/sphinx-exercise/workflows/continuous-integration/badge.svg?branch=master
[github-link]: https://github.com/executablebooks/sphinx-exercise
[codecov-badge]: https://codecov.io/gh/executablebooks/sphinx-exercise/branch/master/graph/badge.svg
[codecov-link]: https://codecov.io/gh/executablebooks/sphinx-exercise
