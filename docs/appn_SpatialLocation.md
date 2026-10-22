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
* appn:SpatialLocation **appn:hasLatitude** [xsd:decimal](http://www.w3.org/2001/XMLSchema#decimal)
    * Decimal latitude for a SpatialLocation
* appn:SpatialLocation **appn:hasLongitude** [xsd:decimal](http://www.w3.org/2001/XMLSchema#decimal)
    * Decimal longitude for a SpatialLocation
* appn:SpatialLocation **appn:hasUncertainty** [xsd:decimal](http://www.w3.org/2001/XMLSchema#decimal)
    * Uncertainty in meters for coordinates
* appn:SpatialLocation **appn:hasAltitude** [xsd:decimal](http://www.w3.org/2001/XMLSchema#decimal)
    * Altitude for a SpatialLocation
* appn:SpatialLocation **appn:hasCountry** [appn:Country](appn_Country.md)
    * Country for a SpatialLocation
* appn:SpatialLocation **appn:hasAddress** [xsd:string](http://www.w3.org/2001/XMLSchema#string)
    * Address for a SpatialLocation
* [appn:Location](appn_Location.md) **appn:isLocationFor** [appn:ObservationUnit](appn_ObservationUnit.md)
    * Specifies the ObservationUnit to which a Location relates.
* [appn:Location](appn_Location.md) **appn:isLocationWithin** [appn:ObservationUnit](appn_ObservationUnit.md)
    * Specifies that a Location is a position within an ObservationUnit.
* [appn:Location](appn_Location.md) **appn:startTime** [xsd:dateTime](http://www.w3.org/2001/XMLSchema#dateTime)
    * The time at which a ResearchActivity started
* [appn:Location](appn_Location.md) **appn:endTime** [xsd:dateTime](http://www.w3.org/2001/XMLSchema#dateTime)
    * The time at which a ResearchActivity ended
* [appn:Location](appn_Location.md) **appn:atTime** [xsd:dateTime](http://www.w3.org/2001/XMLSchema#dateTime)
    * The time at which a ResearchActivity occurred - equivalent to both startTime and endTime
