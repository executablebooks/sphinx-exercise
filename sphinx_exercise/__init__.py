# -*- coding: utf-8 -*-
"""
sphinx_exercise
~~~~~~~~~~~~~~~
This package is an extension for sphinx to support exercise and solutions.
:copyright: Copyright 2020-2021 by the Executable Books team, see AUTHORS.
:license: MIT, see LICENSE for details.
"""

__version__ = "1.2.1"

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

    # Purge node order tracking for this document
    if (
        hasattr(env, "sphinx_exercise_node_order")
        and docname in env.sphinx_exercise_node_order
    ):
        del env.sphinx_exercise_node_order[docname]


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

    # Merge node order tracking
    if not hasattr(env, "sphinx_exercise_node_order"):
        env.sphinx_exercise_node_order = {}

    if hasattr(other, "sphinx_exercise_node_order"):
        env.sphinx_exercise_node_order = {
            **env.sphinx_exercise_node_order,
            **other.sphinx_exercise_node_order,
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


def validate_exercise_solution_order(app: Sphinx, env: BuildEnvironment) -> None:
    """
    Validate that solutions follow their referenced exercises when
    exercise_style='solution_follow_exercise' is set.
    """
    # Only validate if the config option is set
    if app.config.exercise_style != "solution_follow_exercise":
        return

    if not hasattr(env, "sphinx_exercise_node_order"):
        return

    logger = logging.getLogger(__name__)

    # Process each document
    for docname, nodes in env.sphinx_exercise_node_order.items():
        # Build a map of exercise labels to their positions and info
        exercise_info = {}
        for i, node_info in enumerate(nodes):
            if node_info["type"] == "exercise":
                exercise_info[node_info["label"]] = {
                    "position": i,
                    "line": node_info.get("line"),
                }

        # Check each solution
        for i, node_info in enumerate(nodes):
            if node_info["type"] == "solution":
                target_label = node_info["target_label"]
                solution_label = node_info["label"]
                solution_line = node_info.get("line")

                if not target_label:
                    continue

                # Check if target exercise exists in this document
                if target_label not in exercise_info:
                    # Exercise is in a different document or doesn't exist
                    docpath = env.doc2path(docname)
                    path = str(Path(docpath).with_suffix(""))

                    # Build location string with line number if available
                    location = f"{path}:{solution_line}" if solution_line else path

                    logger.warning(
                        f"[sphinx-exercise] Solution '{solution_label}' references exercise '{target_label}' "
                        f"which is not in the same document. When exercise_style='solution_follow_exercise', "
                        f"solutions should appear in the same document as their exercises.",
                        location=location,
                        color="yellow",
                    )
                    continue

                # Check if solution comes after exercise
                exercise_data = exercise_info[target_label]
                exercise_pos = exercise_data["position"]
                exercise_line = exercise_data.get("line")

                if i <= exercise_pos:
                    docpath = env.doc2path(docname)
                    path = str(Path(docpath).with_suffix(""))

                    # Build more informative message with line numbers
                    if solution_line and exercise_line:
                        location = f"{path}:{solution_line}"
                        msg = (
                            f"[sphinx-exercise] Solution '{solution_label}' (line {solution_line}) does not follow "
                            f"exercise '{target_label}' (line {exercise_line}). "
                            f"When exercise_style='solution_follow_exercise', solutions should "
                            f"appear after their referenced exercises."
                        )
                    elif solution_line:
                        location = f"{path}:{solution_line}"
                        msg = (
                            f"[sphinx-exercise] Solution '{solution_label}' does not follow exercise '{target_label}'. "
                            f"When exercise_style='solution_follow_exercise', solutions should "
                            f"appear after their referenced exercises."
                        )
                    else:
                        location = path
                        msg = (
                            f"[sphinx-exercise] Solution '{solution_label}' does not follow exercise '{target_label}'. "
                            f"When exercise_style='solution_follow_exercise', solutions should "
                            f"appear after their referenced exercises."
                        )

                    logger.warning(msg, location=location, color="yellow")


def doctree_read(app: Sphinx, document: Node) -> None:
    """
    Read the doctree and apply updates to sphinx-exercise nodes
    """

    domain = cast(StandardDomain, app.env.get_domain("std"))

    # Initialize node order tracking for this document
    if not hasattr(app.env, "sphinx_exercise_node_order"):
        app.env.sphinx_exercise_node_order = {}

    docname = app.env.docname
    if docname not in app.env.sphinx_exercise_node_order:
        app.env.sphinx_exercise_node_order[docname] = []

    # Traverse sphinx-exercise nodes
    for node in findall(document):
        if is_extension_node(node):
            name = node.get("names", [])[0]
            label = document.nameids[name]
            section_name = node.attributes.get("title")
            domain.anonlabels[name] = docname, label
            domain.labels[name] = docname, label, section_name

            # Track node order for validation
            node_type = node.get("type", "unknown")
            node_label = node.get("label", "")
            target_label = node.get("target_label", None)  # Only for solution nodes

            app.env.sphinx_exercise_node_order[docname].append(
                {
                    "type": node_type,
                    "label": node_label,
                    "target_label": target_label,
                    "line": node.line if hasattr(node, "line") else None,
                }
            )


def setup(app: Sphinx) -> Dict[str, Any]:
    app.add_config_value("hide_solutions", False, "env")
    app.add_config_value("exercise_style", "", "env")

    app.connect("config-inited", init_numfig)  # event order - 1
    app.connect("env-purge-doc", purge_exercises)  # event order - 5 per file
    app.connect("doctree-read", doctree_read)  # event order - 8
    app.connect("env-merge-info", merge_exercises)  # event order - 9
    app.connect("env-updated", validate_exercise_solution_order)  # event order - 10
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
