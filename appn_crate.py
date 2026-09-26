#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
# appn_crate.py - RO-Crate controller
#
# Class for managing metadata additions to RO-Crate
#
# -----------------------------------------------------------------------------
# Created By  : Donald Hobern, donald.hobern@adelaide.edu.au
# Created Date: 2026-09-03
# version ='2026.0.1'
# -----------------------------------------------------------------------------
import logging
import re
import warnings

import numpy as np
import pandas as pd

from pathlib import Path
from typing import Optional, NamedTuple
from appn_iri import IRI
from appn_types import CompletionRuleType
from appn_dictionary import (
    RDF_PROPERTY,
    RDF_TYPE,
    SCHEMA_DESCRIPTION,
    SCHEMA_DOMAIN_INCLUDES,
    SCHEMA_NAME,
    SKOS_CONCEPT,
    SKOS_CONCEPT_SCHEME,
    SKOS_IN_SCHEME,
    Dictionary,
    NAME_REPLACEMENT_PATTERN,
)
from appn_configuration import (
    APPN_VOCABULARY,
    APPN_VOCABULARY_ROOT,
    BIO_SCHEMA,
    CENTRAL_ORGANISATION,
    ConfigurationKey,
    DEFAULT_PREFIXES,
    ExplicitClassesFilter,
    Configuration,
    Organisation,
    APPN_SCHEMA,
    SKOS_SCHEMA,
    SCHEMA_SCHEMA,
    ALT_SCHEMA_SCHEMA,
)
from appn_logger import IssueMessage
from rdflib import Graph, Literal
from rdflib.namespace import Namespace, NamespaceManager
from rocrate.rocrate import ROCrate
from rocrate.model import (
    ComputationalWorkflow,
    SoftwareApplication,
    File,
    Dataset,
    ContextEntity,
    Person,
)

SCHEMA_THING = IRI("schema:Thing")

DATASET_ROOT = "https://data.plantphenomics.org.au/"
DATASET_PREFIX = "this"

