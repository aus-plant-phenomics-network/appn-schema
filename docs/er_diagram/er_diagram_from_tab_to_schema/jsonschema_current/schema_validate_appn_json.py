#!/usr/bin/env python3
"""
Validate APPN example data against an APPN JSON Schema.

Usage:

> python schema_validate_appn_json.py  -h

Validate an APPN JSON object against a definition in an APPN JSON Schema.

positional arguments:
  schema      Path to the APPN JSON Schema
  data        Path to the JSON data document
  definition  An (optional) class defintion to validate against, for example appn:Study
              If not present then a list of classes is tested.

options:
  -h, --help  show this help message and exit
  --template  Remove cardinality wrappers and trailing required-field asterisks before validation

e.g.
python schema_validate_appn_json.py  appn_booking_schema.json booking_form_filled_v2.json "appn:Study"





"""

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any
import logging

from jsonschema import Draft202012Validator, FormatChecker

CLASS_LIST = [
"appn:Investigation",
"appn:Study",
"appn:Person",
"appn:SpatialLocation",
"appn:GrowthFacility",
"appn:Sensor",
"appn:BiologicalMaterial",
"appn:MaterialSource",
"schema:Organization",
"schema:Grant"
]

def load_json(path: Path) -> Any:
    """Load a JSON document."""
    with path.open(
        "r",
        encoding="utf-8",
    ) as handle:
        return json.load(handle)


def unwrap_template_value(value: Any) -> Any:
    """
    Convert a cardinality-annotated template value into plain JSON data.

    For example:

        {
            "cardinality": "1..1",
            "value": "<string> *"
        }

    becomes:

        "<string>"
    """
    if isinstance(value, dict):
        if (
            "cardinality" in value
            and "value" in value
            and set(value).issubset(
                {
                    "cardinality",
                    "value",
                }
            )
        ):
            return unwrap_template_value(
                value["value"]
            )

        return {
            key: unwrap_template_value(
                child_value
            )
            for key, child_value
            in value.items()
        }

    if isinstance(value, list):
        return [
            unwrap_template_value(item)
            for item in value
        ]

    if isinstance(value, str):
        # Remove the required-field marker from
        # the end of example values.
        if value.endswith(" *"):
            return value[:-2]

        if value == "*":
            return ""

    return value


def build_definition_schema(
    complete_schema: dict[str, Any],
    definition_name: str,
) -> dict[str, Any]:
    """
    Build a validation schema for one definition while preserving the
    complete $defs catalogue for local reference resolution.
    """
    definitions = (
        complete_schema.get("$defs")
        or complete_schema.get("definitions")
    )

    if not isinstance(definitions, dict):
        raise ValueError(
            "The schema does not contain "
            "$defs or definitions."
        )

    if definition_name not in definitions:
        available = ", ".join(
            sorted(definitions)
        )

        raise KeyError(
            f"Unknown definition "
            f"{definition_name!r}. "
            f"Available definitions: "
            f"{available}"
        )

    validation_schema = copy.deepcopy(
        complete_schema
    )

    # Point the validation root to the selected
    # definition while preserving every $defs entry.
    if "$defs" in complete_schema:
        validation_schema["$ref"] = (
            f"#/$defs/{definition_name}"
        )
    else:
        validation_schema["$ref"] = (
            f"#/definitions/{definition_name}"
        )
        
    # print(json.dumps(validation_schema, indent=2))

    return validation_schema


def format_error_path(
    error_path: Any,
) -> str:
    """Turn a validation error path into a readable JSON-style path."""
    parts = ["$"]

    for part in error_path:
        if isinstance(part, int):
            parts.append(
                f"[{part}]"
            )
        else:
            parts.append(
                f".{part}"
            )

    return "".join(parts)


def validate_instance(
    instance: Any,
    validation_schema: dict[str, Any],
) -> list[Any]:
    """Return all validation errors in stable path order."""
    Draft202012Validator.check_schema(
        validation_schema
    )

    validator = Draft202012Validator(
        validation_schema,
        format_checker=FormatChecker(),
    )

    return sorted(
        validator.iter_errors(instance),
        key=lambda error: (
            list(error.absolute_path),
            error.message,
        ),
    )



