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
from appn_types import Namespace

APPN_DEFAULT_CONFIGURATION_FOLDER = Path("./")
APPN_DEFAULT_CONFIGURATION_NAME = "APPN"

APPN_CONFIGURATION_FOLDER_ENVIRONMENT_KEY = "APPN_CONFIGURATION_FOLDER"
APPN_CONFIGURATION_NAME_ENVIRONMENT_KEY = "APPN_CONFIGURATION_NAME"

CONFIGURATION_KEY_NAMESPACES = "namespaces"
CONFIGURATION_KEY_NAMESPACE_PATHS = "namespace_paths"

# Standard APPN namespace URLs

APPN_SCHEMA = "https://schema.plantphenomics.org.au/"

# Schema.org publishes versions using both HTTP and HTTPS - we use
# HTTPS which seems to be most widely used.
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

APPN_VOCABULARY = "https://id.plantphenomics.org.au/"
ANU_VOCABULARY = "https://id.plantphenomics.org.au/ANU/"
AU_VOCABULARY = "https://id.plantphenomics.org.au/AU/"
CSU_VOCABULARY = "https://id.plantphenomics.org.au/CSU/"
DPIRD_VOCABULARY = "https://id.plantphenomics.org.au/DPIRD/"
LTU_VOCABULARY = "https://id.plantphenomics.org.au/LTU/"
UQ_VOCABULARY = "https://id.plantphenomics.org.au/UQ/"
USYD_VOCABULARY = "https://id.plantphenomics.org.au/USYD/"
UWA_VOCABULARY = "https://id.plantphenomics.org.au/UWA/"
WSU_VOCABULARY = "https://id.plantphenomics.org.au/WSU/"

DEFAULT_NAMESPACES = {
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
    APPN_VOCABULARY: "appn-all",
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


class Configuration:

    def __init__(
        self,
        configuration_folder: Optional[Path | str] = None,
        configuration_name: Optional[str] = None,
    ) -> None:

        defaults_overridden = (
            configuration_folder is not None or configuration_name is not None
        )

        self.namespaces = None
        self.configuration = {}

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

        if configuration_name is None:
            if APPN_CONFIGURATION_NAME_ENVIRONMENT_KEY in os.environ:
                configuration_name = os.environ[APPN_CONFIGURATION_NAME_ENVIRONMENT_KEY]
                defaults_overridden = True
            else:
                configuration_name = APPN_DEFAULT_CONFIGURATION_NAME

        if not self.configuration_folder.exists():
            if defaults_overridden:
                message = (
                    f"Configuration folder {self.configuration_folder} does not exist"
                )
                logging.error(message)
                raise ValueError(message)
            else:
                return

        self.configuration_filepath = (
            self.configuration_folder / f"{configuration_name}.yaml"
        )

        if not self.configuration_filepath.exists():
            if defaults_overridden:
                message = (
                    f"Configuration file {self.configuration_filepath} does not exist"
                )
                logging.error(message)
                raise ValueError(message)
            else:
                return

        with open(self.configuration_filepath, "r") as stream:
            try:
                print(self.configuration_filepath)
                self.configuration = yaml.safe_load(stream)
                logging.info(f"Loaded configuration: {self.configuration_filepath}")
            except yaml.YAMLError as exc:
                logging.error(f"config.load: {str(exc)}")
                raise ValueError(
                    f"Failed to load configuration from {self.configuration_filepath}"
                )

    def get_namespaces(self) -> dict[str, Namespace]:
        if self.namespaces is not None:
            return self.namespaces

        if CONFIGURATION_KEY_NAMESPACE_PATHS in self.configuration and isinstance(
            self.configuration[CONFIGURATION_KEY_NAMESPACE_PATHS], dict
        ):
            paths = self.configuration[CONFIGURATION_KEY_NAMESPACE_PATHS]
        else:
            paths = {}

        self.namespaces = {
            ns: Namespace(ns, pre, paths[ns] if ns in paths else ns)
            for ns, pre in DEFAULT_NAMESPACES.items()
        }

        if CONFIGURATION_KEY_NAMESPACES in self.configuration:
            definitions = self.configuration[CONFIGURATION_KEY_NAMESPACES]
            if isinstance(definitions, dict):
                for ns, pre in definitions.items():
                    self.namespaces[ns] = Namespace(
                        ns, pre, paths[ns] if ns in paths else ns
                    )

        return self.namespaces
