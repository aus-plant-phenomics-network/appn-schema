# Control
[https://schema.plantphenomics.org.au/Control](https://schema.plantphenomics.org.au/Control)

![UML diagram for Control](/ttl_uml/ttl_appn_Control.png)
## Superclasses
* [appn]:Assay](/doc/appn_Assay.md)
* [appn]:ResearchActivity](/doc/appn_ResearchActivity.md)
* https://schema.org/Action
* https://www.w3.org/ns/sosa/Execution
* http://purl.org/ppeo/PPEO.owl#Assay
## Properties
* appn:Control appn:madeByController [appn:Controller](/doc/appn_Controller.md)
* appn:Control appn:controls [appn:ControlledVariable](/doc/appn_ControlledVariable.md)
* [appn:Assay](/doc/appn_Assay.md) appn:isForObservationUnit [appn:ObservationUnit](/doc/appn_ObservationUnit.md)
* [appn:Assay](/doc/appn_Assay.md) appn:hasResult [schema:Dataset](https://schema.org/Dataset)
* [appn:Assay](/doc/appn_Assay.md) appn:hasResult [schema:File](https://schema.org/File)
* [appn:Assay](/doc/appn_Assay.md) appn:hasResult [appn:Sample](/doc/appn_Sample.md)
* [appn:ResearchActivity](/doc/appn_ResearchActivity.md) appn:isPartOf [appn:ResearchActivity](/doc/appn_ResearchActivity.md)
