# Assay
[https://schema.plantphenomics.org.au/Assay](https://schema.plantphenomics.org.au/Assay)

A research action that observes or modifies a set of ObservationUnits.

![UML diagram for Assay](/ttl_uml/ttl_appn_Assay.png)

## Superclasses
* [https://schema.plantphenomics.org.au/ResearchActivity](/doc/appn_ResearchActivity.md)
* https://schema.org/Action
* https://www.w3.org/ns/sosa/Execution
* http://purl.org/ppeo/PPEO.owl#Assay
## Properties
* appn:Assay appn:isForObservationUnit [appn:ObservationUnit](/doc/appn_ObservationUnit.md)
* appn:Assay appn:hasResult [schema:Dataset](https://schema.org/Dataset)
* appn:Assay appn:hasResult [schema:File](https://schema.org/File)
* appn:Assay appn:hasResult [appn:Sample](/doc/appn_Sample.md)
* [appn:ResearchActivity](/doc/appn_ResearchActivity.md) appn:isPartOf [appn:ResearchActivity](/doc/appn_ResearchActivity.md)
## Subclasses
* [https://schema.plantphenomics.org.au/Observation](/doc/appn_Observation.md)
* [https://schema.plantphenomics.org.au/Control](/doc/appn_Control.md)
* [https://schema.plantphenomics.org.au/Sampling](/doc/appn_Sampling.md)
* [https://schema.plantphenomics.org.au/Transformation](/doc/appn_Transformation.md)
* [https://schema.plantphenomics.org.au/Input](/doc/appn_Input.md)
