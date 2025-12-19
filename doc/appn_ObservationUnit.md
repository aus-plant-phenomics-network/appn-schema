# ObservationUnit
[https://schema.plantphenomics.org.au/ObservationUnit](https://schema.plantphenomics.org.au/ObservationUnit)

An entity for which a Study collects data or controls the environment and other parameters. ObservationUnits may be BiologicalUnits or GrowthFacilities.

![UML diagram for ObservationUnit](/ttl_uml/ttl_appn_ObservationUnit.png)

## Superclasses
* https://schema.org/Thing
* http://www.w3.org/ns/prov#Entity
* http://purl.org/ppeo/PPEO.owl#observation_unit
* https://www.w3.org/ns/sosa/FeatureOfInterest
## Properties
* [appn:Assay](/doc/appn_Assay.md) **appn:isForObservationUnit** appn:ObservationUnit
    * Relates an Assay to an ObservationUnit for which it is carried out. Note that when the Assay is an Observation, the model should infer a schema:observationAbout property from isForObservationUnit.
* appn:ObservationUnit **appn:inheritsContext** [appn:ObservationUnit](/doc/appn_ObservationUnit.md)
    * Indicates an ObservationUnit should be considered to inherit values for Variables from another ObservationUnit. Examples include a plant inheriting environmental variables from a pot, growth cabinet or field or a leaf inheriting environmental and developmental properties from a plant.
* appn:ObservationUnit **appn:hasLocation** [appn:Location](/doc/appn_Location.md)
    * Specifies the location for an ObservationUnit.
* [appn:Location](/doc/appn_Location.md) **appn:isLocationWithin** appn:ObservationUnit
    * Specifies that a location is a position within an ObservationUnit.
## Subclasses
* [https://schema.plantphenomics.org.au/GrowthFacility](/doc/appn_GrowthFacility.md)
* [https://schema.plantphenomics.org.au/BiologicalUnit](/doc/appn_BiologicalUnit.md)
* [https://schema.plantphenomics.org.au/Sample](/doc/appn_Sample.md)
