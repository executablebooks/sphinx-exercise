import sphinx.addnodes as sphinx_nodes
from sphinx.transforms.post_transforms import SphinxPostTransform
from sphinx.util import logging
from sphinx.builders.latex import LaTeXBuilder
from docutils import nodes as docutil_nodes

from .utils import get_node_number, find_parent
from .nodes import (
    exercise_enumerable_node,
    solution_node,
    exercise_title,
    exercise_subtitle,
    solution_title,
)

logger = logging.getLogger(__name__)


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


class UpdateReferencesToEnumerated(SphinxPostTransform):
    """
    Check {ref} to Enumerated Nodes and Update to numref
    """

    default_priority = 5

    def run(self):

        if not hasattr(self.env, "sphinx_exercise_registry"):
            return

        for node in self.document.traverse(sphinx_nodes.pending_xref):
            if node.get("reftype") != "numref":
                target_label = node.get("reftarget")
                if target_label in self.env.sphinx_exercise_registry:
                    target = self.env.sphinx_exercise_registry[target_label]
                    target_node = target.get("node")
                    if isinstance(target_node, exercise_enumerable_node):
                        # Don't modify custom text
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


class ResolveTitlesInEnumerableExercises(SphinxPostTransform):
    """
    Resolve Titles for Enumerated Exercise Nodes
    pending_xref get's resolved with priority = 10
    """

    default_priority = 20

    def resolve_title(self, node):
        title = node.children[0]
        if isinstance(title, exercise_title):
            # Numfig will use "Exercise %s" so we just need the subtitle
            updated_title = docutil_nodes.title()
            updated_title["title"] = self.app.config.numfig_format["exercise"]
            # Parse Custom Titles
            if len(title.children) > 1:
                subtitle = title.children[1]
                if isinstance(subtitle, exercise_subtitle):
                    for child in subtitle.children:
                        updated_title += child
            updated_title.parent = title.parent
            node.children[0] = updated_title
        node.resolved_title = True
        return node

    def run(self):

        if not hasattr(self.env, "sphinx_exercise_registry"):
            return

        for node in self.document.traverse(exercise_enumerable_node):
            node = self.resolve_title(node)


class ResolveTitlesInSolutions(SphinxPostTransform):
    """
    Resolve Titles for Solutions Nodes and merge in
    the main title only from target_nodes
    """

    default_priority = 20

    def resolve_title(self, node, exercise_node):
        """ Resolve Solution Nodes """
        title = node.children[0]
        exercise_title = exercise_node.children[0]
        if isinstance(title, solution_title):
            updated_title = docutil_nodes.title()
            updated_title["title"] = "Solution"
            updated_title += build_reference_node(self.app, exercise_node)
            updated_title += docutil_nodes.Text(node.get("title") + " ")
            updated_title += exercise_title.children[0]
            # numfig captions are resolved at the writer phase so we need
            # to resolve the number for solution titles
            if isinstance(exercise_node, exercise_enumerable_node):
                node_number = get_node_number(self.app, exercise_node, "exercise")
                updated_title += docutil_nodes.Text(f" {node_number}")
            # Parse Custom Titles from Exercise
            if len(exercise_title.children) > 1:
                subtitle = exercise_title.children[1]
                if isinstance(subtitle, exercise_subtitle):
                    updated_title += docutil_nodes.Text(" ")
                    for child in subtitle.children:
                        updated_title += child
            updated_title.parent = title.parent
            node.children[0] = updated_title
        node.resolved_title = True
        return node

    def run(self):

        for node in self.document.traverse(solution_node):
            target_label = node.get("target_label")
            try:
                target = self.env.sphinx_exercise_registry[target_label]
                target_node = target.get("node")
                node = self.resolve_title(node, target_node)
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
