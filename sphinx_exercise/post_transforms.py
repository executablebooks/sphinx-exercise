from sphinx.transforms.post_transforms import SphinxPostTransform
from sphinx.util import logging
from sphinx.addnodes import number_reference
from sphinx.builders.latex import LaTeXBuilder
from docutils import nodes as docutil_nodes
from docutils.nodes import Node

from .utils import get_node_number, get_refuri, has_math_child, find_parent
from .nodes import (
    solution_node,
    is_solution_node,
    is_exercise_node,
    is_exercise_unenumerable_node,
)

logger = logging.getLogger(__name__)

# Variables TODO: centralise these variables

SOLUTION_PLACEHOLDER = "Solution to "
MATH_PLACEHOLDER = ":math:"

# Helper Functions


def update_title(title):
    """
    Does necessary formatting to the title node, and wraps it with an inline node.

    # TODO: Can this be built into the node when instantiated?
    """
    inline = docutil_nodes.inline()

    if len(title) == 1 and isinstance(title[0], docutil_nodes.Text):
        _ = title[0][0].replace("(", "").replace(")", "")
        inline += docutil_nodes.Text(_, _)
    else:
        for ii in range(len(title)):
            item = title[ii]

            if ii == 0 and isinstance(item, docutil_nodes.Text):
                _ = item.replace("exercise", "").replace("(", "").lstrip()
                title.replace(title[ii], docutil_nodes.Text(_, _))
            elif ii == len(title) - 1 and isinstance(item, docutil_nodes.Text):
                _ = item.replace(")", "").rstrip()
                if _:
                    title.replace(title[ii], docutil_nodes.Text(_, _))
                else:
                    continue
            inline += title[ii]

    return inline


def process_math_placeholder(node, update_title, source_node):
    """Convert the placeholder math text to a math node."""

    if MATH_PLACEHOLDER in node.astext():
        title = update_title(source_node[0])
        return node.replace(node[0], title)


def process_reference(self, node, default_title=""):
    """
    Processing reference nodes in the document to set default titles
    """

    label = get_refuri(node)
    if (
        hasattr(self.env, "sphinx_exercise_registry")
        and label in self.env.sphinx_exercise_registry
    ):
        # Process Sources
        source_node = self.env.sphinx_exercise_registry[label].get("node")

        # Solution Node
        if is_solution_node(source_node):
            target_label = source_node.attributes.get("target_label", "")
            if node.astext().strip() == "Solution to":
                default_title = node.astext()
        else:
            target_label = source_node.attributes.get("label", "")

        # Process Targets
        target_attr = self.env.sphinx_exercise_registry[target_label]
        target_node = target_attr.get("node", Node)

        # Exercise Node
        if is_exercise_node(target_node):
            if default_title:
                number = get_node_number(self.app, target_node, "exercise")
                node.insert(len(node[0]), docutil_nodes.Text(" Exercise " + number))
                return
            else:
                node = process_math_placeholder(node, update_title, source_node)

        # Exercise Unenumerable Node
        if is_exercise_unenumerable_node(target_node):
            if default_title:
                if target_attr.get("title"):
                    if has_math_child(target_node[0]):
                        title = update_title(target_node[0])
                        title.insert(
                            0, docutil_nodes.Text(default_title, default_title)
                        )
                        node.replace(node[0], title)
                    else:
                        text = target_attr.get("title", "")
                        if text[0] == "(" and text[-1] == ")":
                            text = text[1:-1]
                        node[0].insert(len(node[0]), docutil_nodes.Text(text, text))
            else:
                node = process_math_placeholder(node, update_title, source_node)


# Transforms


class ReferenceTransform(SphinxPostTransform):
    default_priority = 998  # should be processed before processing solution nodes

    def run(self):

        for node in self.document.traverse(docutil_nodes.reference):
            process_reference(self, node)


class SolutionTransform(SphinxPostTransform):
    default_priority = 999  # should be after processing reference nodes

    def run(self):

        for node in self.document.traverse(solution_node):
            target_labelid = node.get("target_label", "")
            try:
                target_attr = self.env.sphinx_exercise_registry[target_labelid]
            except Exception:
                # target_labelid not found
                if isinstance(self.app.builder, LaTeXBuilder):
                    docname = find_parent(self.app.builder.env, node, "section")
                else:
                    docname = self.app.builder.current_docname
                docpath = self.env.doc2path(docname)
                path = docpath[: docpath.rfind(".")]
                msg = f"undefined label: {target_labelid}"
                logger.warning(msg, location=path, color="red")
                return

            # Create a reference
            refuri = self.app.builder.get_relative_uri(
                self.env.docname, target_attr.get("docname", "")
            )
            refuri += "#" + target_labelid

            # create a text for the reference node
            title = node.attributes["title"]
            newtitle = docutil_nodes.inline("", docutil_nodes.Text(title))
            reference = docutil_nodes.reference(
                "",
                "",
                internal=True,
                refuri=refuri,
                anchorname="",
                *[newtitle],
            )
            process_reference(self, reference, SOLUTION_PLACEHOLDER)
            newnode = docutil_nodes.title("")
            newnode.append(reference)
            node[0].replace_self(newnode)
            # update node
            self.env.sphinx_exercise_registry[node.get("label", "")]["node"] = node


class NumberReferenceTransform(SphinxPostTransform):
    default_priority = 1000

    def run(self):

        for node in self.document.traverse(number_reference):
            labelid = get_refuri(node)

            # If extension directive referenced
            if labelid in self.env.sphinx_exercise_registry:
                source_attr = self.env.sphinx_exercise_registry[labelid]
                source_node = source_attr.get("node", Node)
                node_title = node.get("title", "")

                # processing for nodes which have
                if "{name}" in node_title and has_math_child(source_node[0]):
                    newtitle = docutil_nodes.inline()
                    for item in node_title.split():
                        if item == "{name}":
                            # use extend instead?
                            for _ in update_title(source_node[0]):
                                newtitle += _
                        elif item == "{number}":
                            source_type = source_node.attributes["type"]
                            source_number = get_node_number(
                                self.app, source_node, source_type
                            )
                            source_num = ".".join(map(str, source_number))
                            newtitle += docutil_nodes.Text(source_num, source_num)
                        else:
                            newtitle += docutil_nodes.Text(item, item)
                        newtitle += docutil_nodes.Text(" ", " ")

                    if newtitle[len(newtitle) - 1].astext() == " ":
                        newtitle.pop()
                    node.replace(node[0], newtitle)
