# BiologicalUnit
[https://schema.plantphenomics.org.au/BiologicalUnit](https://schema.plantphenomics.org.au/BiologicalUnit)

A plant or set of plants sharing the same BiologicalMaterial (e.g. a plot or crop in a field) or any Sample of a plant (e.g. an individual organ or leaf clipping) or set of plants (e.g. a cut from a plot) that is treated as an ObservationUnit for collecting or reporting data. BiologicalUnits may be part of larger BiologicalUnits. For example a plant (BiologicalUnit) may be part of a cohort (BiologicalUnit) sharing the same BiologicalMaterial and Treatments. Where relevant, the position of a BiologicalUnit within a larger BiologicalUnit or within a GrowthFacility can be specified using a SpatialLocation.

![UML diagram for BiologicalUnit](/ttl_uml/ttl_appn_BiologicalUnit.png)

## Superclasses
* [https://schema.plantphenomics.org.au/ObservationUnit](/doc/appn_ObservationUnit.md)
* https://schema.org/Thing
* http://www.w3.org/ns/prov#Entity
* http://purl.org/ppeo/PPEO.owl#observation_unit
* https://www.w3.org/ns/sosa/FeatureOfInterest
* https://bioschemas.org/BioChemEntity
## Properties
* appn:BiologicalUnit **appn:hasBiologicalUnitType** [appn:BiologicalUnitType](/doc/appn_BiologicalUnitType.md)
    * Links a BiologicalUnit to its type.
* [appn:Sample](/doc/appn_Sample.md) **appn:derivesFrom** appn:BiologicalUnit
    * Identifies the BiologicalUnit from which a Sample was sampled.
* appn:BiologicalUnit **appn:hasBiologicalMaterial** [appn:BiologicalMaterial](/doc/appn_BiologicalMaterial.md)
    * Identifies the BiologicalMaterial for a BiologicalUnit.
* [appn:Assay](/doc/appn_Assay.md) **appn:isForObservationUnit** [appn:ObservationUnit](/doc/appn_ObservationUnit.md)
    * Relates an Assay to an ObservationUnit for which it is carried out. Note that when the Assay is an Observation, the model should infer a schema:observationAbout property from isForObservationUnit.
* [appn:ObservationUnit](/doc/appn_ObservationUnit.md) **appn:inheritsContext** [appn:ObservationUnit](/doc/appn_ObservationUnit.md)
    * Indicates an ObservationUnit should be considered to inherit values for Variables from another ObservationUnit. Examples include a plant inheriting environmental variables from a pot, growth cabinet or field or a leaf inheriting environmental and developmental properties from a plant.
* [appn:ObservationUnit](/doc/appn_ObservationUnit.md) **appn:hasLocation** [appn:SpatialLocation](/doc/appn_SpatialLocation.md)
    * Specifies the location for an ObservationUnit.
* [appn:SpatialLocation](/doc/appn_SpatialLocation.md) **appn:isLocationWithin** [appn:ObservationUnit](/doc/appn_ObservationUnit.md)
    * Specifies that a location is a position within an ObservationUnit.
## Subclasses
* [https://schema.plantphenomics.org.au/Sample](/doc/appn_Sample.md)
