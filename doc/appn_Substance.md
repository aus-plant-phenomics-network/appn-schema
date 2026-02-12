# Substance
[https://schema.plantphenomics.org.au/Substance](https://schema.plantphenomics.org.au/Substance)

A biological or chemical entity used in a Treatment assay or referenced in a SubstanceQuantity.

![UML diagram for Substance](/ttl_uml/ttl_appn_Substance.png)

## Superclasses
* https://bioschemas.org/Substance
## Properties
* [appn:Treatment](/doc/appn_Treatment.md) **appn:treatsWith** appn:Substance
    * Identifies a Substance or a SubstanceQuantity associated with a Treatment assay. The Treatment makes an input of a quantity of some Substance associated with the SubstanceQuantity. If the result is a known final state for a variable associated with an ObservationUnit, the assay should be modeled as a Control with a ControlledVariable. Treatments are for cases where no definite resulting value is recorded.
* [appn:SubstanceQuantity](/doc/appn_SubstanceQuantity.md) **appn:isOfSubstance** appn:Substance
    * Identifies the Substance associated with a SubstanceQuantity. This represents the biological or chemical substance applied to the ObservationUnit by a Treatment.
* [appn:SubstanceQuantity](/doc/appn_SubstanceQuantity.md) **appn:amount** appn:Substance
    * Identifies the amount of a Substance associated with a SubstanceQuantity according to the associated Scale.
