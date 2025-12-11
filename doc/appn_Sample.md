# Sample
[https://schema.plantphenomics.org.au/Sample](https://schema.plantphenomics.org.au/Sample)

A BiologicalUnit that has been created from an existing BiologicalUnit through a Sampling assay.

![UML diagram for Sample](/ttl_uml/ttl_appn_Sample.png)

## Superclasses
* https://www.w3.org/ns/sosa/Sample
* [https://schema.plantphenomics.org.au/BiologicalUnit](/doc/appn_BiologicalUnit.md)
* [https://schema.plantphenomics.org.au/ObservationUnit](/doc/appn_ObservationUnit.md)
* https://schema.org/Thing
* http://www.w3.org/ns/prov#Entity
* http://purl.org/ppeo/PPEO.owl#ObservationUnit
* https://www.w3.org/ns/sosa/FeatureOfInterest
* https://bioschemas.org/BioChemEntity
## Properties
* [appn:Sampling](/doc/appn_Sampling.md) **appn:producesSample** appn:Sample
    * Identifies the Sample produced by a Sampling assay.
* [appn:Assay](/doc/appn_Assay.md) **appn:isForObservationUnit** [appn:ObservationUnit](/doc/appn_ObservationUnit.md)
    * Relates an Assay to an ObservationUnit for which it is carried out.
* [appn:SpatialLocation](/doc/appn_SpatialLocation.md) **appn:isLocationWithin** [appn:ObservationUnit](/doc/appn_ObservationUnit.md)
    * Specifies that a location is a position within an ObservationUnit
