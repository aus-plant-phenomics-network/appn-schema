#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
# appn_configuration.py
#
# Access to context variables for APPN tools
#
# -----------------------------------------------------------------------------
# Created By  : Donald Hobern, donald.hobern@adelaide.edu.au
# Created Date: 2026-03-31
# version ='2026.0.1'
# -----------------------------------------------------------------------------
import yaml
import os
import logging
from pathlib import Path
from typing import Optional
from appn_types import NamespaceDefinition, Organisation
from rdflib import URIRef

# Default values for finding YAML configuration file
APPN_DEFAULT_CONFIGURATION_FOLDER = Path("./")
APPN_DEFAULT_CONFIGURATION_NAME = "appn"

# Environment keys to access local settings for YAML configuration file
APPN_CONFIGURATION_FOLDER_ENVIRONMENT_KEY = "APPN_CONFIGURATION_FOLDER"
APPN_CONFIGURATION_NAME_ENVIRONMENT_KEY = "APPN_CONFIGURATION_NAME"

# Keys for elements expected in YAML configuration file
CONFIGURATION_KEY_NAMESPACE_PATHS = "namespace_paths"
CONFIGURATION_KEY_VOCABULARY_COLUMN_NAMESPACES = "vocabulary_column_namespaces"
CONFIGURATION_KEY_EXPLICIT_CLASSES = "explicit_classes"
CONFIGURATION_KEY_EXCLUDED_CLASSES = "excluded_classes"
CONFIGURATION_KEY_SHEET_ALIASES = "sheet_aliases"
CONFIGURATION_KEY_COLUMN_ALIASES = "column_aliases"
CONFIGURATION_KEY_COMPLETION_RULES = "completion_rules"
CONFIGURATION_KEY_CLASS_ABBREVIATIONS = "class_abbreviations"
CONFIGURATION_KEY_PROPERTY_EXPANSIONS = "property_expansions"
CONFIGURATION_KEY_EMBEDDED_CLASSES = "embedded_classes"
CONFIGURATION_KEY_ORGANISATIONS = "organisations"

# Recognised values for namespaces in explicit classes element
EXPLICIT_CLASSES_ALL = "all"
EXPLICIT_CLASSES_FIRST = "first"

# Keys for elements in definitions in organisations element
ORGANISATION_SUBKEY_NAME = "name"
ORGANISATION_SUBKEY_ROR = "ror"
ORGANISATION_SUBKEY_NAMESPACE = "namespace"
ORGANISATION_SUBKEY_PREFIX = "prefix"

# Default settings for central organisation (i.e. APPN)
CENTRAL_ORGANISATION = "APPN"
DEFAULT_CENTRAL_VOCABULARY_PREFIX = "appnid"

# Standard APPN namespace URLs
APPN_SCHEMA = "https://schema.plantphenomics.org.au/"
# NOTE: Schema.org publishes versions using both HTTP and HTTPS - we 
# use HTTPS which seems to be most widely used.
SCHEMA_SCHEMA = "https://schema.org/"
BIO_SCHEMA = "https://bioschemas.org/terms/"
CDI_SCHEMA = "http://ddialliance.org/Specification/DDI-CDI/1.0/RDF/"
DC_SCHEMA = "http://purl.org/dc/terms/"
PPEO_SCHEMA = "http://purl.org/ppeo/PPEO.owl#"
PROV_SCHEMA = "http://www.w3.org/ns/prov#"
RDF_SCHEMA = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
RDFS_SCHEMA = "http://www.w3.org/2000/01/rdf-schema#"
SKOS_SCHEMA = "http://www.w3.org/2004/02/skos/core#"
SOSA_SCHEMA = "http://www.w3.org/ns/sosa/"
SSN_SCHEMA = "http://www.w3.org/ns/ssn/"

