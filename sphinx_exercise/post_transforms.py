import sphinx.addnodes as sphinx_nodes
from sphinx.transforms.post_transforms import SphinxPostTransform
from sphinx.util import logging
from sphinx.builders.latex import LaTeXBuilder
from docutils import nodes as docutil_nodes

from ._compat import findall
from .utils import get_node_number, find_parent
from .nodes import (
    exercise_enumerable_node,
    solution_node,
    exercise_title,
    exercise_subtitle,
    solution_title,
    is_exercise_node,
    exercise_latex_number_reference,
)

logger = logging.getLogger(__name__)


def build_reference_node(app, target_node):
    """
    Builds a docutil.nodes.reference object
    to a given target_node.
    """
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


class UpdateReferencesToEnumerated(SphinxPostTransform):
    """
        Updates all :ref: to :numref: if used when referencing
        an enumerated exercise node.
    ]"""

    default_priority = 5

    def run(self):

        if not hasattr(self.env, "sphinx_exercise_registry"):
            return

        for node in findall(self.document, sphinx_nodes.pending_xref):
            if node.get("reftype") != "numref":
                target_label = node.get("reftarget")
                if target_label in self.env.sphinx_exercise_registry:
                    target = self.env.sphinx_exercise_registry[target_label]
                    target_node = target.get("node")
                    if isinstance(target_node, exercise_enumerable_node):
                        # Don't Modify Custom Text
                        if node.get("refexplicit"):
                            continue
                        node["reftype"] = "numref"
                        # Get Metadata from Inline
                        inline = node.children[0]
                        classes = inline["classes"]
                        classes.remove("std-ref")
                        classes.append("std-numref")
                        # Construct a Literal Node
                        literal = docutil_nodes.literal()
                        literal["classes"] = classes
                        literal.children += inline.children
                        node.children[0] = literal


class ResolveTitlesInExercises(SphinxPostTransform):
    """
    Resolve Titles for Exercise Nodes and Enumerated Exercise Nodes
    for:
        1. Numbering
        2. Formatting Title and Subtitles into docutils.title node
    """

    default_priority = 20

    def resolve_title(self, node):
        title = node.children[0]
        if isinstance(title, exercise_title):
            updated_title = docutil_nodes.title()
            if isinstance(node, exercise_enumerable_node):
                # Numfig (HTML) will use "Exercise %s" so we just need the subtitle
                if self.app.builder.format == "latex":
                    # Resolve Title
                    node_number = get_node_number(self.app, node, "exercise")
                    title_text = self.app.config.numfig_format["exercise"] % node_number
                    updated_title += docutil_nodes.Text(title_text)
                updated_title["title"] = self.app.config.numfig_format["exercise"]
            else:
                # Use default text "Exercise"
                updated_title += title.children[0]
            # Parse Custom Titles
            if len(title.children) > 1:
                subtitle = title.children[1]
                if isinstance(subtitle, exercise_subtitle):
                    updated_title += docutil_nodes.Text(" (")
                    for child in subtitle.children:
                        updated_title += child
                    updated_title += docutil_nodes.Text(")")
            updated_title.parent = title.parent
            node.children[0] = updated_title
        node.resolved_title = True
        return node

    def run(self):

        if not hasattr(self.env, "sphinx_exercise_registry"):
            return

        for node in findall(self.document, is_exercise_node):
            node = self.resolve_title(node)


# Solution Nodes


def resolve_solution_title(app, node, exercise_node):
    """
    Resolve Titles for Solution Nodes for:

        1. Numbering of Target Exercise Nodes
        2. Formatting Title and Subtitles into docutils.title node
        3. Ensure mathjax is triggered for pages that include path
           in titles inherited from Exercise Node

    Note: Setup as a resolver function in case we need to resolve titles
    in references to solution nodes.
    """

    title = node.children[0]
    exercise_title = exercise_node.children[0]
    if isinstance(title, solution_title):
        entry_title_text = node.get("title")
        updated_title_text = " " + exercise_title.children[0].astext()
        if isinstance(exercise_node, exercise_enumerable_node):
            node_number = get_node_number(app, exercise_node, "exercise")
            updated_title_text += f" {node_number}"
        # New Title Node
        updated_title = docutil_nodes.title()
        wrap_reference = build_reference_node(app, exercise_node)
        wrap_reference += docutil_nodes.Text(updated_title_text)
        node["title"] = entry_title_text + updated_title_text
        # Parse Custom Titles from Exercise
        if len(exercise_title.children) > 1:
            subtitle = exercise_title.children[1]
            if isinstance(subtitle, exercise_subtitle):
                wrap_reference += docutil_nodes.Text(" (")
                for child in subtitle.children:
                    if isinstance(child, docutil_nodes.math):
                        # Ensure mathjax is loaded for pages that only contain
                        # references to nodes that contain math
                        domain = app.env.get_domain("math")
                        domain.data["has_equations"][app.env.docname] = True
                    wrap_reference += child
                wrap_reference += docutil_nodes.Text(")")
        updated_title += docutil_nodes.Text(entry_title_text)
        updated_title += wrap_reference
        updated_title.parent = title.parent
        node.children[0] = updated_title
    node.resolved_title = True
    return node


class ResolveTitlesInSolutions(SphinxPostTransform):

    default_priority = 21

    def run(self):

        if not hasattr(self.env, "sphinx_exercise_registry"):
            return

        # Update Solution Directives
        for node in findall(self.document, solution_node):
            label = node.get("label")
            target_label = node.get("target_label")
            try:
                target = self.env.sphinx_exercise_registry[target_label]
                target_node = target.get("node")
                node = resolve_solution_title(self.app, node, target_node)
                # Update Registry
                self.env.sphinx_exercise_registry[label]["node"] = node
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


class ResolveLinkTextToSolutions(SphinxPostTransform):
    """
    Resolve Titles for Solutions Nodes and merge in
    the main title only from target_nodes
    """

    default_priority = 22

    def run(self):

        if not hasattr(self.env, "sphinx_exercise_registry"):
            return

        # Update Solution References
        for node in findall(self.document, docutil_nodes.reference):
            refid = node.get("refid")
            if refid in self.env.sphinx_exercise_registry:
                target = self.env.sphinx_exercise_registry[refid]
                target_node = target.get("node")
                if self.app.builder.format == "latex":
                    if isinstance(target_node, exercise_enumerable_node):
                        new_node = exercise_latex_number_reference()
                        new_node.parent = node.parent
                        new_node.attributes = node.attributes
                        for child in node.children:
                            new_node += child
                        node.replace_self(new_node)
                if isinstance(target_node, solution_node):
                    # TODO: Check if this condition is required?
                    if not target_node.resolved_title:
                        exercise_label = target_node.get("target_label")
                        exercise_target = self.env.sphinx_exercise_registry[
                            exercise_label
                        ]  # noqa: E501
                        exercise_node = exercise_target.get("node")
                        target_node = resolve_solution_title(
                            self.app, target_node, exercise_node
                        )  # noqa: E501
                    title_text = target_node.children[0].astext()
                    inline = node.children[0]
                    inline.children = []
                    inline += docutil_nodes.Text(title_text)
                    node.children[0] = inline
