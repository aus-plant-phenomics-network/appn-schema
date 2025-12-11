# Person
[https://schema .plantphenomics .org .au/Person](https://schema .plantphenomics .org .au/Person)

A Person, preferably identified using an ORCID, that may perform an Assay .

![UML diagram for Person](/ttl_uml/ttl_appn_Person.png)

## Superclasses
* [https://schema .plantphenomics .org .au/Observer](/doc/appn_Observer.md)
* https://www .w3 .org/ns/sosa/Sensor
* [https://schema .plantphenomics .org .au/Controller](/doc/appn_Controller.md)
* https://www .w3 .org/ns/sosa/Actuator
* [https://schema .plantphenomics .org .au/Sampler](/doc/appn_Sampler.md)
* https://www .w3 .org/ns/sosa/Sampler
* https://schema .org/Person
## Properties
* [appn:Observation](/doc/appn_Observation.md) **appn:madeByObserver** [appn:Observer](/doc/appn_Observer.md)
    * Identifies the entity (Observer, i .e . one of a Person, Sensor or SoftwareApplication) responsible for carrying out an Observation .
* [appn:Control](/doc/appn_Control.md) **appn:madeByController** [appn:Controller](/doc/appn_Controller.md)
    * Identifies the entity (Controller, i .e . one of a Person, Actuator, SoftwareApplication or ExternalEvent) responsible for carrying out a Control or Treatment .
* [appn:Treatment](/doc/appn_Treatment.md) **appn:madeByController** [appn:Controller](/doc/appn_Controller.md)
    * Identifies the entity (Controller, i .e . one of a Person, Actuator, SoftwareApplication or ExternalEvent) responsible for carrying out a Control or Treatment .
* [appn:Sampling](/doc/appn_Sampling.md) **appn:madeBySampler** [appn:Sampler](/doc/appn_Sampler.md)
    * Identifies the entity (Sampler, i .e . a Person - no other subclasses defined yet) responsible for carrying out an Sampling .
