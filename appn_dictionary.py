#!/usr/bin/env python3
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
# -----------------------------------------------------------------------------
# Created By  : Donald Hobern, donald.hobern@adelaide.edu.au
# Created Date: 2026-08-20
# version ='2026.0.1'
# -----------------------------------------------------------------------------

import argparse
import logging
import sys
from pathlib import Path

from rdflib import Graph, URIRef
from rdflib.namespace import Namespace, NamespaceManager
from typing import Any, Optional

from appn_types import Namespace, Term, Triple
from appn_configuration import load_configuration

logger = logging.getLogger(__name__)



### Dictionary ################################################################
#
# Wrapper class around rdflib Graph instance to simplify common query needs
#
# A new Dictionary has an empty graph and cache. Linked-data objects can be
# added to the graph via the load() method. When the graph changes, the
# response cache is cleared.
#
# All get_* and list_* methods check the cache for a previous response to the
# request and otherwise generate and cache a new response from the graph.
#
class Dictionary:

    def __init__(self, namespaces: Optional[dict[str,Namespace]] = None) -> None:
        self.graph = Graph()
        self.namespace_manager = NamespaceManager(self.graph)
        self.loaded = set()
        self.cache = {}
        self.reverse_namespaces = {}
        self.namespaces = {} if namespaces is None else namespaces

    def load(
        self,
        asset_namespace: str,
        asset_path: Optional[str] = None,
        asset_prefix: Optional[str] = None,
    ) -> None:
        try:
            if asset_namespace in self.namespaces and isinstance(self.namespaces[asset_namespace], Namespace):
                namespace : Namespace = self.namespaces[asset_namespace]
            else:
                namespace = None
            if asset_path is None:
                if namespace is not None and namespace.path is not None:
                    asset_path = namespace.path
                else:
                    asset_path = asset_namespace
            if asset_prefix is None and namespace is not None and namespace.prefix is not None:
                    asset_prefix = namespace.prefix
            logger.info(
                f"Loading {asset_namespace} from {asset_path} with prefix: {asset_prefix}"
            )
            self.graph.parse(asset_path)
            self.loaded.add(asset_namespace)
            if asset_prefix is not None:
                self.namespace_manager.bind(
                    asset_prefix, Namespace(asset_namespace), override=True
                )

            self.cache = {}
            self.namespaces = {
                p: str(ns) for p, ns in self.namespace_manager.namespaces()
            }
            self.reverse_namespaces = {v: k for k, v in self.namespaces.items()}

            logger.info(f"Loaded {asset_namespace}")

        except Exception:
            logger.error(f"Failed to load {asset_namespace}: repr(e)", exc_info=True)

    def import_references(self):
        iris = set()
        for s, o, p in self.graph:
            for iri in [s, o, p]:
                if isinstance(iri, URIRef) and iri not in iris:
                    ns = self.get_namespace_from_iri(iri)
                    logger.debug(f"{iri} -> {ns}")
                    if ns is not None and ns not in self.loaded:
                        self.load(ns)
                    logger.debug(f"Found IRI <{iri}>")
                    iris.add(iri)

    def get_namespace_from_iri(self, iri: str) -> Optional[str]:
        for ns in self.reverse_namespaces.keys():
            if iri.startswith(ns):
                return ns
        return None

    def get_namespaces(self) -> dict[str, str]:
        return self.namespaces

    def list_triples(self) -> list[Triple]:
        return [Triple(s, p, o) for (s, p, o) in self.graph]

    def list_triples_for_subject(self, subject: str) -> list[Triple]:
        subject = self.get_iri(subject)
        subject_key = f"subject|{subject}"

        if subject_key not in self.cache:
            self.cache[subject_key] = [
                (s, p, o) for (s, p, o) in self.graph if (str(s) == subject)
            ]

        return self.cache[subject_key]

    def list_triples_for_object(self, object_: str) -> list[Triple]:
        object_ = self.get_iri(object_)
        object_key = f"object|{object_}"

        if object_key not in self.cache:
            self.cache[object_key] = [
                (s, p, o) for (s, p, o) in self.graph if (str(o) == object_)
            ]

        return self.cache[object_key]

    def list_triples_for_property(self, property_: str) -> list[Triple]:
        property_ = self.get_iri(property_)
        property_key = f"object|{property_}"

        if property_key not in self.cache:
            self.cache[property_key] = [
                (s, p, o) for (s, p, o) in self.graph if (str(p) == property_)
            ]

        return self.cache[property_key]

    def list_classes(self) -> list[Term]:
        return self.list_iris(["?q rdf:type rdfs:Class"], f"classes")

    def list_properties(self) -> list[Term]:
        return self.list_iris(["?q rdf:type rdf:Property"], f"properties")

    def list_superclasses(self, class_iri: str) -> list[Term]:
        logging.info(f"Finding all classes for class {class_iri}")
        return self.list_iris_transitive(
            class_iri, "rdfs:subClassOf", f"superclasses|{class_iri}"
        )

    def list_superproperties(self, property_iri: str) -> list[Term]:
        logging.info(f"Finding all properties for property {property_iri}")
        return self.list_iris_transitive(
            property_iri, "rdfs:subPropertyOf", f"superclasses|{property_iri}"
        )

    def list_domain_properties_for_class(self, class_iri: str) -> list[Term]:
        class_iri = self.get_iri(class_iri)
        query_strings = [
            f"?q schema:domainIncludes <{class_.iri}>"
            for class_ in self.list_superclasses(class_iri)
        ]
        return self.list_iris(query_strings, f"domain|{class_iri}")

    def list_range_properties_for_class(self, class_iri: str) -> list[Term]:
        class_iri = self.get_iri(class_iri)
        query_strings = [
            f"?q schema:rangeIncludes <{class_.iri}>"
            for class_ in self.list_superclasses(class_iri)
        ]
        return self.list_iris(query_strings, f"range|{class_iri}")

    def list_instances(self, class_iri: str) -> list[Term]:
        class_iri = self.get_iri(class_iri)
        return self.list_iris(
            [f"?q rdf:type <{class_iri}> ."], f"instances|{class_iri}"
        )

    def list_instances_by_class_and_name(
        self,
        class_iri: str,
        name: str,
        check_alternate_names: bool = False,
        namespace: Optional[str] = None,
    ) -> list[Term]:
        class_iri = self.get_iri(class_iri)
        cache_key = (
            f"instances-name|{class_iri}|{name}|{check_alternate_names}|{namespace}"
        )
        query_strings = [
            f"?q rdf:type <{class_iri}> . {{ ?q schema:name '{name}'@en }} UNION {{ ?q schema:name '{name}'}}."
        ]
        query_strings.append(
            f"?q rdf:type <{class_iri}> .  {{ ?q rdfs:label '{name}'@en }} UNION {{ ?q rdfs:label '{name}'}}."
        )
        if check_alternate_names:
            query_strings.append(
                f"?q rdf:type <{class_iri}> .  {{ ?q schema:alternateName '{name}'@en }} UNION {{ ?q schema:alternateName '{name}'}}."
            )
        return self.list_iris(query_strings, cache_key, namespace=namespace)

    def list_properties_by_name(
        self,
        name: str,
        check_alternate_names: bool = False,
        namespace: Optional[str] = None,
    ) -> list[Term]:
        return self.list_instances_by_class_and_name(
            "rdf:Property",
            name,
            check_alternate_names=check_alternate_names,
            namespace=namespace,
        )

    def get_iri(self, curie: str) -> str:
        cache_key = f"iri|{curie}"

        if cache_key in self.cache:
            return self.cache[cache_key]

        if curie.startswith("http"):
            iri = curie
        else:
            iri = None
            parts = curie.split(":")
            if len(parts) == 2:
                prefix = parts[0]
                for p, ns in self.namespace_manager.namespaces():
                    if p == prefix:
                        iri = f"{ns}{parts[1]}"
                        logging.debug(f"Expanded {curie} to {iri}")

        if iri is None:
            logging.error(f"Could not expand identifier: {curie}")
            iri = curie

        self.cache[cache_key] = iri

        return iri

    def get_curie(self, iri: str) -> str:
        cache_key = f"curie|{iri}"

        if cache_key in self.cache:
            return self.cache[cache_key]

        curie = iri
        if iri.startswith("http"):
            for ns in self.reverse_namespaces:
                if iri.startswith(ns):
                    curie = f"{self.reverse_namespaces[ns]}:{iri[len(ns):]}"

        self.cache[cache_key] = curie

        return curie

    def get_term(self, iri: str) -> Term:
        cache_key = f"term|{iri}"

        if cache_key in self.cache:
            return self.cache[cache_key]

        if not iri.startswith("http"):
            iri = self.get_iri(iri)
        curie = self.get_curie(iri)
        if curie != iri:
            prefix, name = curie.split(":")
            ns = self.namespaces[prefix]
        else:
            ns, curie, prefix, name = "", "", "", ""
        term = Term(iri, curie, self.namespaces[prefix], prefix, name)

        self.cache[cache_key] = term

        return term

    def list_iris(
        self, query_strings: list[str], cache_key: str, namespace: Optional[str] = None
    ) -> list[Term]:

        logging.info(f"Listing IRIs for query: {query_strings}")

        if namespace is not None and namespace in self.namespaces:
            namespace = self.namespaces[namespace]

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
                if isinstance(p[0], URIRef) and (
                    namespace is None or str(p[0]).startswith(namespace)
                ):
                    term = self.get_term(str(p[0]))
                    if term not in results:
                        results.append(term)

        self.cache[cache_key] = results

        logging.debug(f"Matching terms: {', '.join([t[0] for t in results])}")

        return results

    def list_iris_transitive(
        self,
        subject: str,
        transitive_property: str,
        cache_key: Optional[str],
        matches: Optional[list[Term]] = None,
    ) -> list[Term]:

        logging.info(
            f"Listing IRIs for subject: {subject} with transitive property: {transitive_property}"
        )

        if cache_key is not None and cache_key in self.cache:
            return self.cache[cache_key]

        subject_term = self.get_term(subject)
        property_term = self.get_term(transitive_property)

        if matches is None:
            matches = [subject_term]

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
                match = self.get_term(str(t[0]))
                if match not in matches:
                    matches.append(match)
                    self.list_iris_transitive(
                        match.iri, transitive_property, None, matches
                    )

        if cache_key is not None:
            self.cache[cache_key] = matches

        return matches


