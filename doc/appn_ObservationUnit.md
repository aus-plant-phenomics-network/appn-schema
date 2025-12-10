# ObservationUnit
[https://schema.plantphenomics.org.au/ObservationUnit](https://schema.plantphenomics.org.au/ObservationUnit)

An entity for which a Study collects data.

![UML diagram for ObservationUnit](/ttl_uml/ttl_appn_ObservationUnit.png)

## Superclasses
* https://schema.org/Thing
* http://www.w3.org/ns/prov#Entity
* http://purl.org/ppeo/PPEO.owl#ObservationUnit
* https://www.w3.org/ns/sosa/FeatureOfInterest
## Properties
* [appn:Assay](/doc/appn_Assay.md) appn:isForObservationUnit appn:ObservationUnit
* appn:ObservationUnit appn:inheritsContext [appn:ObservationUnit](/doc/appn_ObservationUnit.md)
* appn:ObservationUnit appn:hasLocation [appn:SpatialLocation](/doc/appn_SpatialLocation.md)
* [appn:SpatialLocation](/doc/appn_SpatialLocation.md) appn:isLocationWithin appn:ObservationUnit
## Subclasses
* [https://schema.plantphenomics.org.au/GrowthFacility](/doc/appn_GrowthFacility.md)
* [https://schema.plantphenomics.org.au/BiologicalUnit](/doc/appn_BiologicalUnit.md)
* [https://schema.plantphenomics.org.au/Sample](/doc/appn_Sample.md)
