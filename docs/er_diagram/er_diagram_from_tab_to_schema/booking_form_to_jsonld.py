from __future__ import annotations

"""
CoPilot request:
I would like a Python processing function that takes the content of a file such as 
the one uploaded and translates it into json-ld. It will take any field that has 
'identifier' in its name (e.g. "personIdentifier" and "organizationIdentifier") and 
use that as the "@id" of the json-ld; It will take the class type from the file 
(e.g. "appn:Study", "appn:Person" etc.)  and use it as the "@type" field; any empty 
string field values will not be included and a class with all empty strings will not 
be added to the json-ld; A field that contains a dict that includes the  "identifier" 
field should reference the value as "@id" : "value";
"""

"""
Usage:
jsonld = booking_form_to_jsonld(
    "booking_form_filled.json",
    context={
        "appn": "https://schema.plantphenomics.org.au/",
        "schema": "https://schema.org/",
    },
)
# Save converted document to jsonld file
with open("booking_form_filled.jsonld", "w", encoding="utf-8") as file:
    json.dump(
        jsonld,
        file,
        ensure_ascii=False,
        indent=2,
    )
"""

import json
from pathlib import Path
from typing import Any


def booking_form_to_jsonld(
    source: str | Path | dict[str, Any],
    *,
    context: dict[str, Any] | str | None = None,
) -> dict[str, Any]:
    """
    Convert an APPN-style booking-form JSON document into JSON-LD.

    Expected input structure:

        {
            "appn:Study": {
                "studyIdentifier": "study-123",
                "studyTitle": "Example study"
            },
            "appn:Person": [
                {
                    "personIdentifier": "https://example.org/person/1",
                    "givenName": "Example"
                }
            ]
        }

    Conversion rules:
    1. Each top-level key becomes the object's "@type".
    2. A non-empty scalar field whose name contains "identifier"
       becomes the object's "@id".
    3. A nested dictionary containing an "identifier" field becomes:
           {"@id": "<identifier value>"}
    4. Empty strings, empty lists, empty dictionaries, and null values
       are omitted.
    5. A class instance containing no meaningful values is omitted.
    6. Multiple instances under the same class are supported.

    Args:
        source:
            A dictionary, or a path to a valid JSON file.
        context:
            Optional JSON-LD context. This may be a context dictionary
            or a URL string.

    Returns:
        A JSON-LD document containing an "@graph" array.

    Raises:
        ValueError:
            If an object contains multiple conflicting identifier fields,
            or if an identifier field has an unsupported value.
        TypeError:
            If the input structure is not supported.
        json.JSONDecodeError:
            If a source file does not contain valid JSON.
    """
    if isinstance(source, (str, Path)):
        with Path(source).open("r", encoding="utf-8") as file:
            source_data = json.load(file)
    elif isinstance(source, dict):
        source_data = source
    else:
        raise TypeError("source must be a dictionary or a JSON file path")

    if not isinstance(source_data, dict):
        raise TypeError("The root of the input document must be an object")

    graph: list[dict[str, Any]] = []

    for class_type, class_content in source_data.items():
        if isinstance(class_content, dict):
            instances = [class_content]
        elif isinstance(class_content, list):
            instances = class_content
        else:
            raise TypeError(
                f"Class {class_type!r} must contain an object or a list "
                f"of objects, not {type(class_content).__name__}"
            )

        for instance in instances:
            if not isinstance(instance, dict):
                raise TypeError(
                    f"Each {class_type!r} instance must be an object, "
                    f"not {type(instance).__name__}"
                )

            converted = _convert_entity(instance, class_type)

            if converted is not None:
                graph.append(converted)

    document: dict[str, Any] = {}

    if context is not None:
        document["@context"] = context

    document["@graph"] = graph
    return document


def _convert_entity(
    entity: dict[str, Any],
    class_type: str,
) -> dict[str, Any] | None:
    """
    Convert one class instance into a JSON-LD graph node.
    """
    output: dict[str, Any] = {"@type": class_type}
    identifiers: list[tuple[str, str]] = []

    for field_name, raw_value in entity.items():
        # A scalar identifier-named field identifies this entity.
        if _is_identifier_field(field_name) and not isinstance(
            raw_value, (dict, list)
        ):
            identifier = _clean_identifier(raw_value)

            if identifier is not None:
                identifiers.append((field_name, identifier))

            continue

        converted_value = _convert_value(raw_value)

        if not _is_empty(converted_value):
            output[field_name] = converted_value

    if identifiers:
        distinct_identifiers = {
            identifier for _, identifier in identifiers
        }

        if len(distinct_identifiers) > 1:
            details = ", ".join(
                f"{field}={identifier!r}"
                for field, identifier in identifiers
            )
            raise ValueError(
                "An entity has multiple conflicting identifier fields: "
                f"{details}"
            )

        output["@id"] = identifiers[0][1]

    # @type by itself is not considered meaningful class content.
    if set(output) == {"@type"}:
        return None

    return output


def _convert_value(value: Any) -> Any:
    """
    Recursively convert a property value.

    A dictionary that contains a usable field named exactly "identifier"
    is treated as a JSON-LD reference. Other dictionaries are cleaned
    recursively.
    """
    if value is None:
        return None

    if isinstance(value, str):
        stripped = value.strip()
        return stripped if stripped else None

    if isinstance(value, list):
        converted_items = [
            converted
            for item in value
            if not _is_empty(converted := _convert_value(item))
        ]
        return converted_items or None

    if isinstance(value, dict):
        reference_identifier = _find_reference_identifier(value)

        if reference_identifier is not None:
            return {"@id": reference_identifier}

        converted_dict: dict[str, Any] = {}

        for field_name, field_value in value.items():
            converted_value = _convert_value(field_value)

            if not _is_empty(converted_value):
                converted_dict[field_name] = converted_value

        return converted_dict or None

    # Keep meaningful numbers and booleans, including 0 and False.
    return value


def _find_reference_identifier(value: dict[str, Any]) -> str | None:
    """
    Find an exact, case-insensitive 'identifier' property in a nested dict.
    """
    for field_name, field_value in value.items():
        if field_name.casefold() == "identifier":
            return _clean_identifier(field_value)

    return None


def _clean_identifier(value: Any) -> str | None:
    """
    Return a cleaned scalar identifier, or None for an empty identifier.
    """
    if value is None:
        return None

    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned if cleaned else None

    if isinstance(value, (int, float)):
        return str(value)

    if isinstance(value, bool):
        return str(value).lower()

    raise ValueError(
        "An identifier must be a string, number, or boolean, "
        f"not {type(value).__name__}"
    )


def _is_identifier_field(field_name: str) -> bool:
    """
    Match fields such as studyIdentifier, personIdentifier, and
    organizationIdentifier, case-insensitively.
    """
    return "identifier" in field_name.casefold()


def _is_empty(value: Any) -> bool:
    """
    Recognize recursively cleaned empty values.

    Numeric zero and False are intentionally retained.
    """
    return value is None or value == "" or value == [] or value == {}