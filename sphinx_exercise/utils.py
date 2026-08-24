# Utility functions

from sphinx.writers.latex import LaTeXTranslator

#: The exercise style that places solutions directly after their exercises,
#: and therefore implies collapsed solutions unless the author opts out.
SOLUTION_FOLLOW_EXERCISE = "solution_follow_exercise"


def solutions_are_collapsed(config) -> bool:
    """Whether solution directives should render folded by default.

    ``solution_collapsed`` is deliberately tri-state:

    ``True`` / ``False``
        An explicit choice by the author, which always wins.
    ``None`` (the default)
        Defer to ``exercise_style``. The ``solution_follow_exercise`` style puts
        the solution directly beneath its exercise, which is precisely the
        layout where an expanded solution is hard to look away from, so that
        style implies collapsed solutions.

    A plain ``False`` default could not express this, because Sphinx cannot
    distinguish "unset" from "explicitly set to False" through the public
    config API - so ``solution_collapsed = False`` would be unable to switch
    the style's implied collapsing back off.
    """
    if config.solution_collapsed is not None:
        return bool(config.solution_collapsed)
    return config.exercise_style == SOLUTION_FOLLOW_EXERCISE


def collapsed_is_implied_by_style(config) -> bool:
    """Whether collapsing came from ``exercise_style`` rather than an explicit opt-in.

    Used to tailor the "sphinx-togglebutton is missing" warning, since an author
    who never asked for collapsing needs to be told how to switch it off as well
    as how to make it work.
    """
    return config.solution_collapsed is None and solutions_are_collapsed(config)


def find_parent(env, node, parent_tag):
    """Find the nearest parent node with the given tagname."""

    while True:
        node = node.parent
        if node is None:
            return None
        # parent should be a document in toc
        if (
            "docname" in node.attributes
            and env.titles[node.attributes["docname"]].astext().lower()
            in node.attributes["names"]
        ):
            return node.attributes["docname"]


def get_node_number(self, node, typ) -> str:
    """Get the number for the directive node for HTML."""

    ids = node.attributes.get("ids", [])[0]
    if isinstance(self, LaTeXTranslator):
        docname = find_parent(self.builder.env, node, "section")
    else:
        docname = node.attributes.get("docname", "")
        # Latex does not have builder.fignumbers
    fignumbers = self.builder.env.toc_fignumbers.get(docname, {})
    number = fignumbers.get(typ, {}).get(ids, ())
    return ".".join(map(str, number))
