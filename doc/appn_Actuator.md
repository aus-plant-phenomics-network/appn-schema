# Actuator
[https://schema.plantphenomics.org.au/Actuator](https://schema.plantphenomics.org.au/Actuator)

An electromechanical device that can control the value for a ControlledVariable and that may be mounted on a Platform. Note that SOSA maps electromechanical components to prov:Agent, but CDIF recommendation is that Agent should be an intentional role.

![UML diagram for Actuator](/ttl_uml/ttl_appn_Actuator.png)

## Superclasses
* [https://schema.plantphenomics.org.au/Controller](/doc/appn_Controller.md)
* https://www.w3.org/ns/sosa/Actuator
* https://schema.org/IndividualProduct
## Properties
* [appn:Deployment](/doc/appn_Deployment.md) appn:deployedSystem appn:Actuator - A transient or long-term association between a Sensor or Actuator and a Platform on which it is mounted.
* [appn:Control](/doc/appn_Control.md) appn:madeByController [appn:Controller](/doc/appn_Controller.md) - An Assay that modifies a property of one or more ObservationUnits.
* [appn:Treatment](/doc/appn_Treatment.md) appn:madeByController [appn:Controller](/doc/appn_Controller.md) - An Assay that adds or removes a quantity of some Variable to a set of ObservationUnits but no resulting state value is recorded.
