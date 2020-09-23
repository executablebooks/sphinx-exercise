# Syntax Guide

```{note}
This documentation utilized the [Markedly Structured Text (MyST)](https://myst-parser.readthedocs.io/en/latest/index.html) syntax.
```

## Exercises

An exercise directive can be included using the `exercise` pattern. The directive is enumerated by default and can take in an optional title argument. The following options are also supported:

* `label` : text

    A unique identifier for your exercise that you can use to reference it with `{ref}`. Cannot contain spaces or special characters.
* `class` : text

    Value of the exercise’s class attribute which can be used to add custom CSS or JavaScript.
* `nonumber` : flag (empty)

    Turns off exercise auto numbering.

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
