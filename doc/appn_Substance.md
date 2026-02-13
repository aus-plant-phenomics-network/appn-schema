# Substance
[https://schema.plantphenomics.org.au/Substance](https://schema.plantphenomics.org.au/Substance)

A biological or chemical entity used in a Treatment assay or referenced in a SubstanceQuantity.

![UML diagram for Substance](/ttl_uml/ttl_appn_Substance.png)

## Superclasses
* [https://schema.plantphenomics.org.au/ObservationUnit](/doc/appn_ObservationUnit.md)
* https://schema.org/Thing
* http://www.w3.org/ns/prov#Entity
* http://purl.org/ppeo/PPEO.owl#observation_unit
* https://www.w3.org/ns/sosa/FeatureOfInterest
* https://bioschemas.org/Substance
## Properties
* [appn:Treatment](/doc/appn_Treatment.md) **appn:treatsWith** appn:Substance
    * Identifies a Substance or a SubstanceQuantity associated with a Treatment assay. The Treatment makes an input of a quantity of some Substance associated with the SubstanceQuantity. If the result is a known final state for a variable associated with an ObservationUnit, the assay should be modeled as a Control with a ControlledVariable. Treatments are for cases where no definite resulting value is recorded.
* appn:Substance **appn:hasComponent** [appn:Substance](/doc/appn_Substance.md)
    * Identifies a Substance or SubstanceQuantity included in the current Substance.
* appn:Substance **appn:hasComponent** [appn:SubstanceQuantity](/doc/appn_SubstanceQuantity.md)
    * Identifies a Substance or SubstanceQuantity included in the current Substance.
* [appn:SubstanceQuantity](/doc/appn_SubstanceQuantity.md) **appn:isOfSubstance** appn:Substance
    * Identifies the Substance associated with a SubstanceQuantity. This represents the biological or chemical substance applied to the ObservationUnit by a Treatment.
* [appn:Assay](/doc/appn_Assay.md) **appn:isForObservationUnit** [appn:ObservationUnit](/doc/appn_ObservationUnit.md)
    * Relates an Assay to an ObservationUnit for which it is carried out. Note that when the Assay is an Observation, the model should infer a schema:observationAbout property from isForObservationUnit.
* [appn:ObservationUnit](/doc/appn_ObservationUnit.md) **appn:inheritsContext** [appn:ObservationUnit](/doc/appn_ObservationUnit.md)
    * Indicates an ObservationUnit should be considered to inherit values for Variables from another ObservationUnit. Examples include a plant inheriting environmental variables from a pot, growth cabinet or field or a leaf inheriting environmental and developmental properties from a plant.
* [appn:ObservationUnit](/doc/appn_ObservationUnit.md) **appn:hasLocation** [appn:Location](/doc/appn_Location.md)
    * Specifies the location for an ObservationUnit.
* [appn:Location](/doc/appn_Location.md) **appn:isLocationWithin** [appn:ObservationUnit](/doc/appn_ObservationUnit.md)
    * Specifies that a location is a position within an ObservationUnit.
