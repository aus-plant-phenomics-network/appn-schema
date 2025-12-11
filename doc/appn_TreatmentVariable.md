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
    * An Assay that adds or removes a quantity of some Variable to a set of ObservationUnits but no resulting state value is recorded.
* TreatmentVariable https://schema.plantphenomics.org.au/hasDefaultValue
