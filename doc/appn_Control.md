# Control
[https://schema.plantphenomics.org.au/Control](https://schema.plantphenomics.org.au/Control)

![UML diagram for Control](/ttl_uml/ttl_appn_Control.png)
## Superclasses
* https://schema.plantphenomics.org.au/Assay
* https://schema.plantphenomics.org.au/ResearchActivity
* https://schema.org/Action
* https://www.w3.org/ns/sosa/Execution
* http://purl.org/ppeo/PPEO.owl#Assay
## Properties
appn:Control appn:madeByController [appn:Controller](https://schema.plantphenomics.org.au/Controller)
appn:Control appn:controls [appn:ControlledVariable](https://schema.plantphenomics.org.au/ControlledVariable)
[appn:Assay](https://schema.plantphenomics.org.au/Assay) appn:isForObservationUnit [appn:ObservationUnit](https://schema.plantphenomics.org.au/ObservationUnit)
[appn:Assay](https://schema.plantphenomics.org.au/Assay) appn:hasResult [schema:Dataset](https://schema.org/Dataset)
[appn:Assay](https://schema.plantphenomics.org.au/Assay) appn:hasResult [schema:File](https://schema.org/File)
[appn:Assay](https://schema.plantphenomics.org.au/Assay) appn:hasResult [appn:Sample](https://schema.plantphenomics.org.au/Sample)
[appn:ResearchActivity](https://schema.plantphenomics.org.au/ResearchActivity) appn:isPartOf [appn:ResearchActivity](https://schema.plantphenomics.org.au/ResearchActivity)
