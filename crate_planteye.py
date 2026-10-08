"""
crate_it.py - convert PlantEye sample data into RO-Crate

Author: Donald Hobern

TODO:

* Add Traits for the Variables.
"""

import pandas as pd
import os
import re
import shutil
import statistics
from pathlib import Path
from datetime import datetime, timezone
from appn_crate import Crate
from appn_configuration import Configuration

# Store values for trait variables organised by plant cohort.
#
# Manages nested dictionaries: {cohort: {timestamp: {trait-variable: [value, value, ...]}}}
# Used to enable statistical calculations for variables for each cohort

cohort_values = {}

def store_cohort_value(values: dict[str,dict[str,list[float]]], c: str, t: str, p: str, value: float) -> None:
    if t == "2024-10-26":
        t = "2024-10-25"
    if c not in values:
        values[c] = (cohort := {})
    else:
        cohort = values[c]
    if t not in cohort:
        cohort[t] = (ts := {})
    else:
        ts = cohort[t]
    if p not in ts:
        ts[p] = (parameter := [])
    else:
        parameter = ts[p]
    parameter.append(value)


# Folders
data_folder = Path("../appn-ro-crate-datapackaging/planteye_example/PlantEye Data")
ro_crate_folder = Path("RO-Crate")
level0_folder = Path("level_0")
level1_folder = Path("level_1")
level2_folder = Path("level_2")
scratch_folder = Path("scratch")

