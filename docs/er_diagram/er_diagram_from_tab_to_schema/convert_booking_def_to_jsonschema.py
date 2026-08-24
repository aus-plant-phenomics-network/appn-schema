#!/usr/bin/env python3
import json
from pathlib import Path

"""
Convert an APPN tab-delimited schema specification into JSON Schema.

Supported property row shapes after the leading indentation tab:

Class rows:
    classURI    [blank]    [blank]    cardinality

Property rows, literal value:
    propertyURI    guiLabel    cardinality    datatype    format

Property rows, reference value:
    propertyURI    guiLabel    cardinality    targetClass

Property rows, explicit 6-column value:
    propertyURI    guiLabel    cardinality    targetClass    datatype    format

Examples:
    schema:Person.givenName      givenName      1..1   string
    schema:Person.email          email          0..n   string      email
    schema:Thing.identifier      identifier     0..1   string      uri
    schema:Person.affiliation    affiliation    1..n   schema:Organization
    
Usage:
# 1. Change the input_file = "appn_schema_tabdelim_appn.txt" filename value in main() function.
# 2. Run:
> python convert_booking_def_to_jsonschema_6cols_oneof_fixed.py 

# 3. The output filename is the input filename wth a json extension
# e.g. "appn_schema_tabdelim_appn.json"
"""

VALID_FORMATS = {
    "uri",
    "email",
    "date",
    "date-time",
    "hostname",
    "ipv4",
    "ipv6",
    "uuid",
}

JSON_TYPES = {
    "string",
    "integer",
    "number",
    "boolean",
    "object",
    "array",
    "null",
}


def parse_cardinality(cardinality):
    """
    Examples:
        1..1 -> required, not repeatable
        0..1 -> optional, not repeatable
        1..n -> required, repeatable
        0..n -> optional, repeatable
    """
    lower, upper = cardinality.strip().split("..")
    required = lower == "1"
    repeatable = upper.lower() == "n"
    return required, repeatable


def datatype_to_jsonschema(datatype):
    """Convert input datatype names into JSON Schema types."""
    if datatype is None:
        return "string"

    datatype_map = {
        "string": "string",
        "integer": "integer",
        "number": "number",
        "boolean": "boolean",
        "object": "object",
        "array": "array",
        "null": "null",
    }
    return datatype_map.get(datatype.lower(), "string")


def is_json_type(value):
    return bool(value) and value.lower() in JSON_TYPES


def is_format(value):
    return bool(value) and value.lower() in VALID_FORMATS


def normalise_property_columns(raw_line, filename):
    """
    Parse one indented property row.

    Important correction:
    A reference row such as this has only four meaningful columns:
        schema:Person.affiliation    affiliation    1..n    schema:Organization

    The previous version padded that row to five columns, then treated
    'schema:Organization' as a datatype rather than a target_class. That meant
    build_property_schema() never entered the target_class branch, so no oneOf
    was generated.
    """
    cols = raw_line.rstrip("\n").split("\t")

    # Remove the indentation column created by the leading tab.
    if cols and cols[0] == "":
        cols = cols[1:]

    cols = [c.strip() for c in cols]

    while len(cols) < 4:
        cols.append("")

    property_uri = cols[0]
    label = cols[1]
    cardinality = cols[2]

    target_class = None
    datatype = None
    format_name = None

    col4 = cols[3] if len(cols) > 3 else ""
    col5 = cols[4] if len(cols) > 4 else ""
    col6 = cols[5] if len(cols) > 5 else ""

    if len(cols) >= 6 and col6:
        # Explicit 6-column layout:
        # propertyURI, label, cardinality, targetClass, datatype, format
        target_class = col4 or None
        datatype = col5 or None
        format_name = col6 or None

        # Forgiving correction if the row was really the 5-column literal shape
        # but had an extra trailing tab/column.
        if is_json_type(target_class) and (is_format(datatype) or not datatype):
            format_name = datatype
            datatype = target_class
            target_class = None

    elif is_json_type(col4):
        # Literal layout:
        # propertyURI, label, cardinality, datatype, format
        datatype = col4 or None
        format_name = col5 or None

    elif col4:
        # Reference layout:
        # propertyURI, label, cardinality, targetClass
        target_class = col4

        # Optional support for rows that include metadata after the target class.
        datatype = col5 or None
        format_name = col6 or None

    else:
        # Fallback: no datatype or targetClass supplied.
        datatype = None
        format_name = col5 or None

    if format_name:
        format_name = format_name.lower()

    if format_name and format_name not in VALID_FORMATS:
        print(
            f"ISSUE: {filename} has an unrecognised format value "
            f"'{format_name}' for property '{property_uri}'. Ignoring it."
        )
        format_name = None

    return {
        "property_uri": property_uri,
        "label": label,
        "cardinality": cardinality,
        "target_class": target_class,
        "datatype": datatype,
        "format": format_name,
    }


