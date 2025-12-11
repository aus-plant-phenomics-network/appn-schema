# BiologicalUnitType
[https://schema.plantphenomics.org.au/BiologicalUnitType](https://schema.plantphenomics.org.au/BiologicalUnitType)

A term from an enumeration of types of BiologicalUnit.

![UML diagram for BiologicalUnitType](/ttl_uml/ttl_appn_BiologicalUnitType.png)

## Superclasses
* https://schema.org/Enumeration
## Properties
* [appn:BiologicalUnit](/doc/appn_BiologicalUnit.md) **appn:hasBiologicalUnitType** appn:BiologicalUnitType
    * A plant or set of plants sharing the same BiologicalMaterial (e.g. a plot or crop in a field) or any Sample of a plant (e.g. an individual organ or leaf clipping) or set of plants (e.g. a cut from a plot) that is treated as an ObservationUnit for collecting or reporting data. BiologicalUnits may be part of larger BiologicalUnits. For example a plant (BiologicalUnit) may be part of a cohort (BiologicalUnit) sharing the same BiologicalMaterial and Treatments. Where relevant, the position of a BiologicalUnit within a larger BiologicalUnit or within a GrowthFacility can be specified using a SpatialLocation.
