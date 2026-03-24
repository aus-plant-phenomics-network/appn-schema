# SoftwareApplication
[https://schema.plantphenomics.org.au/SoftwareApplication](https://schema.plantphenomics.org.au/SoftwareApplication)

A piece of software that may be perform an Assay. Note that SOSA maps software components to prov:Agent, but CDIF recommendation is that Agent should be an intentional role.

![UML diagram for SoftwareApplication](/ttl_uml/ttl_appn_SoftwareApplication.png)

## Superclasses
* https://bioschemas.org/ComputationalWorkflow
* [https://schema.plantphenomics.org.au/Observer](/docs/appn_Observer.md)
* https://www.w3.org/ns/sosa/Sensor
* [https://schema.plantphenomics.org.au/Controller](/docs/appn_Controller.md)
* https://www.w3.org/ns/sosa/Actuator
## Properties
* [appn:Observation](/docs/appn_Observation.md) **appn:madeByObserver** [appn:Observer](/docs/appn_Observer.md)
    * Identifies the entity (Observer, i.e. one of a Person, Sensor or SoftwareApplication) responsible for carrying out an Observation.
* [appn:Control](/docs/appn_Control.md) **appn:madeByController** [appn:Controller](/docs/appn_Controller.md)
    * Identifies the entity (Controller, i.e. one of a Person, Actuator, SoftwareApplication or ExternalEvent) responsible for carrying out a Control or Treatment.
* [appn:Treatment](/docs/appn_Treatment.md) **appn:madeByController** [appn:Controller](/docs/appn_Controller.md)
    * Identifies the entity (Controller, i.e. one of a Person, Actuator, SoftwareApplication or ExternalEvent) responsible for carrying out a Control or Treatment.
