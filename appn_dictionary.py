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
from typing import Optional, Tuple

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
    LTU_VOCAB: "./vocabulary/LTU/vocabulary.rdf",
}

Term = namedtuple("Term", ["iri", "curie", "ns", "prefix", "name"])

class Dictionary:

    def __init__(self) -> None:
        self.graph = Graph()
        self.namespace_manager = NamespaceManager(self.graph)
        self.loaded = set()
        self.cache = {}
        self.namespaces = {}
        self.reverse_namespaces = {v: k for k,v in self.namespaces.items()}

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

            if import_references:
                iris = set()
                for s, o, p in self.graph:
                    for iri in [s, o, p]:
                        if isinstance(iri, URIRef) and iri not in iris:
                            ns = self.get_namespace_from_iri(iri)
                            if ns not in self.loaded:
                                self.load(ns)
                            logger.debug(f"Found IRI <{iri}>")
                            iris.add(iri)
            logger.info(f"Loaded {asset_url}")

            self.cache = {}
            self.namespaces = {p: str(ns) for p, ns in self.namespace_manager.namespaces()}

        except Exception:
            logger.error(f"Failed to load {asset_url}: repr(e)", exc_info=True)

    def get_namespace_from_iri(self, iri: str) -> Optional[str]:
        if iri in self.reverse_namespaces:
            return self.reverse_namespaces[iri]
        return None

    def find_property(self, property_name: str) -> Optional[str]:
        property_iri = None
        for p in list_properties():
            for pre, ns in self.namespace_manager.namespaces():
                if p.startswith(str(ns)):
                    return f"{p}:{iri[len(ns):]}"

    def list_namespaces(self) -> list[Tuple[str,str]]:
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
            self.cache[property_key] = [(s, p, o) for (s, p, o) in self.graph if (str(o) == property_)]

        return self.cache[property_key]

    def list_classes(self) -> list[Term]:
        if "classes" not in self.cache:
            classes = []
            for c in self.graph.query("""
                                    prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                                    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>

                                    SELECT ?c
                                    WHERE {
                                    ?c rdf:type rdfs:Class .
                                    }
                                    """):
                classes.append(self.get_term(str(c[0])))
            self.cache["classes"] = classes
        return self.cache["classes"]

    def list_properties(self) -> list[str]:
        if "properties" not in self.cache:
            properties = []
            for p in self.graph.query("""
                                    prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

                                    SELECT ?p
                                    WHERE {
                                    ?p rdf:type rdf:Property .
                                    }
                                    """):
                properties.append(self.get_term(str(p[0])))
            self.cache["properties"] = properties
        return self.cache["properties"]

    def expand_classes_for_class(self, class_iri: str, class_list: Optional[list[str]] = None) -> list[str]:
        logging.info(f"Finding all classes for class {class_iri}")
        class_iri = self.expand_curie(class_iri)

        cache_key = f"classes|{class_iri}"

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

        cache_key = f"properties|{property_iri}"

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
        logging.info(f"Finding domain properties for class {class_iri}")
        class_iri = self.expand_curie(class_iri)
        class_list = self.expand_classes_for_class(class_iri)

        cache_key = f"domain|{class_iri}"

        if cache_key in self.cache:
            return self.cache[cache_key]

        if property_list is None:
            property_list = []

        for c in class_list:
            query = """
                    prefix schema: <https://schema.org/>

                    SELECT ?p
                    WHERE {
                    ?p schema:domainIncludes <%s> .
                    }
                    """ %(c.iri)
            logging.debug(f"Issuing query:\n{query}")
            for p in self.graph.query(query):
                if isinstance(p[0], URIRef):
                    property_ = self.get_term(str(p[0]))
                    if property_ not in property_list:
                        property_list.append(property_)

        self.cache[cache_key] = property_list

        logging.debug(f"Matching properties: {', '.join([p[0] for p in property_list])}")
        return property_list

    def list_range_properties_for_class(self, class_iri: str, property_list: Optional[list[str]] = None) -> list[Tuple[str, str]]:
        logging.info(f"Finding range properties for class {class_iri}")
        class_iri = self.expand_curie(class_iri)
        class_list = self.expand_classes_for_class(class_iri)

        cache_key = f"range|{class_iri}"

        if cache_key in self.cache:
            return self.cache[cache_key]

        if property_list is None:
            property_list = []

        for c in class_list:
            query = """
                    prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    prefix schema: <https://schema.org/>

                    SELECT ?p
                    WHERE {
                    ?p schema:rangeIncludes <%s> .
                    }
                    """ %(c.iri)
            logging.debug(f"Issuing query:\n{query}")
            for p in self.graph.query(query):
                if isinstance(p[0], URIRef):
                    property_ = self.get_term(str(p[0]))
                    if property_ not in property_list:
                        property_list.append(property_)

        self.cache[cache_key] = property_list

        logging.debug(f"Matching properties: {', '.join([p[0] for p in property_list])}")
        return property_list

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

        for p, ns in self.namespace_manager.namespaces():
            if iri.startswith(str(ns)):
                return f"{p}:{iri[len(ns):]}"

        # The following indicates that a references schema has not been parsed
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


