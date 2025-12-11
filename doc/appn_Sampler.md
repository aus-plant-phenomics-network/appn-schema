# Sampler
[https://schema .plantphenomics .org .au/Sampler](https://schema .plantphenomics .org .au/Sampler)

The entity responsible for performing a Sampling and delivering a Sample . The Observer will normally be a Person, although in some contexts some kind of device could be involved . Note that SOSA maps sosa:Sampler to prov:Agent, but CDIF recommendation is that Agent should be an intentional role .

![UML diagram for Sampler](/ttl_uml/ttl_appn_Sampler.png)

## Superclasses
* https://www .w3 .org/ns/sosa/Sampler
## Properties
* [appn:Sampling](/doc/appn_Sampling.md) **appn:madeBySampler** appn:Sampler
    * Identifies the entity (Sampler, i .e . a Person - no other subclasses defined yet) responsible for carrying out an Sampling .
## Subclasses
* [https://schema .plantphenomics .org .au/Person](/doc/appn_Person.md)
