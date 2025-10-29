# Observation
[https://schema.plantphenomics.org.au/Observation](https://schema.plantphenomics.org.au/Observation)

![UML diagram for Observation](/ttl_uml/ttl_appn_Observation.png)
## Superclasses
* [https://schema.plantphenomics.org.au/Assay](/doc/appn_Assay.md)
* [https://schema.plantphenomics.org.au/ResearchActivity](/doc/appn_ResearchActivity.md)
* https://schema.org/Action
* https://www.w3.org/ns/sosa/Execution
* http://purl.org/ppeo/PPEO.owl#Assay
* http://purl.org/ppeo/PPEO.owl#Observation
## Properties
* appn:Observation appn:madeByObserver [appn:Observer](/doc/appn_Observer.md)
* appn:Observation appn:observes [appn:ObservedVariable](/doc/appn_ObservedVariable.md)
* [appn:Assay](/doc/appn_Assay.md) appn:isForObservationUnit [appn:ObservationUnit](/doc/appn_ObservationUnit.md)
* [appn:Assay](/doc/appn_Assay.md) appn:hasResult [schema:Dataset](https://schema.org/Dataset)
* [appn:Assay](/doc/appn_Assay.md) appn:hasResult [schema:File](https://schema.org/File)
* [appn:Assay](/doc/appn_Assay.md) appn:hasResult [appn:Sample](/doc/appn_Sample.md)
* [appn:ResearchActivity](/doc/appn_ResearchActivity.md) appn:isPartOf [appn:ResearchActivity](/doc/appn_ResearchActivity.md)
