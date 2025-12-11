# ObservationUnit
[https://schema.plantphenomics.org.au/ObservationUnit](https://schema.plantphenomics.org.au/ObservationUnit)

An entity for which a Study collects data or controls the environment and other parameters. ObservationUnits may be BiologicalUnits or GrowthFacilities.

![UML diagram for ObservationUnit](/ttl_uml/ttl_appn_ObservationUnit.png)

## Superclasses
* https://schema.org/Thing
* http://www.w3.org/ns/prov#Entity
* http://purl.org/ppeo/PPEO.owl#ObservationUnit
* https://www.w3.org/ns/sosa/FeatureOfInterest
## Properties
* [appn:Assay](/doc/appn_Assay.md) **appn:isForObservationUnit** appn:ObservationUnit
    * A research action that observes or modifies a set of ObservationUnits.
* [appn:SpatialLocation](/doc/appn_SpatialLocation.md) **appn:isLocationWithin** appn:ObservationUnit
    * A position associated with the placement of a GrowthFacility within another GrowthFacility or of a BiologicalUnit within another BiologicalUnit or GrowthFacility. Position may be expressed as absolute geospatial coordinates or using a locally appropriate organisation into rows and columns (and optionally levels).
## Subclasses
* [https://schema.plantphenomics.org.au/GrowthFacility](/doc/appn_GrowthFacility.md)
* [https://schema.plantphenomics.org.au/BiologicalUnit](/doc/appn_BiologicalUnit.md)
* [https://schema.plantphenomics.org.au/Sample](/doc/appn_Sample.md)
