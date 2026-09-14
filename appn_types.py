#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
# appn_types.py
#
# Type definitions for use in APPN classes
#
# -----------------------------------------------------------------------------
# Created By  : Donald Hobern, donald.hobern@adelaide.edu.au
# Created Date: 2026-03-31
# version ='2026.0.1'
# -----------------------------------------------------------------------------

import logging
from enum import Enum, StrEnum, IntEnum
from typing import NamedTuple, Optional
from rdflib import URIRef, Node

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
    properties: dict[str, str]

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


### CompletionRuleType ########################################################


class CompletionRuleType(StrEnum):
    """
    Simple class for permitted choices for `type` in a `CompletionRule.
    """

    REFLEXIVE = "reflexive"
