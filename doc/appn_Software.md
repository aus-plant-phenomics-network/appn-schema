# Software
[https://schema.plantphenomics.org.au/Software](https://schema.plantphenomics.org.au/Software)

A piece of software that may be perform an Assay. Note that SOSA maps software components to prov:Agent, but CDIF recommendation is that Agent should be an intentional role.

![UML diagram for Software](/ttl_uml/ttl_appn_Software.png)

## Superclasses
* https://bioschemas.org/ComputationalWorkflow
* [https://schema.plantphenomics.org.au/Observer](/doc/appn_Observer.md)
* https://www.w3.org/ns/sosa/Sensor
* [https://schema.plantphenomics.org.au/Controller](/doc/appn_Controller.md)
* https://www.w3.org/ns/sosa/Actuator
## Properties
* [appn:Observation](/doc/appn_Observation.md) appn:madeByObserver [appn:Observer](/doc/appn_Observer.md)
* [appn:Control](/doc/appn_Control.md) appn:madeByController [appn:Controller](/doc/appn_Controller.md)
* [appn:Treatment](/doc/appn_Treatment.md) appn:madeByController [appn:Controller](/doc/appn_Controller.md)
