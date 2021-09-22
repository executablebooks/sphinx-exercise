"""
sphinx_exercise.nodes
~~~~~~~~~~~~~~~~~~~~~

Enumerable and unenumerable nodes

:copyright: Copyright 2020 by the QuantEcon team, see AUTHORS
:licences: see LICENSE for details
"""
from docutils.nodes import Node
from sphinx.util import logging
from docutils import nodes
from sphinx.writers.latex import LaTeXTranslator
from .utils import get_node_number, find_parent

logger = logging.getLogger(__name__)

CR = "\n"
latex_admonition_start = CR + "\\begin{sphinxadmonition}{note}"
latex_admonition_end = "\\end{sphinxadmonition}" + CR


class exercise_node(nodes.Admonition, nodes.Element):
    pass


class solution_node(nodes.Admonition, nodes.Element):
    pass


class exercise_unenumerable_node(nodes.Admonition, nodes.Element):
    pass


def visit_enumerable_node(self, node: Node) -> None:
    if isinstance(self, LaTeXTranslator):
        docname = find_parent(self.builder.env, node, "section")
        self.body.append("\\label{" + f"{docname}:{node.attributes['label']}" + "}")
        self.body.append(latex_admonition_start)
    else:
        for title in node.traverse(nodes.title):
            if "Exercise" in title.astext():
                title[0] = nodes.Text("")
        self.body.append(self.starttag(node, "div", CLASS="admonition"))


def depart_enumerable_node(self, node: Node) -> None:
    typ = "exercise"
    if isinstance(self, LaTeXTranslator):
        number = get_node_number(self, node, typ)
        idx = list_rindex(self.body, latex_admonition_start) + 2
        self.body.insert(idx, f"{typ.title()} {number}")
        self.body.append(latex_admonition_end)
    else:
        number = get_node_number(self, node, typ)
        if number:
            idx = self.body.index(f"{typ.title()} {number} ")
            self.body[idx] = f"{typ.title()} {number} "
        self.body.append("</div>")


def visit_exercise_unenumerable_node(self, node: Node) -> None:
    if isinstance(self, LaTeXTranslator):
        docname = find_parent(self.builder.env, node, "section")
        self.body.append("\\label{" + f"{docname}:{node.attributes['label']}" + "}")
        self.body.append(latex_admonition_start)
    else:
        for title in node.traverse(nodes.title):
            if "Exercise" in title.astext():
                title[0] = nodes.Text("")
        self.body.append(self.starttag(node, "div", CLASS="admonition"))


def depart_exercise_unenumerable_node(self, node: Node) -> None:
    typ = node.attributes.get("type", "")
    if isinstance(self, LaTeXTranslator):
        idx = list_rindex(self.body, latex_admonition_start) + 2
        self.body.insert(idx, f"{typ.title()}")
        self.body.append(latex_admonition_end)
    else:
        idx = list_rindex(self.body, '<p class="admonition-title">') + 1
        element = f"<span>{typ.title()} </span>"
        self.body.insert(idx, element)
        self.body.append("</div>")


def visit_solution_node(self, node: Node) -> None:
    self.body.append(self.starttag(node, "div", CLASS="admonition"))


def depart_solution_node(self, node: Node) -> None:
    typ = "solution"
    number = get_node_number(self, node, typ)
    idx = self.body.index(f"{typ.title()} {number} ")
    self.body.pop(idx)
    self.body.append("</div>")


def is_exercise_node(node):
    return isinstance(node, exercise_node)


def is_unenumerable_node(node):
    return isinstance(node, exercise_unenumerable_node)


def is_solution_node(node):
    return isinstance(node, solution_node)


def is_extension_node(node):
    return (
        is_exercise_node(node) or is_unenumerable_node(node) or is_solution_node(node)
    )


def rreplace(s, old, new, occurrence):
    # taken from https://stackoverflow.com/a/2556252
    li = s.rsplit(old, occurrence)
    return new.join(li)


def list_rindex(li, x) -> int:
    """Getting the last occurence of an item in a list."""
    for i in reversed(range(len(li))):
        if li[i] == x:
            return i
    raise ValueError("{} is not in list".format(x))


NODE_TYPES = {
    "exercise": {"node": exercise_node, "type": "exercise"},
    "solution": {"node": solution_node, "type": "solution"},
}
