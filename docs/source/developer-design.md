# Design of the Package

This page documents some design decisions that were made when building this
`sphinx` extension.

`sphinx-exercise` includes:

1. `directives`
2. `nodes`
3. `post_transforms`
4. integrations with `sphinx.env`

## Directives

See [](syntax.md) for futher details on the available directives and options

## Nodes

The nodes support the directives:

1. `exercise_node`
1. `exercise_enumerable_node`
1. `solution_node`

as well as custom title infrastructure:

1. `exercise_title`
1. `exercise_subtitle`
1. `solution_title`
1. `solution_subtitle`

and support for `:numref:` references to enumerated exercise nodes
in the LaTeX context by resolving the node title numbering:

1. `exercise_latex_number_reference`

The `title` and `reference` nodes are used internally by the
`directives` and are then removed in `post_transforms` negating the need
for any custom `translator` methods. The use
of custom nodes allows for simpler detection of objects by this
extension, rather than catering for additional items that may be added by other
sphinx components.

## Post Transforms

The `post_transforms` run in the following order:

1. UpdateReferencesToEnumerated (priority = 5, before `pending_xref` are resolved)
2. ResolveTitlesInExercises (priority = 20)
3. ResolveTitlesInSolutions (priority = 21)
4. ResolveLinkTextToSolutions (priority = 22)

These `post_transforms` are setup to resolve in `Exercise` -> `Solution` -> `References`
ordering. Any `:ref:` made to an enumerated `exercise` node are converted into `numref`
references prior to `pending_xref` objects are resolved by `sphinx`.

This is aligned with most use cases in a document. In the case of `solutions`
if the target node (title) has not been resolved, this is checked and then resolved
as required.

**Design Decision:** It was decided to integrate with `:ref:` and `:numref:` roles
to support both reference styles to `exercise` and `solution` directives.
The `post_transforms` are required to make adjustments the the `sphinx` abstract
syntax tree (AST) to support `:numref:` and the resolve `titles`
in `exercise` and `solution` admonitions. This is required as components of
`numref` are resolved at the `translator` phase for `html` and is activated
essentially by default for LaTeX but leaves the numbering to the `LaTeX`
builder such as `pdflatex`.

## Additional Notes

###  Package Registry `sphinx.env.sphinx_exercise_registry`

This package includes a registry of all `exercise` and `solution`
nodes that are parsed.

This registry includes nodes referenced by their `label`:

```python
self.env.sphinx_exercise_registry[label] = {
    "type": self.name,
    "docname": self.env.docname,
    "node": node,
}
```

and records the `type`, `docname` where the node is parsed, and
the `node` object.
