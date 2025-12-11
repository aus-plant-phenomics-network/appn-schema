# Observation
[https://schema.plantphenomics.org.au/Observation](https://schema.plantphenomics.org.au/Observation)

An Assay that observes or measures properties of one or more ObservationUnits returning results as property values or images.

![UML diagram for Observation](/ttl_uml/ttl_appn_Observation.png)

## Superclasses
* [https://schema.plantphenomics.org.au/Assay](/doc/appn_Assay.md)
* [https://schema.plantphenomics.org.au/ResearchActivity](/doc/appn_ResearchActivity.md)
* https://schema.org/Action
* http://www.w3.org/ns/prov#Activity
* https://www.w3.org/ns/sosa/Execution
* http://purl.org/ppeo/PPEO.owl#Assay
* http://purl.org/ppeo/PPEO.owl#Observation
## Properties
* appn:Observation **appn:hasResult** [schema:Dataset](https://schema.org/Dataset)
    * Identifies a data output from an Observation or Control assay. Individual values are represented by sosa:hasSimpleResult.
* appn:Observation **appn:hasResult** [schema:File](https://schema.org/File)
    * Identifies a data output from an Observation or Control assay. Individual values are represented by sosa:hasSimpleResult.
* appn:Observation **appn:usesData** [schema:Dataset](https://schema.org/Dataset)
    * Identifies a data input to an Observation assay. This is intended for use in relation to Observations delivered using a SoftwareApplication.
* appn:Observation **appn:usesData** [schema:File](https://schema.org/File)
    * Identifies a data input to an Observation assay. This is intended for use in relation to Observations delivered using a SoftwareApplication.
