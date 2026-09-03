#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
# appn_vocabulary.py
#
# Convert Excel spreadsheets into vocabulary assets
#
# Usage: python appn_vocabulary.py [-n node|"all"] [-l log-level] [-e]
#
# -----------------------------------------------------------------------------
# Created By  : Donald Hobern, donald.hobern@adelaide.edu.au
# Created Date: 2026-03-31
# version ='2026.0.1'
# -----------------------------------------------------------------------------
import argparse
import logging
import re
import sys
import datetime
import warnings

import pandas as pd

from pathlib import Path
from typing import Optional, Any, NamedTuple
from appn_types import Term, URIRefTriple, ColumnMapping
from appn_dictionary import Dictionary
from appn_parser import ExcelVocabularyParser
from appn_configuration import (
    APPN_VOCABULARY,
    BIO_SCHEMA,
    DC_SCHEMA,
    EXPLICIT_CLASSES_ALL,
    EXPLICIT_CLASSES_FIRST,
    RDF_SCHEMA,
    RDFS_SCHEMA,
    SCHEMA_SCHEMA,
    Configuration,
    Organisation,
    APPN_SCHEMA,
    SKOS_SCHEMA,
)
from rdflib import Graph, Namespace, URIRef, Literal

integer_stripper = re.compile(r"[0-9]*$")

rdf_type = URIRef(f"{RDF_SCHEMA}type")
rdf_property = URIRef(f"{RDF_SCHEMA}Property")
schema_name = URIRef(f"{SCHEMA_SCHEMA}name")
schema_description = URIRef(f"{SCHEMA_SCHEMA}description")
skos_concept = URIRef(f"{SKOS_SCHEMA}Concept")
skos_concept_scheme = URIRef(f"{SKOS_SCHEMA}ConceptScheme")
skos_in_scheme = URIRef(f"{SKOS_SCHEMA}inScheme")
dc_title = URIRef(f"{DC_SCHEMA}title")
dc_description = URIRef(f"{DC_SCHEMA}description")


### process_argv ##############################################################
#
# Safely process sys.argv, returning a dictionary of option values.
#
#     -n, --node        : Node name (actually name of subfolder under source)
#                         or "all" to process all nodes (subfolders).
#     -m, --mode        : Output mode "json" for JSON-LD or "rdf" for xml/rdf (default)
#     -l, --log-level   : "info" / "error" / "debug".
#     -e,               : Display logging outputs to stderr.
#      --echo-to-stderr
#
def process_argv(argv: list[str]) -> dict[str, Any]:
    parser = argparse.ArgumentParser(
        prog=argv[0],
        description=f"{argv[0]}: Generate linked-data outputs from APPN node vocabulary sheets",
    )
    parser.add_argument("-m", "--mode", choices=("json", "rdf", "all"), default="rdf")
    parser.add_argument(
        "-l",
        "--log-level",
        choices=("error", "warning", "info", "debug"),
        default="info",
    )
    parser.add_argument(
        "-e", "--echo-to-stderr", action=argparse.BooleanOptionalAction, default=False
    )
    parser.add_argument("-n", "--node", default="all")
    args = vars(parser.parse_args(argv[1:]))
    return args


### start_log #################################################################
#
# Start logging to default or named file and optionally to stderr.
#
#     level             : info / warning / error / debug (string or logging
#                         enumeration).
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
        if level == "warning":
            log_level = logging.WARNING
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

    print(f"Logging started to {logfile_name} at level {level} and echo {echo}")
    logging.info(f"Logging started to {logfile_name} at level {level} and echo {echo}")


### MAIN PROGRAM ##############################################################
#
# Parse arguments and set up logging. Based on arguments, scan one or all
# source folders for all Excel spreadheets and generate a JSON-LD vocabulary
# for all schema class instances included.
#
if __name__ == "__main__":

    args = process_argv(sys.argv)
    start_log(args["log_level"], None, args["echo_to_stderr"])

    configuration = Configuration()

    node = args["node"]

    # Load schemas that provide key definitions. APPN_SCHEMA does not
    # directly reference SKOS, so SKOS_SCHEMA is separately loaded, but
    # others are imported based on their use in these two schemas.
    dictionary = Dictionary(
        namespace_definitions=configuration.get_namespace_definitions()
    )
    dictionary.load(APPN_SCHEMA)
    dictionary.load(SKOS_SCHEMA)
    dictionary.import_references()

    # Make list of folders to process (either for a single node or for all)
    if node == "all":
        folders = sorted(
            list(Path("source").glob("*/")),
            key=lambda p: f"{'0' if 'APPN' in str(p) else '1'}{p}",
        )
        if len(folders) == 0:
            logging.error(f"No folders to process")
            sys.exit(1)
        logging.info(
            f"Processing all folders ({', '.join(str(f.name) for f in folders)})"
        )
    else:
        folders = [Path("source") / node]
        if not folders[0].exists():
            logging.error(f"No folder found for node {node}")
            sys.exit(1)
        logging.info(f"Selected folder {node}")

    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # The openpyxl library generates a warning ("Data Validation extension is not supported and will be removed")
    warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

    organisations = configuration.get_organisations()

    # Generate vocabulary for each selected node in turn.
    for folder in folders:
        node = folder.name

        if node in organisations:

            parser = ExcelVocabularyParser(
                dictionary, configuration, organisations[node]
            )

            # Loop over Excel spreadsheets in the folder for the node.
            for file in folder.glob("*.xls*"):

                # Ignore temporary files that still have xls in their name
                if not file.name.startswith("."):
                    logging.debug(f"Processing file {file}")
                    parser.load(file)

            parser.process_required_properties()

            inspector = Dictionary(parser.graph)

            counts = inspector.count_triples_by_subject()
            print("Counts of triples by subject\n")
            length = max([len(k) for k in counts.keys()])
            for p in sorted(counts.keys()):
                print(f"  {p:{length + 1}s} : {counts[p]:>5d}")
            print()

            counts = inspector.count_triples_by_property()
            print("Counts of triples by property\n")
            length = max([len(k) for k in counts.keys()])
            for p in sorted(counts.keys()):
                print(f"  {p:{length + 1}s} : {counts[p]:>5d}")
            print()

            local_properties = inspector.list_properties(
                namespace=("appnid" if node == "APPN" else node.lower())
            )
            if len(local_properties) > 0:
                print("New properties associated with this vocabulary\n")
                for p in local_properties:
                    print(f"  {p.iri}")
                print()

            parser.get_graph().serialize(
                destination=f"./vocabulary/{node}/vocabulary.ttl"
            )
