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

from typing import NamedTuple

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
#
# Simple class for metadata associated with a spreadsheet column
#
class ColumnMapping(NamedTuple):
    column: str
    property: URIRef
    range_class: Optional(Term)
    primary_identifier: bool
