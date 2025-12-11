# BiologicalUnit
[https://schema.plantphenomics.org.au/BiologicalUnit](https://schema.plantphenomics.org.au/BiologicalUnit)

A plant or set of plants sharing the same BiologicalMaterial (e.g. a plot or crop in a field) or any Sample of a plant (e.g. an individual organ or leaf clipping) or set of plants (e.g. a cut from a plot) that is treated as an ObservationUnit for collecting or reporting data. BiologicalUnits may be part of larger BiologicalUnits. For example a plant (BiologicalUnit) may be part of a cohort (BiologicalUnit) sharing the same BiologicalMaterial and Treatments. Where relevant, the position of a BiologicalUnit within a larger BiologicalUnit or within a GrowthFacility can be specified using a SpatialLocation.

![UML diagram for BiologicalUnit](/ttl_uml/ttl_appn_BiologicalUnit.png)

## Superclasses
* [https://schema.plantphenomics.org.au/ObservationUnit](/doc/appn_ObservationUnit.md)
* https://schema.org/Thing
* http://www.w3.org/ns/prov#Entity
* http://purl.org/ppeo/PPEO.owl#ObservationUnit
* https://www.w3.org/ns/sosa/FeatureOfInterest
* https://bioschemas.org/BioChemEntity
## Properties
* [appn:Assay](/doc/appn_Assay.md) appn:isForObservationUnit [appn:ObservationUnit](/doc/appn_ObservationUnit.md) - A research action that observes or modifies a set of ObservationUnits.
* [appn:SpatialLocation](/doc/appn_SpatialLocation.md) appn:isLocationWithin [appn:ObservationUnit](/doc/appn_ObservationUnit.md) - A position associated with the placement of a GrowthFacility within another GrowthFacility or of a BiologicalUnit within another BiologicalUnit or GrowthFacility. Position may be expressed as absolute geospatial coordinates or using a locally appropriate organisation into rows and columns (and optionally levels).
## Subclasses
* [https://schema.plantphenomics.org.au/Sample](/doc/appn_Sample.md)
