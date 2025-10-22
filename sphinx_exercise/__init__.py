# -*- coding: utf-8 -*-
"""
sphinx_exercise
~~~~~~~~~~~~~~~
This package is an extension for sphinx to support exercise and solutions.
:copyright: Copyright 2020-2021 by the Executable Books team, see AUTHORS.
:license: MIT, see LICENSE for details.
"""

__version__ = "1.1.0"

from pathlib import Path
from typing import Any, Dict, Set, Union, cast
from sphinx.config import Config
from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment
from sphinx.domains.std import StandardDomain
from docutils.nodes import Node
from sphinx.util import logging
from sphinx.util.fileutil import copy_asset
from sphinx.locale import get_translation

from ._compat import findall
from .directive import (
    ExerciseDirective,
    ExerciseStartDirective,
    ExerciseEndDirective,
    SolutionDirective,
    SolutionStartDirective,
    SolutionEndDirective,
)
from .nodes import (
    exercise_node,
    visit_exercise_node,
    depart_exercise_node,
    exercise_enumerable_node,
    visit_exercise_enumerable_node,
    depart_exercise_enumerable_node,
    exercise_end_node,
    solution_node,
    visit_solution_node,
    depart_solution_node,
    solution_start_node,
    solution_end_node,
    is_extension_node,
    exercise_title,
    exercise_subtitle,
    solution_title,
    solution_subtitle,
    exercise_latex_number_reference,
    visit_exercise_latex_number_reference,
    depart_exercise_latex_number_reference,
)
from .transforms import (
    CheckGatedDirectives,
    MergeGatedSolutions,
    MergeGatedExercises,
)
from .post_transforms import (
    ResolveTitlesInExercises,
    ResolveTitlesInSolutions,
    UpdateReferencesToEnumerated,
    ResolveLinkTextToSolutions,
)

logger = logging.getLogger(__name__)

MESSAGE_CATALOG_NAME = "exercise"
translate = get_translation(MESSAGE_CATALOG_NAME)

# Callback Functions


def purge_exercises(app: Sphinx, env: BuildEnvironment, docname: str) -> None:
    """Purge sphinx_exercise registry"""

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


def merge_exercises(
    app: Sphinx, env: BuildEnvironment, docnames: Set[str], other: BuildEnvironment
) -> None:
    """Merge sphinx_exercise_registry"""

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
    numfig_format = {"exercise": f"{translate('Exercise')} %s"}
    # Merge with current sphinx settings
    numfig_format.update(config.numfig_format)
    config.numfig_format = numfig_format


def copy_asset_files(app: Sphinx, exc: Union[bool, Exception]):
    """Copies required assets for formating in HTML"""

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
    """

    domain = cast(StandardDomain, app.env.get_domain("std"))

    # Traverse sphinx-exercise nodes
    for node in findall(document):
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

    # Internal Title Nodes that don't need visit_ and depart_ methods
    # as they are resolved in post_transforms to docutil and sphinx nodes
    app.add_node(exercise_end_node)
    app.add_node(solution_start_node)
    app.add_node(solution_end_node)
    app.add_node(exercise_title)
    app.add_node(exercise_subtitle)
    app.add_node(solution_title)
    app.add_node(solution_subtitle)

    app.add_node(
        exercise_latex_number_reference,
        latex=(
            visit_exercise_latex_number_reference,
            depart_exercise_latex_number_reference,
        ),
    )

    app.add_directive("exercise", ExerciseDirective)
    app.add_directive("exercise-start", ExerciseStartDirective)
    app.add_directive("exercise-end", ExerciseEndDirective)
    app.add_directive("solution", SolutionDirective)
    app.add_directive("solution-start", SolutionStartDirective)
    app.add_directive("solution-end", SolutionEndDirective)

    app.add_transform(CheckGatedDirectives)
    app.add_transform(MergeGatedExercises)
    app.add_transform(MergeGatedSolutions)

    app.add_post_transform(UpdateReferencesToEnumerated)
    app.add_post_transform(ResolveTitlesInExercises)
    app.add_post_transform(ResolveTitlesInSolutions)
    app.add_post_transform(ResolveLinkTextToSolutions)

    app.add_css_file("exercise.css")

    # add translations
    package_dir = Path(__file__).parent.resolve()
    locale_dir = package_dir / "translations" / "locales"
    app.add_message_catalog(MESSAGE_CATALOG_NAME, str(locale_dir))

    return {
        "version": "builtin",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
