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
from appn_types import Term
from appn_dictionary import Dictionary
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
    APPN_SCHEMA,
    SKOS_SCHEMA,
)
from rdflib import Graph, URIRef, Literal


class RequiredProperty(NamedTuple):
    subject: URIRef
    property: URIRef
    object_class: str
    object_iri: str


### get_id ####################################################################
#
# Convert an instance name to a safe (URI) id. The URI has the pattern:
# https://id.plantphenomics.org.au/<node>/<class>/<id>.
#
#     class_name        : name of schema class.
#     node              : short name (abbreviation) for APPN node.
#     name              : name of class instance.
#
name_pattern = re.compile(r"[\s'\"\\?;:,°*+(){}\[\]]+")


def sanitize_name(name: str) -> str:
    return "".join([w.title() for w in name_pattern.sub(" ", name).strip().split()])


def get_id(class_name: str, node: str, name: str, abbreviations: dict[str, str]) -> str:
    clean_name = "".join(
        [w.title() for w in name_pattern.sub(" ", name).strip().split()]
    )
    class_name = (
        abbreviations[class_name] if class_name in abbreviations else class_name
    ).lower()
    return f"https://id.plantphenomics.org.au/{node}/{class_name}_{clean_name}"


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
        "-l", "--log-level", choices=("error", "info", "debug"), default="info"
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

    print(f"Logging started to {logfile_name} at level {level} and echo {echo}")
    logging.info(f"Logging started to {logfile_name} at level {level} and echo {echo}")


### GLOBAL VARIABLES ##########################################################
#
# Definition objects controlled the execution
#

# Dictionary of APPN nodes
organisations = {
    "APPN": ("Australian Plant Phenomics Network", "https://ror.org/02zj7b759"),
    "ANU": ("Australian National University", "https://ror.org/019wvm592"),
    "AU": ("Adelaide University", "https://ror.org/028g18b61"),
    "CSU": ("Charles Sturt University", "https://ror.org/00wfvh315 "),
    "DPIRD": (
        "WA Department of Primary Industry and Regional Development",
        "https://ror.org/01awp2978",
    ),
    "LTU": ("La Trobe University", "https://ror.org/01rxfrp27"),
    "UQ": ("University of Queensland", "https://ror.org/00rqy9422"),
    "USYD": ("University of Sydney", "https://ror.org/0384j8v12"),
    "UWA": ("University of Western Australia", "https://ror.org/047272k79"),
    "WSU": ("Western Sydney University", "https://ror.org/03t52dk35"),
}


def list_explicit_classes(
    class_: Term, configuration: Configuration, dictionary: Dictionary
) -> list[Term]:
    superclasses = dictionary.list_superclasses(class_.iri)
    explicit_rules = configuration.get_explicit_classes()
    excluded_classes = configuration.get_excluded_classes()

    explicit_classes = []

    for superclass in superclasses:
        if superclass.iri == class_:
            explicit_classes.append(URIRef(superclass.iri))
        elif superclass.ns in explicit_rules and superclass.iri not in excluded_classes:
            rule = explicit_rules[superclass.ns]
            if isinstance(rule, list):
                if superclass.name in rule:
                    explicit_classes.append(URIRef(superclass.iri))
            elif isinstance(rule, str):
                if rule == EXPLICIT_CLASSES_ALL:
                    explicit_classes.append(URIRef(superclass.iri))
                elif rule == EXPLICIT_CLASSES_FIRST:
                    explicit_classes.append(URIRef(superclass.iri))
                    explicit_rules.pop(superclass.ns)

    explicit_classes.append(URIRef("http://www.w3.org/2004/02/skos/core#Concept"))

    return explicit_classes


