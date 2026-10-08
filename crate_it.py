"""
crate_it.py - convert PlantEye sample data into RO-Crate

Author: Donald Hobern

TODO:

* Add Traits for the Variables.
"""

import pandas as pd
import numpy as np
import re
import shutil
import math
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from appn_configuration import Configuration, CENTRAL_ORGANISATION
from appn_crate import Crate, at



# Establish the RO-Crate
configuration = Configuration()
appn_organisation = configuration.get_organisation_by_id(CENTRAL_ORGANISATION)
ltu_organisation = configuration.get_organisation_by_id("LTU")
crate = Crate(configuration, ltu_organisation, "MicroTom")

ltu = crate.add("Organization", ltu_organisation.ror, {"name": ltu_organisation.name})
appn = crate.add("Organization", appn_organisation.ror, {"name": appn_organisation.name})
dgh = crate.add("Technician", "https://orcid.org/0000-0001-6492-4016",
    {
        "name": "Donald Hobern",
        "email": "donald.hobern@adelaide.edu.au",
        "affiliation": appn,
        "jobTitle": "APPN Data Management Director",
    },
)
rj = crate.add("Person", "https://orcid.org/0000-0002-3819-6358",
    {
        "name": "Ricarda Jost",
        "affiliation": ltu,
        "jobTitle": "Senior Research Fellow",
        "email": "R.Jost@latrobe.edu.au,",
    },
)
tr = crate.add("Person", "https://orcid.org/0009-0004-1075-265X",
    {
        "name": "Thilina Ranaweera",
        "affiliation": ltu,
        "jobTitle": "Data Platform Architect",
        "email": "t.ranaweera@latrobe.edu.au",
    },
)
cc_by = crate.add("CreativeWork", "https://creativecommons.org/licenses/by/4.0/",
    {
        "name": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
    },
)
studyId = "2024_Exp_3"
study = crate.add("Study", studyId,
    {
        "name": "Optimising N inputs for dwarf tomato cultivation in protected cropping",
        "description": "Optimising N fertilizer application rates for dwarf tomato variety ‘Micro Tom’ to facilitate more uniform fruit ripening and faster cultivation cycles, using three different N levels (3, 6 and 30 mM) and a 35:65 coco coir-Perlite mix.",
        "affiliation": [
            ltu,
            appn,
        ],
    },
)
butPlant = crate.add("BiologicalUnitType", "whole plant")
butCohort = crate.add("BiologicalUnitType", "cohort")
bm = crate.add("BiologicalMaterial", "Micro Tom",
    {
        "genus": "Lycopersicon",
        "scientificName": 'Lycopersicon esculentum "Micro Tom"',
    },
)
script = crate.add_file("crate_it.py", "crate_it.py",
    {
        "name": "Python script to convert PlantEye Excel data to normalised CSV tables based on APPN data schema",
        "programmingLanguage": "Python",
    },
    extra_classes=["SoftwareApplication"],
)
mmol = crate.add("Scale","MilliMOLs",
    {
        "exactMatch": "http://qudt.org/vocab/unit/MilliMOL",
    },
)
mspercm = crate.add("Scale","MicroSiemens per centimeter",
    {
        "exactMatch": "http://qudt.org/vocab/unit/MicroS-PER-CentiM",
    },
)
pH = crate.add("Scale","pH",
    {
        "exactMatch": "http://qudt.org/vocab/unit/PH",
    },
)
percentage = crate.add("Scale","Percentage",
    {
        "exactMatch": "http://qudt.org/vocab/unit/PERCENT",
    },
)
timeHMS = crate.add("Scale",
    "http://rdf-vocabulary.ddialliance.org/cv/DateType/1.1.2/a76d4ef",
    {
        "name": "Time (HH:MM:SS)",
    },
)
isoDate = crate.add("Scale",
    "http://rdf-vocabulary.ddialliance.org/cv/DateType/1.1.2/4474971",
    {
        "name": "Date (YYYY-MM-DD)",
    },
)
hours = crate.add("Scale","Hour",
    {
        "exactMatch": "http://qudt.org/vocab/unit/HR",
    },
)
ppm = crate.add("Scale","Parts per million",
    {
        "exactMatch": "http://qudt.org/vocab/unit/PPM",
    },
)
tempC = crate.add("Scale","Temperature in degrees Celsius",
    {
        "exactMatch": "http://qudt.org/vocab/unit/DEG_C",
    },
)
intensity = crate.add("Scale","Light insensity in MilliMOLs of photons per square meter per second",
    {
        "exactMatch": "http://qudt.org/vocab/unit/MilliMOL-PER-M2-SEC",
    },
)
litres = crate.add("Scale","Litre",
    {
        "exactMatch": "http://qudt.org/vocab/unit/L",
    },
)
millilitres = crate.add("Scale","Millilitre",
    {
        "exactMatch": "http://qudt.org/vocab/unit/MilliL",
    },
)
gpercm3 = crate.add("Scale","Grams per cubic centimeter",
    {
        "exactMatch": "http://qudt.org/vocab/unit/GM-PER-CentiM3",
    },
)
fraction = crate.add("Scale","Grams per cubic centimeter",
    {
        "exactMatch": "http://qudt.org/vocab/unit/FRACTION",
    },
)
mancalc = crate.add("Method", "Manual calculation")
eec = crate.add("ObservedVariable",
    "Expected EC",
    {
        "hasTrait": "https://en.wikipedia.org/wiki/Electrical_resistivity_and_conductivity",
        "hasScale": mspercm,
        "usedMethod": mancalc,
    },
)
epH = crate.add("ObservedVariable",
    "Expected pH",
    {
        "hasTrait": "https://en.wikipedia.org/wiki/PH",
        "hasScale": pH,
        "usedMethod": mancalc,
    },
)
whc = crate.add("ObservedVariable",
    "Water Holding Capacity",
    {
        "hasTrait": "https://en.wikipedia.org/wiki/Available_water_capacity",
        "hasScale": fraction,
    },
)
controlledVariables = {}
controlledVariables["Day Start Time"] = crate.add("ControlledVariable",
    f"https://id.plantphenomics.org.au/LTU/cv_Day_Start_Time",
    {
        "name": "Day Start Time",
        "hasScale": timeHMS,
    },
)
controlledVariables["Day Hours"] = crate.add("ControlledVariable",
    f"https://id.plantphenomics.org.au/LTU/cv_Day_Hours",
    {
        "name": "Day Hours",
        "hasScale": hours,
    },
)
controlledVariables["Night Start Time"] = crate.add("ControlledVariable",
    f"https://id.plantphenomics.org.au/LTU/cv_Night_Start_Time",
    {
        "name": "Night Start Time",
        "hasScale": timeHMS,
    },
)
controlledVariables["Night Hours"] = crate.add("ControlledVariable",
    f"https://id.plantphenomics.org.au/LTU/cv_Night_Hours",
    {
        "name": "Night Hours",
        "hasScale": hours,
    },
)
controlledVariables["Day Temperature"] = crate.add("ControlledVariable",
    f"https://id.plantphenomics.org.au/LTU/cv_Day_Temperature",
    {
        "name": "Day Temperature",
        "hasScale": tempC,
    },
)
controlledVariables["Night  Temperature"] = crate.add("ControlledVariable",
    f"https://id.plantphenomics.org.au/LTU/cv_Night_Temperature",
    {
        "name": "Night Temperature",
        "hasScale": tempC,
    },
)
controlledVariables["Light Intensity"] = crate.add("ControlledVariable",
    f"https://id.plantphenomics.org.au/LTU/cv_Light_Intensity",
    {
        "name": "Light Intensity",
        "hasScale": intensity,
    },
)
controlledVariables["Day Humidity"] = crate.add("ControlledVariable",
    f"https://id.plantphenomics.org.au/LTU/cv_Day_Humidity",
    {
        "name": "Day Humidity",
        "hasScale": percentage,
    },
)
controlledVariables["Night Humidity"] = crate.add("ControlledVariable",
    f"https://id.plantphenomics.org.au/LTU/cv_Night_Humidity",
    {
        "name": "Night Humidity",
        "hasScale": percentage,
    },
)
controlledVariables["Co2 PPM"] = crate.add("ControlledVariable",
    f"https://id.plantphenomics.org.au/LTU/cv_Co2_PPM",
    {
        "name": "Co2 PPM",
        "hasScale": ppm,
    },
)
controlledVariables["Cool White"] = crate.add("ControlledVariable",
    f"https://id.plantphenomics.org.au/LTU/cv_Cool_White",
    {
        "name": "Cool White",
        "hasScale": percentage,
    },
)
controlledVariables["Royal Blue"] = crate.add("ControlledVariable",
    f"https://id.plantphenomics.org.au/LTU/cv_Royal_Blue",
    {
        "name": "Royal Blue",
        "hasScale": percentage,
    },
)
controlledVariables["Blue"] = crate.add("ControlledVariable",
    f"https://id.plantphenomics.org.au/LTU/cv_Blue",
    {
        "name": "Blue",
        "hasScale": percentage,
    },
)
controlledVariables["Cyan"] = crate.add("ControlledVariable",
    f"https://id.plantphenomics.org.au/LTU/cv_Cyan",
    {
        "name": "Cyan",
        "hasScale": percentage,
    },
)
controlledVariables["Deep Red"] = crate.add("ControlledVariable",
    f"https://id.plantphenomics.org.au/LTU/cv_Deep_Red",
    {
        "name": "Deep Red",
        "hasScale": percentage,
    },
)
controlledVariables["Far Red"] = crate.add("ControlledVariable",
    f"https://id.plantphenomics.org.au/LTU/cv_Far_Red",
    {
        "name": "Far Red",
        "hasScale": percentage,
    },
)
# Nutrient recipes
recipes = {}
df = pd.read_csv(Path("../appn-ro-crate-datapackaging/ltu/Nutrient_Recipe") / "NutrientRecipes.csv")
components = {}
for c in df.columns:
    if len(c) < 4:
        components[c] = crate.add("Substance", c)
