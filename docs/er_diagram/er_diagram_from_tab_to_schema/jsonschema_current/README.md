##  Booking Form Schema

This is a `jsonschema` based schema that defines the structure of booking form information that should be collected about a study and is typically available from the booking process that is carried out when a study is being scoped with a researcher when engaging an APPN node.

This directory contains:
1. The schema (*appn_booking_schema.json*) that can be used to verify a json document.
2. An example of booking form data (*booking_form_filled_v2.json*) saved as a JSON document with data provided.
3. A verification script (*schema_validate_appn_json.py*) to test if the json data file conforms to the jsonschema document.

### Use of the validator

To validate an APPN JSON object against a definition in an APPN JSON Schema.

```bash
python schema_validate_appn_json.py schema data [definition]
```
positional arguments:
  schema      Path to the APPN JSON Schema
  data        Path to the JSON data document
  definition  An (optional) class definition to validate against, for example appn:Study.
              If not present then an internal list of classes is tested.
       
e.g.
```bash
python schema_validate_appn_json.py  appn_booking_schema.json booking_form_filled_v2.json "appn:Study"
```



