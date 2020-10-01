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
from sphinx.util import logging
from sphinx.util.fileutil import copy_asset
from sphinx.util.nodes import clean_astext
from .directive import ExerciseDirective
from .nodes import (
    enumerable_node,
    unenumerable_node,
    linked_node,
    visit_enumerable_node,
    depart_enumerable_node,
    visit_unenumerable_node,
    depart_unenumerable_node,
    visit_linked_node,
    depart_linked_node,
)


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
    numfig_format = {
        "exercise": "Exercise %s",
    }
    numfig_format.update(config.numfig_format)
    config.numfig_format = numfig_format


def copy_asset_files(app: Sphinx, exc: Union[bool, Exception]):
    static_path = Path(__file__).parent.joinpath("_static", "exercise.css").absolute()
    asset_files = [str(static_path)]

    if exc is None:
        for path in asset_files:
            copy_asset(path, str(Path(app.outdir).joinpath("_static").absolute()))


def process_docs(app: Sphinx, document: Node) -> None:

    domain = cast(StandardDomain, app.env.get_domain("std"))

    # Traverse exercise nodes
    for node in document.traverse():
        docname, labelid, sectname = "", "", ""
        if node.__class__ == enumerable_node or node.__class__ == unenumerable_node:
            name = node.get("names", [])[0]
            labelid = document.nameids[name]
            docname = app.env.docname
            sectname = clean_astext(node[0])
            # typ = domain.get_enumerable_node_type(node)

            if sectname and node.__class__ == unenumerable_node:
                sectname = sectname.replace("Exercise ", "")

            # if not sectname:
            #     if node.__class__ == enumerable_node:
            #         typ = domain.get_enumerable_node_type(node)
            #         sectname = f"{typ.title()}"

            domain.anonlabels[name] = docname, labelid
            domain.labels[name] = docname, labelid, sectname


def setup(app: Sphinx) -> Dict[str, Any]:

    app.add_css_file("exercise.css")
    app.connect("build-finished", copy_asset_files)
    app.connect("config-inited", init_numfig)
    # app.connect("env-purge-doc", purge_exercises)
    # app.connect("env-merge-info", merge_exercises)
    app.connect("doctree-read", process_docs)

    app.add_enumerable_node(
        enumerable_node,
        "exercise",
        get_title,
        singlehtml=(visit_enumerable_node, depart_enumerable_node),
        html=(visit_enumerable_node, depart_enumerable_node),
    )

    app.add_node(
        unenumerable_node,
        singlehtml=(visit_unenumerable_node, depart_unenumerable_node),
        html=(visit_unenumerable_node, depart_unenumerable_node),
    )

    app.add_node(
        linked_node,
        singlehtml=(visit_linked_node, depart_linked_node),
        html=(visit_linked_node, depart_linked_node),
    )

    app.add_directive("exercise", ExerciseDirective)
    # app.add_directive("solution", SolutionDirective)

    return {
        "version": "builtin",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }


def get_title(self):
    return self[0].astext()
