# GrowthFacility
[https://schema.plantphenomics.org.au/GrowthFacility](https://schema.plantphenomics.org.au/GrowthFacility)

A building, enclosed space, field unit, container or other entity in which plants are grown. GrowthFacilities may be nested inside other GrowthFacilities, e.g. rhizoboxes inside a growth chamber, to any depth. GrowthFacilities include all non-biological ObservationUnits and may be defined for each spatial context at which environmental observations are collected or management actions (Treatments) are performed for one or more BiologicalUnits. Where relevant, the position of a GrowthFacility within a larger GrowthFacility can be specified using a SpatialLocation. GrowthFacilities may be Platforms for Sensors and Actuators.

![UML diagram for GrowthFacility](/ttl_uml/ttl_appn_GrowthFacility.png)

## Superclasses
* [https://schema.plantphenomics.org.au/Platform](/doc/appn_Platform.md)
* https://www.w3.org/ns/sosa/Platform
* https://schema.org/IndividualProduct
* [https://schema.plantphenomics.org.au/ObservationUnit](/doc/appn_ObservationUnit.md)
* https://schema.org/Thing
* http://www.w3.org/ns/prov#Entity
* http://purl.org/ppeo/PPEO.owl#ObservationUnit
* https://www.w3.org/ns/sosa/FeatureOfInterest
## Properties
* appn:GrowthFacility appn:hasGrowthFacilityType [appn:GrowthFacilityType](/doc/appn_GrowthFacilityType.md)
* [appn:Deployment](/doc/appn_Deployment.md) appn:deployedOnPlatform [appn:Platform](/doc/appn_Platform.md)
* [appn:Assay](/doc/appn_Assay.md) appn:isForObservationUnit [appn:ObservationUnit](/doc/appn_ObservationUnit.md)
* [appn:ObservationUnit](/doc/appn_ObservationUnit.md) appn:inheritsContext [appn:ObservationUnit](/doc/appn_ObservationUnit.md)
* [appn:ObservationUnit](/doc/appn_ObservationUnit.md) appn:hasLocation [appn:SpatialLocation](/doc/appn_SpatialLocation.md)
* [appn:SpatialLocation](/doc/appn_SpatialLocation.md) appn:isLocationWithin [appn:ObservationUnit](/doc/appn_ObservationUnit.md)
