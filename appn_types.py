#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
# appn_types.py
#
# Type definitions for use in APPN classes
#
# Usage: python appn_vocabulary.py [-n node|"all"] [-l log-level] [-e]
#
# -----------------------------------------------------------------------------
# Created By  : Donald Hobern, donald.hobern@adelaide.edu.au
# Created Date: 2026-03-31
# version ='2026.0.1'
# -----------------------------------------------------------------------------

import logging
from enum import StrEnum
from typing import NamedTuple, Optional
from rdflib import URIRef

### Issue #####################################################################

class Issue(NamedTuple):
    """
    Simple class for notifiable issues

    :param level: Log level for issue (from `logging`)
    :param module: String name for module logging issue
    :param message: Error message
    :param properties: Dictionary of additional information
    """
    level: int 
    module: str
    message: str
    properties: dict[str: str]

    def __str__(self) -> str:
        if len(self.properties) > 0:
            property_string = f"(Properties: {'; '.join([f'{k}: {v}' for k, v in self.properties.items()])})"
        else:
            property_string = ""
        return f"{logging.getLevelName(self.level)} - {self.module}: {self.message}{property_string}"

### Organisation ##############################################################

class Organisation(NamedTuple):
    """
    Simple class for organisation properties

    :param id: Short identifier for the organisation
    :param name: Name of the organisation
    :param ror: ROR identifier for the organisation
    :param namespace: Namespace for organisation vocabulary
    :param prefix: Prefix to be used for namespace in CURIEs
    """
    id: str
    name: str
    ror: str
    namespace: str
    prefix: str

### NamespaceDefinition #######################################################

class NamespaceDefinition(NamedTuple):
    """
    Simple class for namespace definitions

    :param namespace: Namespace for a linked-data asset
    :param prefix: Prefix to be used for namespace
    :param path: Path to access machine-readable RDF for namespace terms
    """
    ns: str
    prefix: str
    path: str


### Term ######################################################################

class Term(NamedTuple):
    """
    Simple class for accessing elements based on an IRI string

    :param iri: String representation of the IRI
    :param curie: String representation of the CURIE form for the IRI
    :param ns: String representation of the namespace
    :param prefix: String representation of the prefix used for the namespace
    :param name: String representation of the unqualified name from the IRI
    """
    iri: str
    curie: str
    ns: str
    prefix: str
    name: str


### Triple ####################################################################

class Triple(NamedTuple):
    """
    Simple class to represent a triple of strings

    :param subject: String for the subject of a triple
    :param property: String for the property of a triple
    :param object: String for the object of a triple
    """
    subject: str
    property: str
    object: str


### URIRefTriple ##############################################################

class URIRefTriple(NamedTuple):
    """
    Simple class to represent a triple of `URIRef`s

    :param subject: `URIRef` for the subject of a triple
    :param property: `URIRef` for the property of a triple
    :param object: `URIRef` for the object of a triple
    """
    subject: URIRef
    property: URIRef
    object: URIRef


### ColumnMapping##############################################################

class ColumnMapping(NamedTuple):
    """
    Simple class for metadata associated with a `DataFrame` column

    :param column: Name of a `DataFrame` column
    :param property: `URIRef` for the property represented by the column
    :param range_class: `Term` identifying an APPN schema class representing the range if the `property` links two schema instances
    :param primary_identifier: True if the `property` matches `schema:name` (used to create the IRI as the unique identifier for an instance)
    :param is_local_property: True if the `property` is to be defined in the current vocabulary namespace
    """
    column: str
    property: URIRef
    range_class: Optional[Term]
    primary_identifier: bool
    is_local_property: bool


### CompletionRuleType ########################################################

class CompletionRuleType(StrEnum):
    """
    Simple class for permitted choices for `type` in a `CompletionRule.
    """
    REFLEXIVE = "reflexive"

