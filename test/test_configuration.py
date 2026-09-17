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

import logging
import pytest
import os
from appn_logger import IssueLogger
from appn_types import NamespaceDefinition
from appn_configuration import (
    Configuration,
    APPN_CONFIGURATION_FOLDER_ENVIRONMENT_KEY,
    APPN_CONFIGURATION_NAME_ENVIRONMENT_KEY,
    APPN_SCHEMA,
    SKOS_SCHEMA,
)

@pytest.fixture()
def mock_configuration() -> Configuration:
    """
    Return configuration with sample settings for all keys
    """
    os.environ[APPN_CONFIGURATION_NAME_ENVIRONMENT_KEY] = "appn-test-main"
    os.environ[APPN_CONFIGURATION_FOLDER_ENVIRONMENT_KEY] = "./test"
    configuration = Configuration()
    os.environ.pop(APPN_CONFIGURATION_NAME_ENVIRONMENT_KEY)
    os.environ.pop(APPN_CONFIGURATION_FOLDER_ENVIRONMENT_KEY)
    return configuration

def test_configuration_bad_environment():
    """
    ValueError is expected if a bad configuration path is supplied
    """
    os.environ[APPN_CONFIGURATION_FOLDER_ENVIRONMENT_KEY] = "./test"
    caught_error = False
    try:
        Configuration()
    except ValueError:
        caught_error = True
    assert caught_error
    os.environ.pop(APPN_CONFIGURATION_FOLDER_ENVIRONMENT_KEY)


def test_configuration_namespaces():
    """
    Check loading of a namespace with prefix
    """
    os.environ[APPN_CONFIGURATION_NAME_ENVIRONMENT_KEY] = "appn-test-1"
    os.environ[APPN_CONFIGURATION_FOLDER_ENVIRONMENT_KEY] = "./test"
    configuration = Configuration()
    namespaces = configuration.get_namespace_definitions()
    assert "https://test.plantphenomics.org.au/" in namespaces
    assert namespaces["https://test.plantphenomics.org.au/"] == NamespaceDefinition(
        "https://test.plantphenomics.org.au/",
        "test",
        "https://test.plantphenomics.org.au/",
    )
    os.environ.pop(APPN_CONFIGURATION_NAME_ENVIRONMENT_KEY)
    os.environ.pop(APPN_CONFIGURATION_FOLDER_ENVIRONMENT_KEY)


def test_configuration_namespace_paths(mock_configuration: Configuration) -> None:
    """
    Check loading of a configuration with a namespace, prefix and path
    """
    os.environ[APPN_CONFIGURATION_NAME_ENVIRONMENT_KEY] = "appn-test-2"
    os.environ[APPN_CONFIGURATION_FOLDER_ENVIRONMENT_KEY] = "./test"
    configuration = Configuration()
    namespaces = configuration.get_namespace_definitions()
    assert "https://test.plantphenomics.org.au/" in namespaces
    assert namespaces["https://test.plantphenomics.org.au/"] == NamespaceDefinition(
        "https://test.plantphenomics.org.au/", "test-2", "./test/test.ttl"
    )
    os.environ.pop(APPN_CONFIGURATION_NAME_ENVIRONMENT_KEY)
    os.environ.pop(APPN_CONFIGURATION_FOLDER_ENVIRONMENT_KEY)

def test_logger(mock_configuration: Configuration) -> None:
    """
    Check access to APPN Logger
    """
    logger = mock_configuration.get_logger()
    assert isinstance(logger, IssueLogger)
    logger.log(logging.INFO, __name__, "This is just a test", not_for_real=True)
    assert logger.get_issue_counts_by_message()["This is just a test"] == 1
    assert logger.list_issues(logging.INFO, module=__name__, message="This is just a test")[0].properties["not_for_real"]

def test_namespace_definitions(mock_configuration: Configuration) -> None:
    """
    Check get_namespace_definitions
    """
    namespace_definitions = mock_configuration.get_namespace_definitions()
    assert namespace_definitions is not None
    assert APPN_SCHEMA in namespace_definitions
    assert "https://phenomicstest.com/" not in namespace_definitions

def test_vocabulary_column_namespaces(mock_configuration: Configuration) -> None:
    """
    Check get_vocabulary_column_namespaces
    """
    vocabulary_column_namespaces = mock_configuration.get_vocabulary_column_namespaces()
    assert vocabulary_column_namespaces is not None
    assert SKOS_SCHEMA in vocabulary_column_namespaces


def test_explicit_classes(mock_configuration: Configuration) -> None:
    """
    Check get_explicit_classes
    """
    explicit_classes = mock_configuration.get_explicit_classes()
    assert explicit_classes is not None

def test_excluded_classes(mock_configuration: Configuration) -> None:
    """
    Check get_excluded_classes
    """
    excluded_classes = mock_configuration.get_excluded_classes()
    assert excluded_classes is not None

def test_sheet_aliases(mock_configuration: Configuration) -> None:
    """
    Check get_sheet_aliases
    """
    sheet_aliases = mock_configuration.get_sheet_aliases()
    assert sheet_aliases is not None

def test_column_aliases(mock_configuration: Configuration) -> None:
    """
    Check get_column_aliases
    """
    column_aliases = mock_configuration.get_column_aliases()
    assert column_aliases is not None

def test_completion_rules(mock_configuration: Configuration) -> None:
    """
    Check get_completion_rules
    """
    completion_rules = mock_configuration.get_completion_rules()
    assert completion_rules is not None

def test_completion_rules_for_class(mock_configuration: Configuration) -> None:
    """
    Check get_completion_rules_for_class
    """
    completion_rules_for_class = mock_configuration.get_completion_rules_for_class("appn:ObservedVariable")
    assert completion_rules_for_class is not None

def test_class_abbreviations(mock_configuration: Configuration) -> None:
    """
    Check get_class_abbreviations
    """
    class_abbreviations = mock_configuration.get_class_abbreviations()
    assert class_abbreviations is not None

def test_property_expansions(mock_configuration: Configuration) -> None:
    """
    Check get_property_expansions
    """
    property_expansions = mock_configuration.get_property_expansions()
    assert property_expansions is not None

def test_embedded_classes(mock_configuration: Configuration) -> None:
    """
    Check get_embedded_classes
    """
    embedded_classes = mock_configuration.get_embedded_classes()
    assert embedded_classes is not None

def test_domain_range_properties(mock_configuration: Configuration) -> None:
    """
    Check get_domain_range_properties
    """
    domain_range_properties = mock_configuration.get_domain_range_properties()
    assert domain_range_properties is not None

def test_property_range_classes(mock_configuration: Configuration) -> None:
    """
    Check get_property_range_classes
    """
    property_range_classes = mock_configuration.get_property_range_classes()
    assert property_range_classes is not None

def test_organisations(mock_configuration: Configuration) -> None:
    """
    Check get_organisations
    """
    organisations = mock_configuration.get_organisations()
    assert organisations is not None

def test_organisation_by_id(mock_configuration: Configuration) -> None:
    """
    Check get_organisation_by_id
    """
    organisation_by_id = mock_configuration.get_organisation_by_id("LTU")
    assert organisation_by_id is not None

def test_appn(mock_configuration: Configuration) -> None:
    """
    Check get_appn
    """
    appn = mock_configuration.get_appn()
    assert appn is not None

