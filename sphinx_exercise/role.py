# -*- coding: utf-8 -*-
"""
    sphinx_exercise.role
    ~~~~~~~~~~~~~~~~~~~~
    This package is a namespace package that contains all extensions
    distributed in the ``sphinx-contrib`` distribution.
    :copyright: Copyright 2007-2009 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
from typing import Tuple, List
from docutils.nodes import Element, Node, document, system_message
from sphinx.environment import BuildEnvironment

from sphinx.roles import XRefRole


class ExerciseXRefRole(XRefRole):
    def result_nodes(
        self, document: document, env: BuildEnvironment, node: Element, is_ref: bool
    ) -> Tuple[List[Node], List[system_message]]:

        return [node], []
