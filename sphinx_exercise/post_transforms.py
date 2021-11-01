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
    # is_extension_node,
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


def process_math_placeholder(node, source_node):
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
                node = process_math_placeholder(
                    node, source_node
                )  # CHECK: this will never run

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
                        pass
                        # text = target_attr.get("title", "").astext()
            else:
                node = process_math_placeholder(
                    node, source_node
                )  # CHECK: this will never run


# Transforms


class ReferenceTransform(SphinxPostTransform):
    default_priority = 998

    def process_reference(self, node, label, default_title=""):
        """
        Processing reference nodes in the document to:
        1. set title text
        """

        # Process Sources
        src = self.env.sphinx_exercise_registry[label]
        source_node = src["node"]

        # Source Solution Node
        if is_solution_node(source_node):
            target_label = source_node.attributes.get("target_label", "")
            target_node = self.env.sphinx_exercise_registry[target_label]
            default_title = node.astext() + target_node["title"].astext()
        else:
            target_label = source_node.attributes.get("label", "")

        if target_label == "":
            import pdb

            pdb.set_trace()

        # Process Targets
        target = self.env.sphinx_exercise_registry[target_label]
        target_node = target["node"]

        # Exercise Node
        if is_exercise_node(target_node):
            if default_title:
                number = get_node_number(self.app, target_node, "exercise")
                node.insert(len(node[0]), docutil_nodes.Text(" Exercise " + number))
                return
            else:
                node = process_math_placeholder(node, source_node)

        # Exercise Unenumerable Node
        if is_exercise_unenumerable_node(target_node):
            if default_title:
                if target.get("title"):
                    if has_math_child(target_node[0]):
                        # Cast title node to inline node
                        inline_title = docutil_nodes.inline()
                        if is_solution_node(target_node):
                            inline_title.children = [
                                docutil_nodes.Text("Solution to" + " ")
                            ] + target["title"].children
                        else:
                            inline_title.children = target["title"].children
                        node.replace(node[0], inline_title)
                    else:
                        pass
                        # text = target.get("title", "").astext()
            else:
                node = process_math_placeholder(node, source_node)

    def process_number_reference(self, reference_node, refuri):
        """
        Post process number references which is a node provided
        sphinx.addnodes.number_reference

        reference_node: nodes.number_reference
        """

        # Fetch Target Object from Registry
        target = self.env.sphinx_exercise_registry[refuri]
        target_title = target.get("title")

        reference_title = reference_node.get("title")

        if "{name}" in reference_title and has_math_child(target_title):
            updated_title = docutil_nodes.inline()
            for token in reference_title.split(" "):
                if token == "{name}":
                    token = target_title.children
                elif token == "{number}":
                    target_number = get_node_number(
                        self.app, target.get("node"), target.get("type")
                    )
                    # target_number = ".".join(map(str, target_number))  # TODO: review
                    token = docutil_nodes.Text(target_number)
                else:
                    token = docutil_nodes.Text(token)
                updated_title += token
                updated_title += docutil_nodes.Text(" ")
            # Remove trailing white space
            _ = updated_title.pop()
            # Replace reference title
            reference_node.replace(reference_node[0], updated_title)

    def run(self):

        if not hasattr(self.env, "sphinx_exercise_registry"):
            return

        for node in self.document.traverse(docutil_nodes.reference):
            refuri = get_refuri(node)
            if refuri in self.env.sphinx_exercise_registry:
                if isinstance(node, number_reference):
                    self.process_number_reference(node, refuri)
                else:
                    self.process_reference(node, refuri)
            else:
                logger.warn(
                    f"Reference label {refuri} cannot be found in the sphinx_exercise registry"  # noqa: E501
                )


class SolutionTransform(SphinxPostTransform):
    """ Post processing for solution directives """

    # Needs to run after ReferenceTransform
    default_priority = 999

    def construct_reference(self):
        pass

    def run(self):

        for node in self.document.traverse(solution_node):
            target_label = node.get("target_label")
            try:
                target = self.env.sphinx_exercise_registry[target_label]
            except Exception:
                if isinstance(self.app.builder, LaTeXBuilder):
                    docname = find_parent(self.app.builder.env, node, "section")
                else:
                    docname = self.app.builder.current_docname
                docpath = self.env.doc2path(docname)
                path = docpath[: docpath.rfind(".")]
                msg = f"Undefined label: {target_label}"
                logger.warning(msg, location=path, color="red")
                return

            # Create a reference
            refuri = self.app.builder.get_relative_uri(
                self.env.docname, target.get("docname", "")
            )
            refuri += "#" + target_label

            # Create new Title
            if isinstance(node.children[0], docutil_nodes.title):
                updated_title = node.children[0]
            else:
                updated_title = docutil_nodes.title(node.attributes("title"))

            # merge with title from target
            target_title = target.get("title")
            updated_title += docutil_nodes.Text(" ")
            updated_title += target_title.children

            reference = docutil_nodes.reference(
                "",
                "",
                internal=True,
                refuri=refuri,
                anchorname="",
            )

            # WORKING HERE
            # TODO: Commit this work and introduce XML tests to track
            # state of the doctree on master then merge that in here
            # as a reference set

            reference.children = [updated_title]

            process_reference(self, reference, SOLUTION_PLACEHOLDER)

            # TODO: Is the reference in the title of the solution node?
            # updated_title.children.append(reference)

            # Update Node
            if isinstance(node[0], docutil_nodes.title):
                node[0] = updated_title
            node.attributes["title"] = updated_title.astext()

            # Wrap node in a reference node
            # TODO: add in reference node
            # node.append(reference)

            # Update Registry
            label = node.get("label")
            self.env.sphinx_exercise_registry[label]["node"] = node
