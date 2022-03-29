"""
sphinx_exercise.nodes
~~~~~~~~~~~~~~~~~~~~~

Sphinx Exercise Nodes

:copyright: Copyright 2020-2021 by the Executable Books team, see AUTHORS
:licences: see LICENSE for details
"""
<<<<<<< HEAD
from sphinx.locale import get_translation
from docutils.nodes import Node
=======

>>>>>>> master
from sphinx.util import logging
from docutils.nodes import Node
from docutils import nodes as docutil_nodes
from sphinx import addnodes as sphinx_nodes
from sphinx.writers.latex import LaTeXTranslator
from .latex import LaTeXMarkup

logger = logging.getLogger(__name__)
<<<<<<< HEAD
MESSAGE_CATALOG_NAME = "exercise"
_ = get_translation(MESSAGE_CATALOG_NAME)

=======
LaTeX = LaTeXMarkup()
>>>>>>> master


# Nodes


class exercise_node(docutil_nodes.Admonition, docutil_nodes.Element):
    gated = False


class exercise_enumerable_node(docutil_nodes.Admonition, docutil_nodes.Element):
    gated = False
    resolved_title = False


class exercise_end_node(docutil_nodes.Admonition, docutil_nodes.Element):
    pass


class solution_node(docutil_nodes.Admonition, docutil_nodes.Element):
    resolved_title = False


class solution_start_node(docutil_nodes.Admonition, docutil_nodes.Element):
    resolved_title = False


class solution_end_node(docutil_nodes.Admonition, docutil_nodes.Element):
    resolved_title = False  # TODO: is this required?


class exercise_title(docutil_nodes.title):
    def default_title(self):
        title_text = self.children[0].astext()
        if title_text == "Exercise" or title_text == "Exercise %s":
            return True
        else:
            return False


class exercise_subtitle(docutil_nodes.subtitle):
    pass


class solution_title(docutil_nodes.title):
    def default_title(self):
        title_text = self.children[0].astext()
        if title_text == "Solution to":
            return True
        else:
            return False


class solution_subtitle(docutil_nodes.subtitle):
    pass


class exercise_latex_number_reference(sphinx_nodes.number_reference):
    pass


<<<<<<< HEAD
def _depart_nodes_latex(self, node, title, pop_index=False):
    """ Function to handle depart_node for latex. """
    idx = list_rindex(self.body, latex_admonition_start) + 2
    if pop_index:
        self.body.pop(idx)
    self.body.insert(idx, title)
    self.body.append(latex_admonition_end)


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
        _depart_nodes_latex(self, node, f"{_(typ.title())} {number} ")
    else:
        number = get_node_number(self, node, typ)
        idx = list_rindex(self.body, f"{_(typ.title())} {number} ")
        self.body[idx] = f"{_(typ.title())} {number} "
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
        _depart_nodes_latex(self, node, f"{_(typ.title())} ")
    else:
        idx = list_rindex(self.body, '<p class="admonition-title">') + 1
        element = f"<span>{_(typ.title())} </span>"
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
        _depart_nodes_latex(self, node, f"{_(typ.title())} to ", True)
    else:
        number = get_node_number(self, node, typ)
        idx = list_rindex(self.body, f"{_(typ.title())} {number} ")
        self.body.pop(idx)
        self.body.append("</div>")
=======
# Test Node Functions
>>>>>>> master


def is_exercise_node(node):
    return isinstance(node, exercise_node) or isinstance(node, exercise_enumerable_node)


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


def visit_exercise_node(self, node: Node) -> None:
    if isinstance(self, LaTeXTranslator):
        label = (
            "\\phantomsection \\label{" + f"exercise:{node.attributes['label']}" + "}"
        )  # TODO: Check this resolves.
        self.body.append(label)
        self.body.append(LaTeX.visit_admonition())
    else:
        self.body.append(self.starttag(node, "div", CLASS="admonition"))
        self.body.append("\n")


def depart_exercise_node(self, node: Node) -> None:
    if isinstance(self, LaTeXTranslator):
        self.body.append(LaTeX.depart_admonition())
    else:
        self.body.append("</div>")


def visit_exercise_enumerable_node(self, node: Node) -> None:
    """
    LaTeX Reference Structure is exercise:{label} and resolved by
    exercise_latex_number_reference nodes (see below)
    """
    if isinstance(self, LaTeXTranslator):
        label = (
            "\\phantomsection \\label{" + f"exercise:{node.attributes['label']}" + "}\n"
        )
        self.body.append(label)
        self.body.append(LaTeX.visit_admonition())
    else:
        self.body.append(self.starttag(node, "div", CLASS="admonition"))
        self.body.append("\n")


def depart_exercise_enumerable_node(self, node: Node) -> None:
    if isinstance(self, LaTeXTranslator):
        self.body.append(LaTeX.depart_admonition())
    else:
        self.body.append("</div>")
        self.body.append("\n")


def visit_solution_node(self, node: Node) -> None:
    """
    Reference Structure is {docname}:{label} and resolved by Sphinx
    """
    if isinstance(self, LaTeXTranslator):
        target_label = node.attributes["label"]
        target_node = self.builder.env.sphinx_exercise_registry[target_label]
        docname = target_node.get("docname")
        label = (
            "\\phantomsection \\label{"
            + f"{docname}:{node.attributes['label']}"
            + "}\n"
        )
        self.body.append(label)
        self.body.append(LaTeX.visit_admonition())
    else:
        self.body.append(self.starttag(node, "div", CLASS="admonition"))
        self.body.append("\n")


def depart_solution_node(self, node: Node) -> None:
    if isinstance(self, LaTeXTranslator):
        self.body.append(LaTeX.depart_admonition())
    else:
        self.body.append("</div>")
        self.body.append("\n")


def visit_exercise_latex_number_reference(self, node):
    id = node.get("refid")
    text = node.astext()
    hyperref = r"\hyperref[exercise:%s]{%s}" % (id, text)
    self.body.append(hyperref)
    raise docutil_nodes.SkipNode


def depart_exercise_latex_number_reference(self, node):
    pass
