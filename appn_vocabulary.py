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
import pandas as pd
import argparse
import _io
import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Optional, Any


### Mapper ####################################################################
#
# Base class for objects to map excel column values to instance properties.
# Subclasses provide the actual behaviour for different contexts.
#
class Mapper:
    def __init__(self) -> None:
        pass

    # Return a property value based on an Excel row (pandas Series). The
    # instances and node parameters are required by at least one subclass.
    def get_value(
        self,
        instances: dict[str, dict[str, dict[str, str]]],
        node: str,
        series: pd.Series,
    ) -> Optional[str]:
        return None

    # Return the name associated with the Mapper instance - this is to allow
    # a client to check what property will be generated.
    def get_name(self) -> Optional[str]:
        return None


### PropertyMapper ############################################################
#
# Mapper class to return the value of an Excel cell as an instance property if
# it is present and contains a valid value.
#
class PropertyMapper(Mapper):
    def __init__(self, column: str) -> None:
        super().__init__()
        self.column = column

    # Return the cell value as a string unless it is a None value (including
    # "NA").
    def get_value(
        self,
        instances: dict[str, dict[str, dict[str, str]]],
        node: str,
        series: pd.Series,
    ) -> Optional[str]:
        if self.column in series:
            value = str(series[self.column])
            if value not in [
                None,
                "",
                "nan",
                "NA",
                "No",
            ]:
                return str(series[self.column])
        return None

    # Return the name of the property handled by this Mapper.
    def get_name(self) -> Optional[str]:
        return self.column


### InstanceMapper #############################################################
#
# Mapper class to return the id of an associated schema class instance.
#
class InstanceMapper(Mapper):
    def __init__(self, class_name: str) -> None:
        super().__init__()
        self.class_name = class_name

    # Process the series (using get_instance) to find or create an instance of
    # a specified schema class and return its id (URI) as a property value.
    def get_value(
        self,
        instances: dict[str, dict[str, dict[str, str]]],
        node: str,
        series: pd.Series,
    ) -> Optional[str]:
        instance = get_instance(instances, self.class_name, node, series)
        if instance is not None and "@id" in instance:
            return instance["@id"]
        return None


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


def get_id(class_name: str, node: str, name: str) -> str:
    clean_name = name_pattern.sub("_", name).strip("_").lower()
    return f"https://id.plantphenomics.org.au/{node}/{class_name}/{clean_name}"


### get_instance ##############################################################
#
# Process a row from an Excel spreadsheet (as a pandas Series). Most of the
# work is carried out by the Mapper instances from the mappings dictionary.
# This includes recursive calls to this function for processing columns that
# represent instances of other classes referenced by this row (for example, to
# generate a Scale instance as part of processing an ObservedVariable and then
# to return the Scale id, i.e. its URI, as the mapped value to be included as
# a property for the ObservedVariable).
#
#     instances         : dictionary for accessing all currently defined
#                         instances of class classes and returning new ones.
#     class_name        : name of the schema class to be processed from row.
#     node              : abbreviated name for APPN node.
#     series            : row from spreadsheet (as pandas Series).
#
def get_instance(
    instances: dict[str, dict[str, dict[str, str]]],
    class_name: str,
    node: str,
    series: pd.Series,
) -> Optional[dict[str, str]]:

    # Need class to be included in mappings dictionary.
    if class_name not in mappings:
        logging.error(f"No mapping defined for class {class_name}")
        return None
    mapping = mappings[class_name]

    # Need the row to contain a name that can serve as an identifier.
    if "rdfs:label" not in mapping:
        logging.error(f"No name property defined for class {class_name}")
        return None

    # Since the spreadsheets are intended as templates, there may be incomplete
    # rows that should not be processed.
    name = mapping["rdfs:label"].get_value(instances, node, series)
    if name is None:
        logging.debug(f"No name supplied for new instance")
        return None

    # Get URI from instance name.
    id = get_id(class_name, node, name)

    # The instances dictionary is organised by schema class to keep it sorted
    # for when the vocabulary is generated. Make sure this class is included.
    if class_name not in instances:
        instances[class_name] = {}

    # If this instance is already defined (based on the derived URI), just
    # return the current instance.
    if id in instances[class_name]:
        logging.info(f"Returning instance with id {id}")
        return instances[class_name][id]

    # Create the new instance.
    logging.info(f"Creating new instance with id {id}")
    instance = {"@id": id, "@type": class_name}
    if node in organisations:
        instance["schema:owner"] = organisations[node][1]
    instances[class_name][id] = instance

    # Run all mappers associated with the schema class to get all available
    # properties for the instance.
    for property, mapper in mappings[class_name].items():
        value = mapper.get_value(instances, node, series)
        if value is not None:
            instance[property] = value

    return instance


