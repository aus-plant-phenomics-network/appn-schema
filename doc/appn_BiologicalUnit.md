# BiologicalUnit
[https://schema .plantphenomics .org .au/BiologicalUnit](https://schema .plantphenomics .org .au/BiologicalUnit)

A plant or set of plants sharing the same BiologicalMaterial (e .g . a plot or crop in a field) or any Sample of a plant (e .g . an individual organ or leaf clipping) or set of plants (e .g . a cut from a plot) that is treated as an ObservationUnit for collecting or reporting data . BiologicalUnits may be part of larger BiologicalUnits . For example a plant (BiologicalUnit) may be part of a cohort (BiologicalUnit) sharing the same BiologicalMaterial and Treatments . Where relevant, the position of a BiologicalUnit within a larger BiologicalUnit or within a GrowthFacility can be specified using a SpatialLocation .

![UML diagram for BiologicalUnit](/ttl_uml/ttl_appn_BiologicalUnit.png)

## Superclasses
* [https://schema .plantphenomics .org .au/ObservationUnit](/doc/appn_ObservationUnit.md)
* https://schema .org/Thing
* http://www .w3 .org/ns/prov#Entity
* http://purl .org/ppeo/PPEO .owl#ObservationUnit
* https://www .w3 .org/ns/sosa/FeatureOfInterest
* https://bioschemas .org/BioChemEntity
## Properties
* appn:BiologicalUnit **appn:hasBiologicalUnitType** [appn:BiologicalUnitType](/doc/appn_BiologicalUnitType.md)
    * Links a BiologicalUnit to its type
* appn:BiologicalUnit **appn:hasBiologicalMaterial** [appn:BiologicalMaterial](/doc/appn_BiologicalMaterial.md)
    * Links a BiologicalUnit to its genetic material
* [appn:Assay](/doc/appn_Assay.md) **appn:isForObservationUnit** [appn:ObservationUnit](/doc/appn_ObservationUnit.md)
    * Relates an Assay to an ObservationUnit for which it is carried out .
* [appn:ObservationUnit](/doc/appn_ObservationUnit.md) **appn:inheritsContext** [appn:ObservationUnit](/doc/appn_ObservationUnit.md)
    * inheritsContext
* [appn:ObservationUnit](/doc/appn_ObservationUnit.md) **appn:hasLocation** [appn:SpatialLocation](/doc/appn_SpatialLocation.md)
    * Specifies the location for an ObservationUnit
* [appn:SpatialLocation](/doc/appn_SpatialLocation.md) **appn:isLocationWithin** [appn:ObservationUnit](/doc/appn_ObservationUnit.md)
    * Specifies that a location is a position within an ObservationUnit
## Subclasses
* [https://schema .plantphenomics .org .au/Sample](/doc/appn_Sample.md)
