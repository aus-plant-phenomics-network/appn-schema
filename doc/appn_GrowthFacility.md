# GrowthFacility
[https://schema.plantphenomics.org.au/GrowthFacility](https://schema.plantphenomics.org.au/GrowthFacility)

![UML diagram for GrowthFacility](/ttl_uml/ttl_appn_GrowthFacility.png)
## Superclasses
* [https://schema.plantphenomics.org.au/Platform](/doc/appn_Platform.md)
* https://www.w3.org/ns/sosa/Platform
* https://schema.org/IndividualProduct
* [https://schema.plantphenomics.org.au/ObservationUnit](/doc/appn_ObservationUnit.md)
* https://schema.org/Thing
* http://purl.org/ppeo/PPEO.owl#ObservationUnit
* https://www.w3.org/ns/sosa/FeatureOfInterest
## Properties
* appn:GrowthFacility appn:hasGrowthFacilityType [appn:GrowthFacilityType](/doc/appn_GrowthFacilityType.md)
* GrowthFacility https://schema.plantphenomics.org.au/deployedOnPlatform
* [appn:Assay](/doc/appn_Assay.md) appn:isForObservationUnit [appn:ObservationUnit](/doc/appn_ObservationUnit.md)
* [appn:ObservationUnit](/doc/appn_ObservationUnit.md) appn:inheritsContext [appn:ObservationUnit](/doc/appn_ObservationUnit.md)
* [appn:ObservationUnit](/doc/appn_ObservationUnit.md) appn:hasLocation [appn:SpatialLocation](/doc/appn_SpatialLocation.md)
* [appn:SpatialLocation](/doc/appn_SpatialLocation.md) appn:isLocationWithin [appn:ObservationUnit](/doc/appn_ObservationUnit.md)
