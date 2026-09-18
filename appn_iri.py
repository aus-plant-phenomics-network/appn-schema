#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
# appn_iri.py
#
# Class to represent IRIs, both serving as `rdflib` `URIRef` instances and
# providing properties for easier processing and display, and associated
# classes for inclusing IRIs in triples
#
# -----------------------------------------------------------------------------
# Created By  : Donald Hobern, donald.hobern@adelaide.edu.au
# Created Date: 2026-08-14
# version ='2026.0.1'
# -----------------------------------------------------------------------------

from enum import IntEnum
from typing import NamedTuple, Optional, Any
from rdflib import URIRef, Node

from appn_types import NamespaceDefinition
from appn_configuration import Configuration

### IRI #######################################################################


class IRI(URIRef):
    """
    Subclass of URIRef offering easy access to ns, prefix, curie and name

    IRI can be used wherever a URIRef is expected
    """

    # Reserve property names for instances
    __slots__ = ("_ns", "_prefix", "_curie", "_name")

    namespace_definitions: Optional[dict[str, NamespaceDefinition]] = None

    def __new__(cls, iri: str | URIRef, namespace_definitions: Optional[dict[str, NamespaceDefinition]] = None):
        """
        IRI offers URIRef behaviour with additional properties

        :param iri: An existing URIRef or IRI string
        :param namespace_definitions: List of `NamespaceDefinitions` to determine namespace and prefix
        """
        if namespace_definitions is None:
            if cls.namespace_definitions is None:
                cls.namespace_definitions = Configuration().get_namespace_definitions()
            namespace_definitions = cls.namespace_definitions

        iri = str(iri)
        obj = super().__new__(cls, iri)
        if (namespace_definition := cls.get_namespace_definition(iri, namespace_definitions)) is not None:
            obj._ns = namespace_definition.ns
            obj._prefix = namespace_definition.prefix
            obj._name = iri[len(obj._ns) :]
            obj._curie = f"{obj._prefix}:{obj._name}"
        else:
            obj._ns = ""
            obj._prefix = ""
            obj._name = iri
            obj._curie = iri
        return obj

    @staticmethod
    def get_namespace_definition(iri: str, namespace_definitions: dict[str, NamespaceDefinition]) -> Optional[NamespaceDefinition]:
        """
        Find `NamespaceDefinition` for given IRI

        :param iri: An existing URIRef or IRI string
        :param namespace_definitions: `NamespaceDefinitions` to determine namespace and prefix (defaults to dictionary from `Configuration`)
        :return: Matching `NamespaceDefinition` or None
        """
        if namespace_definitions is None:
            namespace_definitions = IRI.namespace_definitions

        if namespace_definitions is not None:
            for namespace, namespace_definition in namespace_definitions.items():
                if iri.startswith(namespace):
                    return namespace_definition
        return None

    @property
    def iri(self) -> str:
        """
        Get IRI as string

        :return: IRI string
        """
        return self.__str__()

    @property
    def curie(self) -> str:
        """
        Get CURIE as string

        :return: CURIE string
        """
        return self._curie

    @property
    def name(self) -> str:
        """
        Get unqualified name as string

        :return: Unqualified name string
        """
        return self._name

    @property
    def ns(self) -> str:
        """
        Get namespace as string

        :return: Namespace string
        """
        return self._ns

    @property
    def prefix(self) -> str:
        """
        Get namespace prefix as string

        :return: Namespace prefix string
        """
        return self._prefix

    def __eq__(self, other: Any) -> bool:
        """
        Equality with other representations of the same IRI

        Assert equality with matching `URIRef` and string instances

        :param other: Object with which to compare
        :return: True is object IRI strings match
        """
        if isinstance(other, URIRef) or isinstance(other, str):
            return str(other) == self.iri
        return super().__eq__(other)

    def __hash__(self) -> int:
        """
        Hash the IRI value

        Hash is based on the IRI string

        :param other: Object with which to compare
        :return: True is object IRI strings match
        """
        return hash(self.iri)


### Triple ####################################################################


class Triple(NamedTuple):
    """
    Simple class to represent a triple of strings

    :param subject: `IRI` for the subject of a triple
    :param property: `IRI` for the property of a triple
    :param object: `IRI`|Literal  for the object of a triple
    """

    subject: IRI | Node
    property: IRI | Node
    object: IRI | Node


### TriplePosition ############################################################


class TriplePosition(IntEnum):
    """
    Simple class for positions in a triple
    """

    SUBJECT = 0
    PROPERTY = 1
    OBJECT = 2