def reference_def_name(target_class):
    return f"{target_class}Reference"


def make_reference_schema(target_class):
    """
    Build a lightweight reference schema for a target class.

    For schema:Organization, this validates an object that can reference an
    Organization using its identifier. Extra optional fields can be added here
    if you want the reference to carry display or relationship metadata.
    """
    if target_class == "schema:Organization":
        return {
            "title": "schema:OrganizationReference",
            "type": "object",
            "properties": {
                "identifier": {
                    "type": "string",
                    "format": "uri",
                    "rocrateProperty": "schema:Thing.identifier",
                },
                "legalName": {
                    "type": "string",
                    "rocrateProperty": "schema:Organization.legalName",
                },
                "roleName": {
                    "type": "string",
                    "rocrateProperty": "schema:Role.roleName",
                },
            },
            "required": ["identifier"],
            "additionalProperties": False,
        }

    return {
        "title": reference_def_name(target_class),
        "type": "object",
        "properties": {
            "identifier": {
                "type": "string",
                "format": "uri",
                "rocrateProperty": "schema:Thing.identifier",
            }
        },
        "required": ["identifier"],
        "additionalProperties": False,
    }


def build_property_schema(
    property_uri,
    label,
    cardinality,
    target_class=None,
    datatype=None,
    format_name=None,
):
    required, repeatable = parse_cardinality(cardinality)

    if target_class:
        property_schema = {
            "oneOf": [
                {
                    "$ref": f"#/$defs/{target_class}"
                },
                {
                    "$ref": f"#/$defs/{reference_def_name(target_class)}"
                },
            ],
            "rocrateProperty": property_uri,
        }
    else:
        property_schema = {
            "type": datatype_to_jsonschema(datatype),
            "rocrateProperty": property_uri,
        }
        if format_name:
            property_schema["format"] = format_name

    if repeatable:
        property_schema = {
            "type": "array",
            "items": property_schema,
        }

    return {
        "label": label,
        "schema": property_schema,
        "required": required,
    }


def build_class_schema(class_name, class_cardinality, properties):
    """Build JSON Schema definition for a class."""
    schema = {
        "title": class_name,
        "type": "object",
        "properties": {},
    }

    required_properties = []

    for prop in properties:
        result = build_property_schema(
            property_uri=prop["property_uri"],
            label=prop["label"],
            cardinality=prop["cardinality"],
            target_class=prop["target_class"],
            datatype=prop["datatype"],
            format_name=prop["format"],
        )
        schema["properties"][result["label"]] = result["schema"]
        if result["required"]:
            required_properties.append(result["label"])

    if required_properties:
        schema["required"] = required_properties

    if class_cardinality:
        schema["appnCardinality"] = class_cardinality

    return schema


def parse_schema_file(filename):
    """Parse APPN tab-delimited schema specification."""
    definitions = {}
    referenced_classes = set()

    current_class = None
    current_class_cardinality = None
    current_properties = []

    def finish_current_class():
        if current_class is None:
            return
        definitions[current_class] = build_class_schema(
            current_class,
            current_class_cardinality,
            current_properties,
        )
        for prop in current_properties:
            if prop.get("target_class"):
                referenced_classes.add(prop["target_class"])

    with open(filename, encoding="utf-8") as f:
        for raw_line in f:
            if not raw_line.strip():
                continue

            if not raw_line.startswith("\t"):
                finish_current_class()

                cols = raw_line.rstrip("\n").split("\t")
                current_class = cols[0].strip()
                current_class_cardinality = None

                non_empty = [c.strip() for c in cols if c.strip()]
                if len(non_empty) > 1:
                    current_class_cardinality = non_empty[-1]

                current_properties = []
            else:
                current_properties.append(
                    normalise_property_columns(raw_line, filename)
                )

    finish_current_class()

    # Add reusable reference definitions for every referenced target class.
    # This ensures the oneOf branch points to an actual $defs entry.
    for target_class in sorted(referenced_classes):
        ref_name = reference_def_name(target_class)
        if ref_name not in definitions:
            definitions[ref_name] = make_reference_schema(target_class)

    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$defs": definitions,
    }



def main():
    # input_file = "person_organization_tabdelim_appn.txt"
    input_file = "appn_schema_tabdelim_appn_hand_edited.txt"
    schema = parse_schema_file(input_file)
    output_file = Path(input_file).stem + ".json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2)

    print(f"Wrote {output_file}")


if __name__ == "__main__":
    main()
