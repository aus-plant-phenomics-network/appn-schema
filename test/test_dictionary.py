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
dictionary = Dictionary()
dictionary.load(APPN_SCHEMA)
dictionary.load(LTU_VOCABULARY)

def test_get_namespaces():
    namespaces = dictionary.get_namespaces()
    assert "appn" in namespaces
    assert "schema" in namespaces

def test_get_superclasses():
    curies = [s.curie for s in dictionary.list_superclasses("appn:Observation")]
    assert "appn:Assay" in curies
    assert "appn:Observation" in curies
    assert "schema:Action" in curies
    assert "schema:Sampling" not in curies
