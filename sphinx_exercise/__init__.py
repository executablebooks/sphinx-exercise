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

from .directive import ExerciseDirective, SolutionDirective
from .nodes import (
    exercise_node,
    exercise_enumerable_node,
    solution_node,
    visit_exercise_node,
    depart_exercise_node,
    visit_exercise_enumerable_node,
    depart_exercise_enumerable_node,
    visit_solution_node,
    depart_solution_node,
    # is_solution_node,
    is_extension_node,
    exercise_title,
    visit_exercise_title,
    depart_exercise_title,
    exercise_subtitle,
    visit_exercise_subtitle,
    depart_exercise_subtitle,
    solution_title,
    visit_solution_title,
    depart_solution_title,
    solution_subtitle,
    visit_solution_subtitle,
    depart_solution_subtitle,
)
from .post_transforms import (
    ResolveTitlesInEnumerableExercises,
    ResolveTitlesInSolutions,
    UpdateReferencesToEnumerated,
)

logger = logging.getLogger(__name__)


# Callback Functions


def purge_exercises(app: Sphinx, env: BuildEnvironment, docname: str) -> None:
    """ Purge sphinx_exercise registry """

    if not hasattr(env, "sphinx_exercise_registry"):
        return

    # Purge env.sphinx_exercise_registry if matching docname
    remove_labels = [
        label
        for (label, node) in env.sphinx_exercise_registry.items()
        if node["docname"] == docname
    ]
    if remove_labels:
        for label in remove_labels:
            del env.sphinx_exercise_registry[label]

    # TODO: CLEAN UP
    # Copy registry entries that aren't equal to docname
    # registry = {}
    # for label in env.sphinx_exercise_registry.keys():
    #     if env.sphinx_exercise_registry[label]["docname"] != docname:
    #         registry[label] = env.sphinx_exercise_registry[label]
    # env.sphinx_exercise_registry = registry


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
    """Initialize numfig"""

    config["numfig"] = True
    numfig_format = {"exercise": "Exercise %s"}
    # Merge with current sphinx settings
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


# TODO: REMOVE


def doctree_read(app: Sphinx, document: Node) -> None:
    """
    Read the doctree and apply updates to sphinx-exercise nodes
    """

    domain = cast(StandardDomain, app.env.get_domain("std"))

    # Traverse sphinx-exercise nodes
    for node in document.traverse():
        if is_extension_node(node):
            name = node.get("names", [])[0]
            label = document.nameids[name]
            docname = app.env.docname
            section_name = node.attributes.get("title")
            domain.anonlabels[name] = docname, label
            domain.labels[name] = docname, label, section_name


def setup(app: Sphinx) -> Dict[str, Any]:

    app.add_config_value("hide_solutions", False, "env")

    app.connect("config-inited", init_numfig)  # event order - 1
    app.connect("env-purge-doc", purge_exercises)  # event order - 5 per file
    app.connect("doctree-read", doctree_read)  # event order - 8
    app.connect("env-merge-info", merge_exercises)  # event order - 9
    app.connect("build-finished", copy_asset_files)  # event order - 16

    app.add_node(
        exercise_node,
        singlehtml=(visit_exercise_node, depart_exercise_node),
        html=(visit_exercise_node, depart_exercise_node),
        latex=(visit_exercise_node, depart_exercise_node),
    )

    app.add_enumerable_node(
        exercise_enumerable_node,
        "exercise",
        None,
        singlehtml=(visit_exercise_enumerable_node, depart_exercise_enumerable_node),
        html=(visit_exercise_enumerable_node, depart_exercise_enumerable_node),
        latex=(visit_exercise_enumerable_node, depart_exercise_enumerable_node),
    )

    app.add_node(
        solution_node,
        singlehtml=(visit_solution_node, depart_solution_node),
        html=(visit_solution_node, depart_solution_node),
        latex=(visit_solution_node, depart_solution_node),
    )

    app.add_node(
        exercise_title,
        html=(visit_exercise_title, depart_exercise_title),
        latex=(visit_exercise_title, depart_exercise_title),
    )

    app.add_node(
        exercise_subtitle,
        html=(visit_exercise_subtitle, depart_exercise_subtitle),
        latex=(visit_exercise_subtitle, depart_exercise_subtitle),
    )

    app.add_node(solution_title, html=(visit_solution_title, depart_solution_title))

    app.add_node(
        solution_subtitle, html=(visit_solution_subtitle, depart_solution_subtitle)
    )

    app.add_directive("exercise", ExerciseDirective)
    app.add_directive("solution", SolutionDirective)

    app.add_post_transform(UpdateReferencesToEnumerated)
    app.add_post_transform(ResolveTitlesInEnumerableExercises)
    app.add_post_transform(ResolveTitlesInSolutions)

    app.add_css_file("exercise.css")

    return {
        "version": "builtin",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