# Names and definitions for Phenospex Phena 1.0 variables
eye_variables = {
    "Digital biomass mm³": "Digital Biomass is calculated as the product of height and 3D leaf area assuming that the plant has a regular body of which the volume can be computed by taking into account height and length. Value Range: 0 – ∞.",
    "greenness average": "The greenness index, also referred to as Green Leaf Index, represents the relation between the reflectance in the green channel compared to the other two visible light channels (red and blue). It is computed as (2*G-R-B)/(2*G+R+B). The higher the green reflection compared to the other channels the lower the greenness index. A value of 1 would represent a full reflection in the green channel and no reflection in the other two channels. The illustration below shows three different examples for the calculation of greenness. The X axis represents a simplified spectrum in the range from 400 to 1,000nm. The Y axis shows the relative reflectance for each wavelength. The colored blocks represent the measurement channels of PlantEye with standard configuration. Value Range: -1 – 1.",
    "Height mm": "To calculate plant height PlantEye uses the distribution of elementary triangles  along the z-axis.  To do that first, the histogram along the z-axis is calculated. This histogram expresses how many elementary triangles are present in what height above ground. After that, the histogram is cropped at both ends which means that a certain safety margin on the upper and lower end of the plants is removed to make the calculation more robust against single outliers. To finally calculate height, the top 10% of the plant are averaged and the height is calculated as the range from pot height up to this averaged value. Value Range: 0 – ∞.",
    "Height Max mm": "Height Max is developed to find the absolute highest point of the plant in millimeters, and is therefore very accurate. This parameter does not replace the current height parameter, but is an addition to the parameter set. The current height is focused on stability over accuracy, by minimizing the effect of small movements, as a result of wind, external artifacts or diurnal plant movements. To compute the maximal height, the PlantEye finds the highest domain (Group of points in the 3D file) that contains enough points and is close enough to the other domains. Of this domain, the highest point is then given as the height_max. This way we compute the highest point of the plant, while at the same time ignoring single noise points or foreign objects far above the plant. Value Range: 0 – ∞.",
    "hue average °": "The standard approach in technical devices is to store colors as a combination of red, green and blue values. Nevertheless, this color model does not well represent the color of object. Each individual color is a combination of red, green and blue values. As an alternative approach to RGB color spaces the HSV color space was developed. In this color space the idea is to express the color (hue) on one dedicated channel that is arranged in the rainbow colors. The saturation of each color represents if it is a pale or very intense color. Last, the Value shows if the color is dark or bright. The advantage of this color space is that a color can be expressed independently from its saturation or value. The example below shows an image of what plots decomposed into the red, green and blue channel as well as decomposed into hue, saturation and value. One can see that it is hard to see the difference of the plot color in the red, green and blue channels whereas the hue channel nicely identifies the color differences of the plots on the left hand side of the image. PlantEye can compute the hue channel for the point cloud and analyze it further. Therefore, the hue channel can be seen as a color analysis taking into account all three measured colors. Value Range 0 - 360.",
    "Leaf angle °": "The weighted average of all angles of every face in the plant mesh based on their normal. Value Range: 0 - 90.",
    "Leaf area mm²": "To measure the 3D leaf area of plants there are several steps involved. Starting from the 3D point cloud, all points that belong to the same sector are triangulated based on certain criteria. To create a triangle in the point cloud the points should be close to each other with no more point in between. The points in the point cloud do not have to be distributed equally in space, therefore the size of the triangles can vary. However, PlantEye can account for that by calculating the area of each individual triangle. Therefore, PlantEye can measure the real leaf area of inclined leaves other than 2D measurements that just take into account a projection of the leaf area. After the triangulation domains are searched within the plant, a domain is a group of triangles that forms a uniform surface. Each plant can have several domains. The number of domains is corresponding to the number of leaves; however, it is not an accurate leaf counting instrument. The 3D area of each domain is calculated by taking the sum of all included triangles. The total 3D leaf area of the plant is then calculated by taking the sum of the elementary triangles area. Value Range: 0 – ∞.",
    "Leaf area (projected) mm²": "Projected leaf area is defined as an area of the projection of all elementary triangles on X-Y plane. The projected leaf area is equivalent to a value that you could measure with a regular 2D camera. It measures the area of the projection of the plant onto the X-Y-plane and turns the 3D object into a flat 2D object. Note that objects with the same position on X-Y plane but different height over ground are not counted twice. Value Range: 0 – sector size",
    "Leaf area index mm²/mm²": "Calculated as: (3d Leaf Area)/( Sector Size). The Leaf Area Index calculates the 3d Leaf Area over the Sector Size to express the number of layers of leaves in a defined area. The Sector Size is the size of the unit as defined by the user during experiment creation.",
    "Leaf inclination mm²/mm²": "Calculated as: (Total Leaf Area)/(Projected Leaf Area). Leaf inclination expresses how erect the leaves of a plant are on average. Calculated as a total leaf area divided by the sum of projections of each elementary triangle on X-Y plane. For a horizontal plane the leaf inclination would be 1. The more erect or bent a leaf is the bigger will be the total leaf area (without changing the projected leaf area) and therefore the leaf inclination will increase. Value Range: 1 – ∞ (or 0 if total leaf area is 0)",
    "Light penetration depth mm": "The depth of the laser light penetration through the canopy of the plant. Very dense plants will therefore exhibit a low value. It is often used with groups of plants. It measures the deepest point in which the laser can penetrate the canopy based on the histogram along the z-axis (similar to the calculation of height). To calculate the LPD the histogram is cropped on both ends again to remove outliers. After that the bottom 20% as well as the top 10% are averaged. The LPD is the distance between the top and bottom average values. Value Range: 0 – ∞",
    "NDVI average": "NDVI is computed as the ratio of the NIR and the Red channel in PlantEye. It is computed as the difference of both channels divided by the sum of both channels. Therefore it is a ratio in the range of -1 to 1. The illustration below shows three different examples for the calculation of NDVI. The X axis represents a simplified spectrum in the range from 400 to 1,000nm. The Y axis shows the relative reflectance for each wavelength. The colored blocks represent the measurement channels of PlantEye with standard configuration. One can see that there are three different examples that show the value for the NDVI index. The first example shows a high NDVI where the reflectance in the NIR channel is much higher than in the Red channel. This is the typical effect for healthy vegetation. The index is around 0.8. The second example shows a low NDVI. In this case the reflectance in the NIR channel is only slightly bigger than in the Red channel. This is a typical pattern for unhealthy vegetation. The last example shows that in theory the NDVI value could also be negative if the Red reflectance is higher than the NIR reflectance. This is typically not observed in any plant related measurements. Value Range: -1 – 1.",
    "NPCI average": "NPCI (normalized pigment chlorophyll ratio index) is computed as (RED − BLUE)/(RED + BLUE). It is correlated to chlorophyll content. Value Range: -1 – 1.",
    "PSRI average": "PSRI (plant senescence reflectance index) is computed as (RED − GREEN)/(NIR). It is correlated to the carotenoid/chlorophyll ratio. Value Range: -1 – 1.",
}

