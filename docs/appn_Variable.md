# Variable
[https://schema.plantphenomics.org.au/Variable](https://schema.plantphenomics.org.au/Variable)

Representation of a Trait using a defined Scale. In the DDI-CDI Variable Cascade, a Variable is a RepresentedVariable or an InstanceVariable.

![UML diagram for Variable](images/ttl_appn_Variable.png)

## Superclasses
* [https://schema.plantphenomics.org.au/Trait](appn_Trait.md)
* http://purl.org/ppeo/PPEO.owl#trait
* http://ddialliance.org/Specification/DDI-CDI/1.0/RDF/Concept
* http://schema.org/DefinedTerm
* http://www.w3.org/ns/sosa/Property
* http://ddialliance.org/Specification/DDI-CDI/1.0/RDF/RepresentedVariable
* http://schema.org/InstanceValue
## Properties
* appn:Variable **appn:hasDefaultValue** [xsd:string](http://www.w3.org/2001/XMLSchema#string)
    * Specifies the default value for a variable.
* appn:Variable **appn:hasDefaultValue** [xsd:integer](http://www.w3.org/2001/XMLSchema#integer)
    * Specifies the default value for a variable.
* appn:Variable **appn:hasDefaultValue** [xsd:float](http://www.w3.org/2001/XMLSchema#float)
    * Specifies the default value for a variable.
* appn:Variable **appn:hasDefaultValue** [xsd:double](http://www.w3.org/2001/XMLSchema#double)
    * Specifies the default value for a variable.
* appn:Variable **appn:hasDefaultValue** [xsd:boolean](http://www.w3.org/2001/XMLSchema#boolean)
    * Specifies the default value for a variable.
* appn:Variable **appn:usedMethod** [appn:Method](appn_Method.md)
    * Identifies a Method used to conduct an Assay or to derive values for a Variable.
* appn:Variable **appn:forBiologicalUnitType** [appn:BiologicalUnitType](appn_BiologicalUnitType.md)
    * Links a Variable to the BiologicalUnitType to which it relates.
* appn:Variable **appn:forBiologicalMaterial** [appn:BiologicalMaterial](appn_BiologicalMaterial.md)
    * Links a Variable to the BiologicalMaterial (i.e. crop) to which it relates.
* appn:Variable **appn:hasScale** [appn:Scale](appn_Scale.md)
    * Identifies the Scale associated with a Variable.
* [appn:ObservedVariable](appn_ObservedVariable.md) **appn:hasTrait** [appn:Trait](appn_Trait.md)
    * Identifies the Trait associated with a Variable.
* [appn:ControlledVariable](appn_ControlledVariable.md) **appn:hasTrait** [appn:Trait](appn_Trait.md)
    * Identifies the Trait associated with a Variable.
## Subclasses
* [https://schema.plantphenomics.org.au/ObservedVariable](appn_ObservedVariable.md)
* [https://schema.plantphenomics.org.au/ControlledVariable](appn_ControlledVariable.md)
* [https://schema.plantphenomics.org.au/SubstanceAmount](appn_SubstanceAmount.md)
