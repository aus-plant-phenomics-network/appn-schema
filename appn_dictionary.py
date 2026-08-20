#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
# appn_dictionary.py
#
# Import RDF assets and expose query interfaces
#
# -----------------------------------------------------------------------------
# Created By  : Donald Hobern, donald.hobern@adelaide.edu.au
# Created Date: 2026-08-20
# version ='2026.0.1'
# -----------------------------------------------------------------------------

import logging
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

asset_mappings = {
    APPN_SCHEMA: f"{APPN_SCHEMA}appn-schema",
    SCHEMA_SCHEMA: "schemaorg-current-https.ttl",
    BIO_SCHEMA: "https://bioschemas.org/types/bioschemas_types.ttl",
    CDI_SCHEMA: "https://www.ddialliance.org/Specification/DDI-CDI/1.0/RDF/ddi-cdi.jsonld",
}


class Dictionary:

    def __init__(self) -> None:
        self.graphs = {}

    def load(
        self, asset_url: str, prefix: Optional[str] = None, chain: bool = False
    ) -> Optional[Graph]:
        try:
            logger.info(f"Loading {asset_url}")
            g = Graph()
            print(
                asset_mappings[asset_url] if asset_url in asset_mappings else asset_url
            )
            print(asset_mappings)
            g.parse(
                asset_mappings[asset_url] if asset_url in asset_mappings else asset_url
            )
            nm = NamespaceManager(g)
            if prefix is not None:
                nm.bind(prefix, Namespace(asset_url), override=True)
            self.graphs[asset_url] = g
            if chain:
                iris = set()
                for s, o, p in g:
                    for iri in [s, o, p]:
                        if isinstance(iri, URIRef) and iri not in iris:
                            if not any(iri.startswith(ns) for ns in self.graphs.keys()):
                                pre = nm.normalizeUri(iri).split(":")[0]
                                for prefix, url in nm.namespaces():
                                    if prefix == pre:
                                        self.load(str(url))
                            logger.info(f"Found IRI <{iri}>")
                            iris.add(iri)
            logger.info(f"Loaded {asset_url}")
            return g
        except Exception:
            logger.error(f"Failed to load {asset_url}: repr(e)", exc_info=True)
        return None

    def list_namespaces(self, asset_url: Optional[str] = None) -> list[Namespace]:
        namespaces = []
        for url, graph in self.graphs.items():
            if asset_url in [None, url]:
                nm = NamespaceManager(graph)
                namespaces += nm.namespaces()
        return namespaces

    def list_triples(
        self, asset_url: Optional[str] = None
    ) -> list[Tuple[str, str, str]]:
        triples = []
        for url, graph in self.graphs.items():
            if asset_url in [None, url]:
                for s, p, o in graph:
                    triples.append((s, p, o))
        return triples

    def list_classes(self, asset_url: Optional[str] = None) -> list[str]:
        classes = []
        for url, graph in self.graphs.items():
            if asset_url in [None, url]:
                for c in graph.query("""
                                     prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                                     prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>

                                     SELECT ?c
                                     WHERE {
                                       ?c rdf:type rdfs:Class .
                                     }
                                     """):
                    classes.append(c[0])

        return classes


if __name__ == "__main__":

    logging.basicConfig(filename="appn_dictionary.log", level=logging.INFO)
    logging.getLogger().addHandler(logging.StreamHandler())
    logger.info("Started")

    d = Dictionary()
    d.load(APPN_SCHEMA, chain=True)
    # d.load(RDFS_SCHEMA)
    # d.load(RDF_SCHEMA)
    # for s, p, o in d.list_triples(APPN_SCHEMA):
    # print(f"{s}\t{p}\t{o}")
    # for c in d.list_classes():
    # print(f"{c}")
    for ns in d.list_namespaces():
        print(f"{ns}")

    logger.info("Finished")
