# Sample
[https://schema.plantphenomics.org.au/Sample](https://schema.plantphenomics.org.au/Sample)

A BiologicalUnit that has been created from an existing BiologicalUnit through a Sampling assay.

![UML diagram for Sample](/ttl_uml/ttl_appn_Sample.png)

## Superclasses
* http://purl.org/ppeo/PPEO.owl#sample
* https://www.w3.org/ns/sosa/Sample
* [https://schema.plantphenomics.org.au/BiologicalUnit](/doc/appn_BiologicalUnit.md)
* [https://schema.plantphenomics.org.au/ObservationUnit](/doc/appn_ObservationUnit.md)
* https://schema.org/Thing
* http://www.w3.org/ns/prov#Entity
* http://purl.org/ppeo/PPEO.owl#observation_unit
* https://www.w3.org/ns/sosa/FeatureOfInterest
* https://bioschemas.org/BioChemEntity
## Properties
* [appn:Sampling](/doc/appn_Sampling.md) **appn:producesSample** appn:Sample
    * Identifies the Sample produced by a Sampling assay.
* appn:Sample **appn:derivesFrom** [appn:BiologicalUnit](/doc/appn_BiologicalUnit.md)
    * Identifies the BiologicalUnit from which a Sample was sampled.
* [appn:BiologicalUnit](/doc/appn_BiologicalUnit.md) **appn:hasBiologicalUnitType** [appn:BiologicalUnitType](/doc/appn_BiologicalUnitType.md)
    * Links a BiologicalUnit to its type.
* [appn:Sample](/doc/appn_Sample.md) **appn:derivesFrom** [appn:BiologicalUnit](/doc/appn_BiologicalUnit.md)
    * Identifies the BiologicalUnit from which a Sample was sampled.
* [appn:BiologicalUnit](/doc/appn_BiologicalUnit.md) **appn:hasBiologicalMaterial** [appn:BiologicalMaterial](/doc/appn_BiologicalMaterial.md)
    * Identifies the BiologicalMaterial for a BiologicalUnit.
* [appn:Assay](/doc/appn_Assay.md) **appn:isForObservationUnit** [appn:ObservationUnit](/doc/appn_ObservationUnit.md)
    * Relates an Assay to an ObservationUnit for which it is carried out. Note that when the Assay is an Observation, the model should infer a schema:observationAbout property from isForObservationUnit.
* [appn:ObservationUnit](/doc/appn_ObservationUnit.md) **appn:inheritsContext** [appn:ObservationUnit](/doc/appn_ObservationUnit.md)
    * Indicates an ObservationUnit should be considered to inherit values for Variables from another ObservationUnit. Examples include a plant inheriting environmental variables from a pot, growth cabinet or field or a leaf inheriting environmental and developmental properties from a plant.
* [appn:ObservationUnit](/doc/appn_ObservationUnit.md) **appn:hasLocation** [appn:SpatialLocation](/doc/appn_SpatialLocation.md)
    * Specifies the location for an ObservationUnit.
* [appn:SpatialLocation](/doc/appn_SpatialLocation.md) **appn:isLocationWithin** [appn:ObservationUnit](/doc/appn_ObservationUnit.md)
    * Specifies that a location is a position within an ObservationUnit.
