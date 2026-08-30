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

from collections import namedtuple

### Namespace #################################################################
#
# Namedtuple as simple class for namespace definitions
#
Namespace = namedtuple("Namespace", ["ns", "prefix", "path"])

### Term ######################################################################
#
# Namedtuple as simple class for IRI elements
#
Term = namedtuple("Term", ["iri", "curie", "ns", "prefix", "name"])

### Triple ####################################################################
#
# Namedtuple as simple class for triples
#
Triple = namedtuple("Triple", ["subject", "property", "object"])
