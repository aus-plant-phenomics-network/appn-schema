# Transformation
[https://schema.plantphenomics.org.au/Transformation](https://schema.plantphenomics.org.au/Transformation)

![UML diagram for Transformation](/ttl_uml/ttl_appn_Transformation.png)
## Superclasses
* https://schema.plantphenomics.org.au/Assay
* https://schema.plantphenomics.org.au/ResearchActivity
* https://schema.org/Action
* https://www.w3.org/ns/sosa/Execution
* http://purl.org/ppeo/PPEO.owl#Assay
## Properties
appn:Transformation appn:madeByTransformer [appn:Transformer](https://schema.plantphenomics.org.au/Transformer)
appn:Transformation appn:usesData [schema:Dataset](https://schema.org/Dataset)
appn:Transformation appn:usesData [schema:File](https://schema.org/File)
[appn:Assay](https://schema.plantphenomics.org.au/Assay) appn:isForObservationUnit [appn:ObservationUnit](https://schema.plantphenomics.org.au/ObservationUnit)
[appn:Assay](https://schema.plantphenomics.org.au/Assay) appn:hasResult [schema:Dataset](https://schema.org/Dataset)
[appn:Assay](https://schema.plantphenomics.org.au/Assay) appn:hasResult [schema:File](https://schema.org/File)
[appn:Assay](https://schema.plantphenomics.org.au/Assay) appn:hasResult [appn:Sample](https://schema.plantphenomics.org.au/Sample)
[appn:ResearchActivity](https://schema.plantphenomics.org.au/ResearchActivity) appn:isPartOf [appn:ResearchActivity](https://schema.plantphenomics.org.au/ResearchActivity)
