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
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

APPN_SCHEMA = "https://schema.plantphenomics.org.au/"
RDFS_SCHEMA = "http://www.w3.org/2000/01/rdf-schema#"
RDF_SCHEMA = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
SCHEMA_SCHEMA = "https://schema.org/"
BIO_SCHEMA = "https://bioschemas.org/"
CDI_SCHEMA = "http://ddialliance.org/Specification/DDI-CDI/1.0/RDF/"
PPEO_SCHEMA = "http://purl.org/ppeo/PPEO.owl#"
SOSA_SCHEMA = "https://www.w3.org/ns/sosa/"
SSN_SCHEMA = "https://www.w3.org/ns/ssn/"
PROV_SCHEMA = "https://www.w3.org/ns/prov#"

# Locations to use for machine-readable assets
schema_assets = {
    APPN_SCHEMA: f"{APPN_SCHEMA}appn-schema",
    RDFS_SCHEMA: "schema_assets/rdf-schema.ttl",
    RDF_SCHEMA: "schema_assets/22-rdf-syntax-ns.ttl",
    SCHEMA_SCHEMA: "schema_assets/schemaorg-current-https.ttl",
    BIO_SCHEMA: "schema_assets/bioschemas_types.ttl",
    CDI_SCHEMA: "schema_assets/ddi-cdi.jsonld",
    PPEO_SCHEMA: "schema_assets/PPEO.owl",
    SOSA_SCHEMA: "schema_assets/sosa.ttl",
    SSN_SCHEMA: "schema_assets/ssn.ttl",
    PROV_SCHEMA: "schema_assets/prov.ttl",
}