### process_sheet #############################################################
#
# Loop over the rows in an Excel spreadsheet to generate all schema class
# instances.
#
#     instances         : dictionary for accessing all currently defined
#                         instances of class classes and returning new ones.
#     class_name        : name of the schema class to be processed from sheet.
#     node              : abbreviated name for APPN node.
#     file_path         : location of Excel spreadsheet.
#     sheet             : name of sheet to process from spreadsheet.
#
def process_sheet(
    instances: dict[str, dict[str, dict[str, str]]],
    class_name: str,
    node: str,
    file_path: Path,
    sheet: str,
) -> None:
    df = pd.read_excel(file_path, sheet_name=sheet)
    for _, series in df.iterrows():
        logging.debug(f"Row: {series.to_dict()}")
        get_instance(instances, class_name, node, series)


### process_argv ##############################################################
#
# Safely process sys.argv, returning a dictionary of option values.
#
#     -n, --node        : Node name (actually name of subfolder under source)
#                         or "all" to process all nodes (subfolders).
#     -l, --log-level   : "info" / "error" / "debug".
#     -e,               : Display logging outputs to stderr.
#      --echo-to-stderr
#
def process_argv(argv: list[str]) -> dict[str, Any]:
    parser = argparse.ArgumentParser(
        prog=argv[0],
        description=f"{argv[0]}: Generate linked-data outputs from APPN node vocabulary sheets",
    )
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


### write_html ################################################################
#
# Write line to HTML file, maintaining tidy indentation.
#
#   NOTE: Type checking is disabled for rows accessing JSON graph nodes.
#
#     html_file         : file to write HTML content.
#     html              : line of HTML to be written.
#     indent            : indentation level.
#
def write_html(html_file: _io.TextIOWrapper, html: str, indent: int = 0) -> int:
    increment = False
    html = html.strip()
    end_tags = html.count("</")
    null_tags = html.count("/>")
    start_tags = html.count("<") - html.count("< ") - 2 * end_tags - null_tags
    if start_tags < 0:
        indent += start_tags
    html_file.write(f"{'    ' * indent}{html}\n")
    if start_tags > 0:
        indent += start_tags
    return 0 if indent < 0 else indent


### substitute ################################################################
#
# Expand prefixes where they appear in a text string
#
def substitute(prefixes: dict[str, str], s: str) -> str:
    for k, v in prefixes.items():
        if k in s:
            s = s.replace(k, v)
    return s


### format_id #################################################################
#
# Expand URIs and link for a property value within or outside this document
#
def format_id(prefixes: dict[str, str], id: str) -> str:
    expanded = substitute(prefixes, id)
    if "plantphenomics" in expanded and "schema" not in expanded:
        return f'<a href="#{id}">{expanded}</a>'
    else:
        return f'<a href="{expanded}" target="_blank">{expanded}</a>'


### format_property ###########################################################
#
# Expand URIs and return link for a property key
#
def format_property(prefixes: dict[str, str], key: str) -> str:
    parts = key.split(":")
    return f'{parts[0]}: <a href="{substitute(prefixes, key)}" target="_blank">{parts[1]}</a>'


### process_value #############################################################
#
# Turn a property value into formatted content to include in a <dd> tag
# Convert dictionaries containing just an @id into links
# Insert <br> between list values
#
def process_value(
    prefixes: dict[str, str], value: str | list[str | dict[str, str]] | dict[str, str]
) -> str:
    if isinstance(value, dict) and "@id" in value:
        return format_id(prefixes, value["@id"])
    elif isinstance(value, list):
        formatted = ""
        for v in value:
            if isinstance(v, dict) and "@id" in v:
                v = format_id(prefixes, v["@id"])
            if len(formatted) > 0:
                formatted += "<br/>"
            formatted += v
        value = formatted
    else:
        value = str(value)
    return value