# Characters to replace with underscores when converting names to ids.
name_pattern = re.compile(r"([\s'\"\\?;:,°(){}\[\]]+)")

# Helper function to create ids from supplied object names 
def get_id(name: str, is_media: bool = False) -> str:
    if is_media or name.startswith("http://") or name.startswith("https://"):
        return name
    return f"this:{name_pattern.sub('_', name.replace('³', '3').replace('²', '2')).strip('_')}"

# Keeping track of objects added as JSON-LD or in dataframes
objects = {}
dataframes = {}
expected_objects = set()

# Establish the RO-Crate
configuration = Configuration()
crate = Crate(configuration, configuration.get_organisation_by_id("ANU"), "UreaseInhibitor")

# Add context objects representing people, organizations and licences
appn = crate.add("Organization", "https://ror.org/02zj7b759", {
    "name": "Australian Plant Phenomics Network"
})
anu = crate.add("Organization", "https://ror.org/019wvm592", {
    "name": "Australian National University"
})
dgh = crate.add("Person", "https://orcid.org/0000-0001-6492-4016", {
    "name": "Donald Hobern",
    "email": "donald.hobern@adelaide.edu.au",
    "affiliation": {"@id": appn},
    "jobTitle": "APPN Data Management Director",
})
hddo = crate.add("Person", "https://orcid.org/0000-0002-1571-0676", {
    "name": "Heber Dias de Oliveira",
    "affiliation": {"@id": anu},
    "jobTitle": "PhD Student",
})
um = crate.add("Person", "https://orcid.org/0000-0002-3557-0105", {
    "name": "Ulrike Mathesius",
    "affiliation": {"@id": anu},
    "jobTitle": "Head of Division, Plant Sciences",
})
cc_by = crate.add("CreativeWork", "https://creativecommons.org/licenses/by/4.0/",{
    "name": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
})

# Add context objects for the Study and MIAPPE metadata elements 
study = crate.add("Study", "Study", properties={
    "name": "Phenospex Plant Data for Investigating Nitrogen use Under Urease Inhibitor Treatment",
    "affiliation": {"@id": appn},  # perhaps this should be 'anu'
})
butPlant = crate.add("BiologicalUnitType", "Plant", {
    "name": "Plant",
})
butCohort = crate.add("BiologicalUnitType", "Cohort", {
    "name": "Cohort",
})
butBlock = crate.add("BiologicalUnitType", "Block", {
    "name": "Block",
})
methSoil = crate.add("Method", "SoilAddition", {
    "name": "Addition to soil mixture",
})
methScan = crate.add("Method", "PlantEyeScan10", {
    "name": "Standard ANU PlantEye scan of 10 plants",
})
methTrait = crate.add("Method", "PlantEyeTraitPhena10", {
    "name": "Derive Phena 1.0 plant traits from PlantEye scan image",
})
methSummary = crate.add("Method", "CohortSummary", {
    "name": "Derive statistical means for cohorts in study",
})
eye = crate.add("Sensor", "PlantEye_A", {
    "name": "PlantEye A",
    "model": "Phenospex PlantEye DualScan F500",
    "serialNumber": "12345-678",
    "url": "https://phenospex.com/products/plant-phenotyping/planteye-f500-multispectral-3d-laser-scanner/"
})
ply_fmt = crate.add("Scale", "https://en.wikipedia.org/wiki/PLY_(file_format)", {
    "name": "PLY file format",
})
mm = crate.add("Scale", "millimeter")
mm2 = crate.add("Scale", "Square millimeters")
mm3 = crate.add("Scale", "Cubic millimeters")
unitless = crate.add("Scale", "Unitless")
deg = crate.add("Scale", "Degrees")
boolean = crate.add("Scale", "Boolean")
hs3d = crate.add("ObservedVariable", f"3D hyperspectral scan", {
    "name": "3D Hyperspectral image polygon file",
    "hasScale": {"@id": ply_fmt},    
})

