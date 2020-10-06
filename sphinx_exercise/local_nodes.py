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


logger = logging.getLogger(__name__)


def is_enumerable_node(node):
    return node.__class__ == enumerable_node


def is_unenumerable_node(node):
    return node.__class__ == unenumerable_node


def is_linked_node(node):
    return node.__class__ == linked_node


def is_extension_node(node):
    return (
        is_enumerable_node(node) or is_unenumerable_node(node) or is_linked_node(node)
    )


class enumerable_node(nodes.Admonition, nodes.Element):
    pass


def visit_enumerable_node(self, node: Node) -> None:
    self.visit_admonition(node)


def depart_enumerable_node(self, node: Node) -> None:
    self.depart_admonition(node)


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
