# Role
[https://schema.plantphenomics.org.au/Role](https://schema.plantphenomics.org.au/Role)

A role performed by a person in the context of a research activity

![UML diagram for Role](images/ttl_appn_Role.png)

## Superclasses
* http://schema.org/Role
* http://purl.org/ppeo/PPEO.owl#role
## Properties
* [appn:Person](appn_Person.md) **appn:hasRole** appn:Role
    * Indicates a role for a Person in a ResearchActivity
* appn:Role **appn:isRoleOfPersonIn** [appn:ResearchActivity](appn_ResearchActivity.md)
    * Indicates a ResearchActivity in which a Person has a Role
