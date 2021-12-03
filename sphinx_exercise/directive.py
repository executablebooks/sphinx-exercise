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


class CustomDirective(SphinxDirective):
    """ A custom Sphinx directive """

    name = ""

    def run(self) -> List[Node]:
        env = self.env
        typ = self.name
        if typ == "solution" and env.app.config.hide_solutions:
            return []

        serial_no = env.new_serialno()

        if not hasattr(env, "exercise_list"):
            env.exercise_list = {}

        classes, class_name = [typ], self.options.get("class", "")
        if class_name:
            classes.extend(class_name)

        # Have a dummy title text if no title specified, as 'std' domain needs
        # a title to process it as enumerable node.
        if typ == "exercise":
            title_text = f"{_(self.name.title())} "

            if self.arguments != []:
                title_text = f"({_(self.arguments[0])})"
        else:
            title_text = f"{_(self.name.title())} to "
            target_label = self.arguments[0]

        # selecting the type of node
        if typ == "exercise":
            if "nonumber" in self.options:
                node = exercise_unenumerable_node()
            else:
                node = exercise_node()
        else:
            node = solution_node()

        # state parsing
        section = nodes.section(ids=[f"{typ}-content"])
        textnodes, messages = self.state.inline_text(title_text, self.lineno)
        self.state.nested_parse(self.content, self.content_offset, section)

        node += nodes.title(title_text, "", *textnodes)
        node += section

        label = self.options.get("label", "")
        if label:
            self.options["noindex"] = False
        else:
            self.options["noindex"] = True
            label = f"{env.docname}-{typ}-{serial_no}"

        # Duplicate label warning
        if not label == "" and label in env.exercise_list.keys():
            docpath = env.doc2path(env.docname)
            path = docpath[: docpath.rfind(".")]
            other_path = env.doc2path(env.exercise_list[label]["docname"])
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

        if typ == "solution":
            node["target_label"] = target_label

        self.add_name(node)
        env.exercise_list[label] = {
            "type": typ,
            "docname": env.docname,
            "node": node,
            "title": title_text,
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
