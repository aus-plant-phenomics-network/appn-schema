#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
# test_configuration.py
#
# Pytest tests for appn_parser.py
#
# -----------------------------------------------------------------------------
# Created By  : Donald Hobern, donald.hobern@adelaide.edu.au
# Created Date: 2026-09-08
# version ='2026.0.1'
# -----------------------------------------------------------------------------

import os
import warnings
import pytest

from pathlib import Path
from appn_types import NamespaceDefinition
from appn_configuration import (
    Configuration,
    APPN_CONFIGURATION_FOLDER_ENVIRONMENT_KEY,
    APPN_CONFIGURATION_NAME_ENVIRONMENT_KEY,
    CENTRAL_ORGANISATION
)
from appn_dictionary import Dictionary
from appn_parser import ExcelVocabularyParser

@pytest.fixture()
def mock_parser() -> ExcelVocabularyParser:
    os.environ[APPN_CONFIGURATION_NAME_ENVIRONMENT_KEY] = "appn-test-parser"
    os.environ[APPN_CONFIGURATION_FOLDER_ENVIRONMENT_KEY] = "./test"
    configuration = Configuration()
    mock_parser = ExcelVocabularyParser(configuration, configuration.get_appn())
    os.environ.pop(APPN_CONFIGURATION_NAME_ENVIRONMENT_KEY)
    os.environ.pop(APPN_CONFIGURATION_FOLDER_ENVIRONMENT_KEY)
    return mock_parser

def test_single_class_in_sheet(mock_parser: ExcelVocabularyParser) -> None:
    """
    Test parsing of Excel spreadsheet with wholly discrete sheets for each class and cross-reference by property
    """
    assert mock_parser.load(Path("./test/appn-simple.xlsx"))
    dictionary = Dictionary(mock_parser.get_graph())
    assert [subject.name for subject in dictionary.list_unique_subjects()] == ["bm_AnyPlant", "bm_Grain", "cs_BiologicalMaterial", "cs_ObservedVariable", "ov_GrowthStage", "ov_OverallStature"]
    assert len(dictionary.list_triples_for_property("appn:forBiologicalMaterial")) == 2

def test_referenced_class_in_sheet(mock_parser: ExcelVocabularyParser) -> None:
    """
    Test parsing of Excel spreadsheet with Biological Material class referenced by name in the Trait sheet
    """
    assert mock_parser.load(Path("./test/appn-reference.xlsx"))
    dictionary = Dictionary(mock_parser.get_graph())
    assert [subject.name for subject in dictionary.list_unique_subjects()] == ["bm_AnyPlant", "bm_Grain", "cs_BiologicalMaterial", "cs_ObservedVariable", "ov_GrowthStage", "ov_OverallStature"]
    assert len(dictionary.list_triples_for_property("appn:forBiologicalMaterial")) == 2

def test_embedded_class_in_sheet(mock_parser: ExcelVocabularyParser) -> None:
    """
    Test parsing of Excel spreadsheet with Biological Material class completely embedded in the Trait sheet
    """
    # Configuration won't be reloaded, so hack the dictionary in the parser
    mock_parser.embedded_classes = {"ObservedVariable": ["BiologicalMaterial"]}
    assert mock_parser.load(Path("./test/appn-embedded.xlsx"))
    dictionary = Dictionary(mock_parser.get_graph())
    assert [subject.name for subject in dictionary.list_unique_subjects()] == ["bm_AnyPlant", "bm_Grain", "cs_BiologicalMaterial", "cs_ObservedVariable", "ov_GrowthStage", "ov_OverallStature"]
    assert len(dictionary.list_triples_for_property("appn:forBiologicalMaterial")) == 2
