# BiologicalUnit
[https://schema.plantphenomics.org.au/BiologicalUnit](https://schema.plantphenomics.org.au/BiologicalUnit)

![UML diagram for BiologicalUnit](/ttl_uml/ttl_appn_BiologicalUnit.png)
## Superclasses
* [https://schema.plantphenomics.org.au/ObservationUnit](/doc/appn_ObservationUnit.md)
* https://schema.org/Thing
* http://purl.org/ppeo/PPEO.owl#ObservationUnit
* https://www.w3.org/ns/sosa/FeatureOfInterest
* https://bioschemas.org/BioChemEntity
## Properties
* appn:BiologicalUnit appn:hasBiologicalUnitType [appn:BiologicalUnitType](/doc/appn_BiologicalUnitType.md)
* appn:BiologicalUnit appn:hasBiologicalMaterial [appn:BiologicalMaterial](/doc/appn_BiologicalMaterial.md)
* [appn:Assay](/doc/appn_Assay.md) appn:isForObservationUnit [appn:ObservationUnit](/doc/appn_ObservationUnit.md)
* [appn:ObservationUnit](/doc/appn_ObservationUnit.md) appn:inheritsContext [appn:ObservationUnit](/doc/appn_ObservationUnit.md)
* [appn:ObservationUnit](/doc/appn_ObservationUnit.md) appn:hasLocation [appn:SpatialLocation](/doc/appn_SpatialLocation.md)
* [appn:SpatialLocation](/doc/appn_SpatialLocation.md) appn:isLocationWithin [appn:ObservationUnit](/doc/appn_ObservationUnit.md)
## Subclasses
* [https://schema.plantphenomics.org.au/Sample](/doc/appn_Sample.md)
