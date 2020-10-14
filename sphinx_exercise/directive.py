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


class CustomDirective(SphinxDirective):
    """ A custom Sphinx directive """

    name = ""

    def run(self) -> List[Node]:
        if self.name == "solution" and self.env.app.config.hide_solutions:
            return []

        serial_no = self.env.new_serialno()

        if not hasattr(self.env, "exercise_list"):
            self.env.exercise_list = {}

        classes, class_name = [self.name], self.options.get("class", "")
        if class_name:
            classes.extend(class_name)

        title_text, title = "", ""
        if self.name == "exercise":
            if "nonumber" in self.options:
                title_text = f"{self.name.title()} "

            if self.arguments != []:
                title_text += f"({self.arguments[0]})"
                title += self.arguments[0]
        else:
            title_text = f"{self.name.title()} to "
            target_label = self.arguments[0]

        textnodes, messages = self.state.inline_text(title_text, self.lineno)

        section = nodes.section(ids=[f"{self.name}-content"])
        self.state.nested_parse(self.content, self.content_offset, section)

        if self.name == "exercise":
            if "nonumber" in self.options:
                node = unenumerable_node()
            else:
                node = enumerable_node()
        else:
            node = linked_node()

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
            docpath = self.env.doc2path(self.env.docname)
            path = docpath[: docpath.rfind(".")]
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
        node["hidden"] = True if "hidden" in self.options else False
        node.document = self.state.document

        if self.name == "solution":
            node["target_label"] = target_label

        self.add_name(node)

        self.env.exercise_list[label] = {
            "type": self.name,
            "docname": self.env.docname,
            "node": node,
            "title": title,
            "hidden": node.get("hidden", bool),
        }

        if node.get("hidden", bool):
            return []

        return [node]


class ExerciseDirective(CustomDirective):
    """ A custom exercise directive """

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


class SolutionDirective(CustomDirective):
    """ A custom solution directive """

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