### format_html ###############################################################
#
# Write JSON-LD vocabulary as an HTML file, maintaining tidy indentation.
#
#   NOTE: Type checking is disabled for rows accessing JSON graph nodes.
#
#     html_path         : path to HTML file.
#     node              : abbreviated APPN node name.
#     json              : JSON-LD vocabulary data.
#     prefixes          : dictionary of vocabulary prefixes.
#
def format_html(
    html_path: Path, node: str, json: Any, prefixes: dict[str, str]
) -> None:

    # Append colons to prefixes for substition
    substitutions = {f"{k}:": v for k, v in prefixes.items()}

    # This assumes objects are sorted by type. Otherwise some headings will repeat.
    with open(html_path, "w") as html_file:
        indent = write_html(html_file, "<html>")
        indent = write_html(html_file, "<head>", indent)
        indent = write_html(html_file, '<meta charset="UTF-8"/>', indent)
        indent = write_html(
            html_file,
            '<meta name="viewport" content="width=device-width, initial-scale=1.0"/>',
            indent,
        )
        indent = write_html(html_file, f"<title>APPN {node} vocabulary</title>", indent)
        indent = write_html(
            html_file, '<link rel="stylesheet" href="/css/style.css"/>', indent
        )
        indent = write_html(html_file, "</head>", indent)
        indent = write_html(html_file, "<body>", indent)
        indent = write_html(html_file, f"<h1>APPN {node} vocabulary</h1>", indent)

        current_class = ""
        for node in json["@graph"]:
            if "@type" in node and node["@type"] != current_class:  # type: ignore
                indent = write_html(html_file, f"<h2>{node['@type']}</h2>", indent)  # type: ignore
                current_class = node["@type"]  # type: ignore
            indent = write_html(
                html_file,
                f'<h3 id="{node['@id']}">{substitute(substitutions, node["@id"])}</h3>',  # type: ignore
                indent,
            )
            indent = write_html(html_file, f"<dl>", indent)
            for k, v in node.items():  # type: ignore
                if not k.startswith("@"):
                    indent = write_html(
                        html_file,
                        f"<dt><b>{format_property(substitutions, k)}</b></dt><dd>{process_value(substitutions, v)}</dd>",
                        indent,
                    )
            indent = write_html(html_file, f"</dl>", indent)

        indent = write_html(html_file, "</body>", indent)
        indent = write_html(html_file, "</html>", indent)


### GLOBAL VARIABLES ##########################################################
#
# Definition objects controlled the execution
#

