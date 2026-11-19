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
* appn:SpatialLocation **appn:hasPolygon** [xsd:string](http://www.w3.org/2001/XMLSchema#string)
    * WKT for a polygon
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
* [appn:Location](appn_Location.md) **appn:hasLocationSchema** [appn:LocationSchema](appn_LocationSchema.md)
    * Specifies the schema defining the levels in describing a Location.
* [appn:Location](appn_Location.md) **appn:schemaFirstLevel** [xsd:string](http://www.w3.org/2001/XMLSchema#string)
    * Specifies the most signicant level of organisation when specifying a location.
* [appn:Location](appn_Location.md) **appn:schemaFirstLevel** [xsd:integer](http://www.w3.org/2001/XMLSchema#integer)
    * Specifies the most signicant level of organisation when specifying a location.
* [appn:Location](appn_Location.md) **appn:schemaFirstLevel** [xsd:decimal](http://www.w3.org/2001/XMLSchema#decimal)
    * Specifies the most signicant level of organisation when specifying a location.
* [appn:Location](appn_Location.md) **appn:schemaSecondLevel** [xsd:string](http://www.w3.org/2001/XMLSchema#string)
    * Specifies the second most signicant level of organisation when specifying a location.
* [appn:Location](appn_Location.md) **appn:schemaSecondLevel** [xsd:integer](http://www.w3.org/2001/XMLSchema#integer)
    * Specifies the second most signicant level of organisation when specifying a location.
* [appn:Location](appn_Location.md) **appn:schemaSecondLevel** [xsd:decimal](http://www.w3.org/2001/XMLSchema#decimal)
    * Specifies the second most signicant level of organisation when specifying a location.
* [appn:Location](appn_Location.md) **appn:schemaThirdLevel** [xsd:string](http://www.w3.org/2001/XMLSchema#string)
    * Specifies the third most signicant level of organisation when specifying a location.
* [appn:Location](appn_Location.md) **appn:schemaThirdLevel** [xsd:integer](http://www.w3.org/2001/XMLSchema#integer)
    * Specifies the third most signicant level of organisation when specifying a location.
* [appn:Location](appn_Location.md) **appn:schemaThirdLevel** [xsd:decimal](http://www.w3.org/2001/XMLSchema#decimal)
    * Specifies the third most signicant level of organisation when specifying a location.
* [appn:Location](appn_Location.md) **appn:schemaFourthLevel** [xsd:string](http://www.w3.org/2001/XMLSchema#string)
    * Specifies the fourth most signicant level of organisation when specifying a location.
* [appn:Location](appn_Location.md) **appn:schemaFourthLevel** [xsd:integer](http://www.w3.org/2001/XMLSchema#integer)
    * Specifies the fourth most signicant level of organisation when specifying a location.
* [appn:Location](appn_Location.md) **appn:schemaFourthLevel** [xsd:decimal](http://www.w3.org/2001/XMLSchema#decimal)
    * Specifies the fourth most signicant level of organisation when specifying a location.
* [appn:Location](appn_Location.md) **appn:schemaFifthLevel** [xsd:string](http://www.w3.org/2001/XMLSchema#string)
    * Specifies the fifth most signicant level of organisation when specifying a location.
* [appn:Location](appn_Location.md) **appn:schemaFifthLevel** [xsd:integer](http://www.w3.org/2001/XMLSchema#integer)
    * Specifies the fifth most signicant level of organisation when specifying a location.
* [appn:Location](appn_Location.md) **appn:schemaFifthLevel** [xsd:decimal](http://www.w3.org/2001/XMLSchema#decimal)
    * Specifies the fifth most signicant level of organisation when specifying a location.
* [appn:Location](appn_Location.md) **appn:schemaSixthLevel** [xsd:string](http://www.w3.org/2001/XMLSchema#string)
    * Specifies the sixth most signicant level of organisation when specifying a location.
* [appn:Location](appn_Location.md) **appn:schemaSixthLevel** [xsd:integer](http://www.w3.org/2001/XMLSchema#integer)
    * Specifies the sixth most signicant level of organisation when specifying a location.
* [appn:Location](appn_Location.md) **appn:schemaSixthLevel** [xsd:decimal](http://www.w3.org/2001/XMLSchema#decimal)
    * Specifies the sixth most signicant level of organisation when specifying a location.
* [appn:Location](appn_Location.md) **appn:schemaSeventhLevel** [xsd:string](http://www.w3.org/2001/XMLSchema#string)
    * Specifies the seventh most signicant level of organisation when specifying a location.
* [appn:Location](appn_Location.md) **appn:schemaSeventhLevel** [xsd:integer](http://www.w3.org/2001/XMLSchema#integer)
    * Specifies the seventh most signicant level of organisation when specifying a location.
* [appn:Location](appn_Location.md) **appn:schemaSeventhLevel** [xsd:decimal](http://www.w3.org/2001/XMLSchema#decimal)
    * Specifies the seventh most signicant level of organisation when specifying a location.
* [appn:Location](appn_Location.md) **appn:schemaEighthLevel** [xsd:string](http://www.w3.org/2001/XMLSchema#string)
    * Specifies the eighth most signicant level of organisation when specifying a location.
* [appn:Location](appn_Location.md) **appn:schemaEighthLevel** [xsd:integer](http://www.w3.org/2001/XMLSchema#integer)
    * Specifies the eighth most signicant level of organisation when specifying a location.
* [appn:Location](appn_Location.md) **appn:schemaEighthLevel** [xsd:decimal](http://www.w3.org/2001/XMLSchema#decimal)
    * Specifies the eighth most signicant level of organisation when specifying a location.
* [appn:Location](appn_Location.md) **appn:startTime** [xsd:dateTime](http://www.w3.org/2001/XMLSchema#dateTime)
    * The time at which a ResearchActivity started
* [appn:Location](appn_Location.md) **appn:endTime** [xsd:dateTime](http://www.w3.org/2001/XMLSchema#dateTime)
    * The time at which a ResearchActivity ended
* [appn:Location](appn_Location.md) **appn:atTime** [xsd:dateTime](http://www.w3.org/2001/XMLSchema#dateTime)
    * The time at which a ResearchActivity occurred - equivalent to both startTime and endTime
