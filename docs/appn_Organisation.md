# Organisation
[https://schema.plantphenomics.org.au/Organisation](https://schema.plantphenomics.org.au/Organisation)

An organization, preferably identified using an ROR.

![UML diagram for Organisation](images/ttl_appn_Organisation.png)

## Superclasses
* http://schema.org/Organization
## Properties
* appn:Organisation **appn:hasRole** [appn:Role](appn_Role.md)
    * Indicates a role for a Person or Organization in a ResearchActivity
* [appn:Person](appn_Person.md) **appn:affiliation** appn:Organisation
    * Associates a Person with an Organization with which they are affiliated.
* [appn:Grant](appn_Grant.md) **appn:funder** appn:Organisation
    * Associates an Organization with a Grant.
* [appn:Grant](appn_Grant.md) **appn:fundedOrganisation** appn:Organisation
    * Associates a recipient Organisation with a Grant.
* appn:Organisation **appn:ror** [xsd:anyURI](http://www.w3.org/2001/XMLSchema#anyURI)
    * The ROR for an Organization.
