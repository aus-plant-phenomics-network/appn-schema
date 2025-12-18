# APPN Schema
This repository is to develop schema artefacts for APPN data management.

## Turtle representation (Active)
The schema is represented in Turtle: [appn-schema.ttl](/appn-schema.ttl). It defines classes and properties in an APPN namespace but indicating subclass relationships to key ontologies and schemas: [schema.org](https://schema.org/), [PPEO](http://purl.org/ppeo/PPEO.owl), [bioschemas.org](https://bioschemas.org/), [SOSA](https://www.w3.org/ns/sosa/)/[SSN](https://www.w3.org/ns/ssn/), [DDI-CDI](http://ddialliance.org/Specification/DDI-CDI/1.0/RDF/) and [PROV](http://www.w3.org/ns/prov). The set of included properties is still incomplete relative to the scope of MIAPPE/PPEO.

The [ttl2uml.py](/ttl2uml.py) script generates a set of UML diagrams from the Turtle representation (using PlantUML). The UML outputs include:
* [ttl_appn_full.png](/ttl_uml/ttl_appn_full.png) - Inheritance of all APPN schema classes, including classes from external packages (very wide diagram)
* [ttl_appn-ppeo-sosa-ssn-cdi-prov.png](/ttl_uml/ttl_appn-ppeo-sosa-ssn-cdi-prov.png) - Inheritiance of APPN schema classes, including inheritance only from schema.org and bioschemas.org
* [UML diagrams for each APPN schema class](/ttl_uml/)

Markdown pages for all classes (including the UML diagrams above) can be found here: [doc/appn_schema.md](/doc/appn_schema.md)

The ttl2uml.py script also generates a JSON-LD context document to include the APPN classes and properties in an RO-Crate: [context.json](/context.json)

## Older UML diagrams (Deprecated)
The following diagrams were prepared previously to assist with concept development. They included outdated representations and will be removed later.

The `uml` subfolder contains PlantUML specifications for class diagrams as .TXT files and .PNG renderings of these. Files with names starting `uml_` present views developed for documentation purposes. Files with names starting `appn_`, `sosa_` and `ro_` are modules defining parts of the model for reuse in one or more `uml_` diagrams. Files with names starting `example_` are to illustrate particular application scenarios. 

Diagrams include:
* [uml_sosa.png](/uml/uml_sosa.png) - Class inheritance and relationships for the portions of [SOSA](https://w3c.github.io/sdw-sosa-ssn/ssn/) of greatest significance to APPN
* [uml_appn_sosa_inheritance.png](/uml/uml_appn_sosa_inheritance.png) - Class inheritance within APPN and between APPN and SOSA
* [uml_appn_inheritance.png](/uml/uml_appn_inheritance.png) - Class inheritance within APPN and between APPN and SOSA and RO-Crate (schema.org)
* [uml_appn_sosa.png](/uml/uml_appn_sosa.png) - Class inheritance and relationships within APPN and SOSA
* [uml_appn_sosa_ro.png](/uml/uml_appn_sosa_ro.png) - Class inheritance and relationships within APPN, SOSA and RO-Crate (schema.org)
* [uml_appn.png](/uml/uml_appn.png) - Class inheritance and relationships within APPN
* [uml_appn_sosa_observation.png](/uml/uml_appn_observation.png) - APPN model for representing an `Assay` that represents an `Observation` that collects data on an `ObservationUnit` 
* [uml_appn_sosa_observation_core.png](/uml/uml_appn_observation_core.png) - Simplified model for representing an `Observation` showing only classes that will normally appear in an RO-Crate
* [uml_appn_sosa_transformation.png](/uml/uml_appn_transformation.png) - APPN model for representing an `Assay` that represents a `Transformation` of data collected on an `ObservationUnit` 
* [uml_appn_sosa_transformation_core.png](/uml/uml_appn_transformation_core.png) - Simplified model for representing a `Transformation` showing only classes that will normally appear in an RO-Crate
* [uml_appn_sosa_control.png](/uml/uml_appn_control.png) - APPN model for representing an `Assay` that represents a `Control` of a variable associated with an `ObservationUnit` 
* [uml_appn_sosa_control_core.png](/uml/uml_appn_control_core.png) - Simplified model for representing a `Control` showing only classes that will normally appear in an RO-Crate
* [uml_appn_sosa_sampling.png](/uml/uml_appn_sampling.png) - APPN model for representing an `Assay` that represents a `Sampling` that derives a new `Sample` from an `ObservationUnit` 
* [uml_appn_sosa_sampling_core.png](/uml/uml_appn_sampling_core.png) - Simplified model for representing a `Sampling` showing only classes that will normally appear in an RO-Crate
