# Variable
[https://schema.plantphenomics.org.au/Variable](https://schema.plantphenomics.org.au/Variable)

Representation of a Trait using a defined Scale. In the DDI-CDI Variable Cascade, a Variable is a RepresentedVariable or an InstanceVriable.

![UML diagram for Variable](/ttl_uml/ttl_appn_Variable.png)

## Superclasses
* https://www.w3.org/ns/sosa/Property
* http://ddialliance.org/Specification/DDI-CDI/1.0/RDF/RepresentedVariable
* https://schema.org/InstanceValue
## Properties
* Variable https://schema.plantphenomics.org.au/hasDefaultValue
* appn:Variable **appn:hasTrait** [appn:Trait](/doc/appn_Trait.md)
    * Identified the Trait associated with a Variable.
* appn:Variable **appn:hasScale** [appn:Scale](/doc/appn_Scale.md)
    * Identified the Scale associated with a Variable.
## Subclasses
* [https://schema.plantphenomics.org.au/ObservedVariable](/doc/appn_ObservedVariable.md)
* [https://schema.plantphenomics.org.au/ControlledVariable](/doc/appn_ControlledVariable.md)
* [https://schema.plantphenomics.org.au/TreatmentVariable](/doc/appn_TreatmentVariable.md)
