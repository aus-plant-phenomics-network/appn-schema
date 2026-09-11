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
import sys
import datetime
import warnings

from pathlib import Path
from typing import Optional, Any
from appn_types import Term, ColumnMapping
from appn_logger import IssueMessage
from appn_dictionary import Dictionary
from appn_parser import ExcelVocabularyParser
from appn_configuration import (
    APPN_VOCABULARY,
    Configuration,
    APPN_SCHEMA,
    SKOS_SCHEMA,
)
from rdflib import Graph, Namespace, URIRef, Literal


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

    # Make list of folders to process (either for a single node or for all)
    # Always process APPN before any nodes because it contains dependencies
    # for other vocabularies.
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

    organisations = configuration.get_organisations()

    # Generate vocabulary for each selected node in turn.
    for folder in folders:
        node = folder.name

        if node in organisations:

            parser = ExcelVocabularyParser(configuration, organisations[node])

            # Loop over Excel spreadsheets in the folder for the node.
            for file in folder.glob("*.xlsx"):

                # Ignore temporary files that still have xls in their name
                if not file.name.startswith("."):
                    logging.debug(f"Processing file {file}")
                    parser.load(file)

            inspector = Dictionary(parser.get_graph())

            with open(f"./vocabulary/{node}/{node}_report.txt", "w") as report:
                counts = inspector.count_triples_by_subject()
                report.write(f"Overview of processing for {node} vocabulary\n\n")
                report.write("Terms defined in vocabulary (with counts of associated properties):\n\n")
                length = max([len(k) for k in counts.keys()])
                for p in sorted(counts.keys()):
                    report.write(f"  {p:{length + 1}s} : {counts[p]:>5d}\n")

                counts = inspector.count_triples_by_property()
                report.write("\nCounts of triples by property\n\n")
                length = max([len(k) for k in counts.keys()])
                for p in sorted(counts.keys()):
                    report.write(f"  {p:{length + 1}s} : {counts[p]:>5d}\n")

                report.write("\n")
                report.write(configuration.get_logger().format_issues())

            parser.get_graph().serialize(
                destination=f"./vocabulary/{node}/{node}_vocabulary.ttl"
            )