# Namespaces for APPN central and node vocabularies
APPN_VOCABULARY_ROOT = "https://id.plantphenomics.org.au/"
APPN_VOCABULARY = f"{APPN_VOCABULARY_ROOT}APPN/"
ANU_VOCABULARY = f"{APPN_VOCABULARY_ROOT}ANU/"
AU_VOCABULARY = f"{APPN_VOCABULARY_ROOT}AU/"
CSU_VOCABULARY = f"{APPN_VOCABULARY_ROOT}CSU/"
DPIRD_VOCABULARY = f"{APPN_VOCABULARY_ROOT}DPIRD/"
LTU_VOCABULARY = f"{APPN_VOCABULARY_ROOT}LTU/"
UQ_VOCABULARY = f"{APPN_VOCABULARY_ROOT}UQ/"
USYD_VOCABULARY = f"{APPN_VOCABULARY_ROOT}USYD/"
UWA_VOCABULARY = f"{APPN_VOCABULARY_ROOT}UWA/"
WSU_VOCABULARY = f"{APPN_VOCABULARY_ROOT}WSU/"

# Dictionary of default prefixes to use in APPN linked data
DEFAULT_PREFIXES = {
    APPN_SCHEMA: "appn",
    SCHEMA_SCHEMA: "schema",
    CDI_SCHEMA: "cdi",
    DC_SCHEMA: "dcterms",
    PPEO_SCHEMA: "ppeo",
    RDF_SCHEMA: "rdf",
    RDFS_SCHEMA: "rdfs",
    SKOS_SCHEMA: "skos",
    PROV_SCHEMA: "prov",
    SOSA_SCHEMA: "sosa",
    SSN_SCHEMA: "ssn",
    BIO_SCHEMA: "bio",
    APPN_VOCABULARY: "appnid",
    ANU_VOCABULARY: "anu",
    AU_VOCABULARY: "au",
    CSU_VOCABULARY: "csu",
    DPIRD_VOCABULARY: "dpird",
    LTU_VOCABULARY: "ltu",
    UQ_VOCABULARY: "uq",
    USYD_VOCABULARY: "usyd",
    UWA_VOCABULARY: "uwa",
    WSU_VOCABULARY: "wsu",
}

### Configuration #############################################################

