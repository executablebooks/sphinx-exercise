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
from .nodes import exercise_node, exercise_unenumerable_node, solution_node
from docutils import nodes
from sphinx.util import logging

logger = logging.getLogger(__name__)


class ExerciseDirective(SphinxDirective):
    """ An exercise directive """

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
        env = self.env
        typ = self.name
        serial_no = env.new_serialno()

        if not hasattr(env, "sphinx_exercise_registry"):
            env.sphinx_exercise_registry = {}

        # Collect Classes  TODO: simplify this?
        classes, class_name = [typ], self.options.get("class", "")
        if class_name:
            classes.extend(class_name)

        # Set Title Text
        title_text = "Exercise"
        if self.arguments != []:
            title_text = f"({self.arguments[0]})"

        # State Parsing
        section = nodes.section(ids=["exercise-content"])
        textnodes, messages = self.state.inline_text(title_text, self.lineno)
        self.state.nested_parse(self.content, self.content_offset, section)

        # Select Node Type and Intialise
        if "nonumber" in self.options:
            node = exercise_unenumerable_node()
        else:
            node = exercise_node()

        node += nodes.title(title_text, "", *textnodes)
        node += section

        # Construct a label
        label = self.options.get("label", "")
        if label:
            self.options["noindex"] = False
        else:
            self.options["noindex"] = True
            label = f"{env.docname}-exercise-{serial_no}"

        # Check for Duplicate Labels
        if not label == "" and label in env.sphinx_exercise_registry.keys():
            docpath = env.doc2path(env.docname)
            path = docpath[: docpath.rfind(".")]
            other_path = env.doc2path(env.sphinx_exercise_registry[label]["docname"])
            msg = f"duplicate label: {label}; other instance in {other_path}"
            logger.warning(msg, location=path, color="red")
            return []

        self.options["name"] = label  # TODO: Remove this?

        # Construct Node
        node["classes"].extend(classes)
        node["ids"].append(label)
        node["label"] = label
        node["docname"] = env.docname
        node["title"] = title_text
        node["type"] = "exercise"  # TODO: Remove this?
        node["hidden"] = True if "hidden" in self.options else False
        node.document = self.state.document

        self.add_name(node)
        env.sphinx_exercise_registry[label] = {
            "type": "exercise",  # noqa: E501 TODO: Can this be removed and sphinx_exercise_registry is specialised?
            "docname": env.docname,
            "node": node,
            "title": title_text,
            "hidden": node.get("hidden", bool),
        }

        if node.get("hidden", bool):
            return []

        return [node]


class SolutionDirective(SphinxDirective):
    """ A solution directive """

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
        env = self.env
        typ = self.name
        serial_no = env.new_serialno()

        if not hasattr(env, "sphinx_exercise_registry"):
            env.sphinx_exercise_registry = {}

        # Option Parsing
        if env.app.config.hide_solutions:
            return []

        # Collect Classes  TODO: simplify this?
        classes, class_name = [typ], self.options.get("class", "")
        if class_name:
            classes.extend(class_name)

        # Set Title Text
        title_text = "Solution to "
        target_label = self.arguments[0]

        # Initialise Node
        node = solution_node()

        # State Parsing
        section = nodes.section(ids=["solution-content"])
        textnodes, messages = self.state.inline_text(title_text, self.lineno)
        self.state.nested_parse(self.content, self.content_offset, section)

        node += nodes.title(title_text, "", *textnodes)
        node += section

        # Fetch Label or Generate One
        label = self.options.get("label", "")
        if label:
            self.options["noindex"] = False
        else:
            self.options["noindex"] = True
            label = f"{env.docname}-solution-{serial_no}"

        # Check for duplicate labels
        if not label == "" and label in env.sphinx_exercise_registry.keys():
            docpath = env.doc2path(env.docname)
            path = docpath[: docpath.rfind(".")]
            other_path = env.doc2path(env.sphinx_exercise_registry[label]["docname"])
            msg = f"duplicate label: {label}; other instance in {other_path}"
            logger.warning(msg, location=path, color="red")
            return []

        self.options["name"] = label

        # Set node attributes
        node["classes"].extend(classes)
        node["ids"].append(label)
        node["label"] = label
        node["docname"] = env.docname
        node["title"] = title_text
        node["type"] = typ
        node["hidden"] = True if "hidden" in self.options else False
        node.document = self.state.document

        # TODO Check for target label in env.sphinx_exercise_registry registry

        node["target_label"] = target_label

        self.add_name(node)
        env.sphinx_exercise_registry[label] = {
            "type": "solution",  # TODO: remove?
            "docname": env.docname,
            "node": node,
            "title": title_text,
            "hidden": node.get("hidden", bool),
        }

        if node.get("hidden", bool):
            return []

        return [node]