# Add an entry for this script
script = crate.add_file("crate_it.py", "crate_it.py", {
    "name": "Python script to convert PlantEye Excel data to normalised CSV tables based on APPN data schema",
    "programmingLanguage": "Python",
}, extra_classes=["SoftwareApplication"])

"""
# Add reused elements from DDI-CDI metadata
svd_uri = crate.add("SubstantiveValueDomain", "URI domain", {
    "recommendedDataType": "http://rdf-vocabulary.ddialliance.org/cv/DataType/1.1.2/6e3915f",
})
svd_string = crate.add("SubstantiveValueDomain", "String domain", {
    "recommendedDataType": "http://rdf-vocabulary.ddialliance.org/cv/DataType/1.1.2/2711832",
})
svd_datetime = crate.add("SubstantiveValueDomain", "DateTime domain", {
    "recommendedDataType": "http://rdf-vocabulary.ddialliance.org/cv/DataType/1.1.2/8cf10d2",
})
svd_double = crate.add("SubstantiveValueDomain", "Double domain", {
    "recommendedDataType": "http://rdf-vocabulary.ddialliance.org/cv/DataType/1.1.2/d909d38",
})
"""

# Add image files and associated observation assays (for block identified in first character of image file name)
# Note image files are treated here as level_0 data.
# ply_files is a dictionary mapping the date (YYYY-MM-DD) concatenated with underscore and the block number (0n) to the id for the image file.
ply_files = {}
for filepath in data_folder.glob('*.ply'):
    f = filepath.parts[-1]
    destpath = level0_folder / f
    ts = datetime.fromisoformat(f"{f[2:6]}-{f[6:8]}-{f[8:10]}T{f[11:13]}:{f[13:15]}:{f[15:17]}Z").astimezone().isoformat()
    block_number = f"0{f[0]}"
    ply = crate.add_file(filepath, str(destpath), {
        "name":  f"PlantEye A polygon file for Block {block_number} at {ts}",
        "encodingFormat": "application/ply",
        "producer": {"@id": anu},
        "license": {"@id": cc_by},
        "dateCreated": ts,
    })
    block_id = get_id(f"Block: {block_number}")
    crate.add("Observation", properties = {
        "isForObservationUnit": {"@id": block_id},
        "madeByObserver": {"@id": eye},
        "observes": {"@id": hs3d},
        "usedMethod": {"@id": methScan},
        "isPartOf": {"@id": study},
        "startTime": ts,
        "endTime": ts,
        "hasResult": {"@id": ply},
    })
    ply_files[f"{ts[0:10]}_{block_number}"] = ply

# Save a copy of the Excel file
excel_file = data_folder / "2024.09.27_Heber_Wheat_20250214_PlantEye_cleaned.xlsx"
destpath = level1_folder / excel_file.parts[-1]
xlsx = crate.add_file(excel_file, destpath, {
            "name": f"Combined data from all runs of PlantEye A for Blocks 1-8",
            "encodingFormat": "application/xlsx",
            "producer": {"@id": anu},
            "license": {"@id": cc_by},
        })

# Load Excel file. this contains timestamped values for the variables in eye_variables along with intermediate values binned to measure these variables. The intermediate values are ignored.
# Note that this file is treated here as level_1 data, as though it was separately derived directly from the polygon files.
xls = pd.ExcelFile(excel_file)
df = pd.read_excel(xls, "2024.09.27_Heber_Wheat_20250214")

# Store ids for summary statistics variables to be summarised as means for each cohort.
mean_variables = {}

