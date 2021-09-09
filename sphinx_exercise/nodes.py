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


def is_enumerable_node(node):
    return isinstance(node, exercise_node)


def is_unenumerable_node(node):
    return isinstance(node, unenumerable_node)


def is_linked_node(node):
    return isinstance(node, linked_node)


def is_extension_node(node):
    return (
        is_enumerable_node(node) or is_unenumerable_node(node) or is_linked_node(node)
    )


class exercise_node(nodes.Admonition, nodes.Element):
    pass


def visit_enumerable_node(self, node: Node) -> None:
    self.body.append(self.starttag(node, "div", CLASS="admonition"))


def depart_enumerable_node(self, node: Node) -> None:
    typ = 'exercise'
    if isinstance(self, LaTeXTranslator):
        number = get_node_number(self, node, typ)
        idx = list_rindex(self.body, latex_admonition_start) + 2
        self.body.insert(idx, f"{typ.title()} {number}")
        self.body.append(latex_admonition_end)
    else:
        # Find index in list of 'Proof #'
        number = get_node_number(self, node, typ)
        import pdb;
        pdb.set_trace()
        idx = self.body.index(f"{typ} {number} ")
        self.body[idx] = f"{typ.title()} {number} "
        self.body.append("</div>")


class unenumerable_node(nodes.Admonition, nodes.Element):
    pass


def visit_unenumerable_node(self, node: Node) -> None:
    self.visit_admonition(node)


def depart_unenumerable_node(self, node: Node) -> None:
    self.depart_admonition(node)


class linked_node(nodes.Admonition, nodes.Element):
    pass


def visit_linked_node(self, node: Node) -> None:
    self.visit_admonition(node)


def depart_linked_node(self, node: Node) -> None:
    self.depart_admonition(node)

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
