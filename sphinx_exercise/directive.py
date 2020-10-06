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
from .local_nodes import enumerable_node, unenumerable_node, linked_node
from docutils import nodes
from sphinx.util import logging

logger = logging.getLogger(__name__)


class ExerciseDirective(SphinxDirective):
    """ A custom Sphinx Directive """

    name = "exercise"
    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {
        "label": directives.unchanged_required,
        "class": directives.class_option,
        "nonumber": directives.flag,
    }

    def run(self) -> List[Node]:
        serial_no = self.env.new_serialno()

        if not hasattr(self.env, "exercise_list"):
            self.env.exercise_list = {}

        # Take care of class option
        classes, class_name = [self.name], self.options.get("class", "")
        if class_name:
            classes.extend(class_name)

        title_text, _ = "", ""
        if "nonumber" in self.options:
            title_text = f"{self.name.title()} "

        if self.arguments != []:
            title_text += f"({self.arguments[0]})"
            _ += self.arguments[0]

        textnodes, messages = self.state.inline_text(title_text, self.lineno)

        section = nodes.section(ids=[f"{self.name}-content"])
        self.state.nested_parse(self.content, self.content_offset, section)

        if "nonumber" in self.options:
            node = unenumerable_node()
        else:
            node = enumerable_node()

        node += nodes.title(title_text, "", *textnodes)
        node += section

        label = self.options.get("label", "")
        if label:
            self.options["noindex"] = False
        else:
            self.options["noindex"] = True
            label = f"{self.env.docname}-{self.name}-{serial_no}"

        # Duplicate label warning
        if not label == "" and label in self.env.exercise_list.keys():
            path = self.env.doc2path(self.env.docname)[:-3]
            other_path = self.env.doc2path(self.env.exercise_list[label]["docname"])
            msg = f"duplicate label: {label}; other instance in {other_path}"
            logger.warning(msg, location=path, color="red")
            return []

        self.options["name"] = label

        # Set node attributes
        node["classes"].extend(classes)
        node["ids"].append(label)
        node["label"] = label
        node["docname"] = self.env.docname
        node.document = self.state.document

        self.add_name(node)

        self.env.exercise_list[label] = {
            "type": self.name,
            "docname": self.env.docname,
            "node": node,
            "title": _,
        }
        return [node]


class SolutionDirective(SphinxDirective):
    """ A custom Sphinx Directive """

    name = "solution"
    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        "label": directives.unchanged_required,
        "class": directives.class_option,
    }
    title_text = f"{name.title()} to "

    def run(self):
        serial_no = self.env.new_serialno()

        if not hasattr(self.env, "exercise_list"):
            self.env.exercise_list = {}

        # Take care of class option
        classes, class_name = [self.name], self.options.get("class", [])
        if class_name:
            classes.extend(class_name)

        target_label = self.arguments[0]

        textnodes, messages = self.state.inline_text(self.title_text, self.lineno)

        section = nodes.section(ids=[f"{self.name}-content"])
        self.state.nested_parse(self.content, self.content_offset, section)

        node = linked_node()
        node.document = self.state.document
        node += nodes.title(self.title_text, "", *textnodes)
        node += section

        label = self.options.get("label", "")
        if label:
            self.options["noindex"] = False
        else:
            self.options["noindex"] = True
            label = f"{self.env.docname}-{self.name}-{serial_no}"

        # Duplicate label warning
        if not label == "" and label in self.env.exercise_list.keys():
            path = self.env.doc2path(self.env.docname)[:-3]
            other_path = self.env.doc2path(self.env.exercise_list[label]["docname"])
            msg = f"duplicate label: {label}; other instance in {other_path}"
            logger.warning(msg, location=path, color="red")
            return []

        self.options["name"] = label

        # Set node attributes
        node["classes"].extend(classes)
        node["ids"].append(label)
        node["label"] = label
        node["docname"] = self.env.docname
        node["target_label"] = target_label
        node.document = self.state.document

        self.add_name(node)

        self.env.exercise_list[label] = {
            "type": self.name,
            "docname": self.env.docname,
            "node": node,
            "title": "",
        }

        return [node]
