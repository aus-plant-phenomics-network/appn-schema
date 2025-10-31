# Sample
[https://schema.plantphenomics.org.au/Sample](https://schema.plantphenomics.org.au/Sample)

Sample.

![UML diagram for Sample](/ttl_uml/ttl_appn_Sample.png)

## Superclasses
* https://www.w3.org/ns/sosa/Sample
* [https://schema.plantphenomics.org.au/BiologicalUnit](/doc/appn_BiologicalUnit.md)
* [https://schema.plantphenomics.org.au/ObservationUnit](/doc/appn_ObservationUnit.md)
* https://schema.org/Thing
* http://purl.org/ppeo/PPEO.owl#ObservationUnit
* https://www.w3.org/ns/sosa/FeatureOfInterest
* https://bioschemas.org/BioChemEntity
## Properties
* [appn:Observation](/doc/appn_Observation.md) appn:hasResult appn:Sample
* [appn:Control](/doc/appn_Control.md) appn:hasResult appn:Sample
* [appn:Transformation](/doc/appn_Transformation.md) appn:hasResult appn:Sample
* [appn:Sampling](/doc/appn_Sampling.md) appn:hasResult appn:Sample
* [appn:BiologicalUnit](/doc/appn_BiologicalUnit.md) appn:hasBiologicalUnitType [appn:BiologicalUnitType](/doc/appn_BiologicalUnitType.md)
* [appn:BiologicalUnit](/doc/appn_BiologicalUnit.md) appn:hasBiologicalMaterial [appn:BiologicalMaterial](/doc/appn_BiologicalMaterial.md)
* [appn:Assay](/doc/appn_Assay.md) appn:isForObservationUnit [appn:ObservationUnit](/doc/appn_ObservationUnit.md)
* [appn:ObservationUnit](/doc/appn_ObservationUnit.md) appn:inheritsContext [appn:ObservationUnit](/doc/appn_ObservationUnit.md)
* [appn:ObservationUnit](/doc/appn_ObservationUnit.md) appn:hasLocation [appn:SpatialLocation](/doc/appn_SpatialLocation.md)
* [appn:SpatialLocation](/doc/appn_SpatialLocation.md) appn:isLocationWithin [appn:ObservationUnit](/doc/appn_ObservationUnit.md)
