# Treatment
[https://schema.plantphenomics.org.au/Treatment](https://schema.plantphenomics.org.au/Treatment)

An Assay that adds or removes a quantity of some Variable to a set of ObservationUnits but no resulting state value is recorded.

![UML diagram for Treatment](/ttl_uml/ttl_appn_Treatment.png)

## Superclasses
* [https://schema.plantphenomics.org.au/Assay](/doc/appn_Assay.md)
* [https://schema.plantphenomics.org.au/ResearchActivity](/doc/appn_ResearchActivity.md)
* https://schema.org/Action
* http://www.w3.org/ns/prov#Activity
* https://www.w3.org/ns/sosa/Execution
* http://purl.org/ppeo/PPEO.owl#Assay
## Properties
* appn:Treatment appn:madeByController [appn:Controller](/doc/appn_Controller.md)
* appn:Treatment appn:treats [appn:TreatmentVariable](/doc/appn_TreatmentVariable.md)
* [appn:Assay](/doc/appn_Assay.md) appn:isForObservationUnit [appn:ObservationUnit](/doc/appn_ObservationUnit.md)
* [appn:Assay](/doc/appn_Assay.md) appn:usedMethod [appn:Method](/doc/appn_Method.md)
* [appn:ResearchActivity](/doc/appn_ResearchActivity.md) appn:isPartOf [appn:ResearchActivity](/doc/appn_ResearchActivity.md)
