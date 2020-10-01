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
from .nodes import enumerable_node, unenumerable_node, linked_node
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
        env = self.env
        serial_no = env.new_serialno()

        if not hasattr(env, "exercise_list"):
            env.exercise_list = {}

        # Take care of class option
        classes, class_name = [self.name], self.options.get("class", "")
        if class_name:
            classes.extend(class_name)

        title_text = ""
        if "nonumber" in self.options:
            title_text = f"{self.name.title()} "

        if self.arguments != []:
            title_text += f"{self.arguments[0]}"

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

        self.options["name"] = label

        # Set node attributes
        node["classes"].extend(classes)
        node["ids"].append(label)
        node["docname"] = self.env.docname
        node.document = self.state.document

        self.add_name(node)

        env.exercise_list[label] = {
            "docname": env.docname,
            "type": self.name,
            "label": label,
            "prio": 0,
            "nonumber": True if "nonumber" in self.options else False,
            "title": self.arguments[0] if self.arguments != [] else "",
            "node": node,
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

    def run(self):
        env = self.env
        serial_no = env.new_serialno()
        self.options["nonumber"] = True

        if not hasattr(env, "exercise_list"):
            env.exercise_list = {}

        # If class in options add to class array
        classes, class_name = [self.name], self.options.get("class", [])
        if class_name:
            classes.extend(class_name)

        label = self.options.get("label", "")
        # If label
        if label:
            self.options["noindex"] = False
            node_id = f"{label}"
        else:
            self.options["noindex"] = True
            label = f"{self.env.docname}-{self.name}-{serial_no}"
            node_id = f"{self.env.docname}-{self.name}-{serial_no}"
        ids = [node_id]

        # Duplicate label warning
        if not label == "" and label in env.exercise_list.keys():
            docpath = env.doc2path(env.docname)
            path = docpath[: docpath.rfind(".")]
            other_path = env.doc2path(env.exercise_list[label]["docname"])
            msg = (
                f"duplicate {self.name} label '{label}', other instance in {other_path}"
            )
            logger.warning(msg, location=path, color="red")

        title_text = ""

        if self.arguments != []:
            title_text = self.arguments[0]

        section = nodes.section(ids=[f"{self.name}-content"])
        self.state.nested_parse(self.content, self.content_offset, section)

        node = linked_node()
        node.document = self.state.document

        node += section

        # Set node attributes
        node["ids"].extend(ids)
        node["classes"].extend(classes)
        node["title"] = title_text
        node["label"] = label
        node["type"] = self.name

        env.exercise_list[label] = {
            "docname": env.docname,
            "type": self.name,
            "ids": ids,
            "label": label,
            "prio": 0,
            "nonumber": True if "nonumber" in self.options else False,
            "title": self.arguments[0] if self.arguments != [] else "",
            "node": node,
        }

        return [node]
