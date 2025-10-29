# BiologicalUnit
[https://schema.plantphenomics.org.au/BiologicalUnit](https://schema.plantphenomics.org.au/BiologicalUnit)

![UML diagram for BiologicalUnit](/ttl_uml/ttl_appn_BiologicalUnit.png)
## Superclasses
* https://schema.plantphenomics.org.au/ObservationUnit
* https://schema.org/Thing
* http://purl.org/ppeo/PPEO.owl#ObservationUnit
* https://www.w3.org/ns/sosa/FeatureOfInterest
* https://bioschemas.org/BioChemEntity
## Properties
appn:BiologicalUnit appn:hasBiologicalUnitType [appn:BiologicalUnitType](https://schema.plantphenomics.org.au/BiologicalUnitType)
appn:BiologicalUnit appn:hasBiologicalMaterial [appn:BiologicalMaterial](https://schema.plantphenomics.org.au/BiologicalMaterial)
[appn:Assay](https://schema.plantphenomics.org.au/Assay) appn:isForObservationUnit [appn:ObservationUnit](https://schema.plantphenomics.org.au/ObservationUnit)
[appn:ObservationUnit](https://schema.plantphenomics.org.au/ObservationUnit) appn:inheritsContext [appn:ObservationUnit](https://schema.plantphenomics.org.au/ObservationUnit)
[appn:ObservationUnit](https://schema.plantphenomics.org.au/ObservationUnit) appn:hasLocation [appn:SpatialLocation](https://schema.plantphenomics.org.au/SpatialLocation)
[appn:SpatialLocation](https://schema.plantphenomics.org.au/SpatialLocation) appn:isLocationWithin [appn:ObservationUnit](https://schema.plantphenomics.org.au/ObservationUnit)
## Subclasses
* https://schema.plantphenomics.org.au/Sample
