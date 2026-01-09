# BiologicalUnitType
[https://schema.plantphenomics.org.au/BiologicalUnitType](https://schema.plantphenomics.org.au/BiologicalUnitType)

A term from an enumeration of types of BiologicalUnit.

![UML diagram for BiologicalUnitType](/ttl_uml/ttl_appn_BiologicalUnitType.png)

## Superclasses
* https://schema.org/Enumeration
## Properties
* [appn:BiologicalUnit](/doc/appn_BiologicalUnit.md) **appn:hasBiologicalUnitType** appn:BiologicalUnitType
    * Links a BiologicalUnit to its type.
* [appn:Variable](/doc/appn_Variable.md) **appn:forBiologicalUnitType** appn:BiologicalUnitType
    * Links a Variable to the BiologicalUnitType to which it relates.
* [appn:Variable](/doc/appn_Variable.md) **appn:forBiologicalMaterial** appn:BiologicalUnitType
    * Links a Variable to the BiologicalMaterial (i.e. crop) to which it relates.
