# Syntax Guide

```{warning}
This extension currently works best when paired with the following themes:

1. [sphinx_book_theme](https://github.com/executablebooks/sphinx-book-theme)
2. [quantecon_book_theme](https://github.com/quantecon/quantecon-book-theme)

When using other themes (such as `alabaster`) the icons for the `exercise` and `solution` admonitions are missing on the top left.
We would like to make this more theme agnostic and status can be found in [this issue](https://github.com/executablebooks/sphinx-exercise/issues/51)
```

`````{note}
To use this extension in a Jupyter Book project, add `sphinx_exercise` as an extension in the `_config.yml` file.

```{code-block} python
sphinx:
    extra_extensions:
        - sphinx_exercise
`````

```{note}
This documentation utilized the [Markedly Structured Text (MyST)](https://myst-parser.readthedocs.io/en/latest/index.html) syntax.
```

## Exercise Directive

An exercise directive can be included using the `exercise` pattern. The directive is enumerated by default and can take in an optional title argument. The following options are also supported:

* `label` : text

    A unique identifier for your exercise that you can use to reference it with `{ref}` and `{numref}`. Cannot contain spaces or special characters.
* `class` : text

    Value of the exercise’s class attribute which can be used to add custom CSS or JavaScript.
* `nonumber` : flag (empty)

    Turns off exercise auto numbering.
* `hidden` : flag (empty)

    Removes the directive from the final output.

**Example**

```{exercise}
:label: my-exercise

Recall that $n!$ is read as "$n$ factorial" and defined as
$n! = n \times (n - 1) \times \cdots \times 2 \times 1$.

There are functions to compute this in various modules, but let's
write our own version as an exercise.

In particular, write a function `factorial` such that `factorial(n)` returns $n!$
for any positive integer $n$.
```

**MyST Syntax**

``````md
```{exercise}
:label: my-exercise

Recall that $n!$ is read as "$n$ factorial" and defined as
$n! = n \times (n - 1) \times \cdots \times 2 \times 1$.

There are functions to compute this in various modules, but let's
write our own version as an exercise.

In particular, write a function `factorial` such that `factorial(n)` returns $n!$
for any positive integer $n$.
```
``````

_Source:_ [QuantEcon](https://python-programming.quantecon.org/functions.html#Exercise-1)

### Referencing Exercises

You can refer to an exercise using the `{ref}` role like ```{ref}`my-exercise` ```, which will display the title of the exercise directive. In the event that directive does not have a title, the title will be the default "Exercise" or "Exercise {number}" like so: {ref}`my-exercise`.

Enumerable directives can also be referenced through the `numref` role like ```{numref}`my-exercise` ```, which will display the number of the exercise directive. Referencing the above directive will display {numref}`my-exercise`. In this case it displays the same result as the `{ref}` role as `exerise` notes are (by default) enumerated.

Furthermore, `numref` can take in three additional placeholders for more customized titles:

1. _%s_
2.  _{number}_ which get replaced by the exercise number, and
3. _{name}_ by the exercise title.[^note]

An example ```{numref}`My custom {number} title and {name}` ``` would resolve to {numref}`My custom {number} title and {name} <my-exercise>`

[^note]: If the exercise directive does not have a title, an `invalid numfig format` warning will be displayed during build if the user tries to use the _{name}_ placeholder.


## Solution Directive

A solution directive can be included using the `solution` pattern. It takes in the label of the directive it wants to link to as a required argument. Unlike the `exercise` directive, the solution directive not enumerable as it inherits directly from the linked exercise.

The following options are also supported:

* `label` : text

    A unique identifier for your solution that you can use to reference it with `{ref}`. Cannot contain spaces or special characters.
* `class` : text

    Value of the solution’s class attribute which can be used to add custom CSS or JavaScript.
* `hidden` : flag (empty)

    Removes the directive from the final output.


**Example**

````{solution} my-exercise
:label: my-solution

Here's one solution.

```{code-block} python
def factorial(n):
    k = 1
    for i in range(n):
        k = k * (i + 1)
    return k

factorial(4)
```
````

**MyST Syntax**

``````md
````{solution} my-exercise
:label: my-solution

Here's one solution.

```{code-block} python
def factorial(n):
    k = 1
    for i in range(n):
        k = k * (i + 1)
    return k

factorial(4)
```
````
``````

_Source:_ [QuantEcon](https://python-programming.quantecon.org/functions.html#Exercise-1)


### Referencing Solutions

You can refer to a solution using the `{ref}` role like: ```{ref}`my-solution` ``` the output of which depends on the attributes of the linked directive. If the linked directive is enumerable, the role will replace the solution reference with the linked directive type and its appropriate number like so: {ref}`my-solution`.

In the event that the directive being referenced is unenumerable, the reference will display its title: {ref}`nfactorial-solution`. Click the toggle to see the supporting directives.

````{toggle}

```{exercise} $n!$ Factorial
:label: nfactorial
:nonumber:

Write a function `factorial` such that `factorial(int n)` returns $n!$
for any positive integer $n$.
```

```{solution} nfactorial
:label: nfactorial-solution

Here's a solution in Java.

```{code-block} java
static int factorial(int n){
    if (n == 0)
        return 1;
    else {
        return(n * factorial(n-1));
    }
}
```
````


If the title of the linked directive being reference does not exist, it will default to {ref}`nfactorial-notitle-solution`. Click the toggle to see the supporting directives.

````{toggle}

```{exercise}
:label: nfactorial-notitle
:nonumber:

Write a function `factorial` such that `factorial(int n)` returns $n!$
for any positive integer $n$.
```

```{solution} nfactorial-notitle
:label: nfactorial-notitle-solution

Here's a solution in Java.

```{code-block} java
static int factorial(int n){
    if (n == 0)
        return 1;
    else {
        return(n * factorial(n-1));
    }
}
```
````


## Hide or Remove Directives

### Hide Content

The content of directives can be hidden using the `dropdown` class which is available through [sphinx-togglebutton](https://sphinx-togglebutton.readthedocs.io/en/latest/). For Sphinx projects, add `"sphinx_togglebutton"` to your `extensions` list in `conf.py` to activate the extension

```python
extensions = [
    ...
    "sphinx_togglebutton"
    ...
]
```

For Jupyter Book projects, add `sphinx_togglebutton` under `extra_extensions`

```yaml
sphinx:
    extra_extensions:
        - sphinx_togglebutton
```

To hide the content, simply add `:class: dropdown` as a directive option.

For more use cases see [sphinx-togglebutton](https://sphinx-togglebutton.readthedocs.io/en/latest/#usage).

**Example**

```{exercise}
:class: dropdown

Recall that $n!$ is read as "$n$ factorial" and defined as
$n! = n \times (n - 1) \times \cdots \times 2 \times 1$.

There are functions to compute this in various modules, but let's
write our own version as an exercise.

In particular, write a function `factorial` such that `factorial(n)` returns $n!$
for any positive integer $n$.
```

**MyST Syntax**:

````
```{exercise}
:class: dropdown

Recall that $n!$ is read as "$n$ factorial" and defined as
$n! = n \times (n - 1) \times \cdots \times 2 \times 1$.

There are functions to compute this in various modules, but let's
write our own version as an exercise.

In particular, write a function `factorial` such that `factorial(n)` returns $n!$
for any positive integer $n$.
```
````

### Remove Directives

Any specific directive can be hidden by introducing the `:hidden:` option. For example, the following example will not be displayed

````md
```{exercise}
    :hidden:

    This is a hidden exercise directive.
```
````

```{exercise}
    :hidden:

    This is a hidden exercise directive.
```

### Remove All Solutions

All solution directives can be removed from the final output by setting `hide_solutions` to `True`. For Sphinx projects, add the configuration key in the `conf.py` file. Jupyter Book projects, should set the configuration key in `_config.yml` as follows

```yaml
...
sphinx:
  config:
    hide_solutions: True
...
```

## Custom CSS or JavaScript

Custom JavaScript scripts and CSS rules will allow you to add additional functionality or customize how elements are displayed. If you'd like to include custom CSS or JavaScript scripts in Jupyter Book, simply add any files ending in `.css` or `.js` under a `_static` folder. Any files under this folder will be automatically copied into the built book.

In Sphinx, this can be achieved by specifying the path of your `_static` folder and including CSS/JavaScript files by using the options `html_css_files` and `html_js_files` in `conf.py`:

```python
# conf.py

html_static_path = ["_static"]

# CSS files
html_css_files = ["custom.css",]
# JS files
html_js_files = ["custom.js",]
```

For example, to include the following CSS content which changes the default color of an exercise directive named "orange" under `docs/_static/custom.css`:

```
/* docs/_static/custom.css */

:root {
    --background-color: rgba(253, 126, 20, .3);
    --border-color: #fd7e14;
}

div.orange {
    background-color: var(--background-color);
    border-color: var(--border-color);
}

div.orange p.admonition-title {
    background-color: var(--background-color);
}
```

Add `html_static_path` and `html_css_files` under `conf.py`:

```python
# conf.py

html_static_path = ['../_static']
html_css_files = ['custom.css']
```

These steps will change the default color of the exercise directive named "orange" displayed below

````md
```{exercise}
:class: orange

This is an example of how to introduce custom CSS.
```
````

```{exercise}
:class: orange

This is an example of how to introduce custom CSS.
```
