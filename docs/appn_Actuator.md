# Actuator
[https://schema.plantphenomics.org.au/Actuator](https://schema.plantphenomics.org.au/Actuator)

An electromechanical device that can control the value for a ControlledVariable and that may be mounted on a Platform. Note that SOSA maps electromechanical components to prov:Agent, but CDIF recommendation is that Agent should be an intentional role.

![UML diagram for Actuator](/ttl_uml/ttl_appn_Actuator.png)

## Superclasses
* [https://schema.plantphenomics.org.au/Controller](/docs/appn_Controller.md)
* https://www.w3.org/ns/sosa/Actuator
* https://schema.org/IndividualProduct
## Properties
* [appn:Deployment](/docs/appn_Deployment.md) **appn:deployedSystem** appn:Actuator
    * Identifies a Sensor or Actuator deployed on a Platform.
* [appn:Control](/docs/appn_Control.md) **appn:madeByController** [appn:Controller](/docs/appn_Controller.md)
    * Identifies the entity (Controller, i.e. one of a Person, Actuator, SoftwareApplication or ExternalEvent) responsible for carrying out a Control or Treatment.
* [appn:Treatment](/docs/appn_Treatment.md) **appn:madeByController** [appn:Controller](/docs/appn_Controller.md)
    * Identifies the entity (Controller, i.e. one of a Person, Actuator, SoftwareApplication or ExternalEvent) responsible for carrying out a Control or Treatment.
