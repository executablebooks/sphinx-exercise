# Developers

Development of this package follows the following conventions and styles.

Design notes and considerations can be found in [](developer-design.md)

## Install

To install the package in `develop` mode:

```shell
cd sphinx-exercise
pip install -e .
```

## Testing

For code tests, `sphinx-exercise` uses [pytest](https://docs.pytest.org/).

Run the tests with the following command:

```shell
>> cd sphinx-exercise
>> pip install -e .[testing]
>> pytest
```

To run the tests in multiple isolated environments, you can also run [tox](https://tox.readthedocs.io/)

```shell
>> cd sphinx-exercise
>> tox
```

To test the build of documentation run

```shell
>> cd sphinx-exercise
>> tox docs-update
```

or

```shell
>> cd sphinx-exercise/docs
>> make clean
>> make html
```

## Unit Testing

We use [pytest](https://docs.pytest.org/en/latest/) for testing, [pytest-regression](https://pytest-regressions.readthedocs.io/en/latest/) to regenerate expected outcomes of test and [pytest-cov](https://pytest-cov.readthedocs.io/en/latest/) for checking coverage.

To run tests with coverage and an html coverage report:

```bash
pytest -v --cov=sphinx_exercise --cov-report=html
```

## Writing Tests

The module `sphinx.testing` is used to run sphinx builds for tests, in a temporary directory.

If creating a new source folder for test files, folder name should start with `test-`.
Your folder should reside inside the `tests/books` directory, which has been set as the root directory for tests.

The tests should start with:

```python
@pytest.mark.sphinx('html', testroot="mybook")
```
In the above declaration, `html` builder is used. And `mybook` is the source folder which was created with the name `test-mybook` inside `tests/books` folder.

Sphinx Application API is available as a parameter to all the test functions:

```python
@pytest.mark.sphinx('html', testroot="mybook")
def mytest(app):
```
