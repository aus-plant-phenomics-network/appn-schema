#!/usr/bin/emv python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
# appn_summarizer.py
#
# Summarise RO-Crate contents
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
      -a, --asset             : Namespace for an asset to be loaded - may be repeated.
      -p, --prefix            : (Optional) Prefix for asset to be loaded - the n-th prefix is used for the n-th asset.
      -f, --filepath-to-asset : (Optional) Filepath for reading asset instead of via URL - the n-th filepath is used for the n-th asset.
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


class UnitDefinition(NamedTuple):
    comparison_hash: int
    iri: IRI
    iri_type: Optional[IRI]
    iri_subtype: Optional[IRI]
    observed_variables: Optional[FrozenSet[IRI]]
    controlled_variables: Optional[FrozenSet[IRI]]
    treatments: Optional[FrozenSet[IRI]]
    nested_iris: Optional[dict[int, list["UnitDefinition"]]]


def build_hierarchy(
    iri: IRI,
    reverse_locations,
    iri_types: dict[IRI, IRI],
    iri_subtypes: dict[IRI, IRI],
    observed_variables: dict[IRI, set[IRI]],
    controlled_variables: dict[IRI, set[IRI]],
    treatments: dict[IRI, set[IRI]],
) -> UnitDefinition:
    subhierarchies = {}
    subhierarchy_hashes = []
    if iri in reverse_locations:
        for nested in sorted(reverse_locations[iri]):
            subhierarchy = build_hierarchy(
                nested,
                reverse_locations,
                iri_types,
                iri_subtypes,
                observed_variables,
                controlled_variables,
                treatments,
            )
            if subhierarchy.comparison_hash not in subhierarchies:
                subhierarchies[subhierarchy.comparison_hash] = [subhierarchy]
            else:
                subhierarchies[subhierarchy.comparison_hash].append(subhierarchy)
            subhierarchy_hashes.append(subhierarchy.comparison_hash)
    iri_type = iri_types[iri] if iri in iri_types else None
    iri_subtype = iri_subtypes[iri] if iri in iri_subtypes else None
    iri_observed_variables = (
        frozenset(observed_variables[iri]) if iri in observed_variables else None
    )
    iri_controlled_variables = (
        frozenset(controlled_variables[iri]) if iri in controlled_variables else None
    )
    iri_treatments = frozenset(treatments[iri]) if iri in treatments else None
    nested_hashes = tuple(subhierarchy_hashes)
    iri_hash = hash(
        (
            iri_type,
            iri_subtype,
            iri_observed_variables,
            iri_controlled_variables,
            iri_treatments,
            nested_hashes,
        )
    )
    return UnitDefinition(
        iri_hash,
        iri,
        iri_type,
        iri_subtype,
        iri_observed_variables,
        iri_controlled_variables,
        iri_treatments,
        subhierarchies,
    )


def display_hierarchy(
    unit: UnitDefinition,
    iri_names: dict[IRI, str],
    indent: str = "",
    count: Optional[int] = None,
    detail: bool = True,
) -> None:
    iri = unit.iri
    if count is None:
        iri_name = f": {iri_names[iri] if iri in iri_names else iri.curie}"
    elif count == 1:
        iri_name = ""
    else:
        iri_name = f": {count} instance{'' if count == 1 else 's'}"
    if unit.iri_type is None:
        type_name = "ObservationUnit"
    else:
        type_name = (
            iri_names[unit.iri_type]
            if unit.iri_type in iri_names
            else unit.iri_type.curie
        )
    if unit.iri_subtype is None:
        subtype_name = ""
    else:
        subtype_name = f" ({iri_names[unit.iri_subtype] if unit.iri_subtype in iri_names else unit.iri_subtype.curie})"
    print(f"{indent}{type_name}{subtype_name}{iri_name}")
    if detail and unit.observed_variables is not None:
        print(f"\n{indent}  Observed variables:")
        for variable in unit.observed_variables:
            variable_name = (
                iri_names[variable] if variable in iri_names else variable.curie
            )
            print(f"{indent}    {variable_name}")
    if detail and unit.controlled_variables is not None:
        print(f"\n{indent}  Controlled variables:")
        for variable in unit.controlled_variables:
            variable_name = (
                iri_names[variable] if variable in iri_names else variable.curie
            )
            print(f"{indent}    {variable_name}")
    if detail and unit.treatments is not None:
        print(f"\n{indent}  Treatments:")
        for variable in unit.treatments:
            variable_name = (
                iri_names[variable] if variable in iri_names else variable.curie
            )
            print(f"{indent}    {variable_name}")
    if unit.nested_iris is not None and len(unit.nested_iris) > 0:
        if detail:
            print(
                f"\n{indent}  {'The' if count is None else 'Each'} {subtype_name.strip(' ()') if len(subtype_name) > 0 else type_name} includes:"
            )
        for nested in unit.nested_iris.values():
            if detail:
                print()
            # Nested count values other than None hide names. Names should
            # be hidden whenever we have more than one observation unit
            # with the same properties (i.e. len(nested) > 1) or when we
            # are in a branch of the hierarchy that dropped names for the
            # same reason (in which case count is not None).
            nested_count = len(nested)
            if count is None and nested_count == 1:
                nested_count = None
            display_hierarchy(
                nested[0], iri_names, indent + "    ", nested_count, detail=detail
            )


