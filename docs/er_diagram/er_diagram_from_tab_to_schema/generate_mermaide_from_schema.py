#!/usr/bin/env python3

import json
import re
import sys
from pathlib import Path

REFERENCE_MAP = {
    "schema:PersonReference": "schema:Person",
    "schema:OrganizationReference": "schema:Organization",
    "appn:InvestigationReference": "appn:Investigation",
    "schema:PlaceReference": "schema:Place",
    "appn:GrowthFacilityReference": "appn:GrowthFacility",
    "appn:BiologicalMaterialReference": "appn:BiologicalMaterial",
    "appn:DeploymentReference": "appn:Deployment",
    "appn:MaterialSourceReference": "appn:MaterialSource",
    "appn:SpatialLocationReference": "appn:SpatialLocation",
}


def sanitize_name(name):
    """
    Mermaid entity names cannot contain ':' or other special chars.
    """
    return re.sub(r"[^A-Za-z0-9_]", "_", name)

def get_property_relationship_cardinality(prop_name, prop_def, required):
    """
    Determine source-side cardinality from property structure.

    Returns:
        source_card, target_card
    """

    is_required = prop_name in required

    # Array -> many targets
    if prop_def.get("type") == "array":

        if is_required:
            source_card = "|{"  # one or many
        else:
            source_card = "o{"  # zero or many

        target_card = "||"
        return source_card, target_card

    # Direct object reference
    if "$ref" in prop_def or "oneOf" in prop_def:

        if is_required:
            source_card = "||"  # exactly one
        else:
            source_card = "o|"  # zero or one

        target_card = "||"
        return source_card, target_card

    return None, None
    
def cardinality_to_mermaid(card):
    """
    Convert appn cardinality to Mermaid cardinality.
    """
    mapping = {
        "0..1": "o|",
        "1..1": "||",
        "0..n": "o{",
        "1..n": "|{",
    }
    return mapping.get(card, "o{")


def extract_refs(node):
    """
    Recursively find all $ref values.
    """
    refs = []

    if isinstance(node, dict):
        if "$ref" in node:
            refs.append(node["$ref"])

        for value in node.values():
            refs.extend(extract_refs(value))

    elif isinstance(node, list):
        for item in node:
            refs.extend(extract_refs(item))

    return refs


def ref_to_entity(ref):
    """
    Convert '#/$defs/schema:Organization'
    to 'schema:Organization'
    """
    if ref.startswith("#/$defs/"):
        return ref.split("/")[-1]
    return None


def build_mermaid(schema):
    defs = schema.get("$defs", {})

    entities = []
    relationships = []

    # Build entities
    for entity_name, entity_def in defs.items():

        fields = []
        required = set(entity_def.get("required", []))

        for prop_name, prop_def in entity_def.get("properties", {}).items():

            ptype = prop_def.get("type", "object")

            if prop_name in required:
                fields.append(f"    {ptype} {prop_name} PK")
            else:
                fields.append(f"    {ptype} {prop_name}")

        entity_id = sanitize_name(entity_name)

        block = [
            f"    {entity_id} {{"
        ]
        block.extend(fields)
        block.append("    }")

        # The jsonschema defines 'reference' versions of classes that 
        # do not need shown as entities or added with relationships
        if not entity_id.endswith("Reference") and not entity_id.endswith("Identifier"):
            entities.append("\n".join(block))

    # Build relationships
    for source_name, source_def in defs.items():

        source_id = sanitize_name(source_name)
        required = set(source_def.get("required", []))

        for prop_name, prop_def in source_def.get("properties", {}).items():

            refs = extract_refs(prop_def)

            if not refs:
                continue

            source_card, target_card = (
                get_property_relationship_cardinality(
                    prop_name,
                    prop_def,
                    required
                )
            )

            for ref in refs:

                target_name = ref_to_entity(ref)
                target_name = REFERENCE_MAP.get(target_name, target_name)

                if not target_name:
                    continue

                target_id = sanitize_name(target_name)
                
                # The jsonschema defines 'reference' versions of classes that 
                # do not need shown as entities or added with relationships
                if not target_id.endswith("Reference"):
                    
                    relationships.append(
                        (
                            target_id,
                            source_id,
                            source_card,
                            target_card,
                            prop_name,
                        )
                    )
                    
                    print(f"relationships[-1] : {relationships[-1]}")
                    print("")

    # Remove duplicates
    unique_relationships = []
    seen = set()

    for rel in relationships:
        key = tuple(rel)

        if key not in seen:
            seen.add(key)
            unique_relationships.append(rel)

    lines = ["erDiagram", ""]

    lines.extend(entities)
    lines.append("")

    for src, dst, src_card, dst_card, label in unique_relationships:
        lines.append(
            f"    {src} {src_card}--{dst_card} {dst} : {label}"
        )

    return "\n".join(lines)
    

LEGEND_TEST = """
<h3>Legend</h3>
<h3>Relationship Cardinality - E2 relationship with E1</h3>

<pre class="mermaid">
erDiagram
    E1 ||--|| E2 : "Exactly one"
    E1 o|--|| E2 : "Zero or one"
    E1 |{--|| E2 : "One or more"
    E1 o{--|| E2 : "Zero or more"
</pre>

<ul>
  <li><strong>PK</strong> = Primary Key</li>
  <li><strong>FK</strong> = Foreign Key</li>
</ul>

"""

def main():
    if len(sys.argv) != 2:
        print(
            f"Usage: {Path(sys.argv[0]).name} schema.json",
            file=sys.stderr,
        )
        sys.exit(1)

    schema_file = sys.argv[1]

    with open(schema_file, "r", encoding="utf-8") as f:
        schema = json.load(f)

    mermaid_text = build_mermaid(schema)
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
<script type="module">
import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
mermaid.initialize({{ startOnLoad: true }});
</script>
</head>
<body>

{LEGEND_TEST}

<pre class="mermaid">
{mermaid_text}
</pre>


</body>
</html>
    """

    with open("erd.html", "w") as f:
        f.write(html)


if __name__ == "__main__":
    main()