# -*- coding: utf-8 -*-
"""
sphinx_exercise
~~~~~~~~~~~~~~~
This package is an extension for sphinx to support exercise and solutions.
:copyright: Copyright 2020-2021 by the Executable Books team, see AUTHORS.
:license: MIT, see LICENSE for details.
"""

from pathlib import Path
from typing import Any, Dict, Set, Union, cast
from sphinx.config import Config
from sphinx.locale import get_translation
from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment
from sphinx.domains.std import StandardDomain
from docutils.nodes import Node
from sphinx.util import logging
from sphinx.util.fileutil import copy_asset

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
_ = get_translation(MESSAGE_CATALOG_NAME)


<<<<<<< HEAD
# Variables
SOLUTION_PLACEHOLDER = _("Solution to ")
MATH_PLACEHOLDER = ":math:"
=======

# Callback Functions
>>>>>>> a6767f0 (Essai d'une nouvelle version)


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
<<<<<<< HEAD

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

                # Lastly, remove parans from title
                _r, _l = sectname.rfind(")"), sectname.find("(") + 1
                sectname = sectname[_l:_r].strip()

            domain.anonlabels[name] = docname, labelid
            domain.labels[name] = docname, labelid, sectname


def update_title(title):
    """
    Does necessary formatting to the title node, and wraps it with an inline node.
    """
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


def process_math_placeholder(node, update_title, source_node):
    """Convert the placeholder math text to a math node."""
    if MATH_PLACEHOLDER in node.astext():
        title = update_title(source_node[0])
        return node.replace(node[0], title)


def process_reference(self, node, default_title=""):
    """
    Processing reference nodes in the document to facilitate the design and the
    functionality requirements.
    """
    label = get_refuri(node)
    if hasattr(self.env, "exercise_list") and label in self.env.exercise_list:
        source_node = self.env.exercise_list[label].get("node")
        # if reference source is a solution node
        if is_solution_node(source_node):
            target_label = source_node.attributes.get("target_label", "")
            if node.astext().strip() == "Solution to":
                default_title = node.astext()
        else:
            target_label = source_node.attributes.get("label", "")
        target_attr = self.env.exercise_list[target_label]
        target_node = target_attr.get("node", Node)
        # if reference target is exercise node
        if is_exercise_node(target_node):
            if default_title:
                number = get_node_number(self.app, target_node, "exercise")
                node.insert(len(node[0]), docutil_nodes.Text(_(" Exercise ") + number))
                return
            else:
                node = process_math_placeholder(node, update_title, source_node)
        # if reference target is an exercise unenumerable node
        if is_exercise_unenumerable_node(target_node):
            if default_title:
                if target_attr.get("title"):
                    if has_math_child(target_node[0]):
                        title = update_title(target_node[0])
                        title.insert(
                            0, docutil_nodes.Text(default_title, default_title)
                        )
                        node.replace(node[0], title)
                    else:
                        text = target_attr.get("title", "")
                        if text[0] == "(" and text[-1] == ")":
                            text = text[1:-1]
                        node[0].insert(len(node[0]), docutil_nodes.Text(text, text))
            else:
                node = process_math_placeholder(node, update_title, source_node)


class ReferenceTransform(SphinxPostTransform):
    default_priority = 998  # should be processed before processing solution nodes

    def run(self):

        for node in self.document.traverse(docutil_nodes.reference):
            process_reference(self, node)


class SolutionTransorm(SphinxPostTransform):
    default_priority = 999  # should be after processing reference nodes

    def run(self):

        for node in self.document.traverse(solution_node):
            target_labelid = node.get("target_label", "")
            try:
                target_attr = self.env.exercise_list[target_labelid]
            except Exception:
                # target_labelid not found
                if isinstance(self.app.builder, LaTeXBuilder):
                    docname = find_parent(self.app.builder.env, node, "section")
                else:
                    docname = self.app.builder.current_docname
                docpath = self.env.doc2path(docname)
                path = docpath[: docpath.rfind(".")]
                msg = f"undefined label: {target_labelid}"
                logger.warning(msg, location=path, color="red")
                return

            # Create a reference
            refuri = self.app.builder.get_relative_uri(
                self.env.docname, target_attr.get("docname", "")
            )
            refuri += "#" + target_labelid

            # create a text for the reference node
            title = node.attributes["title"]
            newtitle = docutil_nodes.inline("", docutil_nodes.Text(title))
            reference = docutil_nodes.reference(
                "",
                "",
                internal=True,
                refuri=refuri,
                anchorname="",
                *[newtitle],
            )
            process_reference(self, reference, SOLUTION_PLACEHOLDER)
            newnode = docutil_nodes.title("")
            newnode.append(reference)
            node[0].replace_self(newnode)
            # update node
            self.env.exercise_list[node.get("label", "")]["node"] = node


class NumberReferenceTransform(SphinxPostTransform):
    default_priority = 1000

    def run(self):

        for node in self.document.traverse(number_reference):
            labelid = get_refuri(node)

            # If extension directive referenced
            if labelid in self.env.exercise_list:
                source_attr = self.env.exercise_list[labelid]
                source_node = source_attr.get("node", Node)
                node_title = node.get("title", "")

                # processing for nodes which have
                if "{name}" in node_title and has_math_child(source_node[0]):
                    newtitle = docutil_nodes.inline()
                    for item in node_title.split():
                        if item == "{name}":
                            # use extend instead?
                            for _ in update_title(source_node[0]):
                                newtitle += _
                        elif item == "{number}":
                            source_type = source_node.attributes["type"]
                            source_number = get_node_number(
                                self.app, source_node, source_type
                            )
                            source_num = ".".join(map(str, source_number))
                            newtitle += docutil_nodes.Text(source_num, source_num)
                        else:
                            newtitle += docutil_nodes.Text(item, item)
                        newtitle += docutil_nodes.Text(" ", " ")

                    if newtitle[len(newtitle) - 1].astext() == " ":
                        newtitle.pop()
                    node.replace(node[0], newtitle)
=======
            section_name = node.attributes.get("title")
            domain.anonlabels[name] = docname, label
            domain.labels[name] = docname, label, section_name
>>>>>>> a6767f0 (Essai d'une nouvelle version)


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

    return {
        "version": "builtin",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