for _, row in df.iterrows():
    if row["Experiment"] == studyId:
        recipe = row["Recipe Name"]
        quantities = []
        for c in components:
            if not math.isnan(row[c]):
                quantities.append(
                    crate.add("SubstanceAmount",
                        f"{recipe}_{c}",
                        {
                            "amount": row[c],
                            "hasScale": mmol,
                            "isOfSubstance": components[c],
                        },
                    )
                )
        recipes[recipe] = crate.add("Substance",
            recipe,
            {
                "description": row["Description"],
                "created": row["Recipe Date"],
                "hasBioChemEntityPart": quantities,
            },
        )
        crate.add("Observation",
            f"{recipe}_expected_EC",
            {
                "isForObservationUnit": recipes[recipe],
                "observes": eec,
                "hasSimpleResult": row["EC Expected"],
                "madeByObserver": rj,
                "isPartOf": study,
            },
        )
        crate.add("Observation",
            f"{recipe}_expected_pH",
            {
                "isForObservationUnit": recipes[recipe],
                "observes": epH,
                "hasSimpleResult": row["Ph Expected"],
                "madeByObserver": rj,
                "isPartOf": study,
            },
        )

# GrowthFacilityTypes and GrowthFacilities
gftGlasshouse = crate.add("GrowthFacilityType", "glasshouse")
gftCompartment = crate.add("GrowthFacilityType", "compartment")
gftPot = crate.add("GrowthFacilityType", "pot")
rda4Location = crate.add("SpatialLocation", 
    properties = {
        "latitude": -37.72389,
        "longitude": 145.0570,
    },
)
rda4 = crate.add("GrowthFacility", "RDA4",
    {
        "hasGrowthFacilityType": gftGlasshouse,
        "hasLocation": rda4Location,
    },
)
facilities = {}
csv = pd.read_csv(
    Path("../appn-ro-crate-datapackaging/ltu/Environmental_Growth_Conditions/compartmentGrowthConditions_batch2.csv")
)
for _, row in csv.iterrows():
    if row["Compartment"] not in facilities:
        location = crate.add("Location",
            f"{row['Compartment']}_location",
            {
                "isLocationWithin": rda4,
            },
        )
        facilities[row["Compartment"]] = crate.add("GrowthFacility",
            row["Compartment"],
            {
                "hasGrowthFacilityType": gftCompartment,
                "hasLocation": location,
            },
        )
    compartment = facilities[row["Compartment"]]
    lighting = crate.add("Actuator",
        f"{row['Compartment']}_{row['Light Source']}",
        {
            "name": f"{row['Light Source']} in compartment {row['Compartment']}",
            "model": row["Light Source"],
        },
    )
    deployment = crate.add("Deployment",
        f"{row['Compartment']}_{row['Light Source']}_deployment",
        {
            "deployedOnPlatform": compartment,
            "deployedSystem": lighting,
        },
    )
    for v in [
        "Day Start Time",
        "Day Hours",
        "Night Start Time",
        "Night Hours",
        "Day Temperature",
        "Night  Temperature",
        "Light Intensity",
        "Day Humidity",
        "Night Humidity",
        "Co2 PPM",
    ]:
        crate.add("Control",
            f"{row['Compartment']}_{v}",
            {
                "isForObservationUnit": compartment,
                "controls": controlledVariables[v],
                "madeByController": compartment,
                "hasSimpleResult": f"{row[v]}:00" if "Time" in v else row[v],
                "isPartOf": study,
                "startTime": f"{row['Set Date']}T00:00:00+11",
            },
        )
    for v in ["Cool White", "Royal Blue", "Blue", "Cyan", "Deep Red", "Far Red"]:
        if not np.isnan(row[v]):
            crate.add("Control",
                f"{row['Compartment']}_{v}",
                {
                    "isForObservationUnit": compartment,
                    "controls": controlledVariables[v],
                    "madeByController": lighting,
                    "hasSimpleResult": row[v],
                    "isPartOf": study,
                    "startTime": f"{row['Set Date']}T00:00:00+11",
                },
            )

