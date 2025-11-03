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
```

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


## Alternative Gated Syntax

A restriction of MyST is that `code-cell` directives must be at the root level of the document for them to be executed. This maintains direct
compatility with the `jupyter notebook` and enables tools like `jupytext` to convert between `myst` and `ipynb` files.

As a result **executable** `code-cell` directives cannot be nested inside of exercises or solution directives.

The solution to this is to use the **gated syntax**.

```{note}
This syntax can also be a convenient way of surrounding blocks of text that may include other directives that you wish
to include in an exercise or solution admonition.
```

### Basic Syntax

````md
```{exercise-start}
:label: ex1
```

```{code-cell}
# Some setup code that needs executing
```

and maybe you wish to add a figure

```{figure} img/example.png
```

```{exercise-end}
```
````

The `exercise-start` directive allows for he same options as core `exercise` directive.

````md
```{solution-start} ex1
```

```{code-cell}
# Solution Code
```

```{solution-end}
```
````

```{warning}
If there are missing `-start` and `-end` directives, this will cause Sphinx to return an extension error,
alongside some helpful feedback to diagnose the issue in document structure.
```

### Example

````md

```{solution-start} exercise-1
:label: solution-gated-1
```

This is a solution to Exercise 1

```{code-cell} python3
import numpy as np
import matplotlib.pyplot as plt

# Fixing random state for reproducibility
np.random.seed(19680801)

dt = 0.01
t = np.arange(0, 30, dt)
nse1 = np.random.randn(len(t))                 # white noise 1
nse2 = np.random.randn(len(t))                 # white noise 2

# Two signals with a coherent part at 10Hz and a random part
s1 = np.sin(2 * np.pi * 10 * t) + nse1
s2 = np.sin(2 * np.pi * 10 * t) + nse2

fig, axs = plt.subplots(2, 1)
axs[0].plot(t, s1, t, s2)
axs[0].set_xlim(0, 2)
axs[0].set_xlabel('time')
axs[0].set_ylabel('s1 and s2')
axs[0].grid(True)

cxy, f = axs[1].cohere(s1, s2, 256, 1. / dt)
axs[1].set_ylabel('coherence')

fig.tight_layout()
plt.show()
```

With some follow up text to the solution

```{solution-end}
```

````

will produce the following `solution` block in your `html` output.

```{figure} img/gated-directive-example.png
```


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

```{tip}
To customize the dropdown toggle button text (e.g., "Show" instead of "Click to show"), add custom CSS in your theme or project. This is typically handled at the theme level for consistent styling across all toggle buttons.
```

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

### Solution Title Styling

By default, solution titles include a hyperlink to the corresponding exercise. This behavior can be modified using the `exercise_style` configuration option.

When solutions follow exercises directly in your content (common in lecture notes), you may want to remove the hyperlink to avoid confusion when using the `dropdown` class. Set `exercise_style` to `"solution_follow_exercise"` to display only text without hyperlinks in solution titles.

For Sphinx projects, add the configuration key in the `conf.py` file:

```python
# conf.py
exercise_style = "solution_follow_exercise"
```

For Jupyter Book projects, set the configuration key in `_config.yml`:

```yaml
...
sphinx:
  config:
    exercise_style: "solution_follow_exercise"
...
```

When `exercise_style` is set to `"solution_follow_exercise"`, the solution title will display plain text like "Solution to Exercise 1 (Title)" instead of a hyperlink. When empty `""` (default), the exercise reference in the solution title remains clickable.

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

## Internationalization (i18n)

`sphinx-exercise` includes built-in support for internationalization across 27 languages. The extension automatically detects your Sphinx project's language setting and displays "Exercise" and "Solution to" labels in the appropriate language.

### Supported Languages

The following languages are currently supported:

- Arabic (ar)
- Bengali (bn)
- Chinese (zh_CN)
- Czech (cs)
- Dutch (nl)
- French (fr)
- German (de)
- Greek (el)
- Hindi (hi)
- Hungarian (hu)
- Indonesian (id)
- Italian (it)
- Japanese (ja)
- Korean (ko)
- Malay (ms)
- Norwegian (no)
- Polish (pl)
- Portuguese (pt)
- Romanian (ro)
- Russian (ru)
- Spanish (es)
- Swedish (sv)
- Tamil (ta)
- Turkish (tr)
- Ukrainian (uk)
- Vietnamese (vi)

### Configuring Language

To configure the language for your Sphinx project, set the `language` option in your `conf.py`:

```python
# conf.py
language = 'es'  # For Spanish
```

For Jupyter Book projects, set the language in `_config.yml`:

```yaml
# _config.yml
sphinx:
  config:
    language: es
```

The exercise and solution directives will automatically use the appropriate translations. For example, with Spanish configured, "Exercise" will display as "Ejercicio" and "Solution to" as "Solución a".

### Contributing Translations

If you'd like to contribute translations for additional languages or improve existing ones, please see the [translation guide](https://github.com/executablebooks/sphinx-exercise/tree/main/sphinx_exercise/translations) in the repository.
