# SoftwareApplication
[https://schema.plantphenomics.org.au/SoftwareApplication](https://schema.plantphenomics.org.au/SoftwareApplication)

A piece of software that may be perform an Assay. Note that SOSA maps software components to prov:Agent, but CDIF recommendation is that Agent should be an intentional role.

![UML diagram for SoftwareApplication](/ttl_uml/ttl_appn_SoftwareApplication.png)

## Superclasses
* https://bioschemas.org/ComputationalWorkflow
* [https://schema.plantphenomics.org.au/Observer](/doc/appn_Observer.md)
* https://www.w3.org/ns/sosa/Sensor
* [https://schema.plantphenomics.org.au/Controller](/doc/appn_Controller.md)
* https://www.w3.org/ns/sosa/Actuator
## Properties
* [appn:Observation](/doc/appn_Observation.md) **appn:madeByObserver** [appn:Observer](/doc/appn_Observer.md)
    * An Assay that observes or measures properties of one or more ObservationUnits returning results as property values or images.
* [appn:Control](/doc/appn_Control.md) **appn:madeByController** [appn:Controller](/doc/appn_Controller.md)
    * An Assay that modifies a property of one or more ObservationUnits.
* [appn:Treatment](/doc/appn_Treatment.md) **appn:madeByController** [appn:Controller](/doc/appn_Controller.md)
    * An Assay that adds or removes a quantity of some Variable to a set of ObservationUnits but no resulting state value is recorded.
