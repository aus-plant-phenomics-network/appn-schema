# BiologicalMaterial
[https://schema.plantphenomics.org.au/BiologicalMaterial](https://schema.plantphenomics.org.au/BiologicalMaterial)

A taxonomic and/or genetic profile for one or more BiologicalUnits. Where possible, this should include the material source for the BiologicalMaterial.

![UML diagram for BiologicalMaterial](/ttl_uml/ttl_appn_BiologicalMaterial.png)

## Superclasses
* http://purl.org/ppeo/PPEO.owl#biological_material
* https://bioschemas.org/Taxon
## Properties
* [appn:Variable](/doc/appn_Variable.md) **appn:forBiologicalMaterial** appn:BiologicalMaterial
    * Links a Variable to the BiologicalMaterial (i.e. crop) to which it relates.
* [appn:BiologicalUnit](/doc/appn_BiologicalUnit.md) **appn:hasBiologicalMaterial** appn:BiologicalMaterial
    * Identifies the BiologicalMaterial for a BiologicalUnit.
* appn:BiologicalMaterial **appn:hasMaterialSource** [appn:MaterialSource](/doc/appn_MaterialSource.md)
    * Identifies the MaterialSource for BiologicalMaterial.
