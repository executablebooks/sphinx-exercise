"""
sphinx_exercise.directive
~~~~~~~~~~~~~~~~~~~~~~~~~

A custom Sphinx Directive

:copyright: Copyright 2020 by the QuantEcon team, see AUTHORS
:licences: see LICENSE for details
"""
from typing import List
from docutils.nodes import Node

from sphinx.util.docutils import SphinxDirective
from docutils.parsers.rst import directives
from .nodes import (
    exercise_node,
    exercise_enumerable_node,
    solution_node,
    exercise_title,
    exercise_subtitle,
)
from docutils import nodes
from sphinx.util import logging

logger = logging.getLogger(__name__)


class SphinxExerciseBaseDirective(SphinxDirective):
    def duplicate_labels(self, label):
        """ Check for duplicate labels """

        if not label == "" and label in self.env.sphinx_exercise_registry.keys():
            docpath = self.env.doc2path(self.env.docname)
            path = docpath[: docpath.rfind(".")]
            other_path = self.env.doc2path(
                self.env.sphinx_exercise_registry[label]["docname"]
            )
            msg = f"duplicate label: {label}; other instance in {other_path}"
            logger.warning(msg, location=path, color="red")
            return True

        return False


class ExerciseDirective(SphinxExerciseBaseDirective):
    """
    An exercise directive

    .. exercise:: <subtitle> (optional)
       :label:
       :class:
       :nonumber:
       :hidden:

    Arguments
    ---------
    subtitle : str (optional)
            Specify a custom subtitle to add to the exercise output

    Parameters:
    -----------
    label : str,
            A unique identifier for your exercise that you can use to reference
            it with {ref} and {numref}
    class : str,
            Value of the exercise’s class attribute which can be used to add custom CSS
    nonumber :  boolean (flag),
                Turns off exercise auto numbering.
    hidden  :   boolean (flag),
                Removes the directive from the final output.

    Notes
    -----
    self.defaults['title_text'] is always added to the node even if numfig is used
    for compatibility with numfig generating numbered titles. Therefore there is a
    post_transform: RemoveDefaultTitleEnumeratedExerciseNodes to remove them to avoid
    duplicate titles prior to writing HTML / LaTeX
    """

    name = "exercise"
    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {
        "label": directives.unchanged_required,
        "class": directives.class_option,
        "nonumber": directives.flag,
        "hidden": directives.flag,
    }

    def run(self) -> List[Node]:

        self.defaults = {"title_text": "Exercise"}
        self.serial_number = self.env.new_serialno()

        # Initialise Registry (if needed)
        if not hasattr(self.env, "sphinx_exercise_registry"):
            self.env.sphinx_exercise_registry = {}

        # Construct Title
        # title = nodes.title()
        title = exercise_title()
        title += nodes.Text("Exercise")

        # Select Node Type and Initialise
        if "nonumber" in self.options:
            node = exercise_node()
        else:
            node = exercise_enumerable_node()

        # Parse custom subtitle option
        if self.arguments != []:
            subtitle = exercise_subtitle()
            subtitle_text = f"{self.arguments[0]}"
            subtitle_nodes, _ = self.state.inline_text(subtitle_text, self.lineno)
            for subtitle_node in subtitle_nodes:
                subtitle += subtitle_node
            title += subtitle

        # State Parsing
        section = nodes.section(ids=["exercise-content"])
        self.state.nested_parse(self.content, self.content_offset, section)

        # Construct a label
        label = self.options.get("label", "")
        if label:
            # TODO: Check how :noindex: is used here
            self.options["noindex"] = False
        else:
            self.options["noindex"] = True
            label = f"{self.env.docname}-exercise-{self.serial_number}"

        # Check for Duplicate Labels
        # TODO: Should we just issue a warning rather than skip content?
        if self.duplicate_labels(label):
            return []

        # Collect Classes
        classes = [f"{self.name}"]
        if self.options.get("class"):
            classes.extend(self.options.get("class"))

        self.options["name"] = label

        # Construct Node
        node += title
        node += section
        node["classes"].extend(classes)
        node["ids"].append(label)
        node["label"] = label
        node["docname"] = self.env.docname
        node["title"] = self.defaults["title_text"]
        node["type"] = self.name
        node["hidden"] = True if "hidden" in self.options else False
        node["serial_number"] = self.serial_number
        node.document = self.state.document

        self.add_name(node)
        self.env.sphinx_exercise_registry[label] = {
            "type": self.name,
            "docname": self.env.docname,
            "node": node,
            "title": title,  # save title node to registry for use by transforms
            "hidden": node.get("hidden", bool),
        }

        # TODO: Could tag this as Hidden to prevent the cell showing
        # rather than removing content
        # https://github.com/executablebooks/sphinx-jupyterbook-latex/blob/8401a27417d8c2dadf0365635bd79d89fdb86550/sphinx_jupyterbook_latex/transforms.py#L108
        if node.get("hidden", bool):
            return []

        return [node]