# Add observed variables for columns in Excel.
for column in df.columns[6:]:

    # Ignore the columns that get binned to create the reported variable values.
    if "bin" not in column:

        # Tidy the column name
        column = column.replace("Â", "").strip()

        # Determine associated scale
        if "mm³" in column:
            scale = mm3
        if "mm²/mm²" in column:
            scale = unitless
        elif "mm²" in column:
            scale = mm2
        elif "mm" in column:
            scale = mm
        elif "°" in column or "hue" in column:
            scale = deg
        else:
            scale = unitless

        # Prepare an informative description (from Phenospex documentation)
        description = "Phenospex Phena 1.0 parameter."
        if column in eye_variables:
            description = f"{description} {eye_variables[column]}"

        # Variable for the individual plant observations.
        ov_name = f"Phenospex Phena 1.0 {column}"
        ov = crate.add("ObservedVariable", column.replace('³', '3').replace('²', '2'), {
            "name": ov_name,
            "description": description,
            "hasScale": {"@id": scale},
        })

        # Variable for the statistical mean cohort observations. Remember for later
        mean_ov = crate.add("ObservedVariable", f"Mean {column} for cohort", {
            "description": f"Mean value for all plants in cohort for {ov_name}",
            "hasScale": {"@id": scale},
        })
        mean_variables[ov] = mean_ov

        # Add alias so this can be found quickly
        objects[column] = ov

# Generate observation assays with simple values for every cell in the variable columns
# As we proceed, add the BiologicalMaterial, TreatmentVariables, BiologicalUnits (plants, blocks and cohorts), XYZLocations and Treatments associated with each row.
for index, row in df.iterrows():
    
    # Only handle the rows with actual plants
    if row['genotype'] != "Empty":

        # Timestamp
        ts = datetime.fromisoformat(str(row['timestamp']).replace(" ", "T") + "Z").astimezone().isoformat()

        # Get the BiologicalMaterial (same for all rows in this case)
        species = row['genotype']
        if species.startswith("T."):
            species = f"Triticum{species[2:]}"
        variety = row['g_alias']
        material = f"{species} {variety}"
        bm = crate.add("BiologicalMaterial", material, {
            "genus": species.split()[0],
            "scientificName": species,
            "infraspecificName": variety,
        })

        # Treatments (as boolean properties) for all urease inhibitor treatments
        treatment = row['treatment']
        additive = treatment.split("_")[0]
        variable = f"Added: {additive}"
        tv = crate.add("Substance", variable, {
            "hasScale": {"@id": boolean},
            "hasDefaultValue": False,
        })

        # Cohort of plants sharing treatment
        cohort = crate.add("BiologicalUnit", f"Cohort: {additive}", {
            "hasBiologicalUnitType": {"@id": butCohort},
            "hasBiologicalMaterial": {"@id": bm},
        })

        # Blocks of eight plants images together, with spatial location in block.
        unit = row['unit']
        position = str(unit).split(":")
        block = crate.add("BiologicalUnit", f"Block: {position[0]}", {
            "hasBiologicalUnitType": {"@id": butBlock},
            "hasBiologicalMaterial": {"@id": bm},
        })
        xyz = crate.add("XYZLocation", f"Location: {unit}", {
            "isLocationWithin": {"@id": block},
            "row": position[2],
            "column": position[1],
        })

        # Actual plants (64 of these)"PlantEye Excel"
        bu = crate.add("BiologicalUnit", f"Plant: {treatment}", {
            "hasBiologicalUnitType": {"@id": butPlant},
            "hasBiologicalMaterial": {"@id": bm},
            "inheritsContext": {"@id": cohort},
            "hasLocation": {"@id": xyz},
        })

        # Treatment applied to cohort for specified TreatmentVariable
        input = crate.add("Treatment", f"Treatment: {additive}", {
            "isForObservationUnit": {"@id": cohort},
            "usedMethod": {"@id": methSoil},
            "treatsWith": {"@id": tv},
            "hasSimpleResult": True,
            "isPartOf": {"@id": study},
            "startTime": "2024-09:20T12:00:00+11:00",
            "endTime": "2024-09:20T13:00:00+11:00",
        })

        # Find the PLY file from which these measurements were derived
        ply = ply_files[f"{str(row['timestamp'])[0:10]}_{position[0]}"]

        # Add Observations for every variable for the plant at the given timestamp.
        for c in df.columns[6:]:
            if "bin" not in c:
                column = c.replace("Â", "").strip()
                ov = objects[column]
                obs = crate.add("Observation", f"{column} {treatment} {row['timestamp']}", {
                    "isForObservationUnit": {"@id": bu},
                    "usedMethod": {"@id": methTrait},
                    "observes": {"@id": ov},
                    "hasSimpleResult": row[c],
                    "hasResult": {"@id": xlsx},
                    "isPartOf": {"@id": study},
                    "startTime": ts,
                    "endTime": ts,
                    "usesData": {"@id": ply},
                })

                # Save the value for later summary
                store_cohort_value(cohort_values, cohort, ts[0:10], ov, row[c])

