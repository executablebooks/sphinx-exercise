from sphinx.transforms.post_transforms import SphinxPostTransform
from sphinx.util import logging
from sphinx.builders.latex import LaTeXBuilder
from docutils import nodes as docutil_nodes
from docutils.nodes import Node

from .utils import get_node_number, get_refuri, has_math_child, find_parent
from .nodes import (
    exercise_node,
    exercise_enumerable_node,
    solution_node,
    exercise_title,
    exercise_subtitle,
    is_solution_node,
    is_exercise_node,
    is_exercise_enumerable_node,
)

logger = logging.getLogger(__name__)


# Variables TODO: centralise these variables

SOLUTION_PLACEHOLDER = "Solution to"
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


# Post Transforms


class ReferenceTextPostTransform(SphinxPostTransform):
    """
    This transform processes all references to
    exercise nodes to adjust titles.
    """

    default_priority = 20

    def run(self, **kwargs):

        if not hasattr(self.env, "sphinx_exercise_registry"):
            return

        for node in self.document.traverse(docutil_nodes.reference):
            ref_target = get_refuri(node)
            if ref_target in self.env.sphinx_exercise_registry:
                # Parse Target Nodes and Construct Title
                target = self.env.sphinx_exercise_registry[ref_target]
                target_node = target.get("node")
                target_node_number = get_node_number(
                    self.app, target.get("node"), target.get("type")
                )
                if isinstance(target_node, exercise_enumerable_node):
                    # Update for numfig Format
                    target_title = target.get("title")
                    if target_title.default_title():
                        updated_title = (
                            target_title.children[0].astext() + f" {target_node_number}"
                        )
                    else:
                        updated_title = target_title.astext()
                    updated_title = docutil_nodes.Text(updated_title)
                    subtitles = [docutil_nodes.Text(": ")]
                    for child in target_title.children:
                        if isinstance(child, exercise_subtitle):
                            subtitles.append(child)
                    # Update reference inline node with updated_title
                    inline_node = node.children[0]
                    inline_node.children = []
                    inline_node += updated_title
                    node.children[0] = inline_node
                    # Update reference inline node with subtitles
                    if len(subtitles) > 1:
                        for subtitle in subtitles:
                            node += subtitle
                elif isinstance(target_node, exercise_node):
                    pass
                elif isinstance(target_node, solution_node):
                    pass


class ResolveTitlesInExercises(SphinxPostTransform):
    """
    Resolve Titles for Enumerated Exercise Nodes
    """

    default_priority = 21

    def update_enumerated_title(self, title, node_number):
        """update enumerate title resolved by numfig"""
        updated_title = exercise_title()
        if title.default_title():
            title_text = title.children[0].astext() + f" {node_number}"
            updated_title += docutil_nodes.Text(title_text)
        else:
            updated_title += title.children[0]
        updated_title += title.children[1:]
        return updated_title

    def run(self):

        if not hasattr(self.env, "sphinx_exercise_registry"):
            return

        for node in self.document.traverse(exercise_enumerable_node):
            title = node.children[0]
            if isinstance(title, exercise_title):
                node_number = get_node_number(self.app, node, node.get("type"))
                updated_title = self.update_enumerated_title(title, node_number)
                node.children[0] = updated_title


class SolutionTransform(SphinxPostTransform):
    """ Post processing for solution directives """

    # Needs to run after ReferenceTransform
    default_priority = 999

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

            # Exercise Enumerable Node
            if is_exercise_enumerable_node(target_node):
                if default_title:
                    # number = get_node_number(self.app, target_node, "exercise")
                    # node.insert(len(node[0]), docutil_nodes.Text(" Exercise " + number)) # noqa: E501
                    return
                else:
                    node = process_math_placeholder(
                        node, source_node
                    )  # CHECK: this will never run

            # ExerciseNode
            if is_exercise_node(target_node):
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

            self.process_reference(reference, SOLUTION_PLACEHOLDER)

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
