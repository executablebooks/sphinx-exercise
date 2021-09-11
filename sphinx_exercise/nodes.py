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


class exercise_unenumerable_node(nodes.Admonition, nodes.Element):
    pass


def visit_enumerable_node(self, node: Node) -> None:
    if isinstance(self, LaTeXTranslator):
        docname = find_parent(self.builder.env, node, "section")
        self.body.append("\\label{" + f"{docname}:{node.attributes['label']}" + "}")
        self.body.append(latex_admonition_start)
    else:
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


def visit_exercise_unenumerable_node(self, node: Node) -> None:
    if isinstance(self, LaTeXTranslator):
        docname = find_parent(self.builder.env, node, "section")
        self.body.append("\\label{" + f"{docname}:{node.attributes['label']}" + "}")
        self.body.append(latex_admonition_start)
    else:
        self.body.append(self.starttag(node, "div", CLASS="admonition"))


def depart_exercise_unenumerable_node(self, node: Node) -> None:
    typ = node.attributes.get("type", "")
    title = node.attributes.get("title", "")
    if isinstance(self, LaTeXTranslator):
        idx = list_rindex(self.body, latex_admonition_start) + 2
        self.body.insert(idx, f"{typ.title()}")
        self.body.append(latex_admonition_end)
    else:
        if title == "":
            idx = list_rindex(self.body, '<p class="admonition-title">') + 1
        else:
            idx = list_rindex(self.body, title)
        element = f"<span>{typ.title()} </span>"
        self.body.insert(idx, element)
        self.body.append("</div>")


def visit_solution_node(self, node: Node) -> None:
    self.body.append(self.starttag(node, "div", CLASS="admonition"))


def depart_solution_node(self, node: Node) -> None:
    target_labelid = node.get("target_label", "")
    typ = "solution"
    if target_labelid in self.builder.env.exercise_list:
        target_attr = self.builder.env.exercise_list[target_labelid]
        target_node = target_attr.get("node", Node)
        if is_exercise_node(target_node):
            target_number = get_node_number(self, target_node, "exercise")
        else:
            target_number = ""
        number = get_node_number(self, node, "solution")
        idx = self.body.index(f"{typ} {number} ")
        ref_idx = idx + 2
        reference = self.body[ref_idx]
        self.body.pop(ref_idx)
        self.body.insert(idx - 1, reference)
        self.body[idx + 1] = f"Solution to Exercise {target_number} "
    else:
        number = get_node_number(self, node, typ)
        idx = self.body.index(f"{typ} {number} ")
        self.body[idx] = f"{typ.title()} {number} "
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
