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

logger = logging.getLogger(__name__)

CR = "\n"
latex_admonition_start = CR + "\\begin{sphinxadmonition}{note}"
latex_admonition_end = "\\end{sphinxadmonition}" + CR


class exercise_node(nodes.Admonition, nodes.Element):
    pass


class solution_node(nodes.Admonition, nodes.Element):
    pass


class unenumerable_node(nodes.Admonition, nodes.Element):
    pass


def visit_enumerable_node(self, node: Node) -> None:
    self.body.append(self.starttag(node, "div", CLASS="admonition"))


def depart_enumerable_node(self, node: Node) -> None:
    typ = "exercise"
    if isinstance(self, LaTeXTranslator):
        number = get_node_number(self, node, typ)
        idx = list_rindex(self.body, latex_admonition_start) + 2
        self.body.insert(idx, f"{typ.title()} {number}")
        self.body.append(latex_admonition_end)
    else:
        # Find index in list of 'Proof #'
        number = get_node_number(self, node, typ)
        idx = self.body.index(f"{typ} {number} ")
        self.body[idx] = f"{typ.title()} {number} "
        self.body.append("</div>")


def visit_unenumerable_node(self, node: Node) -> None:
    self.visit_admonition(node)


def depart_unenumerable_node(self, node: Node) -> None:
    self.depart_admonition(node)


def visit_solution_node(self, node: Node) -> None:
    self.visit_admonition(node)


def depart_solution_node(self, node: Node) -> None:
    self.depart_admonition(node)


def is_exercise_node(node):
    return isinstance(node, exercise_node)


def is_unenumerable_node(node):
    return isinstance(node, unenumerable_node)


def is_solution_node(node):
    return isinstance(node, solution_node)


def is_extension_node(node):
    return (
        is_exercise_node(node) or is_unenumerable_node(node) or is_solution_node(node)
    )


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

    if node.tagname == parent_tag:
        return node.attributes["docname"]

    return None


def list_rindex(li, x) -> int:
    """Getting the last occurence of an item in a list."""
    for i in reversed(range(len(li))):
        if li[i] == x:
            return i
    raise ValueError("{} is not in list".format(x))


def get_node_number(self, node: Node, typ) -> str:
    """Get the number for the directive node for HTML."""
    ids = node.attributes.get("ids", [])[0]
    if isinstance(self, LaTeXTranslator):
        docname = find_parent(self.builder.env, node, "section")
        fignumbers = self.builder.env.toc_fignumbers.get(
            docname, {}
        )  # Latex does not have builder.fignumbers
    else:
        fignumbers = self.builder.fignumbers
    number = fignumbers.get(typ, {}).get(ids, ())
    return ".".join(map(str, number))


NODE_TYPES = {
    "exercise": {"node": exercise_node, "type": "exercise"},
    "solution": {"node": solution_node, "type": "solution"},
}
