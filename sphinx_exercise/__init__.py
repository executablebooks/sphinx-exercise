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
from sphinx.addnodes import number_reference
from docutils.nodes import Node
from docutils import nodes
from sphinx.util import logging
from sphinx.util.fileutil import copy_asset
from .directive import ExerciseDirective, SolutionDirective
from .local_nodes import (
    enumerable_node,
    unenumerable_node,
    linked_node,
    visit_enumerable_node,
    depart_enumerable_node,
    visit_unenumerable_node,
    depart_unenumerable_node,
    visit_linked_node,
    depart_linked_node,
    is_linked_node,
    is_enumerable_node,
    is_unenumerable_node,
    is_extension_node,
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
            if is_linked_node(node):
                sectname = "Solution to "
            else:
                # If other node, simply add :math: to title
                # to allow for easy parsing in ref_node
                for item in node[0]:
                    if isinstance(item, nodes.math):
                        sectname += f":math:`{item.astext()}` "
                        continue
                    sectname += f"{item.astext()} "

                # Lastly, remove parans from title
                _r, _l = sectname.rfind(")"), sectname.find("(") + 1
                sectname = sectname[_l:_r].strip()

            # Now update domain.anonlabels and domain.labels
            # to include the newly updated sectname
            domain.anonlabels[name] = docname, labelid
            domain.labels[name] = docname, labelid, sectname


class DoctreeResolve:
    def __init__(self, app: Sphinx, doctree: nodes.document, docname: str) -> None:
        self.builder = app.builder
        self.config = app.config
        self.env = app.env
        self.docname = docname
        self.domain = cast(StandardDomain, app.env.get_domain("std"))
        self.process(doctree, docname)

    def _is_node_type(self, node: Node, node_type: Any) -> bool:
        return node.__class__ == node_type

    def _update_linked_node_title(self, node):
        target_labelid = node.get("target_label", "")

        try:
            target_attr = self.env.exercise_list[target_labelid]
        except Exception:
            # target_labelid not found
            docpath = self.env.doc2path(self.builder.current_docname)
            path = docpath[: docpath.rfind(".")]
            msg = f"undefined label: {target_labelid}"
            logger.warning(msg, location=path, color="red")
            node[0].insert(1, nodes.Text("Exercise", "Exercise"))
            self.env.exercise_list[node.get("label", "")]["node"] = node
            return

        target_node = target_attr.get("node", Node)

        # If linked node references an enumerable node
        # then replace title to "Solution to Exercise #"

        if is_enumerable_node(target_node):
            target_docname = target_attr.get("docname", "")
            target_type = self.domain.get_enumerable_node_type(target_node)
            target_number = self.domain.get_fignumber(
                self.env, self.builder, target_type, target_docname, target_node
            )
            target_num = ".".join(map(str, target_number))
            text = f"{target_type.title()} {target_num}"
            node[0].insert(1, nodes.Text(text, text))
        else:
            # If linked node references an unenumerable node
            # If title exists
            target_ttl = target_attr.get("title", "")
            if target_ttl:

                # Remove parans
                title = target_node[0]

                if len(title) == 1 and isinstance(title[0], nodes.Text):
                    _ = (
                        title[0]
                        .replace("Exercise", "")
                        .replace("(", "")
                        .replace(")", "")
                        .strip()
                    )
                    node[0].insert(1, nodes.Text(_, _))
                else:
                    new_title = self._update_title(title)
                    new_title.insert(0, node[0][0])
                    node.replace(node[0], new_title)
            else:
                text = "Exercise"
                node[0].insert(1, nodes.Text(text, text))

        # Create a reference
        newnode = nodes.title()
        refnode = nodes.reference()
        refnode["refdocname"] = target_attr.get("docname", "")
        refnode["refuri"] = self.builder.get_relative_uri(
            self.docname, target_attr.get("docname", "")
        )
        refnode["refuri"] += "#" + target_labelid
        inline = nodes.inline()
        title_node = node[0][0]
        for item in node[0][1:]:
            inline.append(item)
        refnode += inline
        newnode += refnode
        newnode.insert(0, title_node)
        node[0].replace_self(newnode)

        # update node
        self.env.exercise_list[node.get("label", "")]["node"] = node

    def _update_title(self, title):
        inline = nodes.inline()

        if len(title) == 1 and isinstance(title[0], nodes.Text):
            _ = title[0][0].replace("(", "").replace(")", "")
            inline += nodes.Text(_, _)
        else:
            for ii in range(len(title)):
                item = title[ii]

                if ii == 0 and isinstance(item, nodes.Text):
                    _ = item.replace("Exercise", "").replace("(", "").lstrip()
                    title.replace(title[ii], nodes.Text(_, _))
                elif ii == len(title) - 1 and isinstance(item, nodes.Text):
                    _ = item.replace(")", "").rstrip()
                    if _:
                        title.replace(title[ii], nodes.Text(_, _))
                    else:
                        continue
                inline += title[ii]

        return inline

    def _has_math_child(self, node):
        for item in node:
            if isinstance(item, nodes.math):
                return True
        return False

    def _update_ref(self, node: Node, labelid: str) -> None:
        source_attr = self.env.exercise_list[labelid]
        source_node = source_attr.get("node", Node)

        if is_linked_node(source_node):
            default_title = "Solution to "
            target_labelid = source_node.get("target_label", "")
            target_attr = self.env.exercise_list[target_labelid]
            target_node = target_attr.get("node", Node)

            if is_enumerable_node(target_node) and node.astext() == default_title:
                node[0].extend(source_node[0][1][0])
                return

            if is_unenumerable_node(target_node) and node.astext() == default_title:
                if target_attr.get("title"):
                    if self._has_math_child(target_node[0]):
                        title = self._update_title(target_node[0])
                        title.insert(0, nodes.Text(default_title, default_title))
                        node.replace(node[0], title)
                    else:
                        text = target_attr.get("title", "")
                        node[0].insert(len(node[0]), nodes.Text(text, text))
                else:
                    node[0].insert(len(node[0]), nodes.Text("Exercise", "Exercise"))
        else:
            # If no node.astext() simply add "Exercise"
            if is_enumerable_node(source_node) and not node.astext():
                text = nodes.Text("Exercise", "Exercise")
                node[0].insert(0, text)
                return

            if ":math:" in node.astext():
                title = self._update_title(source_node[0])
                node.replace(node[0], title)

    def _update_numref(self, node, labelid):
        source_attr = self.env.exercise_list[labelid]
        source_node = source_attr.get("node", Node)
        node_title = node.get("title", "")

        if "{name}" in node_title and self._has_math_child(source_node[0]):
            newtitle = nodes.inline()
            for item in node_title.split():
                if item == "{name}":
                    # use extend instead?
                    for _ in self._update_title(source_node[0]):
                        newtitle += _
                elif item == "{number}":
                    source_docname = source_attr.get("docname", "")
                    source_type = self.domain.get_enumerable_node_type(source_node)
                    source_number = self.domain.get_fignumber(
                        self.env, self.builder, source_type, source_docname, source_node
                    )
                    source_num = ".".join(map(str, source_number))
                    newtitle += nodes.Text(source_num, source_num)
                else:
                    newtitle += nodes.Text(item, item)
                newtitle += nodes.Text(" ", " ")

            if newtitle[len(newtitle) - 1].astext() == " ":
                newtitle.pop()
            node.replace(node[0], newtitle)

    def _get_refuri(self, node):
        id_ = ""
        if node.get("refuri", ""):
            id_ = node.get("refuri", "")

        if node.get("refid", ""):
            id_ = node.get("refid", "")

        return id_.split("#")[-1]

    def process(self, doctree: nodes.document, docname: str) -> None:

        # # If linked node, update title
        for node in doctree.traverse(linked_node):
            self._update_linked_node_title(node)

        # Traverse ref and numref nodes
        for node in doctree.traverse():

            if not hasattr(self.env, "exercise_list"):
                continue

            # If node type is ref
            if isinstance(node, nodes.reference):
                labelid = self._get_refuri(node)

                # If extension directive referenced
                if labelid in self.env.exercise_list:
                    # Update displayed href text
                    self._update_ref(node, labelid)

            # If node type is numref
            if isinstance(node, number_reference):
                labelid = self._get_refuri(node)

                # If extension directive referenced
                if labelid in self.env.exercise_list:

                    # Update displayed href text
                    self._update_numref(node, labelid)


def setup(app: Sphinx) -> Dict[str, Any]:

    app.add_css_file("exercise.css")
    app.connect("build-finished", copy_asset_files)
    app.connect("config-inited", init_numfig)
    app.connect("env-purge-doc", purge_exercises)
    app.connect("env-merge-info", merge_exercises)
    app.connect("doctree-read", doctree_read)

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
    app.add_directive("solution", SolutionDirective)

    app.connect("doctree-resolved", DoctreeResolve)

    return {
        "version": "builtin",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }


def get_title(self):
    return self[0].astext()
