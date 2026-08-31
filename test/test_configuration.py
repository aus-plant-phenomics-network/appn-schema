#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
# test_configuration.py
#
# Pytest tests for appn_configuration.py
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
    APPN_CONFIGURATION_FOLDER_ENVIRONMENT_KEY,
    APPN_CONFIGURATION_NAME_ENVIRONMENT_KEY,
)


def test_configuration_bad_path():
    caught_error = False
    try:
        Configuration(configuration_folder="MISSING")
    except ValueError:
        caught_error = True
    assert caught_error


def test_configuration_bad_filename():
    caught_error = False
    try:
        Configuration(configuration_name="MISSING")
    except ValueError:
        caught_error = True
    assert caught_error


def test_configuration_bad_environment():
    os.environ[APPN_CONFIGURATION_FOLDER_ENVIRONMENT_KEY] = "./test"
    caught_error = False
    try:
        Configuration()
    except ValueError:
        caught_error = True
    assert caught_error
    os.environ.pop(APPN_CONFIGURATION_FOLDER_ENVIRONMENT_KEY)


def test_configuration_namespaces():
    os.environ[APPN_CONFIGURATION_NAME_ENVIRONMENT_KEY] = "appn-test-1"
    configuration = Configuration(configuration_folder="./test")
    namespaces = configuration.get_namespace_definitions()
    assert "https://test.plantphenomics.org.au/" in namespaces
    assert namespaces["https://test.plantphenomics.org.au/"] == NamespaceDefinition(
        "https://test.plantphenomics.org.au/",
        "test",
        "https://test.plantphenomics.org.au/",
    )
    os.environ.pop(APPN_CONFIGURATION_NAME_ENVIRONMENT_KEY)


def test_configuration_namespace_paths():
    configuration = Configuration(
        configuration_folder="./test", configuration_name="appn-test-2"
    )
    namespaces = configuration.get_namespace_definitions()
    assert "https://test.plantphenomics.org.au/" in namespaces
    assert namespaces["https://test.plantphenomics.org.au/"] == NamespaceDefinition(
        "https://test.plantphenomics.org.au/", "test-2", "./test/test.ttl"
    )