# Folder for temporary generation of tables
if not scratch_folder.exists():
    scratch_folder.mkdir()

# Scratch and final name for cohort summary file
scratch_name = scratch_folder / "COHORT_TRAITS.csv"
destpath = level2_folder / "COHORT_TRAITS.csv"

# Calculate observation assays for the mean value for each variable for each cohort at each timepoint.
# Generate dataframe for secondary cohort summary report for each cohort and timepoint.
means = None
for c in cohort_values:
    cohort = cohort_values[c]
    for d in cohort:
        date = cohort[d]
        record = {"cohort": c, "date": d}
        for parameter in date:
            #variable = objects[parameter]
            mean_variable = mean_variables[parameter]
            mean_value = statistics.fmean(date[parameter])
            ts = f"{d}T12:00:00Z"
            mean = crate.add("Observation", properties= {
                "isForObservationUnit": c,
                "madeByObserver": script,
                "usedData": xlsx,
                "usedMethod": methSummary,
                "observes": mean_variable,
                "hasSimpleResult": mean_value,
                "hasResult": str(destpath),
                "startTime": ts,
                "endTime": ts, 
                "isPartOf": study,
            })
            record[mean_variable] = mean_value
        if means is None:
            means = pd.DataFrame.from_records([record])
        else:
            means = pd.concat((means, pd.DataFrame.from_records([record])), ignore_index=True)
