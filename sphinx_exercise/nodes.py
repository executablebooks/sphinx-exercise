"""
sphinx_exercise.nodes
~~~~~~~~~~~~~~~~~~~~~

Sphinx Exercise Nodes

:copyright: Copyright 2020 by the QuantEcon team, see AUTHORS
:licences: see LICENSE for details
"""
from sphinx.util import logging
from docutils.nodes import Node
from docutils import nodes as docutil_nodes
from sphinx.writers.latex import LaTeXTranslator
from .utils import get_node_number, find_parent, list_rindex
from .latex import LaTeXMarkup

logger = logging.getLogger(__name__)
LaTeX = LaTeXMarkup()


# Nodes


class exercise_node(docutil_nodes.Admonition, docutil_nodes.Element):
    pass


class exercise_enumerable_node(docutil_nodes.Admonition, docutil_nodes.Element):
    pass


class solution_node(docutil_nodes.Admonition, docutil_nodes.Element):
    pass


class exercise_title(docutil_nodes.title):
    def default_title(self):
        title_text = self.children[0].astext()
        if title_text == "Exercise" or title_text == "Exercise %s":
            return True
        else:
            return False


class exercise_subtitle(docutil_nodes.subtitle):
    pass


# Test Node Functions


def is_exercise_node(node):
    return isinstance(node, exercise_node)


def is_exercise_enumerable_node(node):
    return isinstance(node, exercise_enumerable_node)


def is_solution_node(node):
    return isinstance(node, solution_node)


def is_extension_node(node):
    return (
        is_exercise_node(node)
        or is_exercise_enumerable_node(node)
        or is_solution_node(node)
    )


# Visit and Depart Functions


def _visit_nodes_latex(self, node, find_parent):
    """ Function to handle visit_node for latex. """
    docname = find_parent(self.builder.env, node, "section")
    self.body.append(
        "\\phantomsection \\label{" + f"{docname}:{node.attributes['label']}" + "}"
    )
    self.body.append(LaTeX.visit_admonition())


def _depart_nodes_latex(self, node, title, pop_index=False):
    """ Function to handle depart_node for latex. """
    idx = list_rindex(self.body, LaTeX.visit_admonition()) + 2
    if pop_index:
        self.body.pop(idx)
    self.body.insert(idx, title)
    self.body.append(LaTeX.depart_admonition())


def visit_exercise_node(self, node: Node) -> None:
    if isinstance(self, LaTeXTranslator):
        # _remove_placeholder_title_exercise(typ, node)
        _visit_nodes_latex(self, node, find_parent)
    else:
        self.body.append(self.starttag(node, "div", CLASS="admonition"))
        self.body.append("\n")


def depart_exercise_node(self, node: Node) -> None:
    typ = node.attributes.get("type", "")
    if isinstance(self, LaTeXTranslator):
        _depart_nodes_latex(self, node, f"{typ.title()} ")
    else:
        self.body.append("</div>")


def visit_exercise_enumerable_node(self, node: Node) -> None:
    if isinstance(self, LaTeXTranslator):
        _visit_nodes_latex(self, node, find_parent)
    else:
        self.body.append(self.starttag(node, "div", CLASS="admonition"))
        self.body.append("\n")


def depart_exercise_enumerable_node(self, node: Node) -> None:
    typ = node.attributes.get("type", "")
    if isinstance(self, LaTeXTranslator):
        number = get_node_number(self, node, typ)
        _depart_nodes_latex(self, node, f"{typ.title()} {number} ")
    else:
        self.body.append("</div>")
        self.body.append("\n")


def visit_solution_node(self, node: Node) -> None:
    if isinstance(self, LaTeXTranslator):
        _visit_nodes_latex(self, node, find_parent)
    else:
        self.body.append(self.starttag(node, "div", CLASS="admonition"))


def depart_solution_node(self, node: Node) -> None:
    typ = node.attributes.get("type", "")
    if isinstance(self, LaTeXTranslator):
        _depart_nodes_latex(self, node, f"{typ.title()} to ", True)
    else:
        number = get_node_number(self, node, typ)
        idx = list_rindex(self.body, f"{typ.title()} {number} ")
        self.body.pop(idx)
        self.body.append("</div>")


def visit_exercise_title(self, node: Node) -> None:
    if isinstance(self, LaTeXTranslator):
        raise NotImplementedError
    else:
        classes = "admonition-title"
        self.body.append(f"<p class={classes}>")


def depart_exercise_title(self, node: Node) -> None:
    if isinstance(self, LaTeXTranslator):
        raise NotImplementedError
    else:
        self.body.append("</p>")
        self.body.append("\n")


def visit_exercise_subtitle(self, node: Node) -> None:
    if isinstance(self, LaTeXTranslator):
        raise NotImplementedError
    else:
        classes = "admonition-exercise-subtitle"
        self.body.append(self.starttag(node, "span", "", CLASS=classes))


def depart_exercise_subtitle(self, node: Node) -> None:
    if isinstance(self, LaTeXTranslator):
        raise NotImplementedError
    else:
        self.body.append("</span>")
