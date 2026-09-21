#!/usr/bin/env python3
"""Generate an editable example JSON document including field cardinalities."""

import argparse
import copy
import json
from pathlib import Path
from typing import Any

PLACEHOLDERS = {
    "string": "<string>",
    "integer": 0,
    "number": 0.0,
    "boolean": False,
    "null": None,
}

FORMAT_PLACEHOLDERS = {
    "date": "YYYY-MM-DD",
    "date-time": "YYYY-MM-DDTHH:MM:SSZ",
    "time": "HH:MM:SS",
    "email": "name@example.org",
    "uri": "https://example.org/resource",
    "uri-reference": "https://example.org/resource",
    "uuid": "00000000-0000-0000-0000-000000000000",
    "hostname": "example.org",
    "ipv4": "192.0.2.1",
    "ipv6": "2001:db8::1",
}

def add_required_marker(
    value: Any,
    required: bool,
) -> Any:
    """
    Add an asterisk to the example value of a required field.

    String placeholders have the marker appended directly. For non-string
    scalar values, the value is converted to a display string so the marker
    can be included.

    Arrays and objects retain their structure, with the marker applied to
    their first generated example value.
    """
    if not required:
        return value

    if isinstance(value, str):
        if value[-1] != '*':
            return f"{value} *"
        else:
            return value

    if value is None:
        return "<null> *"

    if isinstance(value, bool):
        return f"{str(value).lower()} *"

    if isinstance(value, (int, float)):
        return f"{value} *"

    if isinstance(value, list):
        if not value:
            return ["*"]

        marked_value = copy.deepcopy(value)
        marked_value[0] = add_required_marker(
            marked_value[0],
            True,
        )
        return marked_value

    if isinstance(value, dict):
        if not value:
            return {"required": "*"}

        marked_value = copy.deepcopy(value)
        first_property = next(iter(marked_value))

        # Handle values wrapped with cardinality metadata.
        if (
            isinstance(marked_value[first_property], dict)
            and "value" in marked_value[first_property]
        ):
            marked_value[first_property]["value"] = (
                add_required_marker(
                    marked_value[first_property]["value"],
                    True,
                )
            )
        else:
            marked_value[first_property] = (
                add_required_marker(
                    marked_value[first_property],
                    True,
                )
            )

        return marked_value

    return f"{value} *"
    
def resolve_local_ref(ref: str, root_schema: dict[str, Any]) -> Any:
    """Resolve a local JSON Pointer such as #/$defs/appn:Study."""
    if not ref.startswith("#"):
        raise ValueError(f"External $ref is not supported: {ref}")
    if ref == "#":
        return root_schema

    current: Any = root_schema
    for part in ref.removeprefix("#/").split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        current = current[part]
    return current


def merge_schemas(schemas: list[dict[str, Any]]) -> dict[str, Any]:
    """Perform a practical merge for example generation."""
    result: dict[str, Any] = {}
    for schema in schemas:
        for key, value in schema.items():
            if key == "properties":
                result.setdefault("properties", {})
                result["properties"].update(copy.deepcopy(value))
            elif key == "required":
                result.setdefault("required", [])
                result["required"] = list(
                    dict.fromkeys(result["required"] + value)
                )
            elif key == "allOf":
                result = merge_schemas([result, merge_schemas(value)])
            else:
                result[key] = copy.deepcopy(value)
    return result


def infer_schema_type(schema: Any) -> str | None:
    """Infer type where JSON Schema does not explicitly provide one."""
    if not isinstance(schema, dict):
        return None

    declared_type = schema.get("type")
    if isinstance(declared_type, list):
        non_null = [item for item in declared_type if item != "null"]
        return non_null[0] if non_null else "null"
    if isinstance(declared_type, str):
        return declared_type
    if "properties" in schema or "additionalProperties" in schema:
        return "object"
    if "items" in schema or "prefixItems" in schema:
        return "array"
    return None


def field_cardinality(property_schema: Any, required: bool) -> str:
    """Infer field cardinality from required, minItems, and maxItems."""
    if infer_schema_type(property_schema) == "array":
        minimum = property_schema.get("minItems")
        maximum = property_schema.get("maxItems")
        lower = minimum if isinstance(minimum, int) else (1 if required else 0)
        upper = str(maximum) if isinstance(maximum, int) else "n"
        return f"{lower}..{upper}"
    return "1..1" if required else "0..1"


