# Country
[https://schema.plantphenomics.org.au/Country](https://schema.plantphenomics.org.au/Country)

A country

![UML diagram for Country](images/ttl_appn_Country.png)

## Superclasses
* http://schema.org/Country
* http://purl.org/ppeo/PPEO.owl#country
## Properties
* [appn:SpatialLocation](appn_SpatialLocation.md) **appn:hasCountry** appn:Country
    * Country for a SpatialLocation
* [appn:BiologicalMaterial](appn_BiologicalMaterial.md) **appn:hasCountryOfOrigin** appn:Country
    * Country from which BiologicalMaterial originated
* appn:Country **appn:hasCountryCode** [xsd:string](http://www.w3.org/2001/XMLSchema#string)
    * ISO 2-letter country code for country