cocoperlite = crate.add("Substance", "cocoperlite 35/65")
crate.add(
    "Observation",
    "cocoperlite WHC",
    {
        "observes": whc,
        "hasSimpleResult": 0.3,
        "isPartOf": study,
    },
)

pots = {}
for f in Path("../appn-ro-crate-datapackaging/ltu/Potting").glob("*/*.csv"):
    csv = pd.read_csv(Path(f))
    for _, row in csv.iterrows():
        location_id = f"{row['Compartment']}_{row["Plant Position"]}"
        pottingDate = f"{row["Pot Transfer Date"]}T00:00:00"
        location = crate.add("XYZLocation",
            location_id,
            {
                "isLocationWithin": facilities[row["Compartment"]],
                "row": row["Plant Position"][0],
                "column": row["Plant Position"][1:],
                "startTime": pottingDate,
            },
        )
        pot_id = f"{row['Plant UID']}_pot"
        if pot_id in pots:
            pot = pots[pot_id]
            if "hasLocation" in pot:
                crate.known_instances[pot["hasLocation"][-1]]["endTime"] = pottingDate
                pot["hasLocation"].append(location)
            else:
                pot["hasLocation"] = [location]
        else:
            pots[pot_id] = {
                "hasGrowthFacilityType": gftPot,
                "hasLocation": [location],
            }
            tq = crate.add("SubstanceAmount",
                f"cocoperlite_35_65_{row['Pot Size']}",
                {
                    "isOfSubstance": cocoperlite,
                    "hasScale": litres,
                    "amount": row["Pot Size"][0:-1],
                },
            )
            crate.add("Treatment",
                f"{pot_id}_potting",
                {
                    "treatsWith": tq,
                    "isForObservationUnit": f"https://data.plantphenomics.org.au/LTU/MicroTom/gf_{pot_id}",
                    "startTime": pottingDate,
                    "isPartOf": study,
                },
            )