class SolutionDirective(SphinxExerciseBaseDirective):
    """
    A solution directive

    .. solution:: <exercise-reference>
       :label:
       :class:
       :hidden:

    Arguments
    ---------
    exercise-reference : str
                        Specify a linked exercise by label

    Parameters:
    -----------
    label : str,
            A unique identifier for your exercise that you can use to reference
            it with {ref} and {numref}
    class : str,
            Value of the exercise’s class attribute which can be used to add custom CSS
    hidden  :   boolean (flag),
                Removes the directive from the final output.
    """

    name = "solution"
    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        "label": directives.unchanged_required,
        "class": directives.class_option,
        "hidden": directives.flag,
    }

    def run(self) -> List[Node]:

        target_label = self.arguments[0]
        self.serial_number = self.env.new_serialno()

        if not hasattr(self.env, "sphinx_exercise_registry"):
            self.env.sphinx_exercise_registry = {}

        # Parse hide-solutions option
        if self.env.app.config.hide_solutions:
            return []

        # Set Title Text
        title_text = "Solution to {name}"
        textnodes, messages = self.state.inline_text(title_text, self.lineno)
        title = nodes.title(title_text, "", *textnodes)

        # State Parsing
        section = nodes.section(ids=["solution-content"])
        self.state.nested_parse(self.content, self.content_offset, section)

        # Initialise Node
        node = solution_node()
        node += title
        node += section

        # Fetch Label or Generate One
        label = self.options.get("label", "")
        if label:
            # TODO: Check how :noindex: is used here
            self.options["noindex"] = False
        else:
            self.options["noindex"] = True
            label = f"{self.env.docname}-solution-{self.serial_number}"

        # Check for duplicate labels
        # TODO: Should we just issue a warning rather than skip content?
        if self.duplicate_labels(label):
            return []

        self.options["name"] = label

        # Collect Classes
        classes = [f"{self.name}"]
        if self.options.get("class"):
            classes += self.options.get("class")

        # Set node attributes
        node["target_label"] = target_label
        node["classes"].extend(classes)
        node["ids"].append(label)
        node["label"] = label
        node["docname"] = self.env.docname
        node["title"] = title.astext()
        node["type"] = self.name
        node["hidden"] = True if "hidden" in self.options else False
        node["serial_number"] = self.serial_number
        node.document = self.state.document

        # TODO: Check for target label in env.sphinx_exercise_registry registry
        # as exercise should always precede a solution.
        # Otherwise leave this to the SolutionPosTransform in post_transforms.

        self.add_name(node)
        self.env.sphinx_exercise_registry[label] = {
            "type": self.name,
            "docname": self.env.docname,
            "node": node,
            "title": title,  # save title node to registry for use by transforms
            "hidden": node.get("hidden", bool),
        }

        if node.get("hidden", bool):
            return []

        return [node]
