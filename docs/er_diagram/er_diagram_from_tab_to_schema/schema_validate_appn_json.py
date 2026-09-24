#!/usr/bin/env python3
"""Validate APPN example data against an APPN JSON Schema."""

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


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
) -> dict[str, Any\]:
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
) -> list[Any\]:
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

    complete_schema = load_json(
        schema_path
    )

    instance = load_json(
        data_path
    )

    if args.template:
        instance = unwrap_template_value(
            instance
        )

    validation_schema = (
        build_definition_schema(
            complete_schema,
            args.definition,
        )
    )

    errors = validate_instance(
        instance,
        validation_schema,
    )

    if not errors:
        print(
            f"VALID: {data_path} satisfies "
            f"{args.definition}"
        )

        return 0

    print(
        f"INVALID: {data_path} has "
        f"{len(errors)} validation error(s) "
        f"against {args.definition}:"
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

    return 1


if __name__ == "__main__":
    sys.exit(main())