for k, v in pots.items():
    pot = crate.add("GrowthFacility", k, v)
    facilities[k] = pot

cohorts = {}
for f in Path("../appn-ro-crate-datapackaging/ltu/Plant_Information").glob("*.csv"):
    csv = pd.read_csv(f)
    for _, row in csv.iterrows():
        batchId = f"Batch_{row["Batch"]}"
        if batchId not in cohorts:
            cohorts[batchId] = crate.add("BiologicalUnit",
                batchId,
                {
                    "hasBiologicalMaterial": bm,
                    "hasBiologicalUnitType": butCohort,
                },
            )
        location = crate.add("Location",
            f"{row['Plant UID']}_location",
            {
                "isLocationWithin": facilities[f"{row['Plant UID']}_pot"],
            },
        )
        plant = crate.add("BiologicalUnit",
            row["Plant UID"],
            {
                "hasBiologicalUnitType": butPlant,
                "hasBiologicalMaterial": bm,
                "hasLocation": location,
                "altLabel": row["Line ID"],
                "derivesFrom": cohorts[batchId],
            },
        )

for f in Path("../appn-ro-crate-datapackaging/ltu/Feeding").glob("*/*.csv"):
    csv = pd.read_csv(f)
    csv = csv.loc[csv["Treatment Amount (mL)"].notna()]
    for _, row in csv.iterrows():
        plant = f"https://data.plantphenomics.org.au/LTU/MicroTom/bu_{row['Plant UID']}"
        nutrient = f"https://data.plantphenomics.org.au/LTU/MicroTom/substance_{row['Nutrient Recipe ID'][0].upper()+row['Nutrient Recipe ID'][1:]}"
        amount = row["Treatment Amount (mL)"]
        sq = crate.add("SubstanceAmount",
            f"{nutrient}_{amount}",
            {   
                "name": f"{amount} mL {row['Nutrient Recipe ID']}",
                "isOfSubstance": nutrient,
                "hasScale": millilitres,
                "amount": amount,
            },
        )
        crate.add("Treatment", 
            properties = {
                "isForObservationUnit": plant,
                "treatsWith": sq,
                "startTime": f"{row['Feed Date']}T{'00' if row['Daily Index'] == 1 else '12'}:00:00",
                "isPartOf": study,
            },
        )

