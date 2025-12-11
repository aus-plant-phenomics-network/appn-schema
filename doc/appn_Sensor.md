# Sensor
[https://schema.plantphenomics.org.au/Sensor](https://schema.plantphenomics.org.au/Sensor)

An electromechanical device that can return the value for an ObservedVariable and that may be mounted on a Platform. Note that SOSA maps electromechanical components to prov:Agent, but CDIF recommendation is that Agent should be an intentional role.

![UML diagram for Sensor](/ttl_uml/ttl_appn_Sensor.png)

## Superclasses
* [https://schema.plantphenomics.org.au/Observer](/doc/appn_Observer.md)
* https://www.w3.org/ns/sosa/Sensor
* https://schema.org/IndividualProduct
## Properties
* [appn:Deployment](/doc/appn_Deployment.md) **appn:deployedSystem** appn:Sensor
* [appn:Observation](/doc/appn_Observation.md) **appn:madeByObserver** [appn:Observer](/doc/appn_Observer.md)
    * Identifies the entity (Observer, i.e. one of a Person, Sensor or SoftwareApplication) responsible for carrying out an Observation.
