# BiologicalMaterial
[https://schema.plantphenomics.org.au/BiologicalMaterial](https://schema.plantphenomics.org.au/BiologicalMaterial)

A taxonomic and/or genetic profile for one or more BiologicalUnits. Where possible, this should include the material source for the BiologicalMaterial.

![UML diagram for BiologicalMaterial](/ttl_uml/ttl_appn_BiologicalMaterial.png)

## Superclasses
* http://purl.org/ppeo/PPEO.owl#BiologicalMaterial
* https://bioschemas.org/BioSample
## Properties
* [appn:BiologicalUnit](/doc/appn_BiologicalUnit.md) appn:hasBiologicalMaterial appn:BiologicalMaterial - A plant or set of plants sharing the same BiologicalMaterial (e.g. a plot or crop in a field) or any Sample of a plant (e.g. an individual organ or leaf clipping) or set of plants (e.g. a cut from a plot) that is treated as an ObservationUnit for collecting or reporting data. BiologicalUnits may be part of larger BiologicalUnits. For example a plant (BiologicalUnit) may be part of a cohort (BiologicalUnit) sharing the same BiologicalMaterial and Treatments. Where relevant, the position of a BiologicalUnit within a larger BiologicalUnit or within a GrowthFacility can be specified using a SpatialLocation.
