# -*- coding: utf-8 -*-
"""
    sphinx_exercise
    ~~~~~~~~~~~~~~~
    This package is a namespace package that contains all extensions
    distributed in the ``sphinx-contrib`` distribution.
    :copyright: Copyright 2007-2009 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
from pathlib import Path
from typing import Any, Dict, Set, Union, cast
from sphinx.config import Config
from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment
from sphinx.domains.std import StandardDomain
from docutils.nodes import Node
from docutils import nodes as docutil_nodes
from sphinx.util import logging
from sphinx.util.fileutil import copy_asset
from .directive import ExerciseDirective, SolutionDirective
from .nodes import (
    exercise_node,
    exercise_unenumerable_node,
    solution_node,
    visit_enumerable_node,
    depart_enumerable_node,
    visit_exercise_unenumerable_node,
    depart_exercise_unenumerable_node,
    visit_solution_node,
    depart_solution_node,
    is_solution_node,
    is_exercise_node,
    is_unenumerable_node,
    is_extension_node,
    NODE_TYPES,
)
from sphinx.transforms.post_transforms import SphinxPostTransform
from .utils import get_node_number

logger = logging.getLogger(__name__)


def purge_exercises(app: Sphinx, env: BuildEnvironment, docname: str) -> None:
    if not hasattr(env, "exercise_list"):
        return

    # Override env.exercise_list
    env.exercise_list = {
        exercise: env.exercise_list[exercise]
        for exercise in env.exercise_list.keys()
        if env.exercise_list[exercise]["docname"] != docname
    }


def merge_exercises(
    app: Sphinx, env: BuildEnvironment, docnames: Set[str], other: BuildEnvironment
) -> None:
    if not hasattr(env, "exercise_list"):
        env.exercise_list = {}

    # Merge env stored data
    if hasattr(other, "exercise_list"):
        env.exercise_list = {**env.exercise_list, **other.exercise_list}


def init_numfig(app: Sphinx, config: Config) -> None:
    """Initialize exercise numfig format."""

    config["numfig"] = True
    numfig_format = {}
    for typ in NODE_TYPES.keys():
        numfig_format[typ] = typ + " %s"
    numfig_format.update(config.numfig_format)
    config.numfig_format = numfig_format


def copy_asset_files(app: Sphinx, exc: Union[bool, Exception]):
    static_path = Path(__file__).parent.joinpath("_static", "exercise.css").absolute()
    asset_files = [str(static_path)]

    if exc is None:
        for path in asset_files:
            copy_asset(path, str(Path(app.outdir).joinpath("_static").absolute()))


def doctree_read(app: Sphinx, document: Node) -> None:
    domain = cast(StandardDomain, app.env.get_domain("std"))

    # Traverse extension nodes
    for node in document.traverse():
        docname, labelid, sectname = "", "", ""

        if is_extension_node(node):
            name = node.get("names", [])[0]
            labelid = document.nameids[name]
            docname = app.env.docname

            # If solution node
            if is_solution_node(node):
                sectname = "Solution to "
            else:
                for item in node[0]:
                    sectname += f"{item.astext()} "
            domain.anonlabels[name] = docname, labelid
            domain.labels[name] = docname, labelid, sectname


def _has_math_child(node):
    for item in node:
        if isinstance(item, docutil_nodes.math):
            return True
    return False


def _update_title(title):
    inline = docutil_nodes.inline()

    if len(title) == 1 and isinstance(title[0], docutil_nodes.Text):
        _ = title[0][0].replace("(", "").replace(")", "")
        inline += docutil_nodes.Text(_, _)
    else:
        for ii in range(len(title)):
            item = title[ii]

            if ii == 0 and isinstance(item, docutil_nodes.Text):
                _ = item.replace("exercise", "").replace("(", "").lstrip()
                title.replace(title[ii], docutil_nodes.Text(_, _))
            elif ii == len(title) - 1 and isinstance(item, docutil_nodes.Text):
                _ = item.replace(")", "").rstrip()
                if _:
                    title.replace(title[ii], docutil_nodes.Text(_, _))
                else:
                    continue
            inline += title[ii]

    return inline


class solutionTransorm(SphinxPostTransform):
    default_priority = 1000

    def run(self):
        for node in self.document.traverse(solution_node):
            target_labelid = node.get("target_label", "")
            try:
                target_attr = self.env.exercise_list[target_labelid]
            except Exception:
                # target_labelid not found
                msg = f"undefined label: {target_labelid}"
                logger.warning(msg, location=node.attributes["docname"], color="red")
                return

            # Create a reference
            refuri = self.app.builder.get_relative_uri(
                self.env.docname, target_attr.get("docname", "")
            )
            refuri += "#" + target_labelid

            # create a text for the reference node
            title = node.attributes["title"]
            reference = docutil_nodes.reference(
                "",
                "",
                internal=True,
                refuri=refuri,
                anchorname="",
                *[docutil_nodes.Text(title)],
            )
            newnode = docutil_nodes.title("")
            newnode.append(reference)
            node[0].replace_self(newnode)

            # update node
            self.env.exercise_list[node.get("label", "")]["node"] = node

        for node in self.document.traverse(docutil_nodes.reference):
            if "Solution to" in node.astext():
                default_title = "Solution to "
                label = node.attributes["refid"]
                source_node = self.env.exercise_list[label].get("node")
                target_label = source_node.attributes["target_label"]
                target_attr = self.env.exercise_list[target_label]
                target_node = target_attr.get("node", Node)

                if is_exercise_node(target_node) and node.astext() == default_title:
                    number = get_node_number(self.app, target_node, "exercise")
                    node[0].insert(
                        len(node[0]), docutil_nodes.Text(" Exercise " + number)
                    )
                    return

                if is_unenumerable_node(target_node) and node.astext() == default_title:
                    if target_attr.get("title"):
                        if _has_math_child(target_node[0]):
                            title = _update_title(target_node[0])
                            title.insert(
                                0, docutil_nodes.Text(default_title, default_title)
                            )
                            node.replace(node[0], title)
                        else:
                            text = target_attr.get("title", "")
                            node[0].insert(len(node[0]), docutil_nodes.Text(text, text))
                    else:
                        node[0].insert(
                            len(node[0]), docutil_nodes.Text("Exercise", "Exercise")
                        )


def setup(app: Sphinx) -> Dict[str, Any]:

    app.add_config_value("hide_solutions", False, "env")

    app.add_css_file("exercise.css")
    app.connect("config-inited", init_numfig)  # 1
    app.connect("env-purge-doc", purge_exercises)  # 5 per file
    app.connect("doctree-read", doctree_read)  # 8
    app.connect("env-merge-info", merge_exercises)  # 9
    app.connect("build-finished", copy_asset_files)  # 16

    app.add_enumerable_node(
        exercise_node,
        "exercise",
        None,
        singlehtml=(visit_enumerable_node, depart_enumerable_node),
        html=(visit_enumerable_node, depart_enumerable_node),
        latex=(visit_enumerable_node, depart_enumerable_node),
    )

    app.add_node(
        exercise_unenumerable_node,
        singlehtml=(
            visit_exercise_unenumerable_node,
            depart_exercise_unenumerable_node,
        ),
        html=(visit_exercise_unenumerable_node, depart_exercise_unenumerable_node),
        latex=(visit_exercise_unenumerable_node, depart_exercise_unenumerable_node),
    )

    app.add_enumerable_node(
        solution_node,
        "solution",
        None,
        singlehtml=(visit_solution_node, depart_solution_node),
        html=(visit_solution_node, depart_solution_node),
        latex=(visit_solution_node, depart_solution_node),
    )

    app.add_directive("exercise", ExerciseDirective)
    app.add_directive("solution", SolutionDirective)

    app.add_post_transform(solutionTransorm)

    return {
        "version": "builtin",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }


def get_title(self):
    return self[0].astext()