class Crate:

    def __init__(self, configuration: Configuration, node: Organisation, name: str) -> None:
        self.configuration = configuration
        self.node = node
        self.name = name

        self.namespace = f"{DATASET_ROOT}{node.id}/{NAME_REPLACEMENT_PATTERN.sub("", name)}/"
        # TODO: Verify uniqueness for namespace

        # The `IssueLogger` for messages to data administrators
        self.logger = configuration.get_logger()

        # The rdflib library generates a warning ("ConjunctiveGraph is deprecated, use Dataset instead")
        warnings.filterwarnings("ignore", category=DeprecationWarning, module="rdflib")

        # The openpyxl library generates a warning ("Data Validation extension is not supported and will be removed")
        warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

        # Load schemas that provide key definitions. APPN_SCHEMA does not
        # directly reference SKOS, so SKOS_SCHEMA is separately loaded, but
        # others are imported based on their use in these two schemas.
        # For any vocabulary other than the central APPN vocabulary, load
        # the central vocabulary so its terms can be checked.
        self.dictionary = Dictionary()
        self.dictionary.load(APPN_SCHEMA)
        self.dictionary.load(SKOS_SCHEMA)
        appn = self.configuration.get_appn()
        self.dictionary.load(appn.namespace, asset_prefix=appn.prefix)
        self.dictionary.load(node.namespace, asset_prefix=node.prefix)
        self.dictionary.import_references()

        self._crate = ROCrate()
        self.seeds: dict[IRI, int] = {}

        self.known_instances: dict[IRI, dict[str, IRI]] = {}

        return

    def add(self, class_: str, name: Optional[str] = None, parameters: Optional[dict[str, str]] = None) -> IRI:
        class_iri = self.find_class(class_)

        if name is None:
            name = self.seed_name(class_iri)

        if (iri := self.parse_iri(name)) is None:
            iri = self.dictionary.build_iri(class_iri, self.node, name)

        properties: dict[IRI, str|IRI] = {RDF_TYPE: [explicit_class for explicit_class in self.dictionary.list_explicit_classes(class_iri)]}
        if parameters is not None:
            for parameter, value in parameters.items():
                property_ = self.find_property(class_iri, parameter)
                if (value_iri := self.parse_iri(value)) is not None:
                    value = value_iri.iri
                else:
                    range_classes = self.dictionary.list_range_classes_for_property(property_, namespace=APPN_SCHEMA)
                    if len(range_classes) > 0:
                        if len(range_classes) > 1:
                            self.logger.log(
                                logging.ERROR,
                                __name__,
                                IssueMessage.RANGE_CLASS_NOT_SELECTED,
                                PROPERY_SUBJECT=iri.curie,
                                DOMAIN_APPN_CLASS=class_iri.curie,
                                SELECTED_PROPERTY=property_.curie,
                                RANGE_CLASSES=", ".join(
                                    [class_.curie for class_ in range_classes]
                                ),
                            )
                            # TODO - Use placeholder property to document the property and value string
                            # Check schema.org
                        else:
                            value = self.dictionary.build_iri(range_classes[0], self.node, value).iri
                if property_ in properties:
                    if isinstance(properties[property_], str):
                        properties[property_] = [properties[property_], value]
                    else:
                        properties[property_].append(value)
                else:
                    properties[property_] = value

        print(f"{iri}\n{'\n'.join([f'    {p} : {v}' for p, v in properties.items()])}")

        return iri

    def find_class(self, class_: str) -> IRI:
        """
        Find `IRI` for class with supplied name

        If the class is unrecognised, log issue and use schema:Thing.

        :param class_: String holding IRI, CURIE or unqualified name for class
        :return: IRI for class
        """
        appn_classes = self.dictionary.list_classes(namespace=APPN_SCHEMA)
        for appn_class in appn_classes:
            if appn_class.name == class_:
                return appn_class

        # TODO - Log unrecognised class
        return SCHEMA_THING 


    def find_property(self, class_iri: IRI, property_: str) -> IRI:
        """
        Find `IRI` for property with supplied name

        Where applicable, uses the domain class as a hint.

        If the property is unrecognised, log issue and create new local property.

        :param class_iri: IRI for domain class
        :param property_: String holding IRI, CURIE or unqualified name for property
        :return: IRI for property
        """
        # Look for properties which include the current class as their
        # domain. If no such property exists with the specified name, a matching
        # will be selected from one of the namespaces specified in the configuration
        # (in descending order of precedence).
        iri = self.parse_iri(property_)
        if iri is not None:
            return iri

        for iri in self.dictionary.list_domain_properties_for_class(class_iri):
            if iri.name == property_:
                return iri

        for s in self.configuration.get_vocabulary_column_namespaces():
            for iri in self.dictionary.list_properties(namespace=s):
                if iri.name == property_:
                    return iri

        # TODO - Log unrecognised property
        iri = self.dictionary.build_iri(RDF_PROPERTY, self.node, property_)
        return iri 

    def parse_iri(self, string: str) -> Optional[IRI]:
        if string.startswith("http"):
            return IRI(string)

        parts = string.split(":")
        if len(parts) == 2 in parts[0] in self.dictionary.get_namespaces():
            return IRI(string)

        return None


    def seed_name(self, class_iri: IRI, name: str) -> str:
        if class_iri not in self.seeds:
            self.seeds[class_iri] = 1
        else:
            self.seeds[class_iri] = self.seeds[class_iri] + 1
        return f"{self.configuration.get_class_abbreviation(class_iri.name)}_{self.seeds[class_iri]:07d}"


if __name__ == "__main__":
    configuration = Configuration()
    crate = Crate(configuration, configuration.get_organisation_by_id("LTU"), "MicroTom")
    crate.add("GrowthFacility", "GH123", {"description": "A greenhouse", "hasGrowthFacilityType": "glasshouse"})