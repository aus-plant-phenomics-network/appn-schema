#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
# test_dictionary.py
#
# Pytest tests for appn_dictionary.py
#
# -----------------------------------------------------------------------------
# Created By  : Donald Hobern, donald.hobern@adelaide.edu.au
# Created Date: 2026-03-31
# version ='2026.0.1'
# -----------------------------------------------------------------------------

import os
from appn_types import NamespaceDefinition
from appn_configuration import (
    Configuration,
    APPN_SCHEMA,
    LTU_VOCABULARY,
)
from appn_dictionary import Dictionary

test_configuration = Configuration()

def test_get_namespaces():
    dictionary = Dictionary(namespace_definitions = test_configuration.get_namespace_definitions())
    dictionary.load(APPN_SCHEMA)
    dictionary.load(LTU_VOCABULARY)
    namespaces = dictionary.get_namespaces()
    assert "appn" in namespaces
    assert "schema" in namespaces