def composition_branch_score(schema: dict[str, Any]) -> tuple[int, int]:
    """Prefer compact Reference branches over recursively expanded entities."""
    title = str(schema.get("title", ""))
    return (int(title.endswith("Reference")), -len(schema.get("properties", {})))


def choose_composition_branch(
    branches: list[Any], root_schema: dict[str, Any]
) -> dict[str, Any]:
    """Choose a practical oneOf/anyOf branch for example generation."""
    resolved: list[dict[str, Any]] = []
    for branch in branches:
        if not isinstance(branch, dict):
            continue
        if "$ref" in branch:
            referred = resolve_local_ref(branch["$ref"], root_schema)
            siblings = {key: value for key, value in branch.items() if key != "$ref"}
            branch = merge_schemas([referred, siblings])
        resolved.append(branch)
    return max(resolved, key=composition_branch_score) if resolved else {}


def generate_placeholder(
    schema: Any,
    root_schema: dict[str, Any],
    *,
    include_optional: bool = True,
    array_items: int = 1,
    include_cardinality: bool = True,
    exclude_foreign_keys: bool = False,
    ref_stack: frozenset[str] = frozenset(),
) -> Any:
    """Generate an example value from a JSON Schema definition."""
    if schema is True:
        return "<value>"
    if schema is False:
        return None
    if not isinstance(schema, dict):
        return "<value>"

    if "$ref" in schema:
        ref = schema["$ref"]
        if ref in ref_stack:
            return {"identifier": "https://example.org/resource"}
        referred = resolve_local_ref(ref, root_schema)
        siblings = {key: value for key, value in schema.items() if key != "$ref"}
        return generate_placeholder(
            merge_schemas([referred, siblings]),
            root_schema,
            include_optional=include_optional,
            array_items=array_items,
            include_cardinality=include_cardinality,
            exclude_foreign_keys=exclude_foreign_keys,
            ref_stack=ref_stack | {ref},
        )

    if "allOf" in schema:
        siblings = {key: value for key, value in schema.items() if key != "allOf"}
        schema = merge_schemas([siblings, *schema["allOf"]])

    for keyword in ("oneOf", "anyOf"):
        if schema.get(keyword):
            selected = choose_composition_branch(schema[keyword], root_schema)
            siblings = {key: value for key, value in schema.items() if key != keyword}
            schema = merge_schemas([siblings, selected])
            break

    if "const" in schema:
        return copy.deepcopy(schema["const"])
    if "default" in schema:
        return copy.deepcopy(schema["default"])
    if schema.get("examples"):
        return copy.deepcopy(schema["examples"][0])
    if schema.get("enum"):
        return copy.deepcopy(schema["enum"][0])

    schema_type = infer_schema_type(schema)

    if schema_type == "object":
        result: dict[str, Any] = {}
        required_properties = set(schema.get("required", []))
        foreign_key_properties = set(schema.get("x-foreign-key", []))

        for property_name, property_schema in schema.get("properties", {}).items():
            # When requested, omit every property named by this class's
            # x-foreign-key extension, even when that property is required.
            if exclude_foreign_keys and property_name in foreign_key_properties:
                continue

            is_required = property_name in required_properties
            if not include_optional and not is_required:
                continue
                
            value = generate_placeholder(
                property_schema,
                root_schema,
                include_optional=include_optional,
                array_items=array_items,
                include_cardinality=include_cardinality,
                exclude_foreign_keys=exclude_foreign_keys,
                ref_stack=ref_stack,
            )
            
            # Apply the required-field marker before formatting the output.
            # This ensures it is present with or without cardinality metadata.
            if include_optional:
                value = add_required_marker(
                    value,
                    is_required,
                )

            if include_cardinality:
                result[property_name] = {
                    "cardinality": field_cardinality(property_schema, is_required),
                    "value": value,
                }
            else:
                result[property_name] = value

        return result

    if schema_type == "array":
        if "prefixItems" in schema:
            return [
                generate_placeholder(
                    item,
                    root_schema,
                    include_optional=include_optional,
                    array_items=array_items,
                    include_cardinality=include_cardinality,
                    exclude_foreign_keys=exclude_foreign_keys,
                    ref_stack=ref_stack,
                )
                for item in schema["prefixItems"]
            ]

        item_schema = schema.get("items", {})
        if item_schema is False:
            return []

        count = max(int(schema.get("minItems", array_items)), 0)
        return [
            generate_placeholder(
                item_schema,
                root_schema,
                include_optional=include_optional,
                array_items=array_items,
                include_cardinality=include_cardinality,
                exclude_foreign_keys=exclude_foreign_keys,
                ref_stack=ref_stack,
            )
            for _ in range(count)
        ]

    if schema_type == "string":
        return FORMAT_PLACEHOLDERS.get(schema.get("format"), PLACEHOLDERS["string"])
    if schema_type in PLACEHOLDERS:
        return copy.deepcopy(PLACEHOLDERS[schema_type])
    return "<value>"


