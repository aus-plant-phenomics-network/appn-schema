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
from collections import namedtuple
from pathlib import Path
from rdflib import Graph, URIRef
from rdflib.namespace import Namespace, NamespaceManager
from typing import Any, Optional, Tuple

logger = logging.getLogger(__name__)

APPN_SCHEMA = "https://schema.plantphenomics.org.au/"
RDFS_SCHEMA = "http://www.w3.org/2000/01/rdf-schema#"
RDF_SCHEMA = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
SCHEMA_SCHEMA = "https://schema.org/"
BIO_SCHEMA = "https://bioschemas.org/terms/"
CDI_SCHEMA = "http://ddialliance.org/Specification/DDI-CDI/1.0/RDF/"
PPEO_SCHEMA = "http://purl.org/ppeo/PPEO.owl#"
SOSA_SCHEMA = "http://www.w3.org/ns/sosa/"
SSN_SCHEMA = "http://www.w3.org/ns/ssn/"
PROV_SCHEMA = "http://www.w3.org/ns/prov#"

LTU_VOCAB = "https://id.plantphenomics.org.au/LTU/"

# Locations to use for machine-readable assets
schema_assets = {
    APPN_SCHEMA: "./appn-schema.ttl", # f"{APPN_SCHEMA}appn-schema",
    RDFS_SCHEMA: "schema_assets/rdf-schema.ttl",
    RDF_SCHEMA: "schema_assets/22-rdf-syntax-ns.ttl",
    # Schema.org publishes versions using both HTTP and HTTPS - we use
    # HTTPS which seems to be most widely used.
    SCHEMA_SCHEMA: "schema_assets/schemaorg-current-https.ttl",
    BIO_SCHEMA: "schema_assets/bioschemas_types.ttl",
    CDI_SCHEMA: "schema_assets/ddi-cdi.jsonld",
    PPEO_SCHEMA: "schema_assets/PPEO.owl",
    SOSA_SCHEMA: "schema_assets/sosa.ttl",
    SSN_SCHEMA: "schema_assets/ssn.ttl",
    PROV_SCHEMA: "schema_assets/prov.ttl",
}

Term = namedtuple("Term", ["iri", "curie", "ns", "prefix", "name"])

class Dictionary:

    def __init__(self) -> None:
        self.graph = Graph()
        self.namespace_manager = NamespaceManager(self.graph)
        self.loaded = set()
        self.cache = {}
        self.namespaces = {}
        self.reverse_namespaces = {}

    def load(
        self, asset_url: str, prefix: Optional[str] = None, import_references: bool = False
    ) -> None:
        try:
            logger.info(f"Loading {asset_url}")
            self.graph.parse(
                schema_assets[asset_url] if asset_url in schema_assets else asset_url
            )
            self.loaded.add(asset_url)
            if prefix is not None:
                self.namespace_manager.bind(prefix, Namespace(asset_url), override=True)


            self.cache = {}
            self.namespaces = {p: str(ns) for p, ns in self.namespace_manager.namespaces()}
            self.reverse_namespaces = {v: k for k,v in self.namespaces.items()}

            if import_references:
                iris = set()
                for s, o, p in self.graph:
                    for iri in [s, o, p]:
                        if isinstance(iri, URIRef) and iri not in iris:
                            ns = self.get_namespace_from_iri(iri)
                            logger.debug(f"{iri} -> {ns}")
                            if ns not in self.loaded:
                                self.load(ns)
                            logger.debug(f"Found IRI <{iri}>")
                            iris.add(iri)
            logger.info(f"Loaded {asset_url}")

        except Exception:
            logger.error(f"Failed to load {asset_url}: repr(e)", exc_info=True)

    def get_namespace_from_iri(self, iri: str) -> Optional[str]:
        for ns in self.reverse_namespaces.keys():
            if iri.startswith(ns):
                return ns
        return None

    def get_namespaces(self) -> list[Tuple[str,str]]:
        return self.namespaces

    def list_triples(self) -> list[Tuple[str, str, str]]:
        return [(s, p, o) for (s, p, o) in self.graph]

    def list_triples_for_subject(self, subject: str) -> list[Tuple[str, str, str]]:
        subject = self.expand_curie(subject)
        subject_key = f"subject|{subject}"

        if subject_key not in self.cache:
            self.cache[subject_key] = [(s, p, o) for (s, p, o) in self.graph if (str(s) == subject)]

        return self.cache[subject_key]

    def list_triples_for_object(self, object_: str) -> list[Tuple[str, str, str]]:
        object_ = self.expand_curie(object_)
        object_key = f"object|{object_}"

        if object_key not in self.cache:
            self.cache[object_key] = [(s, p, o) for (s, p, o) in self.graph if (str(o) == object_)]

        return self.cache[object_key]

    def list_triples_for_property(self, property_: str) -> list[Tuple[str, str, str]]:
        property_ = self.expand_curie(property_)
        property_key = f"object|{property_}"

        if property_key not in self.cache:
            self.cache[property_key] = [(s, p, o) for (s, p, o) in self.graph if (str(p) == property_)]

        return self.cache[property_key]

    def list_classes(self) -> list[Term]:
        return self.list_iris(["?q rdf:type rdfs:Class"], f"classes")

    def list_properties(self) -> list[str]:
        return self.list_iris(["?q rdf:type rdf:Property"], f"properties")

    def expand_classes_for_class(self, class_iri: str, class_list: Optional[list[str]] = None) -> list[str]:
        logging.info(f"Finding all classes for class {class_iri}")
        class_iri = self.expand_curie(class_iri)

        cache_key = f"superclasses|{class_iri}"

        if cache_key in self.cache:
            return self.cache[cache_key]

        if class_list is None:
            class_list = [self.get_term(class_iri)]

        query = """
                prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>

                SELECT ?c
                WHERE {
                <%s> rdfs:subClassOf ?c .
                }
                """ %(class_iri)
        logging.debug(f"Issuing query:\n{query}")
        for c in self.graph.query(query):
            if isinstance(c[0], URIRef):
                superclass = self.get_term(str(c[0]))
                if superclass not in class_list:
                    class_list.append(superclass)
                    self.expand_classes_for_class(superclass.iri, class_list)
        
        self.cache[cache_key] = class_list

        return class_list

    def expand_properties_for_property(self, property_iri: str, property_list: Optional[list[str]] = None) -> list[str]:
        logging.info(f"Finding all properties for property {property_iri}")
        property_iri = self.expand_curie(property_iri)

        cache_key = f"superproperties|{property_iri}"

        if cache_key in self.cache:
            return self.cache[cache_key]

        if property_list is None:
            property_list = [self.get_term(property_iri)]

        query = """
                prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>

                SELECT ?p
                WHERE {
                <%s> rdfs:subPropertyOf ?p .
                }
                """ %(property_iri)
        logging.debug(f"Issuing query:\n{query}")
        for p in self.graph.query(query):
            if isinstance(p[0], URIRef):
                superproperty = self.get_term(str(p[0]))
                if superproperty not in property_list:
                    property_list.append(superproperty)
                    self.expand_properties_for_property(superproperty.iri, property_list)

        self.cache[cache_key] = property_list

        return property_list

    def list_domain_properties_for_class(self, class_iri: str, property_list: Optional[list[str]] = None) -> list[Tuple[str, str]]:
        class_iri = self.expand_curie(class_iri)
        query_strings = [f"?q schema:domainIncludes <{class_.iri}>" for class_ in self.expand_classes_for_class(class_iri)]
        cache_key = f"range|{class_iri}"
        return self.list_iris(query_strings, f"instances|{class_iri}")

    def list_range_properties_for_class(self, class_iri: str) -> list[Tuple[str, str]]:
        class_iri = self.expand_curie(class_iri)
        query_strings = [f"?q schema:rangeIncludes <{class_.iri}>" for class_ in self.expand_classes_for_class(class_iri)]
        cache_key = f"range|{class_iri}"
        return self.list_iris(query_strings, f"instances|{class_iri}")

    def list_instances(self, class_iri: str) -> List[Term]:
        class_iri = self.expand_curie(class_iri)
        return self.list_iris([f"?q rdf:type <{class_iri}> ."], f"instances|{class_iri}")

    def list_instances_by_class_and_name(self, class_iri: str, name: str, check_alternate_names: bool = False, namespace: Optional[str] = None) -> List[Term]:
        class_iri = self.expand_curie(class_iri)
        cache_key = f"instances-name|{class_iri}|{name}|{check_alternate_names}|{namespace}"
        query_strings = [f"?q rdf:type <{class_iri}> . {{ ?q schema:name '{name}'@en }} UNION {{ ?q schema:name '{name}'}}."]
        query_strings.append(f"?q rdf:type <{class_iri}> .  {{ ?q rdfs:label '{name}'@en }} UNION {{ ?q rdfs:label '{name}'}}.")
        if check_alternate_names:
            query_strings.append(f"?q rdf:type <{class_iri}> .  {{ ?q schema:alternateName '{name}'@en }} UNION {{ ?q schema:alternateName '{name}'}}.")
        return self.list_iris(query_strings, cache_key, namespace = namespace)

    def list_properties_by_name(self, name: str, check_alternate_names: bool = False, namespace: Optional[str] = None) -> List[Term]:
        return self.list_instances_by_class_and_name("rdf:Property", name, check_alternate_names = check_alternate_names, namespace = namespace)

    def expand_curie(self, curie: str) -> str:
        if curie.startswith("http"):
            return curie

        parts = curie.split(":")
        if len(parts) != 2:
            return curie

        prefix = parts[0]

        for p, ns in self.namespace_manager.namespaces():
            if p == prefix:
                expanded = f"{ns}{parts[1]}"
                logging.info(f"Expanded {curie} to {expanded}")
                return expanded

        logging.error(f"Could not expand identifier: {curie}")
        return curie

    def get_curie(self, iri: str) -> str:
        if not iri.startswith("http"):
            return iri

        for ns in self.reverse_namespaces:
            if iri.startswith(ns):
                return f"{self.reverse_namespaces[ns]}:{iri[len(ns):]}"

        # The following indicates that a referenced asset has not been parsed
        logging.warning(f"Could not convert identifier to CURIE: {iri}")

        return iri

    def get_term(self, iri: str) -> Term:
        curie = self.get_curie(iri)
        if curie != iri:
            prefix, name = curie.split(":")
            ns = self.namespaces[prefix]
        else:
            ns, curie, prefix, name = "", "", "", ""
        return Term(iri, curie, self.namespaces[prefix], prefix, name)

    def list_iris(self, query_strings: List[str], cache_key: str, namespace: Optional[str] = None) -> List[Term]:

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
                    """ %(q)

            logging.debug(f"Issuing query:\n{query}")

            for p in self.graph.query(query):
                if isinstance(p[0], URIRef) and (namespace is None or str(p[0]).startswith(namespace)):
                    term = self.get_term(str(p[0]))
                    if term not in results:
                        results.append(term)

        self.cache[cache_key] = results

        logging.debug(f"Matching terms: {', '.join([t[0] for t in results])}")

        return results


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
    subparsers = parser.add_subparsers(dest="query", help = "Subcommands:")
    for cmd in ["namespaces", "triples", "classes", "properties", "test"]:
        subparser = subparsers.add_parser(cmd, help = (subcommand_helptext[cmd] if cmd in subcommand_helptext else None))
    for cmd in ["superclasses", "superproperties", "instances", "domain", "range", "subject", "property", "object"]:
        subparser = subparsers.add_parser(cmd, help = (subcommand_helptext[cmd] if cmd in subcommand_helptext else None))
        subparser.add_argument("iri")
    for cmd in ["property-name", "property-name-all"]:
        subparser = subparsers.add_parser(cmd, help = (subcommand_helptext[cmd] if cmd in subcommand_helptext else None))
        subparser.add_argument("name")
        subparser.add_argument("-n", "--namespace")
    for cmd in ["instance-name", "instance-name-all"]:
        subparser = subparsers.add_parser(cmd, help = (subcommand_helptext[cmd] if cmd in subcommand_helptext else None))
        subparser.add_argument("class")
        subparser.add_argument("name")
        subparser.add_argument("-n", "--namespace")

    parser.add_argument(
        "-l", "--log-level", choices=("error", "warning", "info", "debug"), default="info", help="Set logging level"
    )
    parser.add_argument(
        "-e", "--echo-to-stderr", action=argparse.BooleanOptionalAction, default=False, help="Echo log messages to console"
    )
    parser.add_argument("-a", "--asset", action="append", help="Namespace for linked-data asset to load into graph.")
    parser.add_argument("-p", "--prefix", action="append", help="Optional prefix for loaded asset.")
    parser.add_argument("-f", "--filepath_to_asset", action="append", help="Path to asset file if different from asset namespace.")
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

def show_tuple_list(tuples: List[Tuple], element_count: int, max_rows: Optional[int] = None) -> None:
    if max_rows is not None:
        tuples = tuples[0:max_rows]
    lengths = [0] * element_count
    for t in tuples:
        for element in range(element_count):
            length = len(t[element])
            if length > lengths[element]:
                lengths[element] = length

    for t in tuples:
        print("   ".join([f"{t[e]:{lengths[e]}s}" for e in range(element_count)]).strip())

def execute_query(Dictionary: d, args: dict[str, Any], max_rows: Optional[int] = None) -> None:

    if args["query"] == "classes":
        show_tuple_list(d.list_classes(), 2, max_rows=max_rows)

    elif args["query"] == "properties":
        show_tuple_list(d.list_properties(), 2, max_rows=max_rows)

    elif args["query"] == "superclasses":
        show_tuple_list(d.expand_classes_for_class(args["iri"]), 2, max_rows=max_rows)

    elif args["query"] == "superproperties":
        show_tuple_list(d.expand_properties_for_property(args["iri"]), 2, max_rows=max_rows)

    elif args["query"] == "instances":
        show_tuple_list(d.list_instances(args["iri"]), 2, max_rows=max_rows)

    elif args["query"] == "domain":
        show_tuple_list(d.list_domain_properties_for_class(args["iri"]), 2, max_rows=max_rows)

    elif args["query"] == "range":
        show_tuple_list(d.list_range_properties_for_class(args["iri"]), 2, max_rows=max_rows)

    elif args["query"] == "property-name":
        show_tuple_list(d.list_properties_by_name(args["name"], namespace = args["namespace"] if "namespace" in args else None), 2, max_rows=max_rows)

    elif args["query"] == "property-name-all":
        show_tuple_list(d.list_properties_by_name(args["name"], check_alternate_names=True, namespace = args["namespace"] if "namespace" in args else None), 2, max_rows=max_rows)

    elif args["query"] == "instance-name":
        show_tuple_list(d.list_instances_by_class_and_name(args["class"], args["name"], namespace = args["namespace"] if "namespace" in args else None), 2, max_rows=max_rows)

    elif args["query"] == "instance-name-all":
        show_tuple_list(d.list_instances_by_class_and_name(args["class"], args["name"], check_alternate_names = True, namespace = args["namespace"] if "namespace" in args else None), 2, max_rows=max_rows)

    elif args["query"] == "namespaces":
        namespaces = d.get_namespaces()
        keys = sorted(namespaces.keys())
        if max_rows is not None:
            keys = keys[0:max_rows]
        length = max([len(k) for k in keys])
        for k in keys:
            if len(k) > 0:
                print(f"{k:>{length}s} : {namespaces[k]}")

    elif args["query"] in [ "subject", "property", "object", "triples" ]:
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

    args = process_argv(sys.argv)
    start_log(args["log_level"], None, args["echo_to_stderr"])

    d = Dictionary()
    d.load(APPN_SCHEMA, import_references=True)
    if args["asset"] is not None:
        for i in range(len(args["asset"])):
            asset = args["asset"][i]
            if args["prefix"] is not None and i in range(len(args["prefix"])):
                prefix = args["prefix"][i]
            else:
                prefix = f"asset{i}"
            if args["filepath_to_asset"] is not None and i in range(len(args["filepath_to_asset"])):
                schema_assets[asset] = args["filepath_to_asset"][i]
            d.load(asset, prefix=prefix)

    print()

    if args["query"] == "test":
        for q in [
            ["namespaces", ],
            ["triples", ],
            ["classes", ],
            ["properties", ],
            ["superclasses", "appn:Sampling", ],
            ["superproperties", "schema:name", ],
            ["instances", "appn:Scale", ],
            ["domain", "appn:Scale", ],
            ["range", "appn:Scale", ],
            ["subject", "appn:Scale", ],
            ["property", "appn:hasScale", ],
            ["object", "appn:Scale", ],
            ["property-name", "name"],
            ["property-name-all", "comment", "-n", "schema", ],
            ["instance-name", "appn:Scale", "millimeter", ],
            ["instance-name-all", "appn:Scale", "mm", "-n", "ltu",],
        ]:
            print(f"Executing: {' '.join(q)}\n")
            execute_query(d, process_argv([sys.argv] + q), max_rows = 5)
            print()
    else:
        execute_query(d, args)

    print()

    logger.info("Finished")
