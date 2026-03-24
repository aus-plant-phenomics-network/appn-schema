# Treatment
[https://schema.plantphenomics.org.au/Treatment](https://schema.plantphenomics.org.au/Treatment)

An Assay that adds a Substance or a SubstanceQuantity to an ObservationUnit (includes potting, fertigation, pesticide application, addition of beneficials, etc.).

![UML diagram for Treatment](/ttl_uml/ttl_appn_Treatment.png)

## Superclasses
* http://purl.org/ppeo/PPEO.owl#event
* [https://schema.plantphenomics.org.au/Assay](appn_Assay.md)
* [https://schema.plantphenomics.org.au/ResearchActivity](appn_ResearchActivity.md)
* https://schema.org/Action
* http://www.w3.org/ns/prov#Activity
* https://www.w3.org/ns/sosa/Execution
## Properties
* appn:Treatment **appn:madeByController** [appn:Controller](appn_Controller.md)
    * Identifies the entity (Controller, i.e. one of a Person, Actuator, SoftwareApplication or ExternalEvent) responsible for carrying out a Control or Treatment.
* appn:Treatment **appn:treatsWith** [appn:Substance](appn_Substance.md)
    * Identifies a Substance or a SubstanceQuantity associated with a Treatment assay. The Treatment makes an input of a quantity of some Substance associated with the SubstanceQuantity. If the result is a known final state for a variable associated with an ObservationUnit, the assay should be modeled as a Control with a ControlledVariable. Treatments are for cases where no definite resulting value is recorded.
* appn:Treatment **appn:treatsWith** [appn:SubstanceQuantity](appn_SubstanceQuantity.md)
    * Identifies a Substance or a SubstanceQuantity associated with a Treatment assay. The Treatment makes an input of a quantity of some Substance associated with the SubstanceQuantity. If the result is a known final state for a variable associated with an ObservationUnit, the assay should be modeled as a Control with a ControlledVariable. Treatments are for cases where no definite resulting value is recorded.
* [appn:Assay](appn_Assay.md) **appn:isForObservationUnit** [appn:ObservationUnit](appn_ObservationUnit.md)
    * Relates an Assay to an ObservationUnit for which it is carried out. Note that when the Assay is an Observation, the model should infer a schema:observationAbout property from isForObservationUnit.
* [appn:Assay](appn_Assay.md) **appn:usedMethod** [appn:Method](appn_Method.md)
    * Identifies a Method used to conduct an Assay.
* [appn:ResearchActivity](appn_ResearchActivity.md) **appn:isPartOf** [appn:ResearchActivity](appn_ResearchActivity.md)
    * Relates an Assay to the Study that includes it or a Study to an Investigation.
