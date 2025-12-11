# ExternalEvent
[https://schema.plantphenomics.org.au/ExternalEvent](https://schema.plantphenomics.org.au/ExternalEvent)

A default entity to represent any trigger outside the control of the experimenters that may affect the state of the experiment and alter a Variable of interest, e.g. severe weather events or equipment failures. Where possible, the resulting state of the experiment should be quantified and the ExternalEvent modeled as the Controller for a Control event. Where quantification is impossible, the ExternalEvent should be modeled as the Controller for a Treatment event.

![UML diagram for ExternalEvent](/ttl_uml/ttl_appn_ExternalEvent.png)

## Superclasses
* [https://schema.plantphenomics.org.au/Controller](/doc/appn_Controller.md)
* https://www.w3.org/ns/sosa/Actuator
* https://schema.org/Event
## Properties
* [appn:Control](/doc/appn_Control.md) **appn:madeByController** [appn:Controller](/doc/appn_Controller.md)
    * Identifies the entity (Controller, i.e. one of a Person, Actuator, SoftwareApplication or ExternalEvent) responsible for carrying out a Control or Treatment.
* [appn:Treatment](/doc/appn_Treatment.md) **appn:madeByController** [appn:Controller](/doc/appn_Controller.md)
    * Identifies the entity (Controller, i.e. one of a Person, Actuator, SoftwareApplication or ExternalEvent) responsible for carrying out a Control or Treatment.
