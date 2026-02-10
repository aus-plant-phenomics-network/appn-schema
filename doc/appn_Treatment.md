# Treatment
[https://schema.plantphenomics.org.au/Treatment](https://schema.plantphenomics.org.au/Treatment)

An Assay that adds a quantity of some BioChemEntity to a set of ObservationUnits (includes potting, fertigation, pesticide application, addition of beneficials, etc.).

![UML diagram for Treatment](/ttl_uml/ttl_appn_Treatment.png)

## Superclasses
* http://purl.org/ppeo/PPEO.owl#event
* [https://schema.plantphenomics.org.au/Assay](/doc/appn_Assay.md)
* [https://schema.plantphenomics.org.au/ResearchActivity](/doc/appn_ResearchActivity.md)
* https://schema.org/Action
* http://www.w3.org/ns/prov#Activity
* https://www.w3.org/ns/sosa/Execution
## Properties
* appn:Treatment **appn:madeByController** [appn:Controller](/doc/appn_Controller.md)
    * Identifies the entity (Controller, i.e. one of a Person, Actuator, SoftwareApplication or ExternalEvent) responsible for carrying out a Control or Treatment.
* appn:Treatment **appn:treats** [appn:TreatmentVariable](/doc/appn_TreatmentVariable.md)
    * Identifies a TreatmentVariable associated with a Treatment assay. The Treatment makes an input of a quantity of some BioChemEntity associated with the TreatmentVariable. If the result is a known final state for a variable associated with an ObservationUnit, the assay should be modeled as a Control with a ControlledVariable. Treatments are for cases where no definite resulting value is recorded.
* appn:Treatment **appn:treatsWith** [appn:BioChemEntity](/doc/appn_BioChemEntity.md)
    * Identifies a BioChemEntity linked to a Treatment assay. This represents the biological or chemical substance applied to the ObservationUnit.
* [appn:Assay](/doc/appn_Assay.md) **appn:isForObservationUnit** [appn:ObservationUnit](/doc/appn_ObservationUnit.md)
    * Relates an Assay to an ObservationUnit for which it is carried out. Note that when the Assay is an Observation, the model should infer a schema:observationAbout property from isForObservationUnit.
* [appn:ResearchActivity](/doc/appn_ResearchActivity.md) **appn:isPartOf** [appn:ResearchActivity](/doc/appn_ResearchActivity.md)
    * Relates an Assay to the Study that includes it or a Study to an Investigation.
