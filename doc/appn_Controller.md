# Controller
[https://schema.plantphenomics.org.au/Controller](https://schema.plantphenomics.org.au/Controller)

The entity responsible for performing an Control action and delivering a value for a ControlledVariable. The Controller may be a Person, an Actuator, a SoftwareApplication or an ExternalEvent. Note that SOSA maps sosa:Actuator to prov:Agent, but CDIF recommendation is that Agent should be an intentional role.

![UML diagram for Controller](/ttl_uml/ttl_appn_Controller.png)

## Superclasses
* https://www.w3.org/ns/sosa/Actuator
## Properties
* [appn:Control](/doc/appn_Control.md) **appn:madeByController** appn:Controller
    * An Assay that modifies a property of one or more ObservationUnits.
* [appn:Treatment](/doc/appn_Treatment.md) **appn:madeByController** appn:Controller
    * An Assay that adds or removes a quantity of some Variable to a set of ObservationUnits but no resulting state value is recorded.
## Subclasses
* [https://schema.plantphenomics.org.au/Actuator](/doc/appn_Actuator.md)
* [https://schema.plantphenomics.org.au/ExternalEvent](/doc/appn_ExternalEvent.md)
* [https://schema.plantphenomics.org.au/Person](/doc/appn_Person.md)
* [https://schema.plantphenomics.org.au/SoftwareApplication](/doc/appn_SoftwareApplication.md)