# Dictionary of APPN nodes
organisations = {
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

# Map of maps of maps. A dictionary that maps schema class names to dictionaries
# of associated properties. Each property dictionary maps a property name to a
# Mapper object that encapsulates function to extract a value for the property
# from a spreadsheet row.
mappings = {
    "GrowthFacility": {
        "rdfs:label": PropertyMapper("growth facility name *"),
        "rdfs:comment": PropertyMapper("growth facility description *"),
        "appn:hasGrowthFacilityType": InstanceMapper("GrowthFacilityType"),
        "schema:brand": PropertyMapper("growth facility type brand *"),
        "schema:model": PropertyMapper("growth facility model *"),
        "schema:serialNumber": PropertyMapper("growth facility serial number *"),
        "appn:containmentLevel": PropertyMapper("containment level *"),
        "appn:quarantine": PropertyMapper("quarantine details *"),
        "skos:closeMatch": PropertyMapper("growth facility ontology IRI"),
    },
    "GrowthFacilityType": {
        "rdfs:label": PropertyMapper("growth facility type *"),
    },
    "Platform": {
        "rdfs:label": PropertyMapper("platform name"),
        "rdfs:comment": PropertyMapper("platform description *"),
        "appn:hasPlatformType": InstanceMapper("PlatformType"),
        "schema:brand": PropertyMapper("platform type brand"),
        "schema:model": PropertyMapper("platform model *"),
        "schema:serialNumber": PropertyMapper("platform serial number *"),
        "skos:closeMatch": PropertyMapper("platform ontology IRI"),
    },
    "PlatformType": {
        "rdfs:label": PropertyMapper("platform type *"),
    },
    "Sensor": {
        "rdfs:label": PropertyMapper("sensor name"),
        "rdfs:comment": PropertyMapper("sensor description *"),
        "appn:hasSensorType": InstanceMapper("SensorType"),
        "schema:brand": PropertyMapper("sensor type brand"),
        "schema:model": PropertyMapper("sensor model *"),
        "schema:serialNumber": PropertyMapper("sensor serial number *"),
        "skos:closeMatch": PropertyMapper("sensor ontology IRI"),
    },
    "SensorType": {
        "rdfs:label": PropertyMapper("sensor type *"),
    },
    "Deployment": {
        "rdfs:label": PropertyMapper("appn deployment name"),
        "appn:deployedOnPlatform": InstanceMapper("Platform"),
        "appn:deployedSystem": InstanceMapper("Sensor"),
    },
    "ObservedVariable": {
        "rdfs:label": PropertyMapper("trait name"),
        "rdfs:comment": PropertyMapper("trait description"),
        "skos:closeMatch": PropertyMapper("Variable Xref"),
        "dc:creator": PropertyMapper("Scientist"),
        "dc:created": PropertyMapper("Date"),
        "dc:language": PropertyMapper("Language"),
        "appn:hasScale": InstanceMapper("Scale"),
        "appn:hasTrait": InstanceMapper("Trait"),
        "appn:usedMethod": InstanceMapper("Method"),
        "appn:forBiologicalMaterial": InstanceMapper("BiologicalMaterial"),
        "appn:forBiologicalUnitType": InstanceMapper("BiologicalUnitType"),
    },
    "BiologicalMaterial": {
        "rdfs:label": PropertyMapper("crop"),
    },
    "BiologicalUnitType": {
        "rdfs:label": PropertyMapper("entity"),
    },
    "Trait": {
        "rdfs:label": PropertyMapper("trait name"),
        "rdfs:comment": PropertyMapper("trait description"),
        "schema:alternateName": PropertyMapper("trait alternative label"),
        "skos:exactMatch": PropertyMapper("trait exactmatch"),
        "skos:closeMatch": PropertyMapper("trait closematch"),
        "skos:relatedMatch": PropertyMapper("trait relatedmatch"),
    },
    "Method": {
        "rdfs:label": PropertyMapper("method name"),
        "rdfs:comment": PropertyMapper("method description"),
    },
    "Scale": {
        "rdfs:label": PropertyMapper("scale name"),
        "schema:alternateName": PropertyMapper("scale alternative label"),
        "rdfs:comment": PropertyMapper("scale description"),
        "skos:exactMatch": PropertyMapper("scale exactmatch"),
        "skos:closeMatch": PropertyMapper("scale closematch"),
        "skos:relatedMatch": PropertyMapper("Scale relatedmatch"),
    },
}

# Dictionary of vocabulary prefixes
prefixes = {
    "appn": "https://schema.plantphenomics.org.au/appn-schema.ttl",
    "dc": "http://purl.org/dc/elements/1.1/",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "schema": "https://schema.org/",
    "skos": "http://www.w3.org/2004/02/skos/core#",
}

### MAIN PROGRAM ##############################################################
#
# Parse arguments and set up logging. Based on arguments, scan one or all
# source folders for all Excel spreadheets and generate a JSON-LD vocabulary
# for all schema class instances included.
#
if __name__ == "__main__":

    args = process_argv(sys.argv)
    start_log(args["log_level"], None, args["echo_to_stderr"])

    node = args["node"]

    # Make list of folders to process (either for a single node or for all)
    if node == "all":
        folders = list(Path("source").glob("*/"))
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

    # Generate vocabulary for each selected node in turn.
    for folder in folders:
        node = folder.name

        # Dictionary to map URIs to the class instances (as dictionaries).
        instances = {}

        # Loop over Excel spreadsheets in the folder for the node.
        for file in folder.glob("*.xls*"):

            # Ignore temporary files that still have xls in their name
            if file.name.startswith("."):
                logging.debug(f"Ignoring file {file}")
            else:
                logging.info(f"Processing file {file}")

                # Dictionary to map schema classes to actual sheet names.
                sheets = {}

                # Find sheets with definitions. This code is tolerant of different
                # spacing and capitalisation.
                for sheet in pd.ExcelFile(file).sheet_names:
                    sheet_normal = sheet.lower().replace(" ", "")
                    if "sheet1" in sheet_normal:
                        sheets["ObservedVariable"] = sheet
                    elif "platform" in sheet_normal:
                        sheets["Platform"] = sheet
                    elif "sensor" in sheet_normal:
                        sheets["Sensor"] = sheet
                    elif "deployment" in sheet_normal:
                        sheets["Deployment"] = sheet
                    elif "growthfacility" in sheet_normal:
                        sheets["GrowthFacility"] = sheet
                    else:
                        logging.debug(f"Ignoring sheet {sheet}")

                # Ensure that classes are added in a safe order (Deployment after Platform and Sensor)
                for class_name in [
                    "GrowthFacility",
                    "Platform",
                    "Sensor",
                    "Deployment",
                    "ObservedVariable",
                ]:
                    if class_name in sheets:
                        logging.info(
                            f"{node} / {file} / {sheets[class_name]} --> {class_name}"
                        )

                        # Handle all definitions in the current sheet (including referenced objects).
                        process_sheet(
                            instances, class_name, node, file, sheets[class_name]
                        )

            # Flatten the instance dictionaries into a single list.
            node_instances = []
            for class_name in instances:
                node_instances += instances[class_name].values()

            # Generate and write the JSON-LD vocabulary.
            vocabulary = {
                "@context": prefixes,
                "@graph": node_instances,
            }
            target = Path("vocabulary") / node
            os.makedirs(target, exist_ok=True)
            with open(target / "vocabulary.json", "w", encoding="utf-8") as f:
                json.dump(vocabulary, f, ensure_ascii=False, indent=4)
                format_html(target / "vocabulary.html", node, vocabulary, prefixes)