def process_sheet(
    graph: Graph,
    df: pd.DataFrame,
    class_name: str,
    node: str,
    column_properties: dict[str, URIRef],
    column_classes: dict[str, URIRef],
    name_column: str,
    class_abbreviations: dict[str, str],
    required_properties: list[RequiredProperty],
) -> bool:
    print(type(df))

    success = True
    concept_scheme_term = None

    for _, row in df.iterrows():
        if not pd.isnull(row[name_column]):
            name = row[name_column]
            id = get_id(class_.name, node, name, class_abbreviations)
            id_term = URIRef(id)
            if id in instances[class_name]:
                logging.error(
                    f"ERROR: Multiple entries for class {class_.name} with the same name: {name} - ignoring all but first"
                )
                success = False
            else:
                if concept_scheme_term is None:
                    concept_scheme_id = f"https://id.plantphenomics.org.au/{node}/{class_abbreviations['ConceptScheme'] if 'ConceptScheme' in class_abbreviations else 'conceptscheme'}_{class_.name}"
                    concept_scheme_term = URIRef(concept_scheme_id)
                    graph.add(
                        (
                            concept_scheme_term,
                            rdf_type,
                            skos_concept_scheme,
                        )
                    )
                    for p in [schema_name, dc_title]:
                        graph.add(
                            (
                                concept_scheme_term,
                                p,
                                Literal(class_name),
                            )
                        )
                    for p in [
                        schema_description,
                        dc_description,
                    ]:
                        graph.add(
                            (
                                concept_scheme_term,
                                p,
                                Literal(
                                    f"Concept scheme including instances of the APPN {class_.name} class from the APPN {node} node"
                                ),
                            )
                        )

                instances[class_.name][id] = id_term

                for explicit_class in explicit_classes:
                    graph.add(
                        (
                            id_term,
                            rdf_type,
                            explicit_class,
                        )
                    )

                graph.add(
                    (
                        id_term,
                        skos_in_scheme,
                        concept_scheme_term,
                    )
                )

                for column in column_properties:
                    value = row[column]
                    if not pd.isnull(value):
                        property_term = column_properties[column]
                        if column in column_classes:
                            required_properties.append(
                                RequiredProperty(
                                    id_term,
                                    property_term,
                                    column_classes[column].name,
                                    get_id(
                                        column_classes[column].name,
                                        node,
                                        row[column],
                                        class_abbreviations,
                                    ),
                                )
                            )
                        else:
                            if isinstance(value, str) and value.startswith("http"):
                                value_term = URIRef(value.strip())
                            else:
                                value_term = Literal(value)
                            graph.add(
                                (
                                    id_term,
                                    property_term,
                                    value_term,
                                )
                            )
                            if property_term in property_expansions:
                                for expansion_property in property_expansions[
                                    property_term
                                ]:
                                    graph.add(
                                        (
                                            id_term,
                                            expansion_property,
                                            value_term,
                                        )
                                    )

    return success


def lower_first(name: str) -> str:
    return name[0].lower() + name[1:]


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
    dictionary = Dictionary(configuration.get_namespace_definitions())
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

    integer_stripper = re.compile(r"[0-9]*$")

    sheet_aliases = configuration.get_sheet_aliases()
    column_aliases = configuration.get_column_aliases()
    class_abbreviations = configuration.get_class_abbreviations()
    property_expansions = configuration.get_property_expansions()
    embedded_classes = configuration.get_embedded_classes()

    rdf_type = URIRef(f"{RDF_SCHEMA}type")
    rdfs_property = URIRef(f"{RDFS_SCHEMA}Property")
    schema_name = URIRef(f"{SCHEMA_SCHEMA}name")
    schema_description = URIRef(f"{SCHEMA_SCHEMA}description")
    skos_concept = URIRef(f"{SKOS_SCHEMA}Concept")
    skos_concept_scheme = URIRef(f"{SKOS_SCHEMA}ConceptScheme")
    skos_in_scheme = URIRef(f"{SKOS_SCHEMA}inScheme")
    dc_title = URIRef(f"{DC_SCHEMA}title")
    dc_description = URIRef(f"{DC_SCHEMA}description")

    # Generate vocabulary for each selected node in turn.
    for folder in folders:
        node = folder.name
        organisation_name, ror = organisations[node]

        # Loop over Excel spreadsheets in the folder for the node.
        for file in folder.glob("*.xls*"):

            # Ignore temporary files that still have xls in their name
            if file.name.startswith("."):
                logging.debug(f"Ignoring file {file}")
            else:
                logging.info(f"Processing file {file}")

                graph = Graph()

                # Dictionary to map URIs to the class instances (as dictionaries).
                instances = {}

                classes = {
                    class_.name: class_
                    for class_ in dictionary.list_classes(namespace=APPN_SCHEMA)
                }
                instances: dict[str, dict[str, str]] = {}

                required_properties: list[RequiredProperty] = []

                for sheet in pd.ExcelFile(file).sheet_names:
                    sheet_class = (
                        sheet_aliases[sheet] if sheet in sheet_aliases else sheet
                    )
                    if sheet_class in classes:

                        class_ = classes[sheet_class]

                        # Load the sheet as a Pandas dataframe
                        df = pd.read_excel(file, sheet_name=sheet)

                        embedding_prefixes = (
                            {
                                embedded_class.lower(): embedded_class
                                for embedded_class in embedded_classes[class_.name]
                            }
                            if class_.name in embedded_classes
                            else {}
                        )

                        processing_runs = [""] + list(embedding_prefixes.keys())

                        for processing_run in processing_runs:

                            name_column = lower_first(f"{processing_run}Name")
                            run_class = (
                                dictionary.get_term(
                                    f"{APPN_SCHEMA}{embedding_prefixes[processing_run]}"
                                )
                                if processing_run in embedding_prefixes
                                else class_
                            )

                            if name_column not in df.columns:
                                logging.error(
                                    f"Sheet {sheet} does not include a name column {name_column} - ignoring sheet {sheet} for class {run_class}"
                                )

                            else:
                                logging.debug(
                                    f"Handling rows in sheet {sheet} as instances of {run_class}"
                                )

                                if run_class.name not in instances:
                                    instances[run_class.name] = {}

                                explicit_classes = list_explicit_classes(
                                    run_class, configuration, dictionary
                                )

                                # Build dictionary of candidate properties for the class. Preference those with
                                # the class as the domain, processing them in the returned order (which starts
                                # with properties for the APPN class and proceeds up the superclass chain), and
                                # then include in descending priority properties from schema.org, SKOS or Dublin
                                # Core. If a property with the name has already been found, do not overwrite it.
                                properties = {}

                                # Columns will be handled as properties which include the current class as their
                                # domain. If no such property exists with the specified name, a matching
                                # will be selected from one of the namespaces specified in the configuration
                                # (in descending order of precedence). This code builds a map of unqualified
                                # property names to the preferred property. A clean map is created for each
                                # sheet in the spreadsheet since the domain properties vary by class.
                                for p in dictionary.list_domain_properties_for_class(
                                    run_class.iri
                                ):
                                    if p.name not in properties:
                                        properties[p.name] = p
                                for (
                                    s
                                ) in configuration.get_vocabulary_column_namespaces():
                                    for p in dictionary.list_properties(namespace=s):
                                        if p.name not in properties:
                                            properties[p.name] = p

                                # Build dictionary of property URIRefs for each column.
                                column_properties = {}

                                # Build dictionary of columns that represent references to instances of a
                                # schema class (referenced via the instance name) - these need to be resolved
                                # to the IRI for the corresponding instance.
                                column_classes = {}

                                # Build dictionary of any nested classes that should be processed as though
                                # they were a separate sheet.
                                embeddings = {}

                                # Map each column name to a property
                                # TODO Remember columns that are references by name to instances of other classes.
                                for column in df.columns:
                                    column_name = integer_stripper.sub("", column)

                                    if column_name in column_aliases:
                                        column_name = column_aliases[column_name]

                                    if processing_run == "":
                                        for prefix in embedding_prefixes.keys():
                                            if column_name.startswith(prefix):
                                                if column_name == f"{prefix}Name":
                                                    column_name = embedding_prefixes[
                                                        prefix
                                                    ]
                                                else:
                                                    column_name = None
                                                break
                                    else:
                                        if column_name.startswith(processing_run):
                                            column_name = lower_first(
                                                column_name[len(processing_run)]
                                            )
                                        else:
                                            column_name = None

                                    if column_name is not None:
                                        property_ = None
                                        if column_name in properties:
                                            property_ = properties[column_name]
                                        elif column_name in classes:
                                            related_class = classes[column_name]
                                            range_properties = dictionary.list_properties_by_domain_and_range(
                                                run_class.iri,
                                                related_class.iri,
                                                APPN_SCHEMA,
                                            )
                                            column_classes[column] = related_class
                                            if len(range_properties) == 1:
                                                property_ = range_properties[0]
                                            else:
                                                # TODO A default choice could be specified in the Configuration.
                                                # Otherwise, should this throw an Error?
                                                logging.error(
                                                    f"ERROR: Multiple properties link {class_.curie} to {related_class.curie} - unknown mapping for column {column} in sheet {sheet}"
                                                )

                                        if property_ is None:
                                            local_property_id = f"https://id.plantphenomics.org.au/{node}/{lower_first(sanitize_name(column_name))}"
                                            local_property_term = URIRef(
                                                local_property_id
                                            )
                                            if "Property" not in instances:
                                                instances["Property"] = {}
                                            if (
                                                local_property_id
                                                not in instances["Property"]
                                            ):
                                                graph.add(
                                                    (
                                                        local_property_term,
                                                        rdf_type,
                                                        rdfs_property,
                                                    )
                                                )
                                            column_properties[column] = (
                                                local_property_term
                                            )
                                        else:
                                            logging.info(
                                                f"Column {column} in {sheet} recognised as {property_.curie}"
                                            )
                                            column_properties[column] = URIRef(
                                                property_.iri
                                            )

                                process_sheet(
                                    graph,
                                    df,
                                    class_.name,
                                    node,
                                    column_properties,
                                    column_classes,
                                    "name",
                                    class_abbreviations,
                                    required_properties,
                                )
                                for (
                                    embedding_class,
                                    embedding_columns,
                                ) in embeddings.items():

                                    process_sheet(
                                        graph,
                                        df,
                                        embedding_class,
                                        node,
                                        embedding_columns,
                                    )

                for required_property in required_properties:
                    if (
                        required_property.object_class in instances
                        and required_property.object_iri
                        in instances[required_property.object_class]
                    ):
                        value_term = instances[required_property.object_class][
                            required_property.object_iri
                        ]
                        graph.add(
                            (
                                required_property.subject,
                                required_property.property,
                                value_term,
                            )
                        )
                    else:
                        logging.error(
                            f"ERROR: {str(required_property.subject)} references unknown {required_property.object_class}: {required_property.object_iri}"
                        )

                graph.bind("appnid", APPN_VOCABULARY, override=True)
                graph.bind("appn", APPN_SCHEMA, override=True)
                graph.bind("bio", BIO_SCHEMA)
                graph.bind(node.lower(), f"https://id.plantphenomics.org.au/{node}/")
                graph.serialize(destination=f"./vocabulary/{node}/vocabulary.ttl")
