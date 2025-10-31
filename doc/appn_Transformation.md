# Transformation
[https://schema.plantphenomics.org.au/Transformation](https://schema.plantphenomics.org.au/Transformation)

An Assay that derives new property values or images from existing property values or images.

![UML diagram for Transformation](/ttl_uml/ttl_appn_Transformation.png)

## Superclasses
* [https://schema.plantphenomics.org.au/Assay](/doc/appn_Assay.md)
* [https://schema.plantphenomics.org.au/ResearchActivity](/doc/appn_ResearchActivity.md)
* https://schema.org/Action
* https://www.w3.org/ns/sosa/Execution
* http://purl.org/ppeo/PPEO.owl#Assay
## Properties
* appn:Transformation appn:madeByTransformer [appn:Transformer](/doc/appn_Transformer.md)
* appn:Transformation appn:usesData [schema:Dataset](https://schema.org/Dataset)
* appn:Transformation appn:usesData [schema:File](https://schema.org/File)
* [appn:Assay](/doc/appn_Assay.md) appn:isForObservationUnit [appn:ObservationUnit](/doc/appn_ObservationUnit.md)
* [appn:Assay](/doc/appn_Assay.md) appn:hasResult [schema:Dataset](https://schema.org/Dataset)
* [appn:Assay](/doc/appn_Assay.md) appn:hasResult [schema:File](https://schema.org/File)
* [appn:Assay](/doc/appn_Assay.md) appn:hasResult [appn:Sample](/doc/appn_Sample.md)
* [appn:Assay](/doc/appn_Assay.md) appn:usedMethod [appn:Method](/doc/appn_Method.md)
* [appn:ResearchActivity](/doc/appn_ResearchActivity.md) appn:isPartOf [appn:ResearchActivity](/doc/appn_ResearchActivity.md)
