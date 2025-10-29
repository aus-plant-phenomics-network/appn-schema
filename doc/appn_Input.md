# Input
[https://schema.plantphenomics.org.au/Input](https://schema.plantphenomics.org.au/Input)

![UML diagram for Input](/ttl_uml/ttl_appn_Input.png)
## Superclasses
* https://schema.plantphenomics.org.au/Assay
* https://schema.plantphenomics.org.au/ResearchActivity
* https://schema.org/Action
* https://www.w3.org/ns/sosa/Execution
* http://purl.org/ppeo/PPEO.owl#Assay
## Properties
appn:Input appn:madeByController [appn:Controller](https://schema.plantphenomics.org.au/Controller)
appn:Input appn:inputs [appn:InputVariable](https://schema.plantphenomics.org.au/InputVariable)
[appn:Assay](https://schema.plantphenomics.org.au/Assay) appn:isForObservationUnit [appn:ObservationUnit](https://schema.plantphenomics.org.au/ObservationUnit)
[appn:Assay](https://schema.plantphenomics.org.au/Assay) appn:hasResult [schema:Dataset](https://schema.org/Dataset)
[appn:Assay](https://schema.plantphenomics.org.au/Assay) appn:hasResult [schema:File](https://schema.org/File)
[appn:Assay](https://schema.plantphenomics.org.au/Assay) appn:hasResult [appn:Sample](https://schema.plantphenomics.org.au/Sample)
[appn:ResearchActivity](https://schema.plantphenomics.org.au/ResearchActivity) appn:isPartOf [appn:ResearchActivity](https://schema.plantphenomics.org.au/ResearchActivity)
