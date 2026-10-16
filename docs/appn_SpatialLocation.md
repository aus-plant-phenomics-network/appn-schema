# SpatialLocation
[https://schema.plantphenomics.org.au/SpatialLocation](https://schema.plantphenomics.org.au/SpatialLocation)

A location defined with geospatial coordinates.

![UML diagram for SpatialLocation](images/ttl_appn_SpatialLocation.png)

## Superclasses
* [https://schema.plantphenomics.org.au/Location](appn_Location.md)
* http://purl.org/ppeo/PPEO.owl#spatial_distribution
* http://schema.org/Thing
* http://purl.org/ppeo/PPEO.owl#GPS_location
* http://schema.org/Place
## Properties
* appn:SpatialLocation **appn:hasLatitude** [xsd:float](http://www.w3.org/2001/XMLSchema#float)
    * Decimal latitude for a SpatialLocation
* appn:SpatialLocation **appn:hasLongitude** [xsd:float](http://www.w3.org/2001/XMLSchema#float)
    * Decimal longitude for a SpatialLocation
* appn:SpatialLocation **appn:hasUncertainty** [xsd:float](http://www.w3.org/2001/XMLSchema#float)
    * Uncertainty in meters for coordinates
* appn:SpatialLocation **appn:hasAltitude** [xsd:float](http://www.w3.org/2001/XMLSchema#float)
    * Altitude for a SpatialLocation
* appn:SpatialLocation **appn:hasCountry** [appn:Country](appn_Country.md)
    * Country for a SpatialLocation
* appn:SpatialLocation **appn:hasAddress** [xsd:string](http://www.w3.org/2001/XMLSchema#string)
    * Address for a SpatialLocation
* [appn:ObservationUnit](appn_ObservationUnit.md) **appn:hasLocation** [appn:Location](appn_Location.md)
    * Specifies the location for an ObservationUnit.
* [appn:Location](appn_Location.md) **appn:isLocationWithin** [appn:ObservationUnit](appn_ObservationUnit.md)
    * Specifies that a location is a position within an ObservationUnit.
