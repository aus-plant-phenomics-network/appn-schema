# ObservedVariable
[https://schema.plantphenomics.org.au/ObservedVariable](https://schema.plantphenomics.org.au/ObservedVariable)

A Variable (representation of a Trait using a defined Scale) observed or measured for one or more ObservationUnits.

![UML diagram for ObservedVariable](/ttl_uml/ttl_appn_ObservedVariable.png)

## Superclasses
* http://purl.org/ppeo/PPEO.owl#observed_variable
* [https://schema.plantphenomics.org.au/Variable](/doc/appn_Variable.md)
* https://www.w3.org/ns/sosa/Property
* http://ddialliance.org/Specification/DDI-CDI/1.0/RDF/RepresentedVariable
* https://schema.org/InstanceValue
## Properties
* [appn:Observation](/doc/appn_Observation.md) **appn:observes** appn:ObservedVariable
    * Identifies an ObservedVariable controlled by an Observation assay. The Observation records or estimates the state of the ObservationVariable recorded as a value specified in a hasResult or hasSimpleResult property.
* ObservedVariable https://schema.plantphenomics.org.au/hasDefaultValue
* [appn:Variable](/doc/appn_Variable.md) **appn:forBiologicalUnitType** [appn:BiologicalUnitType](/doc/appn_BiologicalUnitType.md)
    * Links a Variable to the BiologicalUnitType to which it relates.
* [appn:Variable](/doc/appn_Variable.md) **appn:forBiologicalMaterial** [appn:BiologicalUnitType](/doc/appn_BiologicalUnitType.md)
    * Links a Variable to the BiologicalMaterial (i.e. crop) to which it relates.
* [appn:Variable](/doc/appn_Variable.md) **appn:hasTrait** [appn:Trait](/doc/appn_Trait.md)
    * Identifies the Trait associated with a Variable.
* [appn:Variable](/doc/appn_Variable.md) **appn:hasScale** [appn:Scale](/doc/appn_Scale.md)
    * Identifies the Scale associated with a Variable.
