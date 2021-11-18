import sphinx.addnodes as sphinx_nodes
from sphinx.transforms.post_transforms import SphinxPostTransform
from sphinx.util import logging
from sphinx.builders.latex import LaTeXBuilder
from docutils import nodes as docutil_nodes

from .utils import get_node_number, get_refuri, find_parent
from .nodes import (
    exercise_enumerable_node,
    solution_node,
    exercise_title,
    exercise_subtitle,
    solution_title,
    solution_subtitle,
)

logger = logging.getLogger(__name__)


# Resolver Functions


def resolve_enumerated_exercise_node_title(app, node):
    title = node.children[0]
    if isinstance(title, exercise_title):
        node_number = get_node_number(app, node, "exercise")
        updated_title = exercise_title()
        if title.default_title():
            title_text = title.children[0].astext() + f" {node_number}"
            updated_title += docutil_nodes.Text(title_text)
        else:
            updated_title += title.children[0]
        updated_title += title.children[1:]
        node.children[0] = updated_title
    node["title"] = title_text  # TODO: Include subtitle text?
    node.resolved_title = True
    return node


def build_reference_node(app, target_node):
    refuri = app.builder.get_relative_uri(
        app.env.docname, target_node.get("docname", "")
    )
    refuri += "#" + target_node.get("label")
    reference = docutil_nodes.reference(
        "",
        "",
        internal=True,
        refuri=refuri,
        anchorname="",
    )
    return reference


def resolve_solution_node_title(app, node):
    """ Resolve Solution Nodes """
    exercise_target = app.env.sphinx_exercise_registry[node.get("target_label")]["node"]
    title = node.children[0]
    if isinstance(title, solution_title):
        new_title = solution_title()
        new_title += build_reference_node(app, exercise_target)
        new_title += title.children[0]  # Add default text
        # Migrate Target Title Nodes
        target_title = exercise_target.children[0]
        if not isinstance(target_title, exercise_title):
            return node
        new_title += docutil_nodes.Text(" ")
        for title_element in target_title.children:
            if isinstance(title_element, exercise_subtitle):
                new_title += docutil_nodes.Text(" (")
                subtitle = solution_subtitle()
                subtitle += title_element.children
                new_title += subtitle
                new_title += docutil_nodes.Text(")")
            else:
                new_title += title_element
        node.children[0] = new_title
    node.resolved_title = True
    return node


class ReferenceLabelTextPostTransform(SphinxPostTransform):

    default_priority = 1

    def update_label_text(self, node, target_node):
        if node.get("refexplicit"):
            literal = node.children[0]
            label = literal.children[0]
            literal.children = []
            literal += docutil_nodes.Text("|label| ")
            literal += label
            node.children[0] = literal
        return node

    def run(self, **kwargs):

        if not hasattr(self.env, "sphinx_exercise_registry"):
            return

        for node in self.document.traverse(sphinx_nodes.pending_xref):
            target_label = node.get("reftarget")
            try:
                target = self.env.sphinx_exercise_registry[target_label]
                target_node = target.get("node")
                if (
                    isinstance(target_node, exercise_enumerable_node)
                    and not target_node.resolved_title
                ):
                    target_node = resolve_enumerated_exercise_node_title(
                        self.app, target_node
                    )
                    self.env.sphinx_exercise_registry[target_label][
                        "node"
                    ] = target_node
                if (
                    isinstance(target_node, solution_node)
                    and not target_node.resolved_title
                ):
                    target_node = resolve_solution_node_title(self.app, target_node)
                    self.env.sphinx_exercise_registry[target_label][
                        "node"
                    ] = target_node
                node = self.update_label_text(node, target_node)
            except Exception:
                if isinstance(self.app.builder, LaTeXBuilder):
                    docname = find_parent(self.app.builder.env, node, "section")
                else:
                    docname = self.app.builder.current_docname
                docpath = self.env.doc2path(docname)
                path = docpath[: docpath.rfind(".")]
                msg = f"undefined label: {target_label}"
                logger.warning(msg, location=path, color="red")
                return


