#!/usr/bin/emv python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
# appn_explorer.py
#
# Explore contents of APPN linked-data assets (schemas, vocabularies, metadata)
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
from rdflib import Graph, URIRef, Node
from rdflib.namespace import Namespace, NamespaceManager
from typing import Any, Optional

from appn_iri import IRI, Triple, TriplePosition
from appn_types import NamespaceDefinition
from appn_configuration import Configuration, APPN_SCHEMA
from appn_dictionary import Dictionary



### process_argv ##############################################################
#
# Safely process sys.argv, returning a dictionary of option values.
#
#     query             : query type - one of:
#                          { namespaces, classes, properties, 
#                            triples, unique_subjects, 
#                            unique_properties, unique_objects, 
#                            superclasses, superproperties, 
#                            domain_properties, range_properties, 
#                            domain_classes, range_classes, 
#                            domain_range_properties, instances, 
#                            subject, property, object,
#                            property-name, property-name-all,
#                            instance-name, instance-name-all,
#                            subject_counts, property_counts,
#                            object_counts }.
#     -l, --log-level   : "info" / "warning" / "error" / "debug".
#     -e,               : Display logging outputs to stderr.
#      --echo-to-stderr
#
subcommand_helptext = {
    "namespaces": "List all prefixes and namespaces from loaded assets.",
    "triples": "List all triples from loaded assets.",
    "unique_subjects": "List IRIs and CURIEs for all unique subjects of triples.",
    "unique_properties": "List IRIs and CURIEs for all unique properties of triples.",
    "unique_objects": "List IRIs and CURIEs for all unique objects of triples.",
    "classes": "List IRIs and CURIEs for all classes defined or referenced by loaded assets.",
    "properties": "List IRIs and CURIEs for all properties defined or referenced by loaded assets.",
    "superclasses": "List IRIs and CURIEs for all known superclasses for a class specified using its IRI or CURIE.",
    "superproperties": "List IRIs and CURIEs for all known superproperties for a property specified using its IRI or CURIE.",
    "instances": "List  IRIs and CURIEs for all known instances of a class specified using its IRI or CURIE.",
    "domain properties": "List IRIs and CURIEs for all known properties with a domain including a class specified using its IRI or CURIE.",
    "range properties": "List IRIs and CURIEs for all known properties with a range including a class specified using its IRI or CURIE.",
    "domain_range properties": "List IRIs and CURIEs for all known properties with a domain including one class and a range including another class specified using their IRIs or CURIEs.",
    "domain classes": "List IRIs and CURIEs for all known classes included within the domain of a property specified using its IRI or CURIE.",
    "range classes": "List IRIs and CURIEs for all known classes included within the range of a property specified using its IRI or CURIE.",
    "subject": "List all triples with the specified IRI or CURIE as subject.",
    "property": "List all triples with the specified IRI or CURIE as property.",
    "object": "List all triples with the specified IRI or CURIE as object.",
    "property-name": "List IRIs and CURIEs for all properties with the specified value for schema:name or rdfs:label (optionally filtered to a specified namespace).",
    "property-name-all": "List IRIs and CURIEs for all properties with the specified value for schema:name, rdfs:label or schema:alternateName (optionally filtered to a specified namespace).",
    "instance-name": "List IRIs and CURIEs for all terms belonging to the specified class and with the specified value for schema:name or rdfs:label (optionally filtered to a specified namespace).",
    "instance-name-all": "List IRIs and CURIEs for all terms belonging to the specified class and with the specified value for schema:name, rdfs:label or or schema:alternateName (optionally filtered to a specified namespace).",
    "subject_counts": "Count of all triples for each unique subject IRI.",
    "property_counts": "Count of all triples for each unique property IRI.",
    "object_counts": "Count of all triples for each unique object IRI.",
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
        "domain_properties",
        "range_properties",
        "domain_classes",
        "range_classes",
        "subject",
        "property",
        "object",
    ]:
        subparser = subparsers.add_parser(
            cmd, help=(subcommand_helptext[cmd] if cmd in subcommand_helptext else None)
        )
        subparser.add_argument("iri")
    for cmd in [
        "domain_range_properties",
    ]:
        subparser = subparsers.add_parser(
            cmd, help=(subcommand_helptext[cmd] if cmd in subcommand_helptext else None)
        )
        subparser.add_argument("domain")
        subparser.add_argument("range")
        subparser.add_argument("-n", "--namespace")
    for cmd in ["unique-subjects", "unique-properties", "unique-objects"]:
        subparser = subparsers.add_parser(
            cmd, help=(subcommand_helptext[cmd] if cmd in subcommand_helptext else None)
        )
        subparser.add_argument("-n", "--namespace")
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
    for cmd in ["subject_counts", "property_counts", "object_counts"]:
        subparser = subparsers.add_parser(
            cmd, help=(subcommand_helptext[cmd] if cmd in subcommand_helptext else None)
        )

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


