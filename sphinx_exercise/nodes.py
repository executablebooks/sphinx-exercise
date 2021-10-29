"""
sphinx_exercise.nodes
~~~~~~~~~~~~~~~~~~~~~

Enumerable and unenumerable nodes

:copyright: Copyright 2020 by the QuantEcon team, see AUTHORS
:licences: see LICENSE for details
"""
from docutils.nodes import Node
from sphinx.util import logging
from docutils import nodes as docutil_nodes
from sphinx.writers.latex import LaTeXTranslator
from .utils import get_node_number, find_parent, list_rindex
from .latex import LaTeXMarkup

logger = logging.getLogger(__name__)
LaTeX = LaTeXMarkup()


class exercise_node(docutil_nodes.Admonition, docutil_nodes.Element):
    pass


class solution_node(docutil_nodes.Admonition, docutil_nodes.Element):
    pass


class exercise_unenumerable_node(docutil_nodes.Admonition, docutil_nodes.Element):
    pass


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


def _remove_placeholder_title_exercise(typ, node):
    """ Removing the exercise placeholder we put in title earlier."""
    for title in node.traverse(docutil_nodes.title):
        if typ.title() in title.astext():
            title[0] = docutil_nodes.Text("")


def visit_enumerable_node(self, node: Node) -> None:
    typ = node.attributes.get("type", "")
    if isinstance(self, LaTeXTranslator):
        _remove_placeholder_title_exercise(typ, node)
        _visit_nodes_latex(self, node, find_parent)
    else:
        _remove_placeholder_title_exercise(typ, node)
        self.body.append(self.starttag(node, "div", CLASS="admonition"))


def depart_enumerable_node(self, node: Node) -> None:
    typ = node.attributes.get("type", "")
    if isinstance(self, LaTeXTranslator):
        number = get_node_number(self, node, typ)
        _depart_nodes_latex(self, node, f"{typ.title()} {number} ")
    else:
        number = get_node_number(self, node, typ)
        idx = list_rindex(self.body, f"{typ.title()} {number} ")
        self.body[idx] = f"{typ.title()} {number} "
        self.body.append("</div>")


def visit_exercise_unenumerable_node(self, node: Node) -> None:
    typ = node.attributes.get("type", "")
    if isinstance(self, LaTeXTranslator):
        _remove_placeholder_title_exercise(typ, node)
        _visit_nodes_latex(self, node, find_parent)
    else:
        _remove_placeholder_title_exercise(typ, node)
        self.body.append(self.starttag(node, "div", CLASS="admonition"))


def depart_exercise_unenumerable_node(self, node: Node) -> None:
    typ = node.attributes.get("type", "")
    if isinstance(self, LaTeXTranslator):
        _depart_nodes_latex(self, node, f"{typ.title()} ")
    else:
        idx = list_rindex(self.body, '<p class="admonition-title">') + 1
        element = f"<span>{typ.title()} </span>"
        self.body.insert(idx, element)
        self.body.append("</div>")


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


def is_exercise_node(node):
    return isinstance(node, exercise_node)


def is_exercise_unenumerable_node(node):
    return isinstance(node, exercise_unenumerable_node)


def is_solution_node(node):
    return isinstance(node, solution_node)


def is_extension_node(node):
    return (
        is_exercise_node(node)
        or is_exercise_unenumerable_node(node)
        or is_solution_node(node)
    )


def rreplace(s, old, new, occurrence):
    # taken from https://stackoverflow.com/a/2556252
    li = s.rsplit(old, occurrence)
    return new.join(li)


NODE_TYPES = {
    "exercise": {"node": exercise_node, "type": "exercise"},
    "solution": {"node": solution_node, "type": "solution"},
}
