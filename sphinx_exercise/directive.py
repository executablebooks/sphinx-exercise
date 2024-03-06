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
    exercise_end_node,
    solution_node,
    solution_start_node,
    solution_end_node,
    exercise_title,
    exercise_subtitle,
    solution_title,
)
from docutils import nodes
from sphinx.util import logging

logger = logging.getLogger(__name__)


class SphinxExerciseBaseDirective(SphinxDirective):
    def duplicate_labels(self, label):
        """Check for duplicate labels"""

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
        title = exercise_title()
        title += nodes.Text(self.defaults["title_text"])

        # Select Node Type and Initialise
        if "nonumber" in self.options:
            node = exercise_node()
        else:
            node = exercise_enumerable_node()

        if self.name == "exercise-start":
            node.gated = True

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
            # Copy the node so that the post transforms do not modify this original state
            # Prior to Sphinx 6.1.0, the doctree was not cached, and Sphinx loaded a new copy
            # c.f. https://github.com/sphinx-doc/sphinx/commit/463a69664c2b7f51562eb9d15597987e6e6784cd
            "node": node.deepcopy(),
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

    Notes:
    ------
    Checking for target reference is done in post_transforms for Solution Titles
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
    solution_node = solution_node

    def run(self) -> List[Node]:
        self.defaults = {"title_text": "Solution to"}
        target_label = self.arguments[0]
        self.serial_number = self.env.new_serialno()

        # Initialise Registry if Required
        if not hasattr(self.env, "sphinx_exercise_registry"):
            self.env.sphinx_exercise_registry = {}

        # Parse :hide-solutions: option
        if self.env.app.config.hide_solutions:
            return []

        # Construct Title
        title = solution_title()
        title += nodes.Text(self.defaults["title_text"])

        # State Parsing
        section = nodes.section(ids=["solution-content"])
        self.state.nested_parse(self.content, self.content_offset, section)

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

        # Construct Node
        node = self.solution_node()
        node += title
        node += section
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

        self.add_name(node)
        self.env.sphinx_exercise_registry[label] = {
            "type": self.name,
            "docname": self.env.docname,
            "node": node,
        }

        if node.get("hidden", bool):
            return []

        return [node]


# Gated Directives


class ExerciseStartDirective(ExerciseDirective):
    """
    A gated directive for exercises

    .. exercise:: <subtitle> (optional)
       :label:
       :class:
       :nonumber:
       :hidden:

    This class is a child of ExerciseDirective so it supports
    all the same options as the base exercise node
    """

    name = "exercise-start"

    def run(self):
        # Initialise Gated Registry
        if not hasattr(self.env, "sphinx_exercise_gated_registry"):
            self.env.sphinx_exercise_gated_registry = {}
        gated_registry = self.env.sphinx_exercise_gated_registry
        docname = self.env.docname
        if docname not in gated_registry:
            gated_registry[docname] = {
                "start": [],
                "end": [],
                "sequence": [],
                "msg": [],
                "type": "exercise",
            }
        gated_registry[self.env.docname]["start"].append(self.lineno)
        gated_registry[self.env.docname]["sequence"].append("S")
        gated_registry[self.env.docname]["msg"].append(
            f"{self.name} at line: {self.lineno}"
        )
        # Run Parent Methods
        return super().run()


class ExerciseEndDirective(SphinxDirective):
    """
    A simple gated directive to mark end of an exercise

    .. exercise-end::
    """

    name = "exercise-end"

    def run(self):
        # Initialise Gated Registry
        if not hasattr(self.env, "sphinx_exercise_gated_registry"):
            self.env.sphinx_exercise_gated_registry = {}
        gated_registry = self.env.sphinx_exercise_gated_registry
        docname = self.env.docname
        if docname not in gated_registry:
            gated_registry[docname] = {
                "start": [],
                "end": [],
                "sequence": [],
                "msg": [],
                "type": "exercise",
            }
        gated_registry[self.env.docname]["end"].append(self.lineno)
        gated_registry[self.env.docname]["sequence"].append("E")
        gated_registry[self.env.docname]["msg"].append(
            f"{self.name} at line: {self.lineno}"
        )
        return [exercise_end_node()]


class SolutionStartDirective(SolutionDirective):
    """
    A gated directive for solution

    .. solution-start:: <exercise-reference>
       :label:
       :class:
       :hidden:

    This class is a child of SolutionDirective so it supports
    all the same options as the base solution node
    """

    name = "solution-start"
    solution_node = solution_start_node

    def run(self):
        # Initialise Gated Registry (if required)
        if not hasattr(self.env, "sphinx_exercise_gated_registry"):
            self.env.sphinx_exercise_gated_registry = {}
        gated_registry = self.env.sphinx_exercise_gated_registry
        docname = self.env.docname
        if docname not in gated_registry:
            gated_registry[docname] = {
                "start": [],
                "end": [],
                "sequence": [],
                "msg": [],
                "type": "solution",
            }
        gated_registry[self.env.docname]["start"].append(self.lineno)
        gated_registry[self.env.docname]["sequence"].append("S")
        gated_registry[self.env.docname]["msg"].append(
            f"solution-start at line: {self.lineno}"
        )
        # Run Parent Methods
        return super().run()


class SolutionEndDirective(SphinxDirective):
    """
    A simple gated directive to mark end of solution

    .. solution-end::
    """

    name = "solution-end"

    def run(self):
        # Initialise Gated Registry (if required)
        if not hasattr(self.env, "sphinx_exercise_gated_registry"):
            self.env.sphinx_exercise_gated_registry = {}
        gated_registry = self.env.sphinx_exercise_gated_registry
        docname = self.env.docname
        if docname not in gated_registry:
            gated_registry[docname] = {
                "start": [],
                "end": [],
                "sequence": [],
                "msg": [],
                "type": "solution",
            }
        gated_registry[self.env.docname]["end"].append(self.lineno)
        gated_registry[self.env.docname]["sequence"].append("E")
        gated_registry[self.env.docname]["msg"].append(
            f"solution-end at line: {self.lineno}"
        )
        return [solution_end_node()]