def test_and_print_instance(data_path, validation_schema, instance, classdef: str):
    # Load the subset of the data file that corresponds to the class definition being tested
    try:
        instance = instance[classdef]
    except KeyError  as e:
        logging.error("The class definition requested is not present in the data file %s: \nerror: %s",data_path, e)
        # sys.exit(-1)

    errors = validate_instance(
        instance,
        validation_schema,
    )

    if not errors:
        print(
            f"VALID: {data_path} satisfies "
            f"{classdef}"
        )
        # return 0
        
    else:
        print(
            f"INVALID: {data_path} has "
            f"{len(errors)} validation error(s) "
            f"against {classdef}:"
        )

        for error_number, error in enumerate(
            errors,
            start=1,
        ):
            instance_path = format_error_path(
                error.absolute_path
            )

            schema_path_text = format_error_path(
                error.absolute_schema_path
            )

            print()
            print(
                f"{error_number}. "
                f"Instance path: {instance_path}"
            )
            print(
                f"   Error: {error.message}"
            )
            print(
                f"   Schema path: "
                f"{schema_path_text}"
            )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate an APPN JSON object "
            "against a definition in an "
            "APPN JSON Schema."
        )
    )

    parser.add_argument(
        "schema",
        help="Path to the APPN JSON Schema",
    )

    parser.add_argument(
        "data",
        help="Path to the JSON data document",
    )

    parser.add_argument(
        "definition",
        nargs="?",
        help=(
            "Definition to validate against, "
            "for example appn:Study"
        ),
    )

    parser.add_argument(
        "--template",
        action="store_true",
        help=(
            "Remove cardinality wrappers and "
            "trailing required-field asterisks "
            "before validation"
        ),
    )

    args = parser.parse_args()

    schema_path = Path(args.schema)
    data_path = Path(args.data)


    try:
        complete_schema = load_json(schema_path)
    except FileNotFoundError:
        logging.error("JSON file not found: %s", schema_path)
    except json.JSONDecodeError as e:
        logging.error(
            "Invalid JSON in file: %s (line %s, column %s): %s",
            schema_path,
            e.lineno,
            e.colno,
            e.msg,
        )
        sys.exit(-1)
    except UnicodeDecodeError as e:
        logging.error("Encoding error reading %s: %s", schema_path, e)
    except PermissionError:
        logging.error("Permission denied reading %s", schema_path)
    except Exception as e:
        logging.exception("Unexpected error loading JSON from %s: %s", schema_path, e)


    try:
        instance = load_json(data_path)
    except FileNotFoundError:
        logging.error("JSON file not found: %s", data_path)
    except json.JSONDecodeError as e:
        logging.error(
            "Invalid JSON in file: %s (line %s, column %s): %s",
            data_path,
            e.lineno,
            e.colno,
            e.msg,
        )
        sys.exit(-1)
    except UnicodeDecodeError as e:
        logging.error("Encoding error reading %s: %s", data_path, e)
    except PermissionError:
        logging.error("Permission denied reading %s", data_path)
    except Exception as e:
        logging.exception("Unexpected error loading JSON from %s: %s", data_path, e)


    if args.template:
        instance = unwrap_template_value(
            instance
        )

    # Do a single validation if a specific class was 
    # put on the command line
    if args.definition:
        validation_schema = (
            build_definition_schema(
                complete_schema,
                args.definition,
            )
        )
        test_and_print_instance(data_path, validation_schema, instance, classdef)
    else:
        # Go through and test each of a standard 
        # list of classes
        for classdef in CLASS_LIST:
            validation_schema = (
            build_definition_schema(
                complete_schema,
                classdef,
                )
            )
            test_and_print_instance(data_path, validation_schema, instance, classdef)
            
    return 1


if __name__ == "__main__":
    sys.exit(main())