### process_argv ##############################################################
#
# Safely process sys.argv, returning a dictionary of option values.
#
#     query             : query type - one of:
#                          { classes, properties, domain, range, namespaces, 
#                            subject, property, object, triples }.
#     -l, --log-level   : "info" / "error" / "debug".
#     -e,               : Display logging outputs to stderr.
#      --echo-to-stderr
#
def process_argv(argv: list[str]) -> dict[str, Any]:
    parser = argparse.ArgumentParser(
        prog=argv[0],
        description=f"{argv[0]}: Generate linked-data outputs from APPN node vocabulary sheets",
    )
    parser.add_argument("query", choices=["classes", "properties", "domain", "range", "namespaces", "subject", "property", "object", "triples"])
    parser.add_argument("iri", default="all")
    parser.add_argument(
        "-l", "--log-level", choices=("error", "info", "debug"), default="info"
    )
    parser.add_argument(
        "-e", "--echo-to-stderr", action=argparse.BooleanOptionalAction, default=False
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

if __name__ == "__main__":

    def show_tuple_list(tuples: List[Tuple], element_count: int) -> None:
        lengths = [0] * element_count
        for t in tuples:
            for element in range(element_count):
                length = len(t[element])
                if length > lengths[element]:
                    lengths[element] = length
        
        for t in tuples:
            print("   ".join([f"{t[e]:{lengths[e]}s}" for e in range(element_count)]))

    args = process_argv(sys.argv)
    start_log(args["log_level"], None, args["echo_to_stderr"])

    d = Dictionary()
    d.load(APPN_SCHEMA, import_references=True)
    d.load(LTU_VOCAB, prefix="ltu")

    print()

    if args["query"] == "classes":
        if args["iri"] in [None, "all"]:
            show_tuple_list(d.list_classes(), 2)
        else:
            show_tuple_list(d.expand_classes_for_class(args["iri"]), 2)

    if args["query"] == "properties":
        if args["iri"] in [None, "all"]:
            show_tuple_list(d.list_properties(), 2)
        else:
            show_tuple_list(d.expand_properties_for_property(args["iri"]), 2)

    elif args["query"] == "domain":
        show_tuple_list(d.list_domain_properties_for_class(args["iri"]), 2)

    elif args["query"] == "range":
        show_tuple_list(d.list_range_properties_for_class(args["iri"]), 2)

    elif args["query"] == "namespaces":
        namespaces = d.list_namespaces()
        length = max([len(k) for k in namespaces.keys()])
        for k in sorted(namespaces.keys()):
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
        show_tuple_list(triples, 3)

    print()

    logger.info("Finished")