def apply_entity_cardinality(value: Any, cardinality: str, array_items: int) -> Any:
    """Wrap repeated APPN entities in an array."""
    if "..n" in cardinality:
        return [copy.deepcopy(value) for _ in range(max(array_items, 1))]
    return value


def generate_document(
    schema: dict[str, Any],
    *,
    include_optional: bool,
    array_items: int,
    include_cardinality: bool,
    exclude_foreign_keys: bool,
) -> Any:
    """Generate from a conventional root or an APPN $defs catalogue."""
    root_keywords = {"type", "properties", "$ref", "allOf", "oneOf", "anyOf"}
    if root_keywords.intersection(schema):
        return generate_placeholder(
            schema,
            schema,
            include_optional=include_optional,
            array_items=array_items,
            include_cardinality=include_cardinality,
            exclude_foreign_keys=exclude_foreign_keys,
        )

    definitions = schema.get("$defs") or schema.get("definitions")
    if not isinstance(definitions, dict):
        raise ValueError("Schema has no instance root and no $defs/definitions")

    document: dict[str, Any] = {}
    defs_keyword = "$defs" if "$defs" in schema else "definitions"

    for name, definition in definitions.items():
        if name.endswith("Reference") or not isinstance(definition, dict):
            continue

        entity_cardinality = str(definition.get("appnCardinality", "1..1"))
        entity_value = generate_placeholder(
            definition,
            schema,
            include_optional=include_optional,
            array_items=array_items,
            include_cardinality=include_cardinality,
            exclude_foreign_keys=exclude_foreign_keys,
            ref_stack=frozenset({f"#/{defs_keyword}/{name}"}),
        )
        entity_value = apply_entity_cardinality(
            entity_value, entity_cardinality, array_items
        )

        if include_cardinality:
            document[name] = {
                "cardinality": entity_cardinality,
                "value": entity_value,
            }
        else:
            document[name] = entity_value

    return document


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create an example JSON document with field cardinalities."
    )
    parser.add_argument("schema", help="Path to the JSON Schema")
    parser.add_argument("output", help="Path for the generated JSON document")
    parser.add_argument(
        "--required-only",
        action="store_true",
        help="Include only required object properties",
    )
    parser.add_argument(
        "--array-items",
        type=int,
        default=1,
        help="Placeholder items per array and repeated entity (default: 1)",
    )
    parser.add_argument(
        "--no-cardinality",
        action="store_true",
        help="Output plain values without cardinality metadata",
    )
    parser.add_argument(
        "--no-foriegn-key",
        "--no-foreign-key",
        dest="no_foreign_key",
        action="store_true",
        help=(
            "Exclude properties listed in each class's x-foreign-key array. "
            "Both spellings are accepted for compatibility."
        ),
    )
    args = parser.parse_args()

    with Path(args.schema).open("r", encoding="utf-8") as handle:
        schema = json.load(handle)

    generated = generate_document(
        schema,
        include_optional=not args.required_only,
        array_items=max(args.array_items, 0),
        include_cardinality=not args.no_cardinality,
        exclude_foreign_keys=args.no_foreign_key,
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(generated, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    print(f"Generated example JSON: {output_path}")


if __name__ == "__main__":
    main()
