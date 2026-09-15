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
from enum import StrEnum
from pathlib import Path
from typing import Optional, Any
from appn_types import NamespaceDefinition, Organisation
from appn_logger import IssueLogger, IssueMessage
from rdflib import URIRef

# Default values for finding YAML configuration file
APPN_DEFAULT_CONFIGURATION_FOLDER = Path("./")
APPN_DEFAULT_CONFIGURATION_NAME = "appn"

# Environment keys to access local settings for YAML configuration file
APPN_CONFIGURATION_FOLDER_ENVIRONMENT_KEY = "APPN_CONFIGURATION_FOLDER"
APPN_CONFIGURATION_NAME_ENVIRONMENT_KEY = "APPN_CONFIGURATION_NAME"

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
DWC_SCHEMA = "http://rs.tdwg.org/dwc/terms/"
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
DEFAULT_PREFIXES: dict[str, str] = {
    APPN_SCHEMA: "appn",
    SCHEMA_SCHEMA: "schema",
    CDI_SCHEMA: "cdi",
    DC_SCHEMA: "dcterms",
    DWC_SCHEMA: "dwc",
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


### ConfigurationKey ##########################################################


class ConfigurationKey(StrEnum):
    """
    Simple class to define expected YAML keys.
    """

    NAMESPACE_PATHS = "namespace_paths"
    NAMESPACE_PREFIXES = "namespace_prefixes"
    VOCABULARY_COLUMN_NAMESPACES = "vocabulary_column_namespaces"
    EXPLICIT_CLASSES = "explicit_classes"
    EXCLUDED_CLASSES = "excluded_classes"
    SHEET_ALIASES = "sheet_aliases"
    COLUMN_ALIASES = "column_aliases"
    COMPLETION_RULES = "completion_rules"
    CLASS_ABBREVIATIONS = "class_abbreviations"
    PROPERTY_EXPANSIONS = "property_expansions"
    EMBEDDED_CLASSES = "embedded_classes"
    DOMAIN_RANGE_PROPERTIES = "domain_range_properties"
    PROPERTY_RANGE_CLASSES = "property_range_classes"
    ORGANISATIONS = "organisations"


### ExplicitClassesFilter #####################################################


class ExplicitClassesFilter(StrEnum):
    """
    Simple class to define special options for `explicit_classes` filters
    """

    ALL = "all"
    FIRST = "first"


### OrganisationProperty ######################################################


class OrganisationProperty(StrEnum):
    """
    Simple class for property names in organisation definitions
    """

    NAME = "name"
    ROR = "ror"
    NAMESPACE = "namespace"
    PREFIX = "prefix"


### ValidationType ############################################################


class ValidationType(StrEnum):
    """
    Simple class to define expected YAML structures.
    """

    LIST = "list[str]"
    DICT = "dict[str,str]"
    DICT_OF_LIST = "dict[str, list[str]]"
    DICT_OF_DICT = "dict[str, dict[str,str]]"
    DICT_OF_DICT_OF_DICT = "dict[str, dict[str, dict[str,str]]]"
    DICT_OF_STR_OR_LIST = "dict[str, str|list[str]]"


### Configuration #############################################################


class Configuration:
    """
    Class to access configuration settings for APPN code.

    Configuration elements are read from a YAML file for which the folder and
    name can be overridden with environment variables. The default is
    "./appn.yaml".

    Access methods always receive a copy of any lists or dictionaries
    returned so the configuration is not affected by any changes.

    Data from YAML is validated to ensure it fits the expected structure.
    """

    instance: Optional["Configuration"] = None

    def __new__(cls):
        """
        Use the same instance everywhere in this process
        """
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        """
        Read configuration from YAML file
        """
        # The severity of errors reported depends on whether an explicit location was
        # offered or defaults used.
        defaults_overridden = False

        # Safe defaults if nothing is read
        self.namespace_definitions = None
        self.configuration = {}

        # Dictionary to store cached validated content for configuration elements
        self.cache = {}

        # Logger to store messages of importance to data administrators. Anything
        # logged to the logger is also logged via Python logging.
        self.logger = IssueLogger()

        # Use folder from environment or default
        if APPN_CONFIGURATION_FOLDER_ENVIRONMENT_KEY in os.environ:
            self.configuration_folder = Path(
                os.environ[APPN_CONFIGURATION_FOLDER_ENVIRONMENT_KEY]
            )
            defaults_overridden = True
        else:
            self.configuration_folder = Path(APPN_DEFAULT_CONFIGURATION_FOLDER)
        logging.debug(f"Configuration folder: {self.configuration_folder}")

        # Use supplied filename or filename from environment or default
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

    def fetch_dict(
        self,
        key: ConfigurationKey,
    ) -> dict[str, str]:
        """
        Safe and efficient access to YAML dictionary

        Checks presence and structure of YAML metadata

        Callers always receive a copy of the validated version, so the
        configuration is not affected by any external changes.

        :param key: `ConfigurationKey` for requested content
        :return: Dictionary of strings to strings
        """

        # All results are cached for quick return on subseqent calls
        if key not in self.cache:
            # Verify that the YAML content matches the expected structure.
            # All keys in YAML are strings, so the types of any dictionary
            # keys do not need to be validated.
            value = {}
            if key.value in self.configuration:
                value = self.configuration[key.value]
                if not self.validate_configuration_values(ValidationType.DICT, value):
                    self.logger.log(
                        logging.ERROR,
                        __name__,
                        IssueMessage.RANGE_INVALID_CONFIGURATION_DATA,
                        CONFIGURATION_FILE=self.configuration_filepath,
                        CONFIGURATION_KEY=key.value,
                        EXPECTED_TYPE="Dictionary with strings as keys and values",
                        SUPPLIED_VALUE=str(value),
                    )
            self.cache[key] = value
            logging.debug(f"Cached value for configuration key {key.value}")

        return self.cache[key].copy()

    def fetch_dict_of_list(
        self,
        key: ConfigurationKey,
    ) -> dict[str, list[str]]:
        """
        Safe and efficient access to YAML dictionary of lists

        Checks presence and structure of YAML metadata

        Callers always receive a copy of the validated version, so the
        configuration is not affected by any external changes.

        :param key: `ConfigurationKey` for requested content
        :return: Dictionary of strings to lists of strings
        """

        # All results are cached for quick return on subseqent calls
        if key not in self.cache:
            # Verify that the YAML content matches the expected structure.
            # All keys in YAML are strings, so the types of any dictionary
            # keys do not need to be validated.
            value = []
            if key.value in self.configuration:
                value = self.configuration[key.value]
                if not self.validate_configuration_values(
                    ValidationType.DICT_OF_LIST, value
                ):
                    self.logger.log(
                        logging.ERROR,
                        __name__,
                        IssueMessage.RANGE_INVALID_CONFIGURATION_DATA,
                        CONFIGURATION_FILE=self.configuration_filepath,
                        CONFIGURATION_KEY=key.value,
                        EXPECTED_TYPE="Dictionary with strings as keys and lists of strings as values",
                        SUPPLIED_VALUE=str(value),
                    )
            self.cache[key] = value
            logging.debug(f"Cached value for configuration key {key.value}")

        return self.cache[key].copy()

    def fetch_dict_of_dict(
        self,
        key: ConfigurationKey,
    ) -> dict[str, dict[str, str]]:
        """
        Safe and efficient access to YAML dictionary of dictionaries

        Checks presence and structure of YAML metadata

        Callers always receive a copy of the validated version, so the
        configuration is not affected by any external changes.

        :param key: `ConfigurationKey` for requested content
        :return: Dictionary of strings to dictionaries of strings to strings
        """

        # All results are cached for quick return on subseqent calls
        if key not in self.cache:
            # Verify that the YAML content matches the expected structure.
            # All keys in YAML are strings, so the types of any dictionary
            # keys do not need to be validated.
            value = []
            if key.value in self.configuration:
                value = self.configuration[key.value]
                if not self.validate_configuration_values(
                    ValidationType.DICT_OF_DICT, value
                ):
                    self.logger.log(
                        logging.ERROR,
                        __name__,
                        IssueMessage.RANGE_INVALID_CONFIGURATION_DATA,
                        CONFIGURATION_FILE=self.configuration_filepath,
                        CONFIGURATION_KEY=key.value,
                        EXPECTED_TYPE="Dictionary with strings as keys and dictionaries with string keys and values as values",
                        SUPPLIED_VALUE=str(value),
                    )
            self.cache[key] = value
            logging.debug(f"Cached value for configuration key {key.value}")

        return self.cache[key].copy()

    def fetch_dict_of_dict_of_dict(
        self,
        key: ConfigurationKey,
    ) -> dict[str, dict[str, dict[str, str]]]:
        """
        Safe and efficient access to YAML dictionary of dictionaries of dictionaries

        Checks presence and structure of YAML metadata

        Callers always receive a copy of the validated version, so the
        configuration is not affected by any external changes.

        :param key: `ConfigurationKey` for requested content
        :return: Dictionary of dictionaries of dictionaries with strings for all keys and innermost values
        """

        # All results are cached for quick return on subseqent calls
        if key not in self.cache:
            # Verify that the YAML content matches the expected structure.
            # All keys in YAML are strings, so the types of any dictionary
            # keys do not need to be validated.
            value = []
            if key.value in self.configuration:
                value = self.configuration[key.value]
                if not self.validate_configuration_values(
                    ValidationType.DICT_OF_DICT_OF_DICT, value
                ):
                    self.logger.log(
                        logging.ERROR,
                        __name__,
                        IssueMessage.RANGE_INVALID_CONFIGURATION_DATA,
                        CONFIGURATION_FILE=self.configuration_filepath,
                        CONFIGURATION_KEY=key.value,
                        EXPECTED_TYPE="Dictionary of dictionaries of dictionaries with strings for all keys and innermost values",
                        SUPPLIED_VALUE=str(value),
                    )
            self.cache[key] = value
            logging.debug(f"Cached value for configuration key {key.value}")

        return self.cache[key].copy()

    def fetch_dict_of_str_or_list(
        self,
        key: ConfigurationKey,
    ) -> dict[str, str | list[str]]:
        """
        Safe and efficient access to YAML dictionary of strings to strings or lists of strings

        Checks presence and structure of YAML metadata

        Callers always receive a copy of the validated version, so the
        configuration is not affected by any external changes.

        :param key: `ConfigurationKey` for requested content
        :return: Dictionary of strings to strings or lists of strings
        """

        # All results are cached for quick return on subseqent calls
        if key not in self.cache:
            # Verify that the YAML content matches the expected structure.
            # All keys in YAML are strings, so the types of any dictionary
            # keys do not need to be validated.
            value = []
            if key.value in self.configuration:
                value = self.configuration[key.value]
                if not self.validate_configuration_values(
                    ValidationType.DICT_OF_STR_OR_LIST, value
                ):
                    self.logger.log(
                        logging.ERROR,
                        __name__,
                        IssueMessage.RANGE_INVALID_CONFIGURATION_DATA,
                        CONFIGURATION_FILE=self.configuration_filepath,
                        CONFIGURATION_KEY=key.value,
                        EXPECTED_TYPE="Dictionary with strings as keys and strings or lists of strings as values",
                        SUPPLIED_VALUE=str(value),
                    )
            self.cache[key] = value
            logging.debug(f"Cached value for configuration key {key.value}")

        return self.cache[key].copy()

    def fetch_list(
        self,
        key: ConfigurationKey,
    ) -> list[str]:
        """
        Safe and efficient access to YAML list

        Checks presence and structure of YAML metadata

        Callers always receive a copy of the validated version, so the
        configuration is not affected by any external changes.

        :param key: `ConfigurationKey` for requested content
        :return: List of strings
        """

        # All results are cached for quick return on subseqent calls
        if key not in self.cache:
            # Verify that the YAML content matches the expected structure.
            # All keys in YAML are strings, so the types of any dictionary
            # keys do not need to be validated.
            value = []
            if key.value in self.configuration:
                value = self.configuration[key.value]
                if not self.validate_configuration_values(ValidationType.LIST, value):
                    self.logger.log(
                        logging.ERROR,
                        __name__,
                        IssueMessage.RANGE_INVALID_CONFIGURATION_DATA,
                        CONFIGURATION_FILE=self.configuration_filepath,
                        CONFIGURATION_KEY=key.value,
                        EXPECTED_TYPE="List of strings",
                        SUPPLIED_VALUE=str(value),
                    )
            self.cache[key] = value
            logging.debug(f"Cached value for configuration key {key.value}")

        return self.cache[key].copy()

    def validate_configuration_values(
        self, validation_type: ValidationType, value: Any
    ) -> bool:
        """
        Validate YAML configuration elements

        Structure is validated by checking the types of elements and
        confirming they match the expected nesting of dictionaries, lists
        and strings. Since YAML keys are always strings, the types of
        dictionary keys are not checked.

        :param validation_type: `ValidationType`
        :param value: Object to validate
        :return: True if valid
        """
        # Verify that the YAML content matches the expected structure.
        # All keys in YAML are strings, so the types of any dictionary
        # keys do not need to be validated.
        if validation_type == ValidationType.LIST:
            return isinstance(value, list) and all([isinstance(s, str) for s in value])
        elif isinstance(value, dict):
            if validation_type == ValidationType.DICT:
                return all([isinstance(s, str) for s in value.values()])
            elif validation_type == ValidationType.DICT_OF_LIST:
                return all(
                    [
                        self.validate_configuration_values(ValidationType.LIST, lst)
                        for lst in value.values()
                    ]
                )
            elif validation_type == ValidationType.DICT_OF_DICT:
                return all(
                    [
                        self.validate_configuration_values(ValidationType.DICT, dct)
                        for dct in value.values()
                    ]
                )
            elif validation_type == ValidationType.DICT_OF_DICT_OF_DICT:
                return all(
                    [
                        self.validate_configuration_values(
                            ValidationType.DICT_OF_DICT, dct
                        )
                        for dct in value.values()
                    ]
                )
            elif validation_type == ValidationType.DICT_OF_STR_OR_LIST:
                return all(
                    [
                        (isinstance(s, str) or isinstance(s, list))
                        for s in value.values()
                    ]
                ) and all(
                    [
                        isinstance(s, str)
                        for lst in value.values()
                        if isinstance(lst, list)
                        for s in lst
                    ]
                )
        return False

    def get_logger(self) -> IssueLogger:
        """
        Access the `IssueLogger` for the current context

        :return: `IssueLogger` instance
        """
        return self.logger

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
        # Definitions are held in a property to minimise computation.
        if self.namespace_definitions is None:
            # Find any configured namespace paths (locations for schema assets).
            # Assets without paths will be only be loadable by using the namespace
            # as a URL.
            paths = self.fetch_dict(ConfigurationKey.NAMESPACE_PATHS)
            logging.debug(f"Imported namespace paths: {paths}")

            # Find any configured namespace prefixes.
            prefixes = self.fetch_dict(ConfigurationKey.NAMESPACE_PREFIXES)
            logging.debug(f"Imported namespace prefixes: {prefixes}")

            # Build the namespace definitions for all default namespaces, taking
            # into account the configured namespace paths.
            self.namespace_definitions = {
                ns: NamespaceDefinition(ns, pre, paths[ns] if ns in paths else ns)
                for ns, pre in DEFAULT_PREFIXES.items()
            }

            for ns in prefixes:
                self.namespace_definitions[ns] = NamespaceDefinition(
                    ns, prefixes[ns], paths[ns] if ns in paths else ns
                )

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
        return self.fetch_list(ConfigurationKey.VOCABULARY_COLUMN_NAMESPACES)

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

        Returns a copy of the dictionary included in the YAML configuration.

        :return: Dictionary mapping namespaces to selection rules
        """
        return self.fetch_dict_of_str_or_list(ConfigurationKey.EXPLICIT_CLASSES)

    def get_excluded_classes(self) -> list[str]:
        """
        Get list of classes that should NOT be matched when using the
        rules specified by `get_explicit_classes`

        This allows finer control over the exact set of classes asserted
        for an instance.

        Returns a copy of the list included in the YAML configuration.

        :return: List of class IRIs
        """
        return self.fetch_list(ConfigurationKey.EXCLUDED_CLASSES)

    def get_sheet_aliases(self) -> dict[str, str]:
        """
        Get dictionary of class names to use when Excel sheets have
        other names.

        The primary purpose is to ensure that sheets named Trait are
        processed as the subclass ObservedVariable and can include
        Method or Scale embeddings

        Returns a copy of the dictionary included in the YAML configuration.

        :return: Dictionary mapping names to class names
        """
        return self.fetch_dict(ConfigurationKey.SHEET_ALIASES)

    def get_column_aliases(self) -> dict[str, str]:
        """
        Get dictionary of column names to use when Excel sheets have
        other names.

        This allows spreadsheets to use names that may not match those of
        schema properties but that better match the understanding of users.

        Returns a copy of the dictionary included in the YAML configuration.

        :return: Dictionary mapping column names to preferred names
        """
        return self.fetch_dict(ConfigurationKey.COLUMN_ALIASES)

    def get_completion_rules(self) -> dict[str, dict[str, dict[str, str]]]:
        """
        Get dictionary of rules that should be applied to complete terms
        belonging to specific classes to resolve the state of a specific
        property. The dictionary maps class names to dictionaries mapping
        property IRIs to a set of key-value rule elements.

        This is intended to be an extensible framework for post-processing
        terms. Each rule must include a `type` property matching a name
        from the `CompletionRuleType` enumeration from `appn_types`.

        Rules are expected to be applied only if there is no pre-existing
        instance of the property for the term. This could be altered by
        including a property to the rule dictionary that specifies
        multiple instances of the property are allowed.

        The types include `reflexive`, for which the response is to add an
        instance of the specified property to each class instance with the
        same class instance as the object of the property. This can be
        used to ensure that each APPN `ObservedVariable` has a `hasTrait`
        property.

        Returns a copy of the dictionary included in the YAML configuration.

        :return: Dictionary mapping class names to dictionaries mapping
            property IRIs to dictionaries of rule elements
        """
        return self.fetch_dict_of_dict_of_dict(ConfigurationKey.COMPLETION_RULES)

    def get_completion_rules_for_class(
        self, class_name: str
    ) -> dict[str, dict[str, str]]:
        """
        Convenience method to get completion rules for a single class

        :return: Dictionary mapping property IRIs to dictionaries of rule
            elements
        """
        rules = self.get_completion_rules()
        if class_name in rules:
            return rules[class_name]
        return {}

    def get_class_abbreviations(self) -> dict[str, str]:
        """
        Get dictionary of alternate strings (normally abbreviations) to
        substitute for class names in term IRIs.

        This allows otherwise lengthy IRI strings (including e.g.
        "observedvariable_") to be shortened in predictable ways (e.g. "ov_").

        :return: Dictionary mapping class names to abbreviations
        """
        return self.fetch_dict(ConfigurationKey.CLASS_ABBREVIATIONS)

    def get_property_expansions(self) -> dict[URIRef, list[URIRef]]:
        """
        Get dictionary mapping property IRIs to lists of IRIs that should be
        added to terms whenever the primary property IRI is used.

        This allows terms to include multiple properties offering the same
        value (the object term or literal) to users focused on different
        schemas.

        This method returns IRIs as URIRefs.

        :return: Dictionary mapping property IRIs to lists of property IRIs
        """
        property_expansions = self.fetch_dict_of_list(
            ConfigurationKey.PROPERTY_EXPANSIONS
        )
        expansions = {}
        for k, v in property_expansions.items():
            expansions[URIRef(k)] = [URIRef(e) for e in v]
        return expansions

    def get_embedded_classes(self) -> dict[str, list[str]]:
        """
        Get dictionary mapping class names to lists of names for classes that
        may be included as embeddings inside sheets for the primary class.

        If a sheet for the primary class includes one or more columns with
        names starting with a lower-first representation of an embedded class
        (e.g. "methodName", "methodDescription"), these will be processed as
        if they appeared in a sheet named after the embedded class ("Method")
        and had names without the initial class reference ("name",
        "description"). Embedded classes should ALWAYS include a column that
        will map to "name" once the class reference is removed from the
        name.

        Instances of embedded classes may repeat inside the sheet for the
        primary class (allowing the same instance to be referenced by more
        than one instance of the primary class). The embedded class instance
        will be constructed using terms in the first row that references it.
        Subsequent definitions of the same embedded class instance will be
        ignored.

        :return: Dictionary mapping class names to lists of embeddable classes
        """
        return self.fetch_dict_of_list(ConfigurationKey.EMBEDDED_CLASSES)

    def get_domain_range_properties(self) -> dict[str, dict[str, str]]:
        """
        Get dictionary mapping domain class names to dictionaries mapping
        range class names to property IRIs.

        This supports the use of embedded classes. The ExcelVocabularyParser
        needs to create properties linking each primary class instance to
        the embedded class instance, but the relevant column refers to its
        relationship to the embedded class as its name (e.g. "methodName").
        The way that the embedded (range) class instance is linked to the
        primary (domain) class instance is not defined.

        In most cases, only one property exists in the APPN schema that has
        the primary class in its domain and the embedded class in its range.
        In such cases, the behaviour is to assume this is the intended
        property.

        This method allows the property selection to be made explicit. This
        will be required if the APPN schema includes multiple candidate
        properties.

        :return: Dictionary mapping domain class names to dictionaries mapping
            range class names to property IRIs
        """
        return self.fetch_dict_of_dict(ConfigurationKey.DOMAIN_RANGE_PROPERTIES)

    def get_property_range_classes(self) -> dict[str, dict[str, str]]:
        """
        Get classes to expect when processing specified properties for
        specific classes.

        Property values will be converted to IRI references when the specified
        domain class and property are used.

        :return: Dictionary mapping domain class names to dictionaries mapping
            property names to range class IRIs
        """
        return self.fetch_dict_of_dict(ConfigurationKey.PROPERTY_RANGE_CLASSES)

    def get_organisations(self) -> dict[str, Organisation]:
        """
        Get metadata elements for `Organisation`s defined in schema and for
        the APPN central organisation.

        Each `Organisation` holds a short id, a name, a ROR identifier,
        the namespace for the organisation's vocabulary terms, and the prefix
        to be used for the namespace in CURIE representations.

        Organisation ids are used to identify APPN nodes and APPN as a whole
        ("APPN") in data produced by APPN. The other components are attached
        to these ids so that software can correctly generate vocabularies and
        data.

        The organisation definitions are sourced from the YAML configuration
        file.

        If the name is not specified, the id is used in its place.

        If the namespace is not specified, it is constructed from a root URL
        combined with the id.

        If the namespace prefix is not specified, a default is selected from
        `DEFAULT_PREFIXES` if one is defined. Otherwise, the lowercase id is
        used.

        Regardless of the YAML content, an entry is always included for the
        APPN central organisation.

        Since the organisations dictionary is processed and not found directly
        in the YAML configuration, it is stored in an instance property of the
        `Configuration`.

        :return: Dictionary mapping organisation ids to `Organisation`s.
        """
        if self.organisations is None:
            self.organisations = {}
            organisations = self.fetch_dict_of_dict(ConfigurationKey.ORGANISATIONS)
            for id, properties in organisations.items():
                name = str(
                    properties[OrganisationProperty.NAME.value]
                    if OrganisationProperty.NAME.value in properties
                    else id
                )
                ror = str(
                    properties[OrganisationProperty.ROR.value]
                    if OrganisationProperty.ROR.value in properties
                    else None
                )
                namespace = str(
                    properties[OrganisationProperty.NAMESPACE.value]
                    if OrganisationProperty.NAMESPACE.value in properties
                    else f"{APPN_VOCABULARY_ROOT}{id}/"
                )
                prefix = str(
                    properties[OrganisationProperty.PREFIX.value]
                    if OrganisationProperty.PREFIX.value in properties
                    else (
                        DEFAULT_CENTRAL_VOCABULARY_PREFIX
                        if id == CENTRAL_ORGANISATION
                        else (
                            DEFAULT_PREFIXES[id]
                            if id in DEFAULT_PREFIXES
                            else id.lower()
                        )
                    )
                )
                self.organisations[id] = Organisation(id, name, ror, namespace, prefix)
            if CENTRAL_ORGANISATION not in self.organisations:
                self.organisations[CENTRAL_ORGANISATION] = Organisation(
                    CENTRAL_ORGANISATION,
                    "Australian Plant Phenomics Network",
                    "https://ror.org/02zj7b759",
                    APPN_VOCABULARY,
                    DEFAULT_PREFIXES[APPN_VOCABULARY],
                )
        return self.organisations.copy()

    def get_organisation_by_id(self, id: str) -> Optional[Organisation]:
        """
        Convenience method to retrieve a single `Organisation` by its id.

        :return: `Organisation` for given id, if defined
        """
        organisations = self.get_organisations()
        if id in organisations:
            return organisations[id]
        return None

    def get_appn(self) -> Organisation:
        """
        Convenience method to retrieve the APPN central `Organisation`.

        :return: `Organisation` with id "APPN"
        """
        organisations = self.get_organisations()
        return organisations[CENTRAL_ORGANISATION]
