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

def test_single_class_in_sheet():
    configuration = Configuration(configuration_folder="./test", configuration_name="appn-test-parser")
    parser = ExcelVocabularyParser(configuration, configuration.get_appn())
    assert parser.load(Path("./test/appn-simple.xlsx"))
    dictionary = Dictionary(parser.get_graph())
    assert [subject.name for subject in dictionary.list_unique_subjects()] == ["biologicalmaterial_AnyPlant", "biologicalmaterial_Grain", "conceptscheme_BiologicalMaterial", "conceptscheme_ObservedVariable", "observedvariable_GrowthStage", "observedvariable_OverallStature"]
    assert len(dictionary.list_triples_for_property("appn:forBiologicalMaterial")) == 0

def test_referenced_class_in_sheet():
    configuration = Configuration(configuration_folder="./test", configuration_name="appn-test-parser")
    parser = ExcelVocabularyParser(configuration, configuration.get_appn())
    assert parser.load(Path("./test/appn-reference.xlsx"))
    dictionary = Dictionary(parser.get_graph())
    assert [subject.name for subject in dictionary.list_unique_subjects()] == ["biologicalmaterial_AnyPlant", "biologicalmaterial_Grain", "conceptscheme_BiologicalMaterial", "conceptscheme_ObservedVariable", "observedvariable_GrowthStage", "observedvariable_OverallStature"]
    assert len(dictionary.list_triples_for_property("appn:forBiologicalMaterial")) == 2

def test_embedded_class_in_sheet():
    configuration = Configuration(configuration_folder="./test", configuration_name="appn-test-parser")
    parser = ExcelVocabularyParser(configuration, configuration.get_appn())
    assert parser.load(Path("./test/appn-embedded.xlsx"))
    dictionary = Dictionary(parser.get_graph())
    assert [subject.name for subject in dictionary.list_unique_subjects()] == ["biologicalmaterial_AnyPlant", "conceptscheme_BiologicalMaterial", "conceptscheme_ObservedVariable", "observedvariable_GrowthStage", "observedvariable_OverallStature"]
    assert len(dictionary.list_triples_for_property("appn:forBiologicalMaterial")) == 2
