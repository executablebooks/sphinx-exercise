# sphinx-exercise

```{toctree}
:hidden:

install
syntax
```

[![Documentation Status](https://readthedocs.org/projects/sphinx-exercise/badge/?version=latest)](https://sphinx-exercise.readthedocs.io/en/latest/?badge=latest)

**An exercise extension for Sphinx**.

This package contains a [Sphinx](http://www.sphinx-doc.org/en/master/) extension
for producing exercise and solution directives.

```{warning}
sphinx-exercise `0.0.1` is in a development stage and may change rapidly.
```

**Features**:

1. directives are automatically numbered
2. supports directive options such as `class`, `label`, and `nonumber`
3. can easily be referenced through `ref` role

(getting-started)=
## Getting Started

To get started with `sphinx-exercise`, first install it through `pip`:

```bash
pip install sphinx-exercise
```

### JuputerBook Project

Add `sphinx.exercise` to your [extra_extensions](https://jupyterbook.org/advanced/sphinx.html#custom-sphinx-extensions) config in `_config.yml`

```yaml
sphinx:
  extra_extensions:
    - sphinx.exercise
```

you may then use `jb build <project>` and the extension will be used by your `JupyterBook` project.

### Sphinx Project

Add `sphinx.exercise` to your sphinx `extensions` in the `conf.py`

```python
...
extensions = ["sphinx.exercise"]
...
```

you may then build using `make html` and the extension will be used by your `Sphinx` project.
