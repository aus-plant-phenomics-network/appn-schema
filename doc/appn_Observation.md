# Observation
[https://schema.plantphenomics.org.au/Observation](https://schema.plantphenomics.org.au/Observation)

![UML diagram for Observation](/ttl_uml/ttl_appn_Observation.png)
## Superclasses
* https://schema.plantphenomics.org.au/Assay
* https://schema.plantphenomics.org.au/ResearchActivity
* https://schema.org/Action
* https://www.w3.org/ns/sosa/Execution
* http://purl.org/ppeo/PPEO.owl#Assay
* http://purl.org/ppeo/PPEO.owl#Observation
## Properties
appn:Observation appn:madeByObserver [appn:Observer](https://schema.plantphenomics.org.au/Observer)
appn:Observation appn:observes [appn:ObservedVariable](https://schema.plantphenomics.org.au/ObservedVariable)
[appn:Assay](https://schema.plantphenomics.org.au/Assay) appn:isForObservationUnit [appn:ObservationUnit](https://schema.plantphenomics.org.au/ObservationUnit)
[appn:Assay](https://schema.plantphenomics.org.au/Assay) appn:hasResult [schema:Dataset](https://schema.org/Dataset)
[appn:Assay](https://schema.plantphenomics.org.au/Assay) appn:hasResult [schema:File](https://schema.org/File)
[appn:Assay](https://schema.plantphenomics.org.au/Assay) appn:hasResult [appn:Sample](https://schema.plantphenomics.org.au/Sample)
[appn:ResearchActivity](https://schema.plantphenomics.org.au/ResearchActivity) appn:isPartOf [appn:ResearchActivity](https://schema.plantphenomics.org.au/ResearchActivity)
