# XYZLocation
[https://schema.plantphenomics.org.au/XYZLocation](https://schema.plantphenomics.org.au/XYZLocation)

A location defined using an appropriate local spatial geometry in three dimensions.

![UML diagram for XYZLocation](/ttl_uml/ttl_appn_XYZLocation.png)

## Superclasses
* [https://schema.plantphenomics.org.au/Location](/doc/appn_Location.md)
* http://purl.org/ppeo/PPEO.owl#spatial_distribution
* https://schema.org/Thing
## Properties
* XYZLocation https://schema.plantphenomics.org.au/row
* XYZLocation https://schema.plantphenomics.org.au/column
* XYZLocation https://schema.plantphenomics.org.au/level
* [appn:ObservationUnit](/doc/appn_ObservationUnit.md) **appn:hasLocation** [appn:Location](/doc/appn_Location.md)
    * Specifies the location for an ObservationUnit.
* [appn:Location](/doc/appn_Location.md) **appn:isLocationWithin** [appn:ObservationUnit](/doc/appn_ObservationUnit.md)
    * Specifies that a location is a position within an ObservationUnit.
