#!/usr/bin/emv python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
# appn_schema_mapping.py
#
# Display alignment between APPN schema and a referenced schema
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
from typing import FrozenSet, NamedTuple, Optional

from rdflib.plugins.sparql.sparql import FrozenDict

from appn_configuration import APPN_SCHEMA
from appn_dictionary import Dictionary
from appn_iri import IRI

### setup_parser ##############################################################


def setup_parser() -> argparse.ArgumentParser:
    """
    Set up parser to handle command-line sys.argv parameters or
    interactive parameters in the same format.

    The parser handles the following arguments:
      -l, --log-level         : "info" / "warning" / "error" / "debug".
      -e, --echo-to-stderr    : Display logging outputs to stderr.
      schema                  : Prefix identifying schema for comparison
    """
    parser = argparse.ArgumentParser(
        description=f"{__name__}: Summarise RO-Crate contents"
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
        "schema",
        help="Schema with which to compare APPN coverage",
    )

    return parser


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

### MAIN BODY #################################################################

if __name__ == "__main__":

    parser = setup_parser()
    args = vars(parser.parse_args(sys.argv[1:]))
    start_log(args["log_level"], None, args["echo_to_stderr"])

    other_schema = args["schema"]

    # Loading the dictionary brings in the mapped schemas
    d = Dictionary()
    d.load(APPN_SCHEMA)
    d.import_references()

    # Exit if the requested schema prefix is not recognised
    namespaces = d.get_namespaces()
    if other_schema not in namespaces:
        print(f"Schema {other_schema} not recognised")
        sys.exit(1)

    other_namespace = namespaces[other_schema]

    # Get lists of the classes and properties from both schemas
    appn_classes = d.list_classes(namespace=APPN_SCHEMA)
    other_classes = d.list_classes(namespace=other_namespace)
    appn_properties = d.list_properties(namespace=APPN_SCHEMA)
    other_properties = d.list_properties(namespace=other_namespace)
    
    # Build map of superproperties for each APPN schema property
    superproperties = {}
    for appn_iri in appn_properties:
        superproperties[appn_iri] = d.list_superproperties(appn_iri, namespace=other_namespace)
    
    # Build map of domain properties for each class in the other schema
    other_domain_properties = {}
    for other_iri in other_classes:
        other_domain_properties[other_iri] = d.list_domain_properties_for_class(other_iri, namespace=other_namespace)

    # Referenced keeps track of terms in the other schema that have already been displayed
    referenced = set()

    # Display mappings for each APPN class and its properties
    for appn_iri in sorted(appn_classes):
        # Show APPN class and any superclasses in the other schema
        superclasses = d.list_superclasses(appn_iri, namespace=other_namespace)
        print(f"{appn_iri.curie:50s}\t{", ".join([iri.curie for iri in superclasses])}")
        referenced |= set(superclasses)

        # Show APPN properties for the class and any superproperties in the other schema
        for domain_property in d.list_domain_properties_for_class(appn_iri, namespace=APPN_SCHEMA):
            print(f"    {domain_property.curie:46s}\t    {", ".join([iri.curie for iri in superproperties[domain_property]])}")
            referenced |= set(superproperties[domain_property])

        # Show properties from the other schema that are not mapped by APPN for one of the superclasses
        for other_iri in sorted(superclasses):
            domain_properties = d.list_domain_properties_for_class(other_iri, namespace=other_namespace)
            for domain_property in domain_properties:
                if domain_property not in referenced:
                    print(f"{' ' * 50}\t    {domain_property.curie}")
            referenced |= set(domain_properties)

    # Display remaining classes and properties from the other schema
    for other_iri in sorted(other_classes):
        if other_iri not in referenced:
            print(f"{' ' * 50}\t{other_iri.curie}")
            domain_properties = d.list_domain_properties_for_class(other_iri, namespace=other_namespace)
            for domain_property in domain_properties:
                print(f"{' ' * 50}\t    {domain_property.curie}")
            referenced |= set(domain_properties)

    # Display any properties in the other schema that have no domain class
    unknown_shown = False
    for other_iri in sorted(other_properties):
        if other_iri not in referenced:
            if not unknown_shown:
                print(f"{' ' * 50}\tNO KNOWN CLASS")
                unknown_shown = True
            print(f"{' ' * 50}\t    {other_iri.curie}")