class Dictionary:

    def __init__(self) -> None:
        self.graph = Graph()
        self.namespace_manager = NamespaceManager(self.graph)
        self.loaded = set()

    def load(
        self, asset_url: str, prefix: Optional[str] = None, chain: bool = False
    ) -> None:
        try:
            logger.info(f"Loading {asset_url}")
            self.graph.parse(
                schema_assets[asset_url] if asset_url in schema_assets else asset_url
            )
            self.loaded.add(asset_url)
            if prefix is not None:
                self.namespace_manager.bind(prefix, Namespace(asset_url), override=True)
            if chain:
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
        except Exception:
            logger.error(f"Failed to load {asset_url}: repr(e)", exc_info=True)

    def get_namespace_from_iri(self, iri: str) -> Optional[str]:
        pre = self.namespace_manager.normalizeUri(iri).split(":")[0]
        for prefix, url in self.namespace_manager.namespaces():
            if prefix == pre:
                return str(url)
        return None


    def list_namespaces(self) -> list[Tuple[str,str]]:
        return [(p, str(ns)) for p, ns in self.namespace_manager.namespaces()]

    def list_triples(self) -> list[Tuple[str, str, str]]:
        return [(s, p, o) for (s, p, o) in self.graph]

    def list_triples_for_subject(self, subject: str) -> list[Tuple[str, str, str]]:
        subject = self.expand_curie(subject)
        return [(s, p, o) for (s, p, o) in self.graph if (str(s) == subject)]

    def list_triples_for_object(self, object_: str) -> list[Tuple[str, str, str]]:
        object_ = self.expand_curie(object_)
        return [(s, p, o) for (s, p, o) in self.graph if (str(o) == object_)]

    def list_triples_for_property(self, property_: str) -> list[Tuple[str, str, str]]:
        peoperty_ = self.expand_curie(property_)
        return [(s, p, o) for (s, p, o) in self.graph if (str(p) == property_)]

    def list_classes(self) -> list[str]:
        classes = []
        for c in self.graph.query("""
                                prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                                prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>

                                SELECT ?c
                                WHERE {
                                ?c rdf:type rdfs:Class .
                                }
                                """):
            classes.append(str(c[0]))
        return classes

    def expand_classes_for_class(self, class_iri: str, class_list: Optional[list[str]] = None) -> list[str]:
        logging.info(f"Finding all classes for class {class_iri}")
        class_iri = self.expand_curie(class_iri)

        if class_list is None:
            class_list = [class_iri]

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
                superclass = str(c[0])
                if superclass not in class_list:
                    class_list.append(superclass)
                    self.expand_classes_for_class(superclass, class_list)

        return class_list

    def list_domain_properties_for_class(self, class_iri: str, property_list: Optional[list[str]] = None) -> list[Tuple[str, str]]:
        logging.info(f"Finding domain properties for class {class_iri}")
        class_iri = self.expand_curie(class_iri)
        class_list = self.expand_classes_for_class(class_iri)

        if property_list is None:
            property_list = []

        for c in class_list:
            query = """
                    prefix schema: <https://schema.org/>

                    SELECT ?p
                    WHERE {
                    ?p schema:domainIncludes <%s> .
                    }
                    """ %(c)
            logging.debug(f"Issuing query:\n{query}")
            for p in self.graph.query(query):
                if isinstance(p[0], URIRef):
                    property_ = str(p[0])
                    if property_ not in property_list:
                        property_list.append((property_, c))

        logging.debug(f"Matching properties: {', '.join([p for p,c in property_list])}")
        return property_list

    def list_range_properties_for_class(self, class_iri: str, property_list: Optional[list[str]] = None) -> list[Tuple[str, str]]:
        logging.info(f"Finding range properties for class {class_iri}")
        class_iri = self.expand_curie(class_iri)
        class_list = self.expand_classes_for_class(class_iri)

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
                    """ %(c)
            logging.debug(f"Issuing query:\n{query}")
            for p in self.graph.query(query):
                if isinstance(p[0], URIRef):
                    property_ = str(p[0])
                    if property_ not in property_list:
                        property_list.append((property_, c))

        logging.debug(f"Matching properties: {', '.join([p for p,c in property_list])}")
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

        return curie

    def get_curie(self, iri: str) -> str:
        if not iri.startswith("http"):
            return iri

        for p, ns in self.namespace_manager.namespaces():
            if iri.startswith(str(ns)):
                return f"{p}:{iri[len(ns):]}"

        return curie

### process_argv ##############################################################
#
# Safely process sys.argv, returning a dictionary of option values.
#
#     query             : query type - one of:
#                          { classes, domain, range, namespaces, subject, 
#                            property, object }.
#     -l, --log-level   : "info" / "error" / "debug".
#     -e,               : Display logging outputs to stderr.
#      --echo-to-stderr
#
def process_argv(argv: list[str]) -> dict[str, Any]:
    parser = argparse.ArgumentParser(
        prog=argv[0],
        description=f"{argv[0]}: Generate linked-data outputs from APPN node vocabulary sheets",
    )
    parser.add_argument("query", choices=["classes", "domain", "range", "namespaces", "subject", "property", "object"])
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

    args = process_argv(sys.argv)
    start_log(args["log_level"], None, args["echo_to_stderr"])

    d = Dictionary()
    d.load(APPN_SCHEMA, chain=True)

    if args["query"] == "classes":
        if args["iri"] in [None, "all"]:
            result = d.list_classes()
        else:
            result = d.expand_classes_for_class(args["iri"])
        for s in result:
            print(d.get_curie(s))

    elif args["query"] == "domain":
        result = d.list_domain_properties_for_class(args["iri"])
        current_class = None
        for p, c in result:
            if c != current_class:
                if current_class is not None:
                    print("")
                print(f"From {d.get_curie(c)}:")
                current_class = c
            print(f"    {d.get_curie(p)}")

    elif args["query"] == "range":
        result = d.list_range_properties_for_class(args["iri"])
        current_class = None
        for p, c in result:
            if c != current_class:
                if current_class is not None:
                    print("")
                print(f"From {d.get_curie(c)}:")
                current_class = c
            print(f"    {d.get_curie(p)}")

    elif args["query"] == "namespaces":
        for p, ns in d.list_namespaces():
            print(f"{p} : {ns}")

    elif args["query"] in [ "subject", "property", "object" ]:
        if args["query"] == "subject":
            triples = d.list_triples_for_subject(args["iri"])
        elif args["query"] == "property":
            triples = d.list_triples_for_property(args["iri"])
        else:
            triples = d.list_triples_for_object(args["iri"])
        len_s = 0
        len_p = 0
        curie_triples = []
        for s, p, o in triples:
            s = d.get_curie(s)
            p = d.get_curie(p)
            o = d.get_curie(o)
            curie_triples.append((s, p, o))
            if len(s) > len_s:
                len_s = len(s)
            if len(p) > len_p:
                len_p = len(p)
        for s, p, o in curie_triples:
            print(f"{s:{len_s}s}   {p:{len_p}s}   {o}")

    logger.info("Finished")
