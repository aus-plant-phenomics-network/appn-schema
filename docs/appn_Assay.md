# Assay
[https://schema.plantphenomics.org.au/Assay](https://schema.plantphenomics.org.au/Assay)

A research action that observes or modifies a set of ObservationUnits.

![UML diagram for Assay](/ttl_uml/ttl_appn_Assay.png)

## Superclasses
* [https://schema.plantphenomics.org.au/ResearchActivity](/docs/appn_ResearchActivity.md)
* https://schema.org/Action
* http://www.w3.org/ns/prov#Activity
* https://www.w3.org/ns/sosa/Execution
## Properties
* appn:Assay **appn:isForObservationUnit** [appn:ObservationUnit](/docs/appn_ObservationUnit.md)
    * Relates an Assay to an ObservationUnit for which it is carried out. Note that when the Assay is an Observation, the model should infer a schema:observationAbout property from isForObservationUnit.
* appn:Assay **appn:usedMethod** [appn:Method](/docs/appn_Method.md)
    * Identifies a Method used to conduct an Assay.
* [appn:ResearchActivity](/docs/appn_ResearchActivity.md) **appn:isPartOf** [appn:ResearchActivity](/docs/appn_ResearchActivity.md)
    * Relates an Assay to the Study that includes it or a Study to an Investigation.
## Subclasses
* [https://schema.plantphenomics.org.au/Observation](/docs/appn_Observation.md)
* [https://schema.plantphenomics.org.au/Control](/docs/appn_Control.md)
* [https://schema.plantphenomics.org.au/Sampling](/docs/appn_Sampling.md)
* [https://schema.plantphenomics.org.au/Treatment](/docs/appn_Treatment.md)