if __name__ == "__main__":

    parser = setup_parser()
    args = vars(parser.parse_args(sys.argv[1:]))
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

    print("\nSTUDY DESCRIPTION:\n")

    for study in d.list_instances("appn:Study"):
        print(d.describe(study, friendly=True))

    iri_names = {}
    appn_classes = set(d.list_classes(namespace=APPN_SCHEMA))
    iri_names = {
        iri: name
        for iri, name in d.query("SELECT ?i ?n WHERE { ?i schema1:name ?n . }")
    }
    iri_types = {}
    for iri, rdf_type in d.query("SELECT ?i ?t WHERE { ?i rdf:type ?t . }"):
        if rdf_type in appn_classes:
            iri_types[iri] = rdf_type
    iri_subtypes = {}
    for iri, iri_subtype in d.query(
        "SELECT ?i ?t WHERE {{ ?i appn:hasBiologicalUnitType ?t } UNION { ?i appn:hasGrowthFacilityType ?t } UNION { ?i appn:hasPlatformType ?t } UNION { ?i appn:hasSensorType ?t }}"
    ):
        iri_subtypes[iri] = iri_subtype
    locations = {}
    reverse_locations = {}
    for iri, location_iri in d.query(
        "SELECT ?i ?l WHERE { ?i appn:hasLocation ?x . ?x appn:isLocationWithin ?l . }"
    ):
        locations[iri] = location_iri
        if location_iri not in reverse_locations:
            reverse_locations[location_iri] = set()
        reverse_locations[location_iri].add(iri)
    observed_variables = {}
    for iri, observed_variable_iri in d.query(
        "SELECT ?u ?v WHERE {?x appn:isForObservationUnit ?u . ?x appn:observes ?v . }"
    ):
        if iri not in observed_variables:
            observed_variables[iri] = set()
        observed_variables[iri].add(observed_variable_iri)
    controlled_variables = {}
    for iri, controlled_variable_iri in d.query(
        "SELECT ?u ?v WHERE {?x appn:isForObservationUnit ?u . ?x appn:controls ?v . }"
    ):
        if iri not in controlled_variables:
            controlled_variables[iri] = set()
        controlled_variables[iri].add(controlled_variable_iri)
    treatments = {}
    for iri, treatment_iri in d.query(
        "SELECT ?u ?v WHERE {?x appn:isForObservationUnit ?u . ?x appn:treatsWith ?v . }"
    ):
        if iri not in treatments:
            treatments[iri] = set()
        treatments[iri].add(treatment_iri)

    for iri in sorted(reverse_locations):
        if iri not in locations:
            hierarchy = build_hierarchy(
                iri,
                reverse_locations,
                iri_types,
                iri_subtypes,
                observed_variables,
                controlled_variables,
                treatments,
            )

            print("\nOBSERVATION UNIT HIERARCHY (DETAILED):\n")
            display_hierarchy(hierarchy, iri_names, indent="  ")

            print("\nOBSERVATION UNIT HIERARCHY (COMPACT):\n")
            display_hierarchy(hierarchy, iri_names, indent="  ", detail=False)

    print()

    logging.info("Finished")
