### Scripts used to convert Excel schema definitions to ER diagrams

These scripts help with the semi-automated production of the ER diagram from the booking sheet fields that are defined in:
  
  [APPN Booking sheet metadata mapping 2026 RDv1](https://uao365.sharepoint.com/:x:/r/sites/PROVOST-CS-SAFW-APPN/All%20APPN/Coordinating%20Data%20Collection/Central%20Team%20Notes/APPN%20Booking%20sheet%20metadata%20mapping%202026%20RDv1.xlsx?d=wb63090fc0dbf4c939cd41121d24fa394&csf=1&web=1&e=xwUna3)
  

The above spreadsheet was copied and then extended as filename named ```appn_schema_tabdelim_appn_hand_edited.txt```. This file has extra columns and the relationships between classes are added to each class definition. 

The edited file will be the input file to the following script (hand modified to add the filename ```appn_schema_tabdelim_appn_hand_edited.txt```)- 

```python
python convert_booking_def_to_jsonschema.py

```

The above script outputs a Python library```jsonschema``` file named  ```appn_schema_tabdelim_appn.json```

The schema file is then reprocessed to output a Mermaid ER diagram

```python
python generate_mermaide_from_schema.py appn_schema_tabdelim_appn_hand_edited.json
```
The above code produces a file named ```index.html```, that can be loaded into a web browser for interactive display.

  
#### Schema to JSON form fields

The script `schema_to_default_json_with_cardinality.py` uses the `jsonschema` document created by `convert_booking_def_to_jsonschema.py`. The script is used to create JSON documents with fields named by the APPN schema class fields and values used to hold booking information data.

##### Usage example

```bash
usage: schema_to_default_json_with_cardinality.py [-h] [--required-only] [--array-items ARRAY_ITEMS] [--no-cardinality] [--no-foriegn-key] schema output

Create an example JSON document with field cardinalities.

positional arguments:
  schema                Path to the JSON Schema
  output                Path for the generated JSON document

options:
  -h, --help            show this help message and exit
  --required-only       Include only required object properties
  --array-items ARRAY_ITEMS
                        Placeholder items per array and repeated entity (default: 1)
  --no-cardinality      Output plain values without cardinality metadata
  --no-foriegn-key, --no-foreign-key
                        Exclude properties listed in each class's x-foreign-key array. Both spellings are accepted for compatibility.
```


Example output:
```json
# python schema_to_default_json_with_cardinality.py --no-foreign-key --no-cardinality --array-items 1 appn_schema_tabdelim_appn_hand_edited.json booking_form_data_nfk_req.json

{
  "appn:Investigation": {
    "Investigation.identifier": "https://example.org/resource",
    "Investigation.name": "<string>",
    "Investigation.description": "<string>"
  },
  "appn:Study": {
    "Study.identifier": "https://example.org/resource",
    "Study.alternateName": "<string> *",
    "Study.name": "<string> *",
    "Study.description": "<string>",
    "Study.additionalType": "<string>"
  },
  "appn:Person": [
    {
      "Person.givenName": "<string> *",
      "Person.familyName": "<string> *",
      "Person.identifier": "https://example.org/resource",
      "Person.email": [
        "name@example.org"
      ],
      "Person.jobTitle": "<string>",
      "Person.roleName": "<string> *"
    }
  ],
  "schema:Organization": [
    {
      "Organization.legalName": "<string> *",
      "Organization.identifier": "https://example.org/resource",
      "Organization.legalAddress": "<string>",
      "Organization.roleName": "<string> *"
    }
  ],
  "schema:Grant": [
    {
      "Grant.name": "<string>",
      "Grant.identifier": "<string>",
      "Grant.funder": [
        {
          "identifier": "https://example.org/resource *",
          "legalName": "<string>",
          "roleName": "<string>"
        }
      ],
      "Grant.fundedItem": {
        "Person.identifier": "https://example.org/resource *"
      },
      "Grant.amount": 0.0
    }
  ],
  "appn:SpatialLocation": [
    {
      "SpatialLocation.name": "<string> *",
      "SpatialLocation.latitude": "<string>",
      "SpatialLocation.longitude": "<string>",
      "SpatialLocation.polygon": "<string>"
    }
  ],
  "appn:GrowthFacility": [
    {
      "GrowthFacility.name": "https://example.org/resource *",
      "GrowthFacility.hasGrowthFacilityType": "<string> *"
    }
  ],
  "appn:Sensor": [
    {
      "Sensor.name": "<string> *",
      "Sensor.hasSensorType": "<string>"
    }
  ],
  "appn:BiologicalMaterial": [
    {
      "BiologicalMaterial.name": "<string> *",
      "BiologicalMaterial.identifier": "https://example.org/resource",
      "BiologicalMaterial.scientificName": "<string> *",
      "BiologicalMaterial.cultivarEpithet": "<string>",
      "BiologicalMaterial.hasPreprocessing": "<string>",
      "BiologicalMaterial.geneticallyModifiedStatus": "<string> *",
      "BiologicalMaterial.quaratineStatus": "<string> *",
      "BiologicalMaterial.MaterialSource": {
        "identifier": "https://example.org/resource *"
      }
    }
  ],
  "appn:MaterialSource": [
    {
      "MaterialSource.hasMaterialSource": [
        "<string> *"
      ],
      "MaterialSource.identifier": [
        "<string> *"
      ]
    }
  ]
}
```