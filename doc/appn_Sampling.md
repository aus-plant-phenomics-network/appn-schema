# Sampling
[https://schema.plantphenomics.org.au/Sampling](https://schema.plantphenomics.org.au/Sampling)

An Assay that derives a new representative ObservationUnit from an existing ObservationUnit.

![UML diagram for Sampling](/ttl_uml/ttl_appn_Sampling.png)

## Superclasses
* [https://schema.plantphenomics.org.au/Assay](/doc/appn_Assay.md)
* [https://schema.plantphenomics.org.au/ResearchActivity](/doc/appn_ResearchActivity.md)
* https://schema.org/Action
* http://www.w3.org/ns/prov#Activity
* https://www.w3.org/ns/sosa/Execution
## Properties
* appn:Sampling **appn:madeBySampler** [appn:Sampler](/doc/appn_Sampler.md)
    * Identifies the entity (Sampler, i.e. a Person - no other subclasses defined yet) responsible for carrying out an Sampling.
* appn:Sampling **appn:producesSample** [appn:Sample](/doc/appn_Sample.md)
    * Identifies the Sample produced by a Sampling assay.
* [appn:Assay](/doc/appn_Assay.md) **appn:isForObservationUnit** [appn:ObservationUnit](/doc/appn_ObservationUnit.md)
    * Relates an Assay to an ObservationUnit for which it is carried out. Note that when the Assay is an Observation, the model should infer a schema:observationAbout property from isForObservationUnit.
* [appn:ResearchActivity](/doc/appn_ResearchActivity.md) **appn:isPartOf** [appn:ResearchActivity](/doc/appn_ResearchActivity.md)
    * Relates an Assay to the Study that includes it or a Study to an Investigation.
