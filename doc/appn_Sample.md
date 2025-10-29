# Sample
[https://schema.plantphenomics.org.au/Sample](https://schema.plantphenomics.org.au/Sample)

![UML diagram for Sample](/ttl_uml/ttl_appn_Sample.png)
## Superclasses
* https://www.w3.org/ns/sosa/Sample
* https://schema.plantphenomics.org.au/BiologicalUnit
* https://schema.plantphenomics.org.au/ObservationUnit
* https://schema.org/Thing
* http://purl.org/ppeo/PPEO.owl#ObservationUnit
* https://www.w3.org/ns/sosa/FeatureOfInterest
* https://bioschemas.org/BioChemEntity
## Properties
[appn:Assay]([appn:Assay](/doc/appn_Assay.md)) appn:hasResult appn:Sample
[appn:BiologicalUnit](/doc/appn_BiologicalUnit.md) appn:hasBiologicalUnitType [appn:BiologicalUnitType](/doc/appn_BiologicalUnitType.md)
[appn:BiologicalUnit](/doc/appn_BiologicalUnit.md) appn:hasBiologicalMaterial [appn:BiologicalMaterial](/doc/appn_BiologicalMaterial.md)
[appn:Assay]([appn:Assay](/doc/appn_Assay.md)) appn:isForObservationUnit [appn:ObservationUnit](/doc/appn_ObservationUnit.md)
[appn:ObservationUnit](/doc/appn_ObservationUnit.md) appn:inheritsContext [appn:ObservationUnit](/doc/appn_ObservationUnit.md)
[appn:ObservationUnit](/doc/appn_ObservationUnit.md) appn:hasLocation [appn:SpatialLocation](/doc/appn_SpatialLocation.md)
[appn:SpatialLocation]([appn:SpatialLocation](/doc/appn_SpatialLocation.md)) appn:isLocationWithin [appn:ObservationUnit](/doc/appn_ObservationUnit.md)
