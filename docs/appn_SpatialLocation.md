# SpatialLocation
[https://schema.plantphenomics.org.au/SpatialLocation](https://schema.plantphenomics.org.au/SpatialLocation)

A location defined with geospatial coordinates. The definition of the location should include a schema:geo property with coordinates or a shape.

![UML diagram for SpatialLocation](images/ttl_appn_SpatialLocation.png)

## Superclasses
* [https://schema.plantphenomics.org.au/Location](appn_Location.md)
* http://purl.org/ppeo/PPEO.owl#spatial_distribution
* https://schema.org/Thing
* https://schema.org/Place
## Properties
* [appn:ObservationUnit](appn_ObservationUnit.md) **appn:hasLocation** [appn:Location](appn_Location.md)
    * Specifies the location for an ObservationUnit.
* [appn:Location](appn_Location.md) **appn:isLocationWithin** [appn:ObservationUnit](appn_ObservationUnit.md)
    * Specifies that a location is a position within an ObservationUnit.