class Configuration:
    """
    Class to access configuration settings for APPN code.
    
    Configuration elements are read from a YAML file for which the folder and
    name can be overridden with environment variables. The default is 
    "./appn.yaml".

    Access methods always receive a copy of any lists or dictionaries 
    returned so the configuration is not affected by any changes.

    NOTE: The access methods could be hardened to check the types and 
    contents of the YAML data.
    """

    def __init__(
        self,
        configuration_folder: Optional[Path | str] = None,
        configuration_name: Optional[str] = None,
    ) -> None:
        """
        Read configuration from YAML file

        :param configuration_folder: Folder location containing YAML file
        :param configuration_name: Name of YAML file (with or without yaml extension)
        """

        # The severity of errors reported depends on whether an explicit location was
        # offered or defaults used.
        defaults_overridden = (
            configuration_folder is not None or configuration_name is not None
        )

        # Safe defaults if nothing is read
        self.namespace_definitions = None
        self.configuration = {}

        # Use supplied folder or folder from environment or default
        if configuration_folder is None:
            if APPN_CONFIGURATION_FOLDER_ENVIRONMENT_KEY in os.environ:
                self.configuration_folder = Path(
                    os.environ[APPN_CONFIGURATION_FOLDER_ENVIRONMENT_KEY]
                )
                defaults_overridden = True
            else:
                self.configuration_folder = Path(APPN_DEFAULT_CONFIGURATION_FOLDER)
        else:
            self.configuration_folder = Path(configuration_folder)
        logging.debug(f"Configuration folder: {self.configuration_folder}")

        # Use supplied filename or filename from environment or default
        if configuration_name is None:
            if APPN_CONFIGURATION_NAME_ENVIRONMENT_KEY in os.environ:
                configuration_name = os.environ[APPN_CONFIGURATION_NAME_ENVIRONMENT_KEY]
                defaults_overridden = True
            else:
                configuration_name = APPN_DEFAULT_CONFIGURATION_NAME
        if not configuration_name.lower().endswith(".yaml"):
            configuration_name = f"{configuration_name}.yaml"
        logging.debug(f"Configuration name: {configuration_name}")

        # Validate folder
        if not self.configuration_folder.exists():
            message = f"Configuration folder {self.configuration_folder} does not exist"
            if defaults_overridden:
                logging.error(message)
                raise ValueError(message)
            else:
                logging.debug(message)
                return

        # Validate file
        self.configuration_filepath = self.configuration_folder / configuration_name
        if not self.configuration_filepath.exists():
            message = f"Configuration file {self.configuration_filepath} does not exist"
            if defaults_overridden:
                logging.error(message)
                raise ValueError(message)
            else:
                logging.debug(message)
                return

        # Load configuration from file
        with open(self.configuration_filepath, "r") as stream:
            try:
                logging.debug(f"Loading configuration: {self.configuration_filepath}")
                self.configuration = yaml.safe_load(stream)
                logging.debug(f"Loaded configuration: \n{self.configuration}")
            except yaml.YAMLError as exc:
                logging.error(f"config.load: {str(exc)}")
                raise ValueError(
                    f"Failed to load configuration from {self.configuration_filepath}"
                )

        # Organisations element requires parsing before use - only do this when
        # requested
        self.organisations = None

        return

    def get_namespace_definitions(self) -> dict[str, NamespaceDefinition]:
        """
        Return `NamespaceDefinition`s from configuration

        `NamespaceDefinitions` include the namespace, preferred namespace
        prefix and path for accessing a machine-readable version of the 
        definitions in the namespace.

        The namespaces and prefixes are defined by `DEFAULT_PREFIXES`. 
        Any paths are set via the `namespace_paths` key in the YAML
        configuration.

        :return: Dictionary of `NameDefinition` objects keyed by the 
            namespace string
        """
        # Cache the definitions since these are built from configuration
        # information combined with defaults where necessary.
        if self.namespace_definitions is not None:
            return self.namespace_definitions.copy()

        # Find any configured namespace paths (locations for schema assets).
        # Assets without paths will be only be loadable by using the namespace 
        # as a URL.
        
        if CONFIGURATION_KEY_NAMESPACE_PATHS in self.configuration and isinstance(
            self.configuration[CONFIGURATION_KEY_NAMESPACE_PATHS], dict
        ):
            paths = self.configuration[CONFIGURATION_KEY_NAMESPACE_PATHS]
            logging.debug(f"Imported namespace paths: {paths}")
        else:
            paths = {}

        # Build the namespace definitions for all default namespaces, taking
        # into account the configured namespace paths.
        self.namespace_definitions = {
            ns: NamespaceDefinition(ns, pre, paths[ns] if ns in paths else ns)
            for ns, pre in DEFAULT_PREFIXES.items()
        }

        return self.namespace_definitions.copy()

    def get_vocabulary_column_namespaces(self) -> list[str]:
        """
        Get list of namespaces to search for mapping spreadsheet columns.

        The `column_namespaces` list controls the eligibility of namespaces
        to serve as the source of properties matching spreadsheet column 
        names. The namespaces will be checked in the supplied order to 
        find a property with a name exactly matching a column heading.
        Properties from the APPN schema will automatically be checked.
        Unmatched names will be converted into locally defined properties.

        The list should contain schema.org, SKOS Core and Dublin Core.

        Returns a copy of any list included in the YAML configuration.

        :return: List of namespace strings
        """
        if CONFIGURATION_KEY_VOCABULARY_COLUMN_NAMESPACES in self.configuration:
            return self.configuration[
                CONFIGURATION_KEY_VOCABULARY_COLUMN_NAMESPACES
            ].copy()
        return []

    def get_explicit_classes(self) -> dict[str, str | list[str]]:
        """
        Get dictionary of additional classes that should explicitly be 
        specified when applicable

        The APPN schema inherits from classes in several other schemas.
        Users of the data may benefit if the classes they expect are 
        explicitly identified via `rdf:type` for all instances of any
        relevant APPN class.

        The `explicit_classes` list identifies namespaces that should be
        included as additional `rdf:type` statements. For each such
        namespace, a list of specific classes for inclusion may be 
        supplied, or the keyword "all" (indicating any relevant class 
        from the schema) or the keyword "first" (indicating the class
        from the schema that is closest in the superclass hierarchy to
        the APPN class being assigned.
        
        The expected behaviour is that, when an instance of an APPN 
        class is created, the known superclasses of the APPN class should
        be scanned for classes that match any of these rules, and extra
        `rdf:type` statements should be added for each match.

        Returns a copy of any dictionary included in the YAML configuration.

        :return: List of namespace strings
        """
        if CONFIGURATION_KEY_EXPLICIT_CLASSES in self.configuration:
            return self.configuration[CONFIGURATION_KEY_EXPLICIT_CLASSES].copy()
        return {}

    def get_excluded_classes(self) -> list[str]:
        if CONFIGURATION_KEY_EXCLUDED_CLASSES in self.configuration:
            return self.configuration[CONFIGURATION_KEY_EXCLUDED_CLASSES].copy()
        return []

    def get_sheet_aliases(self) -> dict[str, str]:
        if CONFIGURATION_KEY_SHEET_ALIASES in self.configuration:
            return self.configuration[CONFIGURATION_KEY_SHEET_ALIASES].copy()
        return {}

    def get_column_aliases(self) -> dict[str, str]:
        if CONFIGURATION_KEY_COLUMN_ALIASES in self.configuration:
            return self.configuration[CONFIGURATION_KEY_COLUMN_ALIASES].copy()
        return {}

    def get_completion_rules(self) -> dict[str, dict[str, dict[str, str]]]:
        if CONFIGURATION_KEY_COMPLETION_RULES in self.configuration:
            return self.configuration[CONFIGURATION_KEY_COMPLETION_RULES].copy()
        return {}

    def get_completion_rules(self, class_name: str) -> dict[str, dict[str, str]]:
        if CONFIGURATION_KEY_COMPLETION_RULES in self.configuration and class_name in self.configuration[CONFIGURATION_KEY_COMPLETION_RULES]:
            return self.configuration[CONFIGURATION_KEY_COMPLETION_RULES][class_name].copy()
        return {}

    def get_class_abbreviations(self) -> dict[str, str]:
        if CONFIGURATION_KEY_CLASS_ABBREVIATIONS in self.configuration:
            return self.configuration[CONFIGURATION_KEY_CLASS_ABBREVIATIONS].copy()
        return {}

    def get_property_expansions(self) -> dict[URIRef, list[URIRef]]:
        expansions = {}
        if CONFIGURATION_KEY_PROPERTY_EXPANSIONS in self.configuration:
            for k, v in self.configuration[
                CONFIGURATION_KEY_PROPERTY_EXPANSIONS
            ].items():
                expansions[URIRef(k)] = [URIRef(e) for e in v]
        return expansions

    def get_embedded_classes(self) -> dict[str, list[str]]:
        if CONFIGURATION_KEY_EMBEDDED_CLASSES in self.configuration:
            return self.configuration[CONFIGURATION_KEY_EMBEDDED_CLASSES].copy()
        return {}

    def get_organisations(self) -> dict[str, Organisation]:
        if self.organisations is None:
            self.organisations = {}
            if CONFIGURATION_KEY_ORGANISATIONS in self.configuration:
                for id, properties in self.configuration[
                    CONFIGURATION_KEY_ORGANISATIONS
                ].items():
                    name = str(
                        properties[ORGANISATION_SUBKEY_NAME]
                        if ORGANISATION_SUBKEY_NAME in properties
                        else None
                    )
                    ror = str(
                        properties[ORGANISATION_SUBKEY_ROR]
                        if ORGANISATION_SUBKEY_ROR in properties
                        else None
                    )
                    namespace = str(
                        properties[ORGANISATION_SUBKEY_NAMESPACE]
                        if ORGANISATION_SUBKEY_NAMESPACE in properties
                        else f"{APPN_VOCABULARY_ROOT}{id}/"
                    )
                    prefix = str(
                        properties[ORGANISATION_SUBKEY_PREFIX]
                        if ORGANISATION_SUBKEY_PREFIX in properties
                        else (DEFAULT_CENTRAL_VOCABULARY_PREFIX if id == CENTRAL_ORGANISATION else id.lower())
                    )
                    self.organisations[id] = Organisation(id, name, ror, namespace, prefix)
            if CENTRAL_ORGANISATION not in self.organisations:
                self.organisations[CENTRAL_ORGANISATION] = Organisation(CENTRAL_ORGANISATION, "Australian Plant Phenomics Network", "https://ror.org/02zj7b759", APPN_VOCABULARY, DEFAULT_PREFIXES[APPN_VOCABULARY])
        return self.organisations.copy()

    def get_organisation_by_id(self, id: str) -> Optional[Organisation]:
        organisations = self.get_organisations()
        if id in organisations:
            return organisations[id]
        return None

    def get_appn(self) -> Organisation:
        return self.get_organisation_by_id(CENTRAL_ORGANISATION)