# Person
[https://schema.plantphenomics.org.au/Person](https://schema.plantphenomics.org.au/Person)

A Person, preferably identified using an ORCID, that may perform an Assay.

![UML diagram for Person](/ttl_uml/ttl_appn_Person.png)

## Superclasses
* [https://schema.plantphenomics.org.au/Observer](/doc/appn_Observer.md)
* https://www.w3.org/ns/sosa/Sensor
* [https://schema.plantphenomics.org.au/Controller](/doc/appn_Controller.md)
* https://www.w3.org/ns/sosa/Actuator
* [https://schema.plantphenomics.org.au/Sampler](/doc/appn_Sampler.md)
* https://www.w3.org/ns/sosa/Sampler
* https://schema.org/Person
## Properties
* [appn:Observation](/doc/appn_Observation.md) **appn:madeByObserver** [appn:Observer](/doc/appn_Observer.md)
    * An Assay that observes or measures properties of one or more ObservationUnits returning results as property values or images.
* [appn:Control](/doc/appn_Control.md) **appn:madeByController** [appn:Controller](/doc/appn_Controller.md)
    * An Assay that modifies a property of one or more ObservationUnits.
* [appn:Treatment](/doc/appn_Treatment.md) **appn:madeByController** [appn:Controller](/doc/appn_Controller.md)
    * An Assay that adds or removes a quantity of some Variable to a set of ObservationUnits but no resulting state value is recorded.
* [appn:Sampling](/doc/appn_Sampling.md) **appn:madeBySampler** [appn:Sampler](/doc/appn_Sampler.md)
    * An Assay that derives a new representative ObservationUnit from an existing ObservationUnit.
