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

from functools import cache
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
    Entity,
)

SCHEMA_THING = IRI("schema:Thing")
SCHEMA_FILE = IRI("schema:CreativeWork")
SCHEMA_DATASET = IRI("schema:Dataset")

JSONLD_ID = "@id"
JSONLD_TYPE = "@type"

DATASET_ROOT = "https://data.plantphenomics.org.au/"
DATASET_PREFIX = "this"

def at(iri: str) -> dict[str,str]:
    """
    Return dictionary to represent referenced IRI

    :param iri: String for IRI
    :return:    Dictionary for supplied IRI as the id for an object
    """
    return {JSONLD_ID: iri}

class Crate:

    def __init__(self, configuration: Configuration, node: Organisation, name: str) -> None:
        """
        Wrapper to build RO-Crate for APPN dataset

        :param configuration: Configuration settings
        :param node:          `Organisation` owning RO-Crate
        :param name:          Unique name for dataset
        """
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

        # Indexes for uniquely identifying unnamed objects per class (as IRI)
        self.seeds: dict[IRI, int] = {}

        # Keep track of objects already created - map of IRIs to properties
        self.known_instances: dict[IRI, dict[str,str|int|float|dict[str,str]|list[str|int|float|dict[str,str]]]] = {}

        # Keep track of objects already created - map of class IRIs to instances.
        # This includes mappings for all classes included in the @type parameter.
        # This is to allow e.g. a GrowthFacility to be recognised as an
        # ObservationUnit.
        self.known_instances_by_class: dict[IRI, set[IRI]] = {}

        self.files: tuple[Path, str, dict] = []

        return

    def add_folder(self, source: Path, destination: str, properties: Optional[dict[str, str|int|float|list[str|int|float]]] = None, extra_classes: list[str] = None) -> str:
        """
        Add file system folder to RO-Crate (as Dataset)

        :param source:      Path to folder to add
        :param destination: Path inside RO-Crate (as string)
        :param properties:  Dictionary of properties for metadata object
        :return:            Destination string (the id for the object)
        """
        return self.add_file(source, destination, properties, True, extra_classes=extra_classes)

    def add_file(self, source: Path, destination: str, properties: Optional[dict[str, str|int|float|list[str|int|float]]] = None, is_folder: bool = False, extra_classes: list[str] = None) -> str:
        """
        Add file system object (including folder to RO-Crate)

        :param source:      Path to file/folder to add
        :param destination: Path inside RO-Crate (as string)
        :param properties:  Dictionary of properties for metadata object
        :param is_folder:   If true, the object is a `schema:Dataset`
        :return:            Destination string (the id for the object)
        """
        destination = str(destination)
        current_properties: dict[IRI, str|IRI] = {JSONLD_TYPE: SCHEMA_DATASET if is_folder else SCHEMA_FILE}
        
        if properties is not None:
            self.process_properties(SCHEMA_FILE, current_properties, properties)

        self.files.append((source, destination, current_properties, is_folder, extra_classes))
        return destination

    def add(self, class_: str, name: Optional[str] = None, properties: Optional[dict[str, str|int|float|list[str|int|float]]] = None) -> IRI:
        """
        Add an object or update an object in the crate

        This method stores the IRI and current properties in the 
        `known_instances` dictionary. This simplifies potentially 
        adding extra properties later in processing. All instances
        are serialised to the RO-Crate by the `serialise` method.

        The name is used to create the name part of the IRI and to
        recognise references to the same object by class.

        :param class_: The primary class of the object to be added.
        :param name:   The name (label) for the object
        :param properties: Properties and values for the object
        :return: `IRI` for the object
        """
        class_iri = self.find_class(class_)

        seeded = False
        if name is None:
            name = self.seed_name(class_iri)
            seeded = True
                    
        if (iri := self.parse_iri(name)) is None:
            if not seeded:
                if properties is None:
                    properties = {}
                if "name" not in properties:
                    properties["name"] = name
            current_instance = self.find_known_instance(class_iri, name)
            if current_instance is not None:
                iri = current_instance
            else:
                iri = self.dictionary.build_iri(class_iri, self.namespace, name)

        if iri in self.known_instances:
            current_properties = self.known_instances[iri]
        else:
            explicit_classes = []
            for explicit_class in self.dictionary.list_explicit_classes(class_iri):
                explicit_classes.append(explicit_class.name)
                if explicit_class not in self.known_instances_by_class:
                    self.known_instances_by_class[explicit_class] = set()
                self.known_instances_by_class[explicit_class].add(iri)
            current_properties: dict[IRI, str|list[str]] = {JSONLD_TYPE: explicit_classes}
            self.known_instances[iri] = current_properties

        if properties is not None:
            self.process_properties(class_iri, current_properties, properties)

        completion_rules = self.configuration.get_completion_rules_for_class(
            class_iri.name
        )
        if len(completion_rules) > 0:
            for desired_property, rule in completion_rules.items():
                # Current rules are expected to fire only of no instance of the desired
                # property is found - this could be controlled by additional rule
                # properties
                if desired_property not in current_properties:
                    if "type" not in rule:
                        self.logger.log(
                            logging.ERROR,
                            "Configuration",
                            IssueMessage.COMPLETION_RULE_MISSING_TYPE,
                            CONFIGURATION_FILE=self.configuration.configuration_filepath,
                            CONFIGURATION_KEY=ConfigurationKey.COMPLETION_RULES,
                            APPN_SCHEMA_CLASS=target_class.curie,
                            TARGET_PROPERTY=desired_property,
                        )
                        success = False
                    elif rule["type"] == CompletionRuleType.REFLEXIVE.value:
                        # Rules with the type "reflexive" indicate that the IRI should have
                        # a reflexive property linking it to itself.
                        logging.debug(
                            f"Completing iri {iri} with property {desired_property} using rule {rule}"
                        )
                        current_properties[desired_property] = at(iri.iri)
                    else:
                        self.logger.log(
                            logging.ERROR,
                            "Configuration",
                            IssueMessage.COMPLETION_RULE_UNKNOWN_TYPE,
                            CONFIGURATION_FILE=self.configuration.configuration_filepath,
                            CONFIGURATION_KEY=ConfigurationKey.COMPLETION_RULES,
                            APPN_SCHEMA_CLASS=target_class.curie,
                            TARGET_PROPERTY=desired_property,
                            COMPLETION_RULE_TYPE=rule["type"],
                        )
                        success = False

        return iri


    def process_properties(self, class_iri: IRI, current_properties: dict, properties: dict) -> None:
        appn = self.configuration.get_appn()

        for new_property, value in properties.items():
            property_iri = self.find_property(class_iri, new_property)
            if property_iri.prefix in ["schema", "appn"]:
                property_ = property_iri.name
            else:
                property_ = property_iri.iri
            if isinstance(value, str):
                if (value_iri := self.parse_iri(value)) is not None:
                    value = at(value_iri.iri)
                else:
                    range_classes = self.dictionary.list_range_classes_for_property(property_iri, namespace=APPN_SCHEMA)
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
                            current_instance = self.find_known_instance(range_classes[0], value)
                            if current_instance is not None:
                                value = at(current_instance.iri)
                            else:
                                value = at(self.dictionary.build_iri(range_classes[0], self.namespace, value).curie)
                    elif SCHEMA_FILE in self.dictionary.list_range_classes_for_property(property_iri, namespace=SCHEMA_SCHEMA):
                        value = at(value)
            elif isinstance(value, list):
                for i in range(len(value)):
                    if isinstance(value[i], str) and self.parse_iri(value[i]) is not None:
                        value[i] = at(value[i])
            if property_ in current_properties:
                values = current_properties[property_]
                if not isinstance(values, list):
                    values = [values]
                for value in (value if isinstance(value, list) else [value]):
                    if value not in values:
                        values.append(value)
                if len(values) == 1:
                    values = values[0]
                current_properties[property_] = values
            else:
                current_properties[property_] = value

        return

    def serialise(self, ro_crate_folder: Path, properties: dict = None) -> None:
        """
        Write the RO-Crate to disk

        This method uses the `rocrate` package to write the content
        but then rewrites it to include the APPN context.json and to
        use some namespace prefixes for readbility.

        :param ro_crate_folder: Path to folder to contain the RO-Crate
        """
        crate = ROCrate()
        for source, destination, properties, is_folder, extra_classes in self.files:
            if is_folder:
                f = crate.add(Dataset(crate, source=source, dest_path=destination, properties=properties))
            else:
                f = crate.add(File(crate, source=source, dest_path=destination, properties=properties))
            if extra_classes is not None:
                classes = ["Dataset" if is_folder else "CreativeWork"]
                for class_name in extra_classes:
                    class_iri = self.find_class(class_name)
                    if class_iri is not None:
                        classes.append(class_iri.name if class_iri.ns in [APPN_SCHEMA, SCHEMA_SCHEMA] else class_iri.iri)
                f._jsonld["@type"] = classes
        for iri, properties in self.known_instances.items():
            crate.add(ContextEntity(crate, iri.iri, properties))

        if properties is not None:
            crate_properties = crate.default_entities[0].properties()
            crate_properties |= properties 

        crate.write(ro_crate_folder)

        # Make the metadata more readable - this could be a subprocess
        # using sed, but we are avoiding the extra dependency.
        appn = self.configuration.get_appn()
        metadata: list[str] = []
        with open(ro_crate_folder / "ro-crate-metadata.json") as f:
            for line in f.readlines():
                if "@context" in line:
                    metadata.append('    "@context": [\n')
                    metadata.append('         "https://w3id.org/ro/crate/1.2/context",\n')
                    metadata.append('         "https://schema.plantphenomics.org.au/context.json",\n')
                    metadata.append('         {\n')
                    metadata.append(f'             "this": "{self.namespace}",\n')
                    metadata.append(f'             "{self.node.prefix}": "{self.node.namespace}",\n')
                    metadata.append(f'             "{appn.prefix}": "{appn.namespace}"\n')
                    metadata.append('         }\n')
                    metadata.append('    ],\n')
                else:
                    metadata.append(line.replace(self.namespace, "this:").replace(self.node.namespace, f"{self.node.prefix}:").replace(appn.namespace, f"{appn.prefix}:").replace(APPN_SCHEMA, ""))
        with open(ro_crate_folder / "ro-crate-metadata.json", "w") as f:
            f.writelines(metadata)

    @cache
    def find_class(self, class_: str) -> IRI:
        """
        Find `IRI` for class with supplied name

        If the class is unrecognised, log issue and use schema:Thing.

        :param class_: String holding IRI, CURIE or unqualified name for class
        :return: IRI for class
        """
        for namespace in [APPN_SCHEMA, SCHEMA_SCHEMA]:
            namespace_classes = self.dictionary.list_classes(namespace=namespace)
            for namespace_class in namespace_classes:
                if namespace_class.name == class_:
                    return namespace_class

        # TODO - Log unrecognised class
        return SCHEMA_THING 

    def find_known_instance(self, class_iri: IRI, name: str) -> Optional[IRI]:
        """
        Select existing object meeting policy-based criteria as the current
        instance of a class with a given name

        This is a special method to support parsing definitions for objects
        complying with the APPN schema and having a specified name

        The policy is to look for instances of the specified class in the 
        current crate and otherwise in the vocabulary namespace for the 
        current APPN node or (if no such match is found) in the central 
        APPN vocabulary namespace.

        Candidates are evaluated based on the IRI string for each instance.
        The goal is to find an instance for which IRI belongs to the expected
        class (which may mean belonging to a subclass) and that the name part 
        of the IRI ends wuth a cleaned version of the supplied name. Case is 
        ignored when comparing the cleaned name parts, so a request for an 
        instance of the GrowthFacilityType class with any of "glasshouse", 
        "Glasshouse", "GlassHouse", "Glass House", "GLASSHOUSE", etc. provided 
        as the search name will match an instance with an IRI ending "gft_Glasshouse".

        :param class_iri: The class to which the instance should belong
        :param name:      String name for the search
        :return:          Matching instance if found, else None
        """
        iri_name = "_" + self.dictionary.build_clean_name(name).lower()
        if class_iri in self.known_instances_by_class:
            for iri in self.known_instances_by_class[class_iri]:
                if iri.name.lower().endswith(iri_name):
                    return iri

        for namespace in [self.node.namespace, APPN_VOCABULARY]:
            for iri in self.dictionary.list_instances(class_iri, namespace=namespace):
                if iri.name.lower().endswith(iri_name):
                    return iri

        return None

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
        iri = self.dictionary.build_iri(RDF_PROPERTY, self.namespace, property_)
        return iri 

    def parse_iri(self, string: str) -> Optional[IRI]:
        """
        If the supplied string is an IRI or CURIE, return it as an `IRI` object

        :param string: String that may contain an IRI
        :return:       `IRI` or None
        """
        if string.startswith("http"):
            return IRI(string)

        parts = string.split(":")
        if len(parts) == 2 and parts[0] in self.dictionary.get_namespaces():
            return IRI(string)

        return None


    def seed_name(self, class_iri: IRI) -> str:
        """
        Get unique (numeric) name for object within a class

        The name will be prefixed with a class abbreviation before use.

        :param class_iri: Class within which name should be unique
        :return:          Unique string containing next consecutive number
        """
        if class_iri not in self.seeds:
            self.seeds[class_iri] = 1
        else:
            self.seeds[class_iri] = self.seeds[class_iri] + 1
        return f"{self.seeds[class_iri]:07d}"


if __name__ == "__main__":
    configuration = Configuration()
    crate = Crate(configuration, configuration.get_organisation_by_id("LTU"), "MicroTom")
    crate.add("GrowthFacility", "GH123", {"description": "A greenhouse", "hasGrowthFacilityType": "glasshouse"})
    crate.add("GrowthFacility", "GH123", {"lights": "Bright"})
    crate.add_file(Path("appn.yaml"), "./MyFirstFile.txt", {"created": "2026-09-26"} )
    crate.add_folder(Path("schema_assets"), "./Assets", {"created": "2026-09-26"} )
    crate.add("Observation", parameters={"isForObservationUnit": "GH123", "hasResult": "./MyFirstFile.txt"})
    crate.add("Observation", parameters={"isForObservationUnit": "GH123", "hasSimpleResult": 1.2, "observes": "liquid quantity"})
    crate.add("ObservedVariable", "liquid quantity", {"hasScale": "milliliter"})
    crate.add("Scale", "Milliliter")
    crate.serialise(Path("RO-Crate"))