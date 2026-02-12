# SubstanceQuantity
[https://schema.plantphenomics.org.au/SubstanceQuantity](https://schema.plantphenomics.org.au/SubstanceQuantity)

A Variable (representation of a quantity using a defined Scale) for a Substance applied to an ObservationUnit.

![UML diagram for SubstanceQuantity](/ttl_uml/ttl_appn_SubstanceQuantity.png)

## Superclasses
* [https://schema.plantphenomics.org.au/Variable](/doc/appn_Variable.md)
* https://www.w3.org/ns/sosa/Property
* http://ddialliance.org/Specification/DDI-CDI/1.0/RDF/RepresentedVariable
* https://schema.org/InstanceValue
## Properties
* [appn:Treatment](/doc/appn_Treatment.md) **appn:treatsWith** appn:SubstanceQuantity
    * Identifies a Substance or a SubstanceQuantity associated with a Treatment assay. The Treatment makes an input of a quantity of some Substance associated with the SubstanceQuantity. If the result is a known final state for a variable associated with an ObservationUnit, the assay should be modeled as a Control with a ControlledVariable. Treatments are for cases where no definite resulting value is recorded.
* appn:SubstanceQuantity **appn:isOfSubstance** [appn:Substance](/doc/appn_Substance.md)
    * Identifies the Substance associated with a SubstanceQuantity. This represents the biological or chemical substance applied to the ObservationUnit by a Treatment.
* appn:SubstanceQuantity **appn:amount** [appn:Substance](/doc/appn_Substance.md)
    * Identifies the amount of a Substance associated with a SubstanceQuantity according to the associated Scale.
* appn:SubstanceQuantity **appn:hasScale** [appn:Scale](/doc/appn_Scale.md)
    * Identifies the Scale associated with a Variable.
* SubstanceQuantity https://schema.plantphenomics.org.au/hasDefaultValue
* [appn:Variable](/doc/appn_Variable.md) **appn:usedMethod** [appn:Method](/doc/appn_Method.md)
    * Identifies a Method used to conduct an Assay.
* [appn:Variable](/doc/appn_Variable.md) **appn:forBiologicalUnitType** [appn:BiologicalUnitType](/doc/appn_BiologicalUnitType.md)
    * Links a Variable to the BiologicalUnitType to which it relates.
* [appn:Variable](/doc/appn_Variable.md) **appn:forBiologicalMaterial** [appn:BiologicalMaterial](/doc/appn_BiologicalMaterial.md)
    * Links a Variable to the BiologicalMaterial (i.e. crop) to which it relates.
* [appn:Variable](/doc/appn_Variable.md) **appn:hasScale** [appn:Scale](/doc/appn_Scale.md)
    * Identifies the Scale associated with a Variable.