# Write out the cohort summary report and add it to the RO-Crate.
time_now = datetime.now(timezone.utc).astimezone().isoformat()
means.to_csv(scratch_name, index=False)
csv = crate.add_file(scratch_name, str(destpath), {
    "encodingFormat": "text/csv",
    "producer": {"@id": appn},
    "license": {"@id": cc_by},
    "dateCreated": time_now,
})
crate.add("Observation", f"Generate COHORT_TRAITS.csv", {
    "madeByObserver": { "@id": script},
    "usedData": {"@id": xlsx},
    "usedMethod": {"@id": methSummary},
    "hasResult": {"@id": csv},
    "startTime": time_now,
    "endTime": time_now,
    "isPartOf": {"@id": study},
})
"""
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
    csv = crate.add(FILE, str(destpath), {
        "description": f"Properties for instances of APPN class {name}",
        "encodingFormat": "text/csv",
        "producer": {"@id": appn},
        "license": {"@id": cc_by},
        "dateCreated": datetime.now(timezone.utc).astimezone().isoformat(),
    }, scratch_name, destpath)
    crate.add("Observation", f"Generate {name}", {
        "madeByObserver": { "@id": script},
        "usedData": {"@id": xlsx},
        "hasResult": {"@id": csv},
        "startTime": time_now,
        "endTime": time_now,
        "isPartOf": {"@id": study},
    })
    wide_elements = []
    logical_elements = []
    layout_elements = []
    position = 1
    for c in df.columns:
        if c == "id":
            field = crate.add(REPRESENTED_VARIABLE, f"{name} id", {
                "definition": f"URI for instance of {name} class",
                "takesSubstantiveValuesFrom": {"@id": svd_uri},
            })
            component = crate.add(IDENTIFIER_COMPONENT, f"{name} id component", {
                "isDefinedBy": {"@id": field}
            })
            key_component = crate.add(PRIMARY_KEY_COMPONENT, f"{name} key component", {
                "correspondsTo": {"@id": component}
            })
            key = crate.add(PRIMARY_KEY, f"{name} key", {
                "isComposedOf": {"@id": key_component}
            })
            wide_elements.append(key)
            wide_elements.append(component)
            logical_elements.append(field)
        elif c == "name":
            field = crate.add(REPRESENTED_VARIABLE, f"{name} name", {
                "definition": f"Name for instance of {name} class",
                "takesSubstantiveValuesFrom": {"@id": svd_string},
            })
            component = crate.add(ATTRIBUTE_COMPONENT, f"{name} name component", {
                "isDefinedBy": {"@id": field},
            })
            wide_elements.append(component)
            logical_elements.append(field)
        elif c in [ "startTime", "endTime" ]:
            field = crate.add(REPRESENTED_VARIABLE, f"{name} {c}", {
                "definition": f"{c[0].upper()}{c[1:]} for instance of {name} class",
                "takesSubstantiveValuesFrom": {"@id": svd_datetime},
            })
            component = crate.add(ATTRIBUTE_COMPONENT, f"{name} {c} component", {
                "isDefinedBy": {"@id": field},
            })
            wide_elements.append(component)
            logical_elements.append(field)
        elif c == "hasSimpleResult":
            field = crate.add(REPRESENTED_VARIABLE, f"{name} {c}", {
                "definition": f"Simple result for instance of {name} class",
                "takesSubstantiveValuesFrom": {"@id": svd_double},
            })
            component = crate.add(MEASURE_COMPONENT, f"{name} {c} component", {
                "isDefinedBy": {"@id": field},
            })
            wide_elements.append(component)
            logical_elements.append(field)
        else:
            field = crate.add(REPRESENTED_VARIABLE, f"{name} {c}", {
                "definition": f"{c[0].upper()}{c[1:]} for instance of {name} class",
                "takesSubstantiveValuesFrom": {"@id": svd_uri},
            })
            component = crate.add(ATTRIBUTE_COMPONENT, f"{name} {c} component", {
                "isDefinedBy": {"@id": field},
            })
            wide_elements.append(component)
            logical_elements.append(field)
        mapping = crate.add(VALUE_MAPPING, f"{name} value mapping for {c}", {
            "formats": {"@id": field},
        })
        mapping_position = crate.add(VALUE_MAPPING_POSITION, f"{name} value mapping position for {c}", {
            "indexes": {"@id": field},
            "value": str(position),
        })
        layout_elements.append(mapping)
        layout_elements.append(mapping_position)
        position += 1
    structure = crate.add(WIDE_DATA_STRUCTURE, f"{name} wide structure", {
        "has": [{"@id": id} for id in wide_elements],
    })
    wide = crate.add(WIDE_DATASET, f"{name} wide dataset", {
        "physicalFileName": f"level_2/{csv_name}",
        "isStructuredBy": {"@id": structure},
    })
    logical = crate.add(LOGICAL_RECORD, f"{name} logical record", {
        "has": [{"@id": wide}] + [{"@id": id} for id in logical_elements],
    })
    psl = crate.add(PHYSICAL_SEGMENT_LAYOUT, f"{name} layout", {
        "isDelimited": True,
        "delimiter": ",",
        "hasHeader": True,
        "headerRowCount": 1,
        "formats": {"@id":  logical},
        "has": [{"@id": id} for id in layout_elements],
    })

# Write the files after generating the associated objects so the data is included in the dataframes.
for name in list(dataframes):
    df = dataframes[name]
    df.to_csv(scratch_folder / f"{name}.csv", index=False)
"""
crate.serialise(Path("PlantEyeROCrate"), {
    "name": "Phenospex Plant Data for Investigating Nitrogen use Under Urease Inhibitor Treatment",
    "description": "The objective of the dataset is to determine whether novel urease inhibitors influence plant development and productivity, and to assess the potential of high-throughput phenomics techniques in validating phenotypic traits for predicting nitrogen dynamics.",
    "license": {"@id": cc_by},
    "maintainer": {"@id": dgh},
    "mainEntity": {"@id": study},
})

# Validation: report any expected but purely external or missing objects
for id in expected_objects:
    if id.startswith("http://") or id.startswith("https://"):
        print(f"External object: {id}")
    else:
        print(f"Missing object: {id}")
