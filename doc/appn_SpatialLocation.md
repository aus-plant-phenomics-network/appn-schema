# SpatialLocation
[https://schema.plantphenomics.org.au/SpatialLocation](https://schema.plantphenomics.org.au/SpatialLocation)

A position associated with the placement of a GrowthFacility within another GrowthFacility or of a BiologicalUnit within another BiologicalUnit or GrowthFacility. Position may be expressed as absolute geospatial coordinates or using a locally appropriate organisation into rows and columns (and optionally levels).

![UML diagram for SpatialLocation](/ttl_uml/ttl_appn_SpatialLocation.png)

## Superclasses
* http://purl.org/ppeo/PPEO.owl#SpatialDistribution
* https://schema.org/Thing
## Properties
* [appn:ObservationUnit](/doc/appn_ObservationUnit.md) **appn:hasLocation** appn:SpatialLocation
    * Specifies the location for an ObservationUnit.
* appn:SpatialLocation **appn:isLocationWithin** [appn:ObservationUnit](/doc/appn_ObservationUnit.md)
    * Specifies that a location is a position within an ObservationUnit.
* SpatialLocation https://schema.plantphenomics.org.au/row
* SpatialLocation https://schema.plantphenomics.org.au/column
* SpatialLocation https://schema.plantphenomics.org.au/level
