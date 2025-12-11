# Observer
[https://schema.plantphenomics.org.au/Observer](https://schema.plantphenomics.org.au/Observer)

The entity responsible for performing an Observation and delivering a value for an ObservedVariable. The Observer may be a Person, a Sensor or a SoftwareApplication. Note that SOSA maps sosa:Sensor to prov:Agent, but CDIF recommendation is that Agent should be an intentional role.

![UML diagram for Observer](/ttl_uml/ttl_appn_Observer.png)

## Superclasses
* https://www.w3.org/ns/sosa/Sensor
## Properties
* [appn:Observation](/doc/appn_Observation.md) **appn:madeByObserver** appn:Observer
    * Identifies the entity (Observer, i.e. one of a Person, Sensor or SoftwareApplication) responsible for carrying out an Observation.
## Subclasses
* [https://schema.plantphenomics.org.au/Sensor](/doc/appn_Sensor.md)
* [https://schema.plantphenomics.org.au/Person](/doc/appn_Person.md)
* [https://schema.plantphenomics.org.au/SoftwareApplication](/doc/appn_SoftwareApplication.md)