### process_argv ##############################################################
#
# Safely process sys.argv, returning a dictionary of option values.
#
#     query             : query type - one of:
#                          { classes, properties, domain, range, namespaces,
#                            subject, property, object, triples,
#                            property-name, property-name-all,
#                            instance-name, instance-name-all }.
#     -l, --log-level   : "info" / "error" / "debug".
#     -e,               : Display logging outputs to stderr.
#      --echo-to-stderr
#
subcommand_helptext = {
    "namespaces": "List all prefixes and namespaces from loaded assets.",
    "triples": "List all triples from loaded assets.",
    "classes": "List IRIs and CURIEs for all classes defined or referenced by loaded assets.",
    "properties": "List IRIs and CURIEs for all properties defined or referenced by loaded assets.",
    "superclasses": "List IRIs and CURIEs for all known superclasses for a class specified using its IRI or CURIE.",
    "superproperties": "List IRIs and CURIEs for all known superproperties for a property specified using its IRI or CURIE.",
    "instances": "List  IRIs and CURIEs for all known instances of a class specified using its IRI or CURIE.",
    "domain": "List IRIs and CURIEs for all known properties with a domain including a class specified using its IRI or CURIE.",
    "range": "List IRIs and CURIEs for all known properties with a range including a class specified using its IRI or CURIE.",
    "subject": "List all triples with the specified IRI or CURIE as subject.",
    "property": "List all triples with the specified IRI or CURIE as property.",
    "object": "List all triples with the specified IRI or CURIE as object.",
    "property-name": "List IRIs and CURIEs for all properties with the specified value for schema:name or rdfs:label (optionally filtered to a specified namespace).",
    "property-name-all": "List IRIs and CURIEs for all properties with the specified value for schema:name, rdfs:label or schema:alternateName (optionally filtered to a specified namespace).",
    "instance-name": "List IRIs and CURIEs for all terms belonging to the specified class and with the specified value for schema:name or rdfs:label (optionally filtered to a specified namespace).",
    "instance-name-all": "List IRIs and CURIEs for all terms belonging to the specified class and with the specified value for schema:name, rdfs:label or or schema:alternateName (optionally filtered to a specified namespace).",
    "test": "Run tests for all subcommands.",
}


