#!/usr/bin/emv python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
# appn_dictionary.py
#
# Import RDF assets into a graph and support diverse query mechanisms
#
# A primary use case is to make the APPN schema and the ontologies it
# references accessible for automated use in data processing.
#
# A `Dictionary` can wrap any existing `Graph` to enable it to be explored
# more easily
#
# -----------------------------------------------------------------------------
# Created By  : Donald Hobern, donald.hobern@adelaide.edu.au
# Created Date: 2026-08-20
# version ='2026.0.1'
# -----------------------------------------------------------------------------

import logging

from pathlib import Path
from rdflib import Graph, URIRef, Node
from rdflib.namespace import Namespace, NamespaceManager
from typing import Any, Optional

from appn_iri import IRI, Triple, TriplePosition
from appn_types import NamespaceDefinition
from appn_configuration import Configuration, APPN_SCHEMA

### Dictionary ################################################################


class Dictionary:
    """
    Wrapper class around rdflib Graph instance to simplify common query needs

    A new Dictionary has an empty graph and cache. Linked-data objects can be
    added to the graph via the load() method. When the graph changes, the
    response cache is cleared.

    All get_* and list_* methods check the cache for a previous response to the
    request and otherwise generate and cache a new response from the graph.
    """

    def __init__(
        self,
        graph: Optional[Graph] = None,
        namespace_definitions: Optional[list[NamespaceDefinition]] = None,
    ) -> None:
        """
        Initialise properties based either on a supplied `Graph` or a new
        empty one.

        Use any `NamespaceDefinition`s to manage prefixes and locations for
        loading assets.

        :param graph: Optional `Graph` to initialise `Dictionary` - note that
            any `load` operations will modify the graph for all users.
        :param namespace_definitions: List of `NamespaceDefinition` objects to
            assist with use of RDF assets. These are treated as supplements or
            overrides to those from the local `Configuration`.
        """
        self.graph = Graph() if graph is None else graph
        self.namespace_manager = NamespaceManager(self.graph)

        # The `namespaces` and `reverse_namespaces` dictionaries enable access
        # by namespace or by namespace prefix.
        if graph is not None:
            self.namespaces = {
                p: str(ns) for p, ns in self.namespace_manager.namespaces()
            }
            self.reverse_namespaces = {v: k for k, v in self.namespaces.items()}
        else:
            self.namespaces = {}
            self.reverse_namespaces = {}
        self.loaded = set()
        self.cache = {}

        # Get `NamespaceDefinitions` from `Configuration` and add/overwrite any
        # supplied as a parameter
        self.namespace_definitions = Configuration().get_namespace_definitions()
        if namespace_definitions is not None:
            for namespace_definition in namespace_definitions:
                self.namespace_definitions[namespace_definition.ns] = (
                    namespace_definition
                )

    def load(
        self,
        asset_namespace: str,
        asset_path: Optional[str] = None,
        asset_prefix: Optional[str] = None,
    ) -> bool:
        """
        Load an RDF asset (any format supported by `rdflib`).

        The method loads definitions from the specified namespace into the
        `Graph`. If the path (file location) and/or prefix are not passed to
        the method, the supplied `NamespaceDefinition`s (if any) are checked
        for the missing information. If they are still not defined, the
        namespace will be given an anonymous prefix and loaded from the
        namespace URL.

        :param asset_namespace: Namespace string for asset
        :param asset_path: Optional location for a file containing RDF definitions for the namespace (in any supported RDF format)
        :param asset_prefix: Prefix to use for namespace in CURIE representations
        :return: True if successful
        """
        # Tolerate prefix as alias for namespace
        if not asset_namespace.startswith("http"):
            for namespace_definition in self.namespace_definitions.values():
                if namespace_definition.prefix == asset_namespace:
                    asset_namespace = namespace_definition.ns
                    break

        # Check for `NamespaceDefinition`
        if asset_namespace in self.namespace_definitions and isinstance(
            self.namespace_definitions[asset_namespace], NamespaceDefinition
        ):
            namespace_definition = self.namespace_definitions[asset_namespace]
            logging.debug(
                f"Found namespace for {asset_namespace}: {namespace_definition}"
            )
        else:
            namespace_definition = None

        # Determine where to load the asset from, either a supplied path, or
        # one from a `NamespaceDefinition`, or the namespace URL.
        if asset_path is None:
            if (
                namespace_definition is not None
                and namespace_definition.path is not None
            ):
                asset_path = namespace_definition.path
            else:
                asset_path = asset_namespace

        # Determine what prefix to use for the namespace, either a supplied
        # parameter, or one from a `NamespaceDefinition`, or an anonymous
        # prefix in the series ns1, ns2, ...
        if asset_prefix is None:
            if (
                namespace_definition is not None
                and namespace_definition.prefix is not None
            ):
                asset_prefix = namespace_definition.prefix
            else:
                index = 1
                while f"ns{index}" in self.namespaces:
                    index += 1
                asset_prefix = f"ns{index}"

        # Load the asset into the `Graph` and bind it with the prefix
        logging.debug(
            f"Loading {asset_namespace} from {asset_path} with prefix: {asset_prefix}"
        )
        try:
            self.graph.parse(asset_path)
            self.loaded.add(asset_namespace)
            if asset_prefix is not None:
                self.namespace_manager.bind(
                    asset_prefix, Namespace(asset_namespace), override=True
                )
                self.namespace_definitions[asset_namespace] = NamespaceDefinition(asset_namespace, asset_prefix, asset_path)

            # Clear any cached query results because the `Graph` has changed,
            # and update the namespace dictionaries.
            self.cache = {}
            self.namespaces = {
                p: str(ns) for p, ns in self.namespace_manager.namespaces()
            }
            self.reverse_namespaces = {v: k for k, v in self.namespaces.items()}

            logging.debug(f"Loaded {asset_namespace}")

        except Exception:
            logging.error(f"Failed to load {asset_namespace} as linked data asset", exc_info=True)
            return False

        return True

    def import_references(self) -> bool:
        """
        Load all RDF assets referenced (one-hop) by existing triples in
        the `Graph`

        For all IRIs in the `Graph`, if the namespace asset has not already been
        loaded, attempt to do so.

        :return: True if successful
        """
        success = True
        iris = set()
        for s, o, p in self.graph:
            for iri in [s, o, p]:
                if isinstance(iri, URIRef) and iri not in iris:
                    ns = self.get_namespace_from_iri(iri)
                    logging.debug(f"Mapped <{iri}> to namespace <{ns}>")
                    if ns is not None and ns not in self.loaded:
                        if not self.load(ns):
                            success = False
                    logging.debug(f"Found IRI <{iri}>")
                    iris.add(iri)
        return success

    def get_namespace_from_iri(self, iri: str | IRI) -> Optional[str]:
        """
        Find the namespace to which an IRI belongs

        :param iri: IRI for request
        :return: Namespace string if the IRI matches one of the known
            namespaces, otherwise None
        """
        iri = self.get_iri(iri)
        if iri.ns not in [None, ""]:
            return iri.ns
        return None

    def get_namespaces(self) -> dict[str, str]:
        """
        Get mappings of namespace prefixes to namespaces

        :return: Dictionary of namespace prefixes to loaded namespaces
        """
        return self.namespaces

    def list_triples(self) -> list[Triple]:
        """
        Return all `Triple`s in the `Graph` with `URIRef`s upgraded to `IRI`s

        :return: List of `Triples` based on `Graph` contents
        """
        key = "triples"
        if key not in self.cache:
            self.cache[key] = [self.get_triple(s, p, o) for s, p, o in self.graph]
        return self.cache[key]

    def get_triple(self, s: Node, p: Node, o: Node) -> Triple:
        """
        Produce `Triple` with IRIs in place or URIRefs

        :param s: Triple subject as `rdflib` `Node`
        :param p: Triple property as `rdflib` `Node`
        :param o: Triple object as `rdflib` `Node`
        :return: `Triple`
        """
        return Triple(
            self.get_iri(s) if isinstance(s, URIRef) else s,
            self.get_iri(p) if isinstance(p, URIRef) else p,
            self.get_iri(o) if isinstance(o, URIRef) else o,
        )

    def list_unique_subjects(self, namespace: Optional[str] = None) -> list[IRI]:
        """
        Return list of all IRIs used as subjects for triples

        Results may optionally be filtered to matches within a specified
        namespace.

        :param namespace: Optional namespace for filtering results
        :return: List of `IRIs` for subject IRIs
        """
        return self.list_unique_terms_by_position(TriplePosition.SUBJECT, namespace)

    def list_unique_properties(self, namespace: Optional[str] = None) -> list[IRI]:
        """
        Return list of all IRIs used as properties for triples

        Results may optionally be filtered to matches within a specified
        namespace.

        :param namespace: Optional namespace for filtering results
        :return: List of `IRIs` for property IRIs
        """
        return self.list_unique_terms_by_position(TriplePosition.PROPERTY, namespace)

    def list_unique_objects(self, namespace: Optional[str] = None) -> list[IRI]:
        """
        Return list of all IRIs used as objects for triples

        Results may optionally be filtered to matches within a specified
        namespace.

        :param namespace: Optional namespace for filtering results
        :return: List of `IRIs` for object IRIs
        """
        return self.list_unique_terms_by_position(TriplePosition.OBJECT, namespace)

    def list_unique_terms_by_position(
        self, position: TriplePosition, namespace: Optional[str] = None
    ) -> list[IRI]:
        """
        Return list of all IRIs from a position in a triple

        Results may optionally be filtered to matches within a specified
        namespace.

        :param position: `TriplePosition` specifying which item in triple is
            targeted
        :param namespace: Optional namespace for filtering results
        :return: List of `IRIs` for IRIs in specified position
        """
        if namespace is None:
            namespace = ""
        elif namespace in self.namespaces:
            namespace = self.namespaces[namespace]
        if namespace in self.reverse_namespaces:
            full_curie = f"{self.reverse_namespaces[namespace]}:"
        else:
            full_curie = None

        values = {
            str(triple[position])
            for triple in self.graph
            if isinstance(triple[position], URIRef)
        }
        return [
            self.get_iri(value)
            for value in sorted(values)
            if (value.startswith(namespace) or (full_curie is not None and value.startswith(full_curie)))
        ]

    def list_triples_for_subject(self, subject: str | IRI) -> list[Triple]:
        """
        Return list of all `Triple`s with a given term as subject

        :param subject: String IRI or `IRI`
        :return: List of `Triple`s with given subject
        """
        subject = self.get_iri(subject)
        key = f"subject|{subject}"

        matching_values = [str(subject), subject.curie]

        if key not in self.cache:
            self.cache[key] = [
                self.get_triple(s, p, o) for s, p, o in self.graph if str(s) in matching_values
            ]

        return self.cache[key]

    def list_triples_for_object(self, object_: str | IRI) -> list[Triple]:
        """
        Return list of all `Triple`s with a given term as object

        :param object_: String IRI or `IRI`
        :return: List of `Triple`s with given object
        """
        object_ = self.get_iri(object_)
        key = f"object|{object_}"

        matching_values = [str(object_), object_.curie]

        if key not in self.cache:
            self.cache[key] = [
                self.get_triple(s, p, o) for s, p, o in self.graph if str(o) in matching_values
            ]

        return self.cache[key]

    def list_triples_for_property(self, property_: str | IRI) -> list[Triple]:
        """
        Return list of all `Triple`s with a given property term

        :param property_: String IRI or `IRI`
        :return: List of `Triple`s with given property term
        """
        property_ = self.get_iri(property_)
        key = f"property|{property_}"

        matching_values = [str(property_), property_.curie]

        if key not in self.cache:
            self.cache[key] = [
                self.get_triple(s, p, o) for s, p, o in self.graph if str(p) in matching_values
            ]

        return self.cache[key]

    def count_triples_by_subject(self) -> dict[IRI, int]:
        """
        Return count of Triple`s  for every term usedm as subject

        :return: Counts of matching `Triple`s per term
        """
        return self.count_triples_by_term(TriplePosition.SUBJECT)

    def count_triples_by_property(self) -> dict[IRI, int]:
        """
        Return count of Triple`s for every term used as property

        :return: Counts of matching `Triple`s per term
        """
        return self.count_triples_by_term(TriplePosition.PROPERTY)

    def count_triples_by_object(self) -> dict[IRI, int]:
        """
        Return count of Triple`s for every term used as object

        :return: Counts of matching `Triple`s per term
        """
        return self.count_triples_by_term(TriplePosition.OBJECT)

    def count_triples_by_term(self, position: TriplePosition) -> dict[IRI, int]:
        """
        Return counts of Triple`s for every term in a specified position

        :param position: `TriplePosition` specifying which item in triple is
            targeted
        :return: Counts of matching `Triple`s per term
        """
        key = f"counts|position"
        if key in self.cache:
            return self.cache[key]

        counts = {}
        for term in [triple[position] for triple in self.list_triples()]:
            if isinstance(term, IRI):
                if term not in counts:
                    counts[term] = 1
                else:
                    counts[term] += 1

        self.cache[key] = counts

        return counts

    def list_classes(
        self,
        namespace: Optional[str] = None,
    ) -> list[IRI]:
        """
        List all classes (type rdfs:Class) in `Graph`.

        Results may optionally be filtered to matches within a specified
        namespace.

        :param namespace: Optional namespace for filtering results
        :return: List of `IRI`s for classes
        """
        return self.list_iris(
            ["?q rdf:type rdfs:Class"], f"classes|{namespace}", namespace
        )

    def list_properties(
        self,
        namespace: Optional[str] = None,
    ) -> list[IRI]:
        """
        List all properties (type rdfs:Property) in `Graph`.

        Results may optionally be filtered to matches within a specified
        namespace.

        :param namespace: Optional namespace for filtering results
        :return: List of `IRI`s for properties
        """
        return self.list_iris(
            ["?q rdf:type rdf:Property"], f"properties|{namespace}", namespace
        )

    def list_superclasses(
        self,
        class_iri: str | IRI,
        namespace: Optional[str] = None,
    ) -> list[IRI]:
        """
        List all superclasses of a specified class (including the class
        itself)

        Results may optionally be filtered to matches within a specified
        namespace.

        :param class_iri: String IRI or `IRI` for class
        :param namespace: Optional namespace for filtering results
        :return: List of `IRI`s for classes
        """
        logging.debug(f"Finding all superclasses for class {class_iri}")
        return self.list_iris_transitive(
            class_iri,
            "rdfs:subClassOf",
            f"superclasses|{class_iri}|{namespace}",
            namespace=namespace,
        )

    def list_superproperties(
        self,
        property_iri: str | IRI,
        namespace: Optional[str] = None,
    ) -> list[IRI]:
        """
        List all superproperties of a specified property (including the property
        itself).

        Results may optionally be filtered to matches within a specified
        namespace.

        :param property_iri: String IRI or `IRI` for property
        :param namespace: Optional namespace for filtering results
        :return: List of `IRI`s for properties
        """
        logging.debug(f"Finding all superproperties for property {property_iri}")
        return self.list_iris_transitive(
            property_iri,
            "rdfs:subPropertyOf",
            f"superproperties|{property_iri}|{namespace}",
            namespace=namespace,
        )

    def list_subclasses(
        self,
        class_iri: str | IRI,
        namespace: Optional[str] = None,
    ) -> list[IRI]:
        """
        List all subclasses of a specified class (including the class
        itself)

        Results may optionally be filtered to matches within a specified
        namespace.

        :param class_iri: String IRI or `IRI` for class
        :param namespace: Optional namespace for filtering results
        :return: List of `IRI`s for classes
        """
        logging.debug(f"Finding all subclasses for class {class_iri}")
        return self.list_iris_transitive(
            class_iri,
            "rdfs:subClassOf",
            f"subclasses|{class_iri}|{namespace}",
            namespace=namespace,
            reverse=True,
        )

    def list_subproperties(
        self,
        property_iri: str | IRI,
        namespace: Optional[str] = None,
    ) -> list[IRI]:
        """
        List all subproperties of a specified property (including the property
        itself).

        Results may optionally be filtered to matches within a specified
        namespace.

        :param property_iri: String IRI or `IRI` for property
        :param namespace: Optional namespace for filtering results
        :return: List of `IRI`s for properties
        """
        logging.debug(f"Finding all subproperties for property {property_iri}")
        return self.list_iris_transitive(
            property_iri,
            "rdfs:subPropertyOf",
            f"subproperties|{property_iri}|{namespace}",
            namespace=namespace,
            reverse=True,
        )

    def list_domain_properties_for_class(
        self,
        class_iri: str | IRI,
        namespace: Optional[str] = None,
    ) -> list[IRI]:
        """
        List all known properties that include a specified class in their domain.

        Results may optionally be filtered to matches within a specified
        namespace.

        :param class_iri: String IRI or `IRI` for class
        :param namespace: Optional namespace for filtering results
        :return: List of `IRI`s for properties
        """
        class_iri = self.get_iri(class_iri)
        query_strings = [
            f"?q schema:domainIncludes <{class_.iri}>"
            for class_ in self.list_superclasses(class_iri)
        ]
        return self.list_iris(
            query_strings, f"domain|{class_iri}|{namespace}", namespace
        )

    def list_range_properties_for_class(
        self,
        class_iri: str | IRI,
        namespace: Optional[str] = None,
    ) -> list[IRI]:
        """
        List all known properties that include a specified class in their range.

        Results may optionally be filtered to matches within a specified
        namespace.

        :param class_iri: String IRI or `IRI` for class
        :param namespace: Optional namespace for filtering results
        :return: List of `IRI`s for properties
        """
        class_iri = self.get_iri(class_iri)
        query_strings = [
            f"?q schema:rangeIncludes <{class_.iri}>"
            for class_ in self.list_superclasses(class_iri)
        ]
        return self.list_iris(
            query_strings, f"range|{class_iri}|{namespace}", namespace
        )

    def list_domain_classes_for_property(
        self,
        property_iri: str | IRI,
        namespace: Optional[str] = None,
    ) -> list[IRI]:
        """
        List all known classes that are included in the domain of a specified
        property.

        Results may optionally be filtered to matches within a specified
        namespace.

        :param property_iri: String IRI or `IRI` for property
        :param namespace: Optional namespace for filtering results
        :return: List of `IRI`s for classes
        """
        property_iri = self.get_iri(property_iri)
        query_strings = [
            f"<{property_}> schema:domainIncludes ?q"
            for property_ in self.list_superproperties(property_iri)
        ]
        return self.list_iris(
            query_strings, f"range|{property_iri}|{namespace}", namespace
        )

    def list_range_classes_for_property(
        self,
        property_iri: str | IRI,
        namespace: Optional[str] = None,
    ) -> list[IRI]:
        """
        List all known classes that are included in the range of a specified
        property.

        Results may optionally be filtered to matches within a specified
        namespace.

        :param property_iri: String IRI or `IRI` for property
        :param namespace: Optional namespace for filtering results
        :return: List of `IRI`s for classes
        """
        property_iri = self.get_iri(property_iri)
        query_strings = [
            f"<{property_}> schema:rangeIncludes ?q"
            for property_ in self.list_superproperties(property_iri)
        ]
        return self.list_iris(
            query_strings, f"range|{property_iri}|{namespace}", namespace
        )

    def list_instances_without_subclasses(
        self, class_iri: str | IRI, namespace: Optional[str] = None
    ) -> list[IRI]:
        """
        List all known instances of the specified class ignoring 
        subclasses.

        Results may optionally be filtered to matches within a specified
        namespace.

        :param class_iri: String IRI or `IRI` for class
        :param namespace: Optional namespace for filtering results
        :return: List of `IRI`s for instances
        """
        class_iri = self.get_iri(class_iri)
        return self.list_iris(
            [f"?q rdf:type <{class_iri}> ."],
            f"instances-specific|{class_iri}|{namespace}",
            namespace,
        )

    def list_instances(
        self, class_iri: str | IRI, namespace: Optional[str] = None
    ) -> list[IRI]:
        """
        List all known instances of the specified class or a known
        subclass.

        Results may optionally be filtered to matches within a specified
        namespace.

        :param class_iri: String IRI or `IRI` for class
        :param namespace: Optional namespace for filtering results
        :return: List of `IRI`s for instances
        """
        key = f"instances|{class_iri}|{namespace}"
        if key in self.cache:
            return self.cache[key]

        instances = []
        for class_ in self.list_subclasses(class_iri):
            instances += self.list_instances_without_subclasses(class_)
        self.cache[key] = instances
        return instances

    def list_instances_by_class_and_name(
        self,
        class_iri: str | IRI,
        name: str,
        check_alternate_names: bool = False,
        namespace: Optional[str] = None,
    ) -> list[IRI]:
        """
        List all known instances of the specified class with the specified
        unqualified name.

        Results may optionally be filtered to matches within a specified
        namespace.

        :param class_iri: String IRI or `IRI` for class
        :param name: Unqualified name to find
        :param check_alternate_names: True if alternateName properties should
            also be checked
        :param namespace: Optional namespace for filtering results
        :return: List of `IRI`s for instances
        """
        class_iri = self.get_iri(class_iri)
        cache_key = f"instances-class-name|{class_iri}|{name}|{check_alternate_names}|{namespace}"
        query_strings = [
            f"?q rdf:type <{class_iri}> . {{ ?q schema:name '{name}'@en }} UNION {{ ?q schema:name '{name}'}}."
        ]
        query_strings.append(
            f"?q rdf:type <{class_iri}> .  {{ ?q rdfs:label '{name}'@en }} UNION {{ ?q rdfs:label '{name}'}} UNION {{ ?q skos:prefLabel '{name}'@en}} UNION {{ ?q skos:prefLabel '{name}'}}."
        )
        if check_alternate_names:
            query_strings.append(
                f"?q rdf:type <{class_iri}> .  {{ ?q schema:alternateName '{name}'@en }} UNION {{ ?q schema:alternateName '{name}'}}."
            )
        return self.list_iris(query_strings, cache_key, namespace=namespace)

    def list_instances_by_name(
        self,
        name: str,
        check_alternate_names: bool = False,
        namespace: Optional[str] = None,
    ) -> list[IRI]:
        """
        List all known instances of any or no class with the specified
        unqualified name.

        Results may optionally be filtered to matches within a specified
        namespace.

        :param name: Unqualified name to find
        :param check_alternate_names: True if alternateName properties should
            also be checked
        :param namespace: Optional namespace for filtering results
        :return: List of `IRI`s for instances
        """
        cache_key = f"instances-name|{name}|{check_alternate_names}|{namespace}"
        query_strings = [
            f"{{ ?q schema:name '{name}'@en }} UNION {{ ?q schema:name '{name}'}}."
        ]
        query_strings.append(
            f"{{ ?q rdfs:label '{name}'@en }} UNION {{ ?q rdfs:label '{name}'}} UNION {{ ?q skos:prefLabel '{name}'@en}} UNION {{ ?q skos:prefLabel '{name}'}}."
        )
        if check_alternate_names:
            query_strings.append(
                f"{{ ?q schema:alternateName '{name}'@en }} UNION {{ ?q schema:alternateName '{name}'}}."
            )
        return self.list_iris(query_strings, cache_key, namespace=namespace)

    def list_properties_by_name(
        self,
        name: str,
        check_alternate_names: bool = False,
        namespace: Optional[str] = None,
    ) -> list[IRI]:
        """
        List all known properties with the specified unqualified name.

        Results may optionally be filtered to matches within a specified
        namespace.

        :param property_iri: String IRI or `IRI` for property
        :param name: Unqualified name to find
        :param check_alternate_names: True if alternateName properties should
            also be checked
        :param namespace: Optional namespace for filtering results
        :return: List of `IRI`s for properties
        """
        return self.list_instances_by_class_and_name(
            "rdf:Property",
            name,
            check_alternate_names=check_alternate_names,
            namespace=namespace,
        )

    def list_properties_by_domain_and_range(
        self, domain_iri: str | IRI, range_iri: str, namespace: Optional[str] = None
    ) -> list[IRI]:
        """
        List all known properties with the specified classes in their domain and
        range (one of each)

        Results may optionally be filtered to matches within a specified
        namespace.

        :param domain_iri: String IRI or `IRI` for domain
        :param range_iri: String IRI for domain
        :param namespace: Optional namespace for filtering results
        :return: List of `IRI`s for properties
        """
        cache_key = f"domain-and-range|{domain_iri}|{range_iri}|{namespace}"

        if cache_key in self.cache:
            return self.cache[cache_key]

        domain_properties = self.list_domain_properties_for_class(domain_iri, namespace)
        range_properties = self.list_range_properties_for_class(range_iri, namespace)

        properties = list(set(domain_properties) & set(range_properties))

        self.cache[cache_key] = properties

        return properties

    def get_iri(self, id: str | URIRef | IRI) -> IRI:
        """
        Get `IRI` for specified CURIE or IRI string, `URIRef`` or `IRI`

        If the supplied value is an `IRI`, it is returned directly

        CURIEs are mapped to IRI strings using the current namespace_definitions

        IRI strings are then coverted to `IRI` instances

        :param id: String IRI or CURIE
        :return: `IRI` instance
        """
        if isinstance(id, IRI):
            return id

        iri = str(id)

        cache_key = f"term|{iri}"

        if cache_key in self.cache:
            return self.cache[cache_key]

        if not iri.startswith("http"):
            for namespace, namespace_definition in self.namespace_definitions.items():
                if iri.startswith(f"{namespace_definition.prefix}:"):
                    iri = f"{namespace}{iri[len(namespace_definition.prefix) + 1:]}"

        return IRI(iri, self.namespace_definitions)

    def list_iris(
        self, query_strings: list[str], cache_key: str, namespace: Optional[str] = None
    ) -> list[IRI]:
        """
        List IRIs matching any of a set of SPARQL query strings.

        Results may optionally be filtered using a specified namespace.

        :param query_strings: List of SPARQL query elements
        :param cache_key: Key to store results in cache - this should be
            supplied by the initial caller and None during recursion
        :param namespace: Optional namespace for filtering results
        :return: List of `IRI` instances
        """
        logging.debug(
            f"Listing IRIs for query: {query_strings} (namespace: {namespace})"
        )

        full_curie = None
        if namespace is not None and namespace in self.namespaces:
            namespace = self.namespaces[namespace]
        if namespace in self.reverse_namespaces:
            full_curie = f"{self.reverse_namespaces[namespace]}:"

        if cache_key in self.cache:
            return self.cache[cache_key]

        results = []

        for q in query_strings:

            query = """
                    prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    prefix schema: <https://schema.org/>

                    SELECT ?q
                    WHERE { %s }
                    """ % (q)

            logging.debug(f"Issuing query:\n{query}")

            for p in self.graph.query(query):
                # The rdflib `Result` object may be a boolean
                if not isinstance(p, bool):
                    if isinstance(p[0], URIRef) and (
                        namespace is None or str(p[0]).startswith(namespace) or (full_curie is not None and str(p[0]).startswith(full_curie))
                    ):
                        iri = self.get_iri(str(p[0]))
                        if iri not in results:
                            results.append(iri)

        self.cache[cache_key] = results

        logging.debug(f"Matching terms: {', '.join([iri.curie for iri in results])}")

        return results

    def list_iris_transitive(
        self,
        subject: str,
        transitive_property: str,
        cache_key: Optional[str],
        matches: Optional[list[IRI]] = None,
        namespace: Optional[str] = None,
        reverse: Optional[bool] = False,
    ) -> list[IRI]:
        """
        List IRIs connected to the subject IRI or CURIE by any number of
        links of the specified property.

        The `matches` parameter is internal for the recursion and should
        not be set by a caller.

        Results may optionally be filtered using a specified namespace.

        :param subject: String IRI or CURIE for starting term
        :param transitive_property: String IRI or CURIE for property to follow
        :param cache_key: Key to store results in cache - this should be
            supplied by the initial caller and None during recursion
        :param matches: IRIs for terms already matched - this should be
            None on the initial call and is set during recursion
        :param namespace: Optional namespace for filtering results
        :param reverse: If True, treat `subject` as the object and find matching subjects
        :return: List of `IRI` instances
        """
        logging.debug(
            f"Listing IRIs for subject: {subject} with transitive property: {transitive_property}"
        )

        if cache_key is not None and cache_key in self.cache:
            return self.cache[cache_key]

        full_curie = None
        if namespace is not None and namespace in self.namespaces:
            namespace = self.namespaces[namespace]
        if namespace in self.reverse_namespaces:
            full_curie = f"{self.reverse_namespaces[namespace]}:"
            
        subject_term = self.get_iri(subject)
        property_term = self.get_iri(transitive_property)

        if matches is None:
            matches = [subject_term]

        if reverse:
            query = """
                    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>

                    SELECT ?t
                    WHERE {
                    ?t <%s> <%s> .
                    }
                    """ % (property_term.iri, subject_term.iri)
        else:
            query = """
                    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>

                    SELECT ?t
                    WHERE {
                    <%s> <%s> ?t .
                    }
                    """ % (subject_term.iri, property_term.iri)

        logging.debug(f"Issuing query:\n{query}")

        for t in self.graph.query(query):
            if isinstance(t[0], URIRef):
                match = self.get_iri(t[0])
                if match not in matches:
                    if namespace is None or match.ns.startswith(namespace) or (full_curie is not None and str(p[0]).startswith(full_curie)):
                        matches.append(match)
                    self.list_iris_transitive(
                        match.iri, transitive_property, None, matches, namespace=namespace, reverse=reverse
                    )

        if cache_key is not None:
            self.cache[cache_key] = matches

        return matches

    def format_iri_list(
        self,
        iris: list[IRI],
        max_rows: Optional[int] = None,
        descriptions: Optional[bool] = False
    ) -> str:
        """
        Return string containing (column-aligned) a specified number of elements
        from each in a list of tuples.

        :param tuples: list of `IRIs` or `Triples` (treated as tuples)
        :param element_count: number of tuple elements to display
        :param max_rows: optional cap on the number of tuples to process
        :param descriptions: If True, output properties for each IRI.
        """
        if iris is None or len(iris) == 0:
            return ""

        if max_rows is not None:
            iris = iris[0:max_rows]

        curie_length = max([len(iri.curie) for iri in iris])
        formatted = []
        for iri in iris:
            if len(formatted) > 0:
                formatted.append("")
            formatted.append(f"{iri.curie:{curie_length}s}   {iri.iri}")
            if descriptions:
                for _, pp, po in self.list_triples_for_subject(iri):
                    formatted.append(f"    {pp.curie} : {po.curie if isinstance(po, IRI) else str(po)}")
        return "\n".join(formatted)

    def format_triple_list(
        self,
        triples: list[Triple],
        max_rows: Optional[int] = None,
        max_node_length: Optional[int] = None,
    ) -> str:
        """
        Return string containing (column-aligned) a specified number of elements
        from each in a list of tuples.

        :param tuples: list of `IRIs` or `Triples` (treated as tuples)
        :param max_rows: optional cap on the number of tuples to process
        :param max_node_length: maximum string length for any triple member
        """
        if triples is None or len(triples) == 0:
            return ""

        if max_rows is not None and max_rows > 1:
            triples = triples[0:max_rows]

        if max_node_length is not None and max_node_length < 1:
            max_node_length = None

        formatted: list[tuple[str, str, str]] = []
        subject_length = 0
        property_length = 0

        for triple in triples:
            if isinstance(triple[0], IRI):
                s = triple[0].curie
            else:
                s = str(triple[0])
            p = (
                triple[TriplePosition.PROPERTY].curie
                if isinstance(triple[TriplePosition.PROPERTY], IRI)
                else str(triple[TriplePosition.PROPERTY])
            )
            o = (
                triple[TriplePosition.OBJECT].curie
                if isinstance(triple[TriplePosition.OBJECT], IRI)
                else str(triple[TriplePosition.OBJECT])
            )
            formatted.append((s, p, o))
        subject_length = max([len(s) for s, _, _ in formatted])
        if max_node_length is not None and max_node_length < subject_length:
            subject_length = max_node_length
        property_length = max([len(p) for _, p, _ in formatted])
        if max_node_length is not None and max_node_length < property_length:
            property_length = max_node_length

        return "\n".join(
            [
                f"{s:{subject_length}s}   {p:{property_length}s}   {o if max_node_length is None else o[0:max_node_length]}"
                for s, p, o in formatted
            ]
        )
