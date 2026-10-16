# ObservedVariable
[https://schema.plantphenomics.org.au/ObservedVariable](https://schema.plantphenomics.org.au/ObservedVariable)

A Variable (representation of a Trait using a defined Scale) observed or measured for an ObservationUnit.

![UML diagram for ObservedVariable](images/ttl_appn_ObservedVariable.png)

## Superclasses
* http://purl.org/ppeo/PPEO.owl#observed_variable
* http://www.w3.org/ns/sosa/ObservableProperty
* [https://schema.plantphenomics.org.au/Variable](appn_Variable.md)
* [https://schema.plantphenomics.org.au/Trait](appn_Trait.md)
* http://purl.org/ppeo/PPEO.owl#trait
* http://ddialliance.org/Specification/DDI-CDI/1.0/RDF/Concept
* http://schema.org/DefinedTerm
* http://www.w3.org/ns/sosa/Property
* http://ddialliance.org/Specification/DDI-CDI/1.0/RDF/RepresentedVariable
* http://schema.org/InstanceValue
## Properties
* [appn:Observation](appn_Observation.md) **appn:observes** appn:ObservedVariable
    * Identifies an ObservedVariable controlled by an Observation assay. The Observation records or estimates the state of the ObservationVariable recorded as a value specified in a hasResult or hasSimpleResult property.
* appn:ObservedVariable **appn:hasTrait** [appn:Trait](appn_Trait.md)
    * Identifies the Trait associated with a Variable.
* [appn:Variable](appn_Variable.md) **appn:hasDefaultValue** [xsd:string](http://www.w3.org/2001/XMLSchema#string)
    * Specifies the default value for a variable.
* [appn:Variable](appn_Variable.md) **appn:hasDefaultValue** [xsd:integer](http://www.w3.org/2001/XMLSchema#integer)
    * Specifies the default value for a variable.
* [appn:Variable](appn_Variable.md) **appn:hasDefaultValue** [xsd:float](http://www.w3.org/2001/XMLSchema#float)
    * Specifies the default value for a variable.
* [appn:Variable](appn_Variable.md) **appn:hasDefaultValue** [xsd:double](http://www.w3.org/2001/XMLSchema#double)
    * Specifies the default value for a variable.
* [appn:Variable](appn_Variable.md) **appn:hasDefaultValue** [xsd:boolean](http://www.w3.org/2001/XMLSchema#boolean)
    * Specifies the default value for a variable.
* [appn:Variable](appn_Variable.md) **appn:usedMethod** [appn:Method](appn_Method.md)
    * Identifies a Method used to conduct an Assay or to derive values for a Variable.
* [appn:Variable](appn_Variable.md) **appn:forBiologicalUnitType** [appn:BiologicalUnitType](appn_BiologicalUnitType.md)
    * Links a Variable to the BiologicalUnitType to which it relates.
* [appn:Variable](appn_Variable.md) **appn:forBiologicalMaterial** [appn:BiologicalMaterial](appn_BiologicalMaterial.md)
    * Links a Variable to the BiologicalMaterial (i.e. crop) to which it relates.
* [appn:Variable](appn_Variable.md) **appn:hasScale** [appn:Scale](appn_Scale.md)
    * Identifies the Scale associated with a Variable.
* [appn:ObservedVariable](appn_ObservedVariable.md) **appn:hasTrait** [appn:Trait](appn_Trait.md)
    * Identifies the Trait associated with a Variable.
* [appn:ControlledVariable](appn_ControlledVariable.md) **appn:hasTrait** [appn:Trait](appn_Trait.md)
    * Identifies the Trait associated with a Variable.