def process_argv(argv: list[str]) -> dict[str, Any]:
    parser = argparse.ArgumentParser(
        prog=argv[0],
        description=f"{argv[0]}: Query linked-data graphs for common filters, based on the APPN schema and schemas referenced by the APPN schema and on any assets loaded using the asset command-line argument.",
    )
    subparsers = parser.add_subparsers(dest="query")
    for cmd in ["namespaces", "triples", "classes", "properties", "test"]:
        subparser = subparsers.add_parser(
            cmd, help=(subcommand_helptext[cmd] if cmd in subcommand_helptext else None)
        )
    for cmd in [
        "superclasses",
        "superproperties",
        "instances",
        "domain",
        "range",
        "subject",
        "property",
        "object",
    ]:
        subparser = subparsers.add_parser(
            cmd, help=(subcommand_helptext[cmd] if cmd in subcommand_helptext else None)
        )
        subparser.add_argument("iri")
    for cmd in ["property-name", "property-name-all"]:
        subparser = subparsers.add_parser(
            cmd, help=(subcommand_helptext[cmd] if cmd in subcommand_helptext else None)
        )
        subparser.add_argument("name")
        subparser.add_argument("-n", "--namespace")
    for cmd in ["instance-name", "instance-name-all"]:
        subparser = subparsers.add_parser(
            cmd, help=(subcommand_helptext[cmd] if cmd in subcommand_helptext else None)
        )
        subparser.add_argument("class")
        subparser.add_argument("name")
        subparser.add_argument("-n", "--namespace")

    parser.add_argument(
        "-l",
        "--log-level",
        choices=("error", "warning", "info", "debug"),
        default="info",
        help="Set logging level",
    )
    parser.add_argument(
        "-e",
        "--echo-to-stderr",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Echo log messages to console",
    )
    parser.add_argument(
        "-a",
        "--asset",
        action="append",
        help="Namespace for linked-data asset to load into graph.",
    )
    parser.add_argument(
        "-p", "--prefix", action="append", help="Optional prefix for loaded asset."
    )
    parser.add_argument(
        "-f",
        "--filepath_to_asset",
        action="append",
        help="Path to asset file if different from asset namespace.",
    )
    args = vars(parser.parse_args(argv[1:]))

    return args