def execute_query(
    d: Dictionary, args: dict[str, Any], max_rows: Optional[int] = None
) -> None:

    if args["query"] == "classes":
        print(d.format_iri_list(d.list_classes(), max_rows=max_rows))

    elif args["query"] == "properties":
        print(d.format_iri_list(d.list_properties(), max_rows=max_rows))

    elif args["query"] == "superclasses":
        print(d.format_iri_list(d.list_superclasses(args["iri"]), max_rows=max_rows))

    elif args["query"] == "superproperties":
        print(d.format_iri_list(d.list_superproperties(args["iri"]), max_rows=max_rows))

    elif args["query"] == "instances":
        print(d.format_iri_list(d.list_instances(args["iri"]), max_rows=max_rows))

    elif args["query"] == "unique-subjects":
        print(
            d.format_iri_list(
                d.list_unique_subjects(
                    namespace=args["namespace"] if "namespace" in args else None
                ),
                max_rows=max_rows,
            )
        )

    elif args["query"] == "unique-properties":
        print(
            d.format_iri_list(
                d.list_unique_properties(
                    namespace=args["namespace"] if "namespace" in args else None
                ),
                max_rows=max_rows,
            )
        )

    elif args["query"] == "unique-objects":
        print(
            d.format_iri_list(
                d.list_unique_objects(
                    namespace=args["namespace"] if "namespace" in args else None
                ),
                max_rows=max_rows,
            )
        )

    elif args["query"] == "domain_properties":
        print(
            d.format_iri_list(
                d.list_domain_properties_for_class(args["iri"]), max_rows=max_rows
            )
        )

    elif args["query"] == "range_properties":
        print(
            d.format_iri_list(
                d.list_range_properties_for_class(args["iri"]), max_rows=max_rows
            )
        )

    elif args["query"] == "domain_range_properties":
        print(
            d.format_iri_list(
                d.list_properties_by_domain_and_range(args["domain"], args["range"]), max_rows=max_rows
            )
        )

    elif args["query"] == "property-name":
        print(
            d.format_iri_list(
                d.list_properties_by_name(
                    args["name"],
                    namespace=args["namespace"] if "namespace" in args else None,
                ),
                max_rows=max_rows,
            )
        )

    elif args["query"] == "property-name-all":
        print(
            d.format_iri_list(
                d.list_properties_by_name(
                    args["name"],
                    check_alternate_names=True,
                    namespace=args["namespace"] if "namespace" in args else None,
                ),
                max_rows=max_rows,
            )
        )

    elif args["query"] == "instance-name":
        print(
            d.format_iri_list(
                d.list_instances_by_class_and_name(
                    args["class"],
                    args["name"],
                    namespace=args["namespace"] if "namespace" in args else None,
                ),
                max_rows=max_rows,
            )
        )

    elif args["query"] == "instance-name-all":
        print(
            d.format_iri_list(
                d.list_instances_by_class_and_name(
                    args["class"],
                    args["name"],
                    check_alternate_names=True,
                    namespace=args["namespace"] if "namespace" in args else None,
                ),
                max_rows=max_rows,
            )
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
        print(d.format_triple_list(triples, max_rows=max_rows))

    elif args["query"] == "subject_counts":
        print("\n".join([f"{count:>5d} {iri.curie}" for iri, count in d.count_triples_by_subject().items()]))
        
    elif args["query"] == "property_counts":
        print("\n".join([f"{count:>5d} {iri.curie}" for iri, count in d.count_triples_by_property().items()]))
        
    elif args["query"] == "object_counts":
        print("\n".join([f"{count:>5d} {iri.curie}" for iri, count in d.count_triples_by_object().items()]))

if __name__ == "__main__":

    args = process_argv(sys.argv)
    start_log(args["log_level"], None, args["echo_to_stderr"])

    d = Dictionary()
    d.load(APPN_SCHEMA)
    if args["asset"] is not None:
        for i in range(len(args["asset"])):
            asset = args["asset"][i]
            if args["prefix"] is not None and i in range(len(args["prefix"])):
                prefix = args["prefix"][i]
            else:
                prefix = None
            if args["filepath_to_asset"] is not None and i in range(
                len(args["filepath_to_asset"])
            ):
                path = args["filepath_to_asset"][i]
            else:
                path = None
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

    logging.info("Finished")
