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

from typing import NamedTuple, Optional
from rdflib import URIRef


### Organisation ##############################################################
#
# Simple class for organisation properties
#
class Organisation(NamedTuple):
    id: str
    name: str
    ror: str
    namespace: str
    prefix: str

### NamespaceDefinition #######################################################
#
# Simple class for namespace definitions
#
class NamespaceDefinition(NamedTuple):
    ns: str
    prefix: str
    path: str


### Term ######################################################################
#
# Simple class for IRI elements
#
class Term(NamedTuple):
    iri: str
    curie: str
    ns: str
    prefix: str
    name: str


### Triple ####################################################################
#
# Simple class for triples of string
#
class Triple(NamedTuple):
    subject: str
    property: str
    object: str


### URIRefTriple ##############################################################
#
# Simple class for triples of URIRef
#
class URIRefTriple(NamedTuple):
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
