# Observation
[https://schema.plantphenomics.org.au/Observation](https://schema.plantphenomics.org.au/Observation)

An Assay that observes or measures properties of one or more ObservationUnits returning results as property values or images.

![UML diagram for Observation](/ttl_uml/ttl_appn_Observation.png)

## Superclasses
* https://schema.org/Observation
* [https://schema.plantphenomics.org.au/Assay](/doc/appn_Assay.md)
* [https://schema.plantphenomics.org.au/ResearchActivity](/doc/appn_ResearchActivity.md)
* https://schema.org/Action
* http://www.w3.org/ns/prov#Activity
* https://www.w3.org/ns/sosa/Execution
* http://purl.org/ppeo/PPEO.owl#observation
## Properties
* appn:Observation **appn:madeByObserver** [appn:Observer](/doc/appn_Observer.md)
    * Identifies the entity (Observer, i.e. one of a Person, Sensor or SoftwareApplication) responsible for carrying out an Observation.
* appn:Observation **appn:hasResult** [schema:Dataset](https://schema.org/Dataset)
    * Identifies a data output from an Observation or Control assay. Individual values are represented by sosa:hasSimpleResult.
* appn:Observation **appn:hasResult** [schema:File](https://schema.org/File)
    * Identifies a data output from an Observation or Control assay. Individual values are represented by sosa:hasSimpleResult.
* appn:Observation **appn:usesData** [schema:Dataset](https://schema.org/Dataset)
    * Identifies a data input to an Observation assay. This is intended for use in relation to Observations delivered using a SoftwareApplication.
* appn:Observation **appn:usesData** [schema:File](https://schema.org/File)
    * Identifies a data input to an Observation assay. This is intended for use in relation to Observations delivered using a SoftwareApplication.
* appn:Observation **appn:observes** [appn:ObservedVariable](/doc/appn_ObservedVariable.md)
    * Identifies an ObservedVariable controlled by an Observation assay. The Observation records or estimates the state of the ObservationVariable recorded as a value specified in a hasResult or hasSimpleResult property.
* [appn:Assay](/doc/appn_Assay.md) **appn:isForObservationUnit** [appn:ObservationUnit](/doc/appn_ObservationUnit.md)
    * Relates an Assay to an ObservationUnit for which it is carried out. Note that when the Assay is an Observation, the model should infer a schema:observationAbout property from isForObservationUnit.
* [appn:Assay](/doc/appn_Assay.md) **appn:usedMethod** [appn:Method](/doc/appn_Method.md)
    * Identifies a Method used to conduct an Assay.
* [appn:ResearchActivity](/doc/appn_ResearchActivity.md) **appn:isPartOf** [appn:ResearchActivity](/doc/appn_ResearchActivity.md)
    * Relates an Assay to the Study that includes it or a Study to an Investigation.
