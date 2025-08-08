# APPN Schema
This repository is to develop schema artefacts for APPN data management.

## UML diagrams
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
