# XYZLocation
[https://schema.plantphenomics.org.au/XYZLocation](https://schema.plantphenomics.org.au/XYZLocation)

A location defined using an appropriate local spatial geometry in three dimensions.

![UML diagram for XYZLocation](images/ttl_appn_XYZLocation.png)

## Superclasses
* [https://schema.plantphenomics.org.au/Location](appn_Location.md)
* http://purl.org/ppeo/PPEO.owl#spatial_distribution
* https://schema.org/Thing
## Properties
* XYZLocation https://schema.plantphenomics.org.au/row
* XYZLocation https://schema.plantphenomics.org.au/column
* XYZLocation https://schema.plantphenomics.org.au/level
* [appn:ObservationUnit](appn_ObservationUnit.md) **appn:hasLocation** [appn:Location](appn_Location.md)
    * Specifies the location for an ObservationUnit.
* [appn:Location](appn_Location.md) **appn:isLocationWithin** [appn:ObservationUnit](appn_ObservationUnit.md)
    * Specifies that a location is a position within an ObservationUnit.