### start_log #################################################################
#
# Start logging to default or named file and optionally to stderr.
#
#     level             : info / error / debug (string or logging enumeration).
#     name              : (optional) name for log file.
#     echo              : boolean - duplicate logging to stderr
#
def start_log(
    level: str | int = logging.INFO, name: Optional[str] = None, echo: bool = True
) -> None:
    if isinstance(level, str):
        level = level.lower()
        if level == "error":
            log_level = logging.ERROR
        elif level == "debug":
            log_level = logging.DEBUG
        else:
            log_level = logging.INFO
    else:
        log_level = level

    if name is None:
        name = Path(sys.argv[0]).stem
    logfile_name = f"{name}.log"
    logging.basicConfig(
        filename=logfile_name,
        filemode="w",
        level=log_level,
        format="%(asctime)s %(levelname)s %(filename)s : %(lineno)s - %(funcName)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    if echo:
        logging.getLogger().addHandler(logging.StreamHandler())

    logging.info(f"Logging started to {logfile_name} at level {level} and echo {echo}")


### show_tuple_list ###########################################################
#
# Print (column-aligned) a specified number of elements from each in a list of
# tuples.
#
#     tuples            : list of tuples
#     element_count     : number of tuple elements to display
#     max_rows          : optional cap on the number of tuples to process
#
def show_tuple_list(
    tuples: list[Term] | list[Triple],
    element_count: Optional[int] = None,
    max_rows: Optional[int] = None,
) -> None:
    if max_rows is not None:
        tuples = tuples[0:max_rows]
    if element_count is None:
        if len(tuples) > 0:
            element_count = len(tuples[0])
        else:
            element_count = 1
    lengths = [0] * element_count
    for t in tuples:
        for element in range(min(element_count, len(t))):
            length = len(t[element])
            if length > lengths[element]:
                lengths[element] = length

    for t in tuples:
        print(
            "   ".join(
                [f"{t[e]:{lengths[e]}s}" for e in range(min(element_count, len(t)))]
            ).strip()
        )


def execute_query(
    d: Dictionary, args: dict[str, Any], max_rows: Optional[int] = None
) -> None:

    if args["query"] == "classes":
        show_tuple_list(d.list_classes(), 2, max_rows=max_rows)

    elif args["query"] == "properties":
        show_tuple_list(d.list_properties(), 2, max_rows=max_rows)

    elif args["query"] == "superclasses":
        show_tuple_list(d.list_superclasses(args["iri"]), max_rows=max_rows)

    elif args["query"] == "superproperties":
        show_tuple_list(d.list_superproperties(args["iri"]), 2, max_rows=max_rows)

    elif args["query"] == "instances":
        show_tuple_list(d.list_instances(args["iri"]), 2, max_rows=max_rows)

    elif args["query"] == "domain":
        show_tuple_list(
            d.list_domain_properties_for_class(args["iri"]), 2, max_rows=max_rows
        )

    elif args["query"] == "range":
        show_tuple_list(
            d.list_range_properties_for_class(args["iri"]), 2, max_rows=max_rows
        )

    elif args["query"] == "property-name":
        show_tuple_list(
            d.list_properties_by_name(
                args["name"],
                namespace=args["namespace"] if "namespace" in args else None,
            ),
            2,
            max_rows=max_rows,
        )

    elif args["query"] == "property-name-all":
        show_tuple_list(
            d.list_properties_by_name(
                args["name"],
                check_alternate_names=True,
                namespace=args["namespace"] if "namespace" in args else None,
            ),
            2,
            max_rows=max_rows,
        )

    elif args["query"] == "instance-name":
        show_tuple_list(
            d.list_instances_by_class_and_name(
                args["class"],
                args["name"],
                namespace=args["namespace"] if "namespace" in args else None,
            ),
            2,
            max_rows=max_rows,
        )

    elif args["query"] == "instance-name-all":
        show_tuple_list(
            d.list_instances_by_class_and_name(
                args["class"],
                args["name"],
                check_alternate_names=True,
                namespace=args["namespace"] if "namespace" in args else None,
            ),
            2,
            max_rows=max_rows,
        )

    elif args["query"] == "namespaces":
        namespaces = d.get_namespaces()
        keys = sorted(namespaces.keys())
        if max_rows is not None:
            keys = keys[0:max_rows]
        length = max([len(k) for k in keys])
        for k in keys:
            if len(k) > 0:
                print(f"{k:>{length}s} : {namespaces[k]}")

    elif args["query"] in ["subject", "property", "object", "triples"]:
        if args["query"] == "subject":
            triples = d.list_triples_for_subject(args["iri"])
        elif args["query"] == "property":
            triples = d.list_triples_for_property(args["iri"])
        elif args["query"] == "object":
            triples = d.list_triples_for_object(args["iri"])
        else:
            triples = d.list_triples()
        show_tuple_list(triples, 3, max_rows=max_rows)


if __name__ == "__main__":

    # Locations to use for machine-readable assets
    schema_assets = {
        APPN_SCHEMA: "./appn-schema.ttl",
        SCHEMA_SCHEMA: "schema_assets/schemaorg-current-https.ttl",
        BIO_SCHEMA: "schema_assets/bioschemas_types.ttl",
        CDI_SCHEMA: "schema_assets/ddi-cdi.jsonld",
        DC_SCHEMA: "schema_assets/dublin_core_terms.rdf",
        PPEO_SCHEMA: "schema_assets/PPEO.owl",
        PROV_SCHEMA: "schema_assets/prov.ttl",
        RDFS_SCHEMA: "schema_assets/rdf-schema.ttl",
        RDF_SCHEMA: "schema_assets/22-rdf-syntax-ns.ttl",
        SKOS_SCHEMA: "schema_assets/skos.rdf",
        SOSA_SCHEMA: "schema_assets/sosa.ttl",
        SSN_SCHEMA: "schema_assets/ssn.ttl",
        APPN_VOCABULARY: "vocabulary/APPN/vocabulary.rdf",
        ANU_VOCABULARY: "vocabulary/ANU/vocabulary.rdf",
        AU_VOCABULARY: "vocabulary/AU/vocabulary.rdf",
        CSU_VOCABULARY: "vocabulary/CSU/vocabulary.rdf",
        DPIRD_VOCABULARY: "vocabulary/DPIRD/vocabulary.rdf",
        LTU_VOCABULARY: "vocabulary/LTU/vocabulary.rdf",
        UQ_VOCABULARY: "vocabulary/UQ/vocabulary.rdf",
        USYD_VOCABULARY: "vocabulary/USYD/vocabulary.rdf",
        UWA_VOCABULARY: "vocabulary/UWA/vocabulary.rdf",
        WSU_VOCABULARY: "vocabulary/WSU/vocabulary.rdf",
    }

    args = process_argv(sys.argv)
    start_log(args["log_level"], None, args["echo_to_stderr"])

    config = load_configuration("appn")
    namespace_definitions = []
    if "namespaces" in config and isinstance(config["namespaces"], dict):
        for ns, properties = config["namespaces"].items():
            prefix, path = None, None
            if isinstance(properties, dict):
                if "prefix" in properties:
                    prefix = properties["prefix"]
                if "path" in properties:
                    path = properties["path"]
            namespace_definitions.append(Namespace(ns, prefix, path))

    d = Dictionary(namespace_definitions = namespace_definitions)
    d.load(APPN_SCHEMA)
    if args["asset"] is not None:
        for i in range(len(args["asset"])):
            asset = args["asset"][i]
            if args["prefix"] is not None and i in range(len(args["prefix"])):
                prefix = args["prefix"][i]
            else:
                prefix = f"asset{i}"
            if args["filepath_to_asset"] is not None and i in range(
                len(args["filepath_to_asset"])
            ):
                path = args["filepath_to_asset"][i]
            else:
                path = asset
            d.load(asset, asset_path=path, asset_prefix=prefix)
    d.import_references()

    print()

    if args["query"] == "test":
        for q in [
            [
                "namespaces",
            ],
            [
                "triples",
            ],
            [
                "classes",
            ],
            [
                "properties",
            ],
            [
                "superclasses",
                "appn:Sampling",
            ],
            [
                "superproperties",
                "schema:name",
            ],
            [
                "instances",
                "appn:Scale",
            ],
            [
                "domain",
                "appn:Scale",
            ],
            [
                "range",
                "appn:Scale",
            ],
            [
                "subject",
                "appn:Scale",
            ],
            [
                "property",
                "appn:hasScale",
            ],
            [
                "object",
                "appn:Scale",
            ],
            ["property-name", "name"],
            [
                "property-name-all",
                "comment",
                "-n",
                "schema",
            ],
            [
                "instance-name",
                "appn:Scale",
                "millimeter",
            ],
            [
                "instance-name-all",
                "appn:Scale",
                "mm",
                "-n",
                "ltu",
            ],
        ]:
            print(f"Executing: {' '.join(q)}\n")
            execute_query(d, process_argv([sys.argv[0]] + q), max_rows=5)
            print()
    else:
        execute_query(d, args)

    print()

    logger.info("Finished")