class ResolveTitlesInExercises(SphinxPostTransform):
    """
    Resolve Titles for Enumerated Exercise Nodes

    pending_xref get's resolved with priority = 10
    """

    default_priority = 20

    def run(self):

        if not hasattr(self.env, "sphinx_exercise_registry"):
            return

        for node in self.document.traverse(exercise_enumerable_node):
            label = node.get("label")
            # TODO: The registry can contain resolved nodes whcih could be
            # used instead of updating the `node` in the doctree
            node = resolve_enumerated_exercise_node_title(self.app, node)
            self.env.sphinx_exercise_registry[label]["node"] = node


class ResolveTitlesInSolutions(SphinxPostTransform):
    """
    Resolve Titles for Solutions Nodes and merge in
    the main title only from target_nodes
    """

    default_priority = 20

    def run(self):

        for node in self.document.traverse(solution_node):
            target_label = node.get("target_label")
            try:
                target = self.env.sphinx_exercise_registry[target_label]
                target_node = target.get("node")
                if (
                    isinstance(target_node, exercise_enumerable_node)
                    and not target_node.resolved_title
                ):
                    target_node = resolve_enumerated_exercise_node_title(
                        self.app, target_node
                    )
                    self.env.sphinx_exercise_registry[target_label][
                        "node"
                    ] = target_node
                node = resolve_solution_node_title(self.app, node)
            except Exception:
                if isinstance(self.app.builder, LaTeXBuilder):
                    docname = find_parent(self.app.builder.env, node, "section")
                else:
                    docname = self.app.builder.current_docname
                docpath = self.env.doc2path(docname)
                path = docpath[: docpath.rfind(".")]
                msg = f"undefined label: {target_label}"
                logger.warning(msg, location=path, color="red")
                return


class ReferenceTextPostTransform(SphinxPostTransform):
    """
    This transform processes all references to
    exercise nodes to adjust titles.

    Note: Adjusting labels without text:

    As the XML tree for _unenum_ref_mathtitle

    <section ids="unenum-ref-mathtitle" names="_unenum_ref_mathtitle">
    <title>
        _unenum_ref_mathtitle
    <paragraph>
        This is a reference
        <inline classes="xref std std-ref">
            unen-exc-label-math
        .
    <paragraph>
        This is a second reference
        <reference internal="True" refuri="_unenum_mathtitle_label.html#unen-exc-label-math">  # noqa: #501
            <inline classes="std std-ref">
                some text
    """

    default_priority = 21

    def update_label_text(self, node, target_node):

        # exclide already labelled nodes from title processing
        if "|label|" in node.astext():
            inline = node.children[0]
            inline.children[0] = docutil_nodes.Text(
                inline.children[0].astext().replace("|label| ", "")
            )
            return node

        if node.children == []:
            return node

        inline = node.children[0]
        inline.children = []

        # Add title text from target node
        title = target_node.children[0]
        for title_element in title.children:
            if isinstance(target_node, solution_node) and isinstance(
                title_element, docutil_nodes.subtitle
            ):
                inline += title_element.children
            elif isinstance(title_element, docutil_nodes.subtitle):
                inline += docutil_nodes.Text(": ")
                inline += title_element.children
            else:
                inline += title_element

        node.children[0] = inline
        return node

    def run(self, **kwargs):

        if not hasattr(self.env, "sphinx_exercise_registry"):
            return

        for node in self.document.traverse(docutil_nodes.reference):
            target_label = get_refuri(node)
            try:
                target = self.env.sphinx_exercise_registry[target_label]
                target_node = target.get("node")
                if (
                    isinstance(target_node, exercise_enumerable_node)
                    and not target_node.resolved_title
                ):
                    target_node = resolve_enumerated_exercise_node_title(
                        self.app, target_node
                    )
                    self.env.sphinx_exercise_registry[target_label][
                        "node"
                    ] = target_node
                if (
                    isinstance(target_node, solution_node)
                    and not target_node.resolved_title
                ):
                    target_node = resolve_solution_node_title(self.app, target_node)
                    self.env.sphinx_exercise_registry[target_label][
                        "node"
                    ] = target_node
                node = self.update_label_text(node, target_node)
            except Exception:
                if isinstance(self.app.builder, LaTeXBuilder):
                    docname = find_parent(self.app.builder.env, node, "section")
                else:
                    docname = self.app.builder.current_docname
                docpath = self.env.doc2path(docname)
                path = docpath[: docpath.rfind(".")]
                msg = f"undefined label: {target_label}"
                logger.warning(msg, location=path, color="red")
                return
