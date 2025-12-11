# TreatmentVariable
[https://schema.plantphenomics.org.au/TreatmentVariable](https://schema.plantphenomics.org.au/TreatmentVariable)

A Variable (representation of a Trait using a defined Scale) modified for one or more ObservationUnits but with undefined resulting state.

![UML diagram for TreatmentVariable](/ttl_uml/ttl_appn_TreatmentVariable.png)

## Superclasses
* [https://schema.plantphenomics.org.au/Variable](/doc/appn_Variable.md)
* https://www.w3.org/ns/sosa/Property
* http://ddialliance.org/Specification/DDI-CDI/1.0/RDF/RepresentedVariable
* https://schema.org/InstanceValue
## Properties
* [appn:Treatment](/doc/appn_Treatment.md) **appn:treats** appn:TreatmentVariable
    * Identifies a TreatmentVariable controlled by a Treatment assay. The Treatment makes an input of some quantity associated with the TreatmentVariable. If the result is a known final state for a variable associated with an ObservationUnit, the assay should be modeled as a Control with a ControlledVariable. Treatments are for cases where no definite resulting value is recorded.
* TreatmentVariable https://schema.plantphenomics.org.au/hasDefaultValue
* [appn:Variable](/doc/appn_Variable.md) **appn:hasTrait** [appn:Trait](/doc/appn_Trait.md)
    * Identified the Trait associated with a Variable.
* [appn:Variable](/doc/appn_Variable.md) **appn:hasScale** [appn:Scale](/doc/appn_Scale.md)
    * Identified the Scale associated with a Variable.