jpeg_fmt = crate.add("Scale",
    "https://en.wikipedia.org/wiki/JPEG",
    {
        "name": "JPEG file format",
    },
)
iphone = crate.add("Sensor", "iPhone")
fruit = crate.add("ObservedVariable",
    "fruit image",
    {
        "hasScale": jpeg_fmt,
        "forBiologicalUnitType": butPlant,
    },
)
level_1 = Path("level_1")
for f in Path("Images").glob("**/*.jpg"):
    parts = f.stem.split("-")
    dest = level_1 / str(f)
    jpg = crate.add_file(
        f,
        dest,
        {
            "name": f"{f.stem}",
            "encodingFormat": "image/jpeg",
            "producer": ltu,
            "license": cc_by,
            "dateCreated": parts[0],
        }
    )
    crate.add("Observation",
        properties={
            "hasResult": jpg,
            "isForObservationUnit": get_id(parts[1]),
            "startDate": f"{parts[0][0:4]}-{parts[0][4-6]}-{parts[0][6-8]}T12:00:00",
            "madeByObserver": iphone,
            "observes": fruit,
            "isPartOf": at(
                study,
            ),
        },
    )

variables = {}
for f in Path("../appn-ro-crate-datapackaging/ltu/Measurements").glob("*/*.csv"):
    csv = pd.read_csv(f)
    csv = csv.loc[csv["Plant UID"].notna()]
    for c in csv.columns[8:-1]:
        variables[c] = crate.add("ObservedVariable",
            f"Variable_{c}",
            {
                "name": c,
            },
        )
    for _, row in csv.iterrows():
        plant = f'https://data.plantphenomics.org.au/LTU/MicroTom/bu_{row["Plant UID"]}'
        date = f"{row['Measurement Date']}T12:00:00"
        for c in csv.columns[8:-1]:
            value = row[c]
            if isinstance(row[c], str):
                if value == "Y":
                    value = True
                elif value == "N":
                    value = False
            elif math.isnan(value):
                continue
            crate.add("Observation", 
                properties={
                    "isForObservationUnit": plant,
                    "startDate": date,
                    "observes": variables[c],
                    "hasSimpleResult": value,
                },
            )
