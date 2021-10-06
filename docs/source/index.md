# sphinx-exercise

```{toctree}
:hidden:

install
syntax
testing
```


[![Documentation Status][rtd-badge]][rtd-link]
[![Github-CI][github-ci]][github-link]
[![Coverage Status][codecov-badge]][codecov-link]

**An exercise extension for Sphinx**.

This package contains a [Sphinx](http://www.sphinx-doc.org/en/master/) extension
for producing exercise and solution directives, for html and pdf outputs.

**Features**:

The **exercise** directive is

1. automatically numbered
2. supports options such as `class`, `label`, `nonumber`, and `hidden`
3. can easily be referenced through `ref` and `numref` roles

The **solution** directive

1. supports options such as `class`, `label`, and `hidden`
2. can be referenced through `ref` role

(getting-started)=
## Getting Started

To get started with `sphinx-exercise`, first install it through `pip`:

```bash
pip install -e.
```

### Jupyter-Book Project

Add `sphinx_exercise` to your [extra_extensions](https://jupyterbook.org/advanced/sphinx.html#custom-sphinx-extensions) config in `_config.yml`

```yaml
sphinx:
  extra_extensions:
    - sphinx_exercise
```

you may then use `jb build <project>` and the extension will be used by your `JupyterBook` project.

### Sphinx Project

Add `sphinx_exercise` to your sphinx `extensions` in the `conf.py`

```python
...
extensions = ["sphinx_exercise"]
...
```

you may then build using `make html` and the extension will be used by your `Sphinx` project.



[rtd-badge]: https://readthedocs.org/projects/ebp-sphinx-exercise/badge/?version=latest
[rtd-link]: https://ebp-sphinx-exercise.readthedocs.io/en/latest/?badge=latest
[github-ci]: https://github.com/executablebooks/sphinx-exercise/workflows/continuous-integration/badge.svg?branch=master
[github-link]: https://github.com/executablebooks/sphinx-exercise
[codecov-badge]: https://codecov.io/gh/executablebooks/sphinx-exercise/branch/master/graph/badge.svg
[codecov-link]: https://codecov.io/gh/executablebooks/sphinx-exercise
