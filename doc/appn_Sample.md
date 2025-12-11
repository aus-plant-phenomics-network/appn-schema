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
    * An Assay that derives a new representative ObservationUnit from an existing ObservationUnit.
* [appn:Assay](/doc/appn_Assay.md) **appn:isForObservationUnit** [appn:ObservationUnit](/doc/appn_ObservationUnit.md)
    * A research action that observes or modifies a set of ObservationUnits.
* [appn:SpatialLocation](/doc/appn_SpatialLocation.md) **appn:isLocationWithin** [appn:ObservationUnit](/doc/appn_ObservationUnit.md)
    * A position associated with the placement of a GrowthFacility within another GrowthFacility or of a BiologicalUnit within another BiologicalUnit or GrowthFacility. Position may be expressed as absolute geospatial coordinates or using a locally appropriate organisation into rows and columns (and optionally levels).
