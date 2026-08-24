### Scripts used to convert Excel schema definitions to ER diagrams

These scripts help with the semi-automated production of the ER diagram from the booking sheet fields that are defined in:
  
  [APPN Booking sheet metadata mapping 2026 RDv1](https://uao365.sharepoint.com/:x:/r/sites/APPF2023-28/Shared%20Documents/Coordinating%20Data%20Collection/Central%20Team%20Notes/APPN%20Booking%20sheet%20metadata%20mapping%202026%20RDv1.xlsx?d=wbbb765a5bc6e44cdb1150648d866ad58&csf=1&web=1&e=3hz8bC)
  

The above spreadsheet was copied and then extended as filename named ```appn_schema_tabdelim_appn_hand_edited.txt```. This file has extra columns and the relationships between classes are added to each class definition. 

The edited file will be the input file to the following script (hand modified to add the filename ```appn_schema_tabdelim_appn_hand_edited.txt``` - 

```python
python convert_booking_def_to_jsonschema.py

```

The above script outputs a Python library```jsonschema``` file named  ```appn_schema_tabdelim_appn.json```

The schema file is then reprocessed to output a Mermaid ER diagram

```python
python generate_mermaide_from_schema.py appn_schema_tabdelim_appn_hand_edited.json
```

The current output generates something like the following:
  
```mermaid
erDiagram

    appn_Investigation {
    string investigationIdentifier
    string investigationTitle
    string investigationDescription
    array studyIdentifier PK
    }
    appn_Study {
    string studyIdentifier PK
    string studyalternateIdentifier
    string studyTitle PK
    string studyDescription PK
    string additionalType PK
    array personIdentifier PK
    object investigationIdentifier
    array placeName PK
    array growthFacilityName PK
    array biologicalMaterialIdentifier PK
    array deploymentName
    }
    schema_Person {
    string givenName PK
    string familyName PK
    array identifier
    array email
    string jobTitle
    string roleName PK
    array affiliation PK
    }
    schema_Organization {
    string legalName PK
    array identifier PK
    string address
    string roleName
    }
    schema_Grant {
    string name
    array identifier
    object funder
    object fundedItem
    number amount
    }
    appn_SpatialLocation {
    string name PK
    string GeoLatLong
    string GeoShape
    }
    appn_GrowthFacility {
    string growthFacilityName PK
    string growthFacilityType PK
    string growthFacilityContainmentLevel PK
    boolean growthFacilityQuarantine PK
    }
    appn_Deployment {
    string deploymentName PK
    }
    appn_BiologicalMaterial {
    string biologicalMaterialIdentifier
    string biologicalMaterialGenus PK
    string biologicalMaterialSpecies PK
    array biologicalMaterialInfraspecificName
    string biologicalMaterialPreprocessing
    string geneticallyModifiedStatus
    string quaratineStatus
    object materialSourceIdentifier
    }
    appn_MaterialSource {
    array materialSourceDescription
    array materialSourceIdentifier PK
    }

    appn_Study |{--|| appn_Investigation : studyIdentifier
    schema_Person |{--|| appn_Study : personIdentifier
    appn_Investigation o|--|| appn_Study : investigationIdentifier
    appn_SpatialLocation |{--|| appn_Study : placeName
    appn_GrowthFacility |{--|| appn_Study : growthFacilityName
    appn_BiologicalMaterial |{--|| appn_Study : biologicalMaterialIdentifier
    appn_Deployment o{--|| appn_Study : deploymentName
    schema_Grant o{--|| schema_Person : identifier
    schema_Organization |{--|| schema_Person : affiliation
    schema_Person |{--|| schema_Organization : identifier
    schema_Organization o{--|| schema_Grant : identifier
    schema_Organization o|--|| schema_Grant : funder
    schema_Person o|--|| schema_Grant : fundedItem
    appn_MaterialSource o|--|| appn_BiologicalMaterial : materialSourceIdentifier
```

  
With some definitions of relationship types - 
  
```mermaid
erDiagram
    E1 ||--|| E2 : "Exactly one"
    E1 o|--|| E2 : "Zero or one"
    E1 |{--|| E2 : "One or more"
    E1 o{--|| E2 : "Zero or more"
```

<ul>
  <li><strong>PK</strong> = Primary Key</li>
  <li><strong>FK</strong> = Foreign Key</li>
</ul>
  
> N.B. The foreign key designation is not automated from the generator script and the primary key field is currently a temporary placeholder.