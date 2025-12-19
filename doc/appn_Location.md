# Location
[https://schema.plantphenomics.org.au/Location](https://schema.plantphenomics.org.au/Location)

A position associated with the placement of a GrowthFacility within another GrowthFacility or of a BiologicalUnit within another BiologicalUnit or GrowthFacility. Position may be expressed as absolute geospatial coordinates (SpatialLocation) or using a locally appropriate organisation into rows and columns and optionally levels (XYZLocation).

![UML diagram for Location](/ttl_uml/ttl_appn_Location.png)

## Superclasses
* http://purl.org/ppeo/PPEO.owl#spatial_distribution
* https://schema.org/Thing
## Properties
* [appn:ObservationUnit](/doc/appn_ObservationUnit.md) **appn:hasLocation** appn:Location
    * Specifies the location for an ObservationUnit.
* appn:Location **appn:isLocationWithin** [appn:ObservationUnit](/doc/appn_ObservationUnit.md)
    * Specifies that a location is a position within an ObservationUnit.
## Subclasses
* [https://schema.plantphenomics.org.au/SpatialLocation](/doc/appn_SpatialLocation.md)
* [https://schema.plantphenomics.org.au/XYZLocation](/doc/appn_XYZLocation.md)