variables = {}
for f in Path("../appn-ro-crate-datapackaging/ltu/Harvesting").glob("*/*.csv"):
    csv = pd.read_csv(f)
    csv = csv.loc[csv["Plant UID"].notna()]
    organ_type = f.stem.split("_")[-2]
    for c in csv.columns[-4:-1]:
        variables[c] = crate.add("ObservedVariable",
            f"{organ_type}_{c}",
            {
                "name": f"{c} for {organ_type} harvest",
            },
        )
    for _, row in csv.iterrows():
        plant = f'https://data.plantphenomics.org.au/LTU/MicroTom/bu_{row["Plant UID"]}'
        date = f"{row['Harvest Date']}T12:00:00"
        for c in csv.columns[-4:-1]:
            value = row[c]
            if math.isnan(value):
                continue
            crate.add("Observation",
                properties = {
                    "isForObservationUnit": plant,
                    "startDate": date,
                    "observes": variables[c],
                    "hasSimpleResult": value,
                },
            )
"""
# Add reused elements from DDI-CDI metadata
svd_uri = crate.add(SUBSTANTIVE_VALUE_DOMAIN,
    "URI domain",
    {
        "recommendedDataType": "http://rdf-vocabulary.ddialliance.org/cv/DataType/1.1.2/6e3915f",
    },
)
svd_string = crate.add(SUBSTANTIVE_VALUE_DOMAIN,
    "String domain",
    {
        "recommendedDataType": "http://rdf-vocabulary.ddialliance.org/cv/DataType/1.1.2/2711832",
    },
)
svd_datetime = crate.add(SUBSTANTIVE_VALUE_DOMAIN,
    "DateTime domain",
    {
        "recommendedDataType": "http://rdf-vocabulary.ddialliance.org/cv/DataType/1.1.2/8cf10d2",
    },
)
svd_double = crate.add(SUBSTANTIVE_VALUE_DOMAIN,
    "Double domain",
    {
        "recommendedDataType": "http://rdf-vocabulary.ddialliance.org/cv/DataType/1.1.2/d909d38",
    },
)

# Enrich metadata for crate itself
crate_properties = crate.default_entities[0].properties()
crate_properties |= {
    "name": "Optimising N inputs for dwarf tomato cultivation in protected cropping",
    "description": "Optimising N fertilizer application rates for dwarf tomato variety ‘Micro Tom’ to facilitate more uniform fruit ripening and faster cultivation cycles, using three different N levels (3, 6 and 30 mM) and a 35:65 coco coir-Perlite mix.",
    "license": cc_by,
    "maintainer": dgh,
    "mainEntity": study,
}

# Folder for temporary generation of tables
if not scratch_folder.exists():
    scratch_folder.mkdir()

# Now write out the model class dataframes and add them to the RO-Crate
for name in list(dataframes):
    df = dataframes[name]
    columns = list(df.columns)
    columns.remove("id")
    columns.remove("name")
    dataframes[name] = df[["id", "name"] + columns]
    csv_name = f"{name}.csv"
    scratch_name = scratch_folder / csv_name
    destpath = level2_folder / csv_name
    csv = crate.add(FILE,
        str(destpath),
        {
            "description": f"Properties for instances of APPN class {name}",
            "encodingFormat": "text/csv",
            "producer": appn,
            "license": cc_by,
            "dateCreated": datetime.now(timezone.utc).astimezone().isoform,
        },
        scratch_name,
        destpath,
    )
    wide_elements = []
    logical_elements = []
    layout_elements = []
    position = 1
    for c in df.columns:
        if c == "id":
            field = crate.add(REPRESENTED_VARIABLE,
                f"{name} id",
                {
                    "definition": f"URI for instance of {name} class",
                    "takesSubstantiveValuesFrom": svd_uri,
                },
            )
            component = crate.add(IDENTIFIER_COMPONENT,
                f"{name} id component",
                {"isDefinedBy": field},
            )
            key_component = crate.add(PRIMARY_KEY_COMPONENT,
                f"{name} key component",
                {"correspondsTo": component},
            )
            key = add(
                crate, PRIMARY_KEY, f"{name} key", {"isComposedOf": key_component}
            )
            wide_elements.append(key)
            wide_elements.append(component)
            logical_elements.append(field)
        elif c == "name":
            field = crate.add(REPRESENTED_VARIABLE,
                f"{name} name",
                {
                    "definition": f"Name for instance of {name} class",
                    "takesSubstantiveValuesFrom": svd_string,
                },
            )
            component = crate.add(ATTRIBUTE_COMPONENT,
                f"{name} name component",
                {
                    "isDefinedBy": field,
                },
            )
            wide_elements.append(component)
            logical_elements.append(field)
        elif c in ["startTime", "endTime"]:
            field = crate.add(REPRESENTED_VARIABLE,
                f"{name} {c}",
                {
                    "definition": f"{c[0].upper()}{c[1:]} for instance of {name} class",
                    "takesSubstantiveValuesFrom": svd_datetime,
                },
            )
            component = crate.add(ATTRIBUTE_COMPONENT,
                f"{name} {c} component",
                {
                    "isDefinedBy": field,
                },
            )
            wide_elements.append(component)
            logical_elements.append(field)
        elif c == "hasSimpleResult":
            field = crate.add(REPRESENTED_VARIABLE,
                f"{name} {c}",
                {
                    "definition": f"Simple result for instance of {name} class",
                    "takesSubstantiveValuesFrom": svd_double,
                },
            )
            component = crate.add(MEASURE_COMPONENT,
                f"{name} {c} component",
                {
                    "isDefinedBy": field,
                },
            )
            wide_elements.append(component)
            logical_elements.append(field)
        else:
            field = crate.add(REPRESENTED_VARIABLE,
                f"{name} {c}",
                {
                    "definition": f"{c[0].upper()}{c[1:]} for instance of {name} class",
                    "takesSubstantiveValuesFrom": svd_uri,
                },
            )
            component = crate.add(ATTRIBUTE_COMPONENT,
                f"{name} {c} component",
                {
                    "isDefinedBy": field,
                },
            )
            wide_elements.append(component)
            logical_elements.append(field)
        mapping = crate.add(VALUE_MAPPING,
            f"{name} value mapping for {c}",
            {
                "formats": field,
            },
        )
        mapping_position = crate.add(VALUE_MAPPING_POSITION,
            f"{name} value mapping position for {c}",
            {
                "indexes": field,
                "value": str(position),
            },
        )
        layout_elements.append(mapping)
        layout_elements.append(mapping_position)
        position += 1
    structure = crate.add(WIDE_DATA_STRUCTURE,
        f"{name} wide structure",
        {
            "has": [id for id in wide_elements],
        },
    )
    wide = crate.add(WIDE_DATASET,
        f"{name} wide dataset",
        {
            "physicalFileName": f"level_2/{csv_name}",
            "isStructuredBy": structure,
        },
    )
    logical = crate.add(LOGICAL_RECORD,
        f"{name} logical record",
        {
            "has": [wide)] + [at(id for id in logical_elements],
        },
    )
    psl = crate.add(PHYSICAL_SEGMENT_LAYOUT,
        f"{name} layout",
        {
            "isDelimited": True,
            "delimiter": ",",
            "hasHeader": True,
            "headerRowCount": 1,
            "formats": logical,
            "has": [id for id in layout_elements],
        },
    )

# Write the files after generating the associated objects so the data is included in the dataframes.
for name in list(dataframes):
    df = dataframes[name]
    df.to_csv(scratch_folder / f"{name}.csv", index=False)

# Write the RO-Crate
if ro_crate_folder.exists():
    shutil.rmtree(ro_crate_folder)
crate.write(ro_crate_folder)

# Clean up scratch folder
if scratch_folder.exists():
    shutil.rmtree(scratch_folder)

# Validation: report any expected but purely external or missing objects
for id in expected_objects:
    if id.startswith("http://") or id.startswith("https://"):
        print(f"External object: {id}")
    else:
        print(f"Missing object: {id}")
"""

crate.serialise(Path("LTUCrate"))