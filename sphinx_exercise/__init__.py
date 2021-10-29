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
    is_extension_node,
    NODE_TYPES,
)
from .post_transforms import (
    ReferenceTransform,
    SolutionTransform,
    NumberReferenceTransform,
)

logger = logging.getLogger(__name__)

# Variables  TODO: centralise these variables

SOLUTION_PLACEHOLDER = "Solution to "
MATH_PLACEHOLDER = ":math:"

# Callback Functions


def purge_exercises(app: Sphinx, env: BuildEnvironment, docname: str) -> None:
    """ Purge sphinx_exercise registry """

    if not hasattr(env, "sphinx_exercise_registry"):
        return

    # Override env.sphinx_exercise_registry
    env.sphinx_exercise_registry = {
        exercise: env.sphinx_exercise_registry[exercise]
        for exercise in env.sphinx_exercise_registry.keys()
        if env.sphinx_exercise_registry[exercise]["docname"] != docname
    }


def merge_exercises(
    app: Sphinx, env: BuildEnvironment, docnames: Set[str], other: BuildEnvironment
) -> None:
    """ Merge sphinx_exercise_registry """

    if not hasattr(env, "sphinx_exercise_registry"):
        env.sphinx_exercise_registry = {}

    # Merge env stored data
    if hasattr(other, "sphinx_exercise_registry"):
        env.sphinx_exercise_registry = {
            **env.sphinx_exercise_registry,
            **other.sphinx_exercise_registry,
        }


def init_numfig(app: Sphinx, config: Config) -> None:
    """Initialize numfig format."""

    config["numfig"] = True
    numfig_format = {}
    for typ in NODE_TYPES.keys():
        numfig_format[typ] = typ.title() + " %s"
    numfig_format.update(config.numfig_format)
    config.numfig_format = numfig_format


def copy_asset_files(app: Sphinx, exc: Union[bool, Exception]):
    """ Copies required assets for formating in HTML """

    static_path = (
        Path(__file__).parent.joinpath("assets", "html", "exercise.css").absolute()
    )
    asset_files = [str(static_path)]

    if exc is None:
        for path in asset_files:
            copy_asset(path, str(Path(app.outdir).joinpath("_static").absolute()))


def doctree_read(app: Sphinx, document: Node) -> None:
    """
    Read the doctree and apply updates to sphinx-exercise nodes
    # TODO: What exactly is this updating? (domain labels?)
    # TODO: Can this be built into the node when instantiated?
    """

    domain = cast(StandardDomain, app.env.get_domain("std"))

    # Traverse sphinx-exercise nodes
    for node in document.traverse():
        docname, labelid, sectname = "", "", ""

        if is_extension_node(node):
            name = node.get("names", [])[0]
            labelid = document.nameids[name]
            docname = app.env.docname

            # If solution node
            if is_solution_node(node):
                sectname = SOLUTION_PLACEHOLDER
            else:
                # If other node, simply add :math: to title
                # to allow for easy parsing in ref_node
                for item in node[0]:
                    if isinstance(item, docutil_nodes.math):
                        sectname += f"{MATH_PLACEHOLDER}`{item.astext()}` "
                        continue
                    sectname += f"{item.astext()} "

                # Lastly, remove paranthesis from title
                _r, _l = sectname.rfind(")"), sectname.find("(") + 1
                sectname = sectname[_l:_r].strip()

            domain.anonlabels[name] = docname, labelid
            domain.labels[name] = docname, labelid, sectname


def setup(app: Sphinx) -> Dict[str, Any]:

    app.add_config_value("hide_solutions", False, "env")

    app.add_css_file("exercise.css")
    app.connect("config-inited", init_numfig)  # event order - 1
    app.connect("env-purge-doc", purge_exercises)  # event order - 5 per file
    app.connect("doctree-read", doctree_read)  # event order - 8
    app.connect("env-merge-info", merge_exercises)  # event order - 9
    app.connect("build-finished", copy_asset_files)  # event order - 16

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

    app.add_post_transform(ReferenceTransform)
    app.add_post_transform(SolutionTransform)
    app.add_post_transform(NumberReferenceTransform)

    return {
        "version": "builtin",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
