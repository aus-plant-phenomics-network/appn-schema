# Person
[https://schema.plantphenomics.org.au/Person](https://schema.plantphenomics.org.au/Person)

A Person, preferably identified using an ORCID, that may perform an Assay.

![UML diagram for Person](/ttl_uml/ttl_appn_Person.png)

## Superclasses
* http://purl.org/ppeo/PPEO.owl#person
* [https://schema.plantphenomics.org.au/Observer](/docs/appn_Observer.md)
* https://www.w3.org/ns/sosa/Sensor
* [https://schema.plantphenomics.org.au/Controller](/docs/appn_Controller.md)
* https://www.w3.org/ns/sosa/Actuator
* [https://schema.plantphenomics.org.au/Sampler](/docs/appn_Sampler.md)
* https://www.w3.org/ns/sosa/Sampler
* https://schema.org/Person
## Properties
* [appn:Observation](/docs/appn_Observation.md) **appn:madeByObserver** [appn:Observer](/docs/appn_Observer.md)
    * Identifies the entity (Observer, i.e. one of a Person, Sensor or SoftwareApplication) responsible for carrying out an Observation.
* [appn:Control](/docs/appn_Control.md) **appn:madeByController** [appn:Controller](/docs/appn_Controller.md)
    * Identifies the entity (Controller, i.e. one of a Person, Actuator, SoftwareApplication or ExternalEvent) responsible for carrying out a Control or Treatment.
* [appn:Treatment](/docs/appn_Treatment.md) **appn:madeByController** [appn:Controller](/docs/appn_Controller.md)
    * Identifies the entity (Controller, i.e. one of a Person, Actuator, SoftwareApplication or ExternalEvent) responsible for carrying out a Control or Treatment.
* [appn:Sampling](/docs/appn_Sampling.md) **appn:madeBySampler** [appn:Sampler](/docs/appn_Sampler.md)
    * Identifies the entity (Sampler, i.e. a Person - no other subclasses defined yet) responsible for carrying out an Sampling.
