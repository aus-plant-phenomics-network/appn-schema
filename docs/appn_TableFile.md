# TableFile
[https://schema.plantphenomics.org.au/TableFile](https://schema.plantphenomics.org.au/TableFile)

A data file containing tabular data in CSV or similar format

![UML diagram for TableFile](images/ttl_appn_TableFile.png)

## Superclasses
* [https://schema.plantphenomics.org.au/File](appn_File.md)
* http://schema.org/CreativeWork
* http://purl.org/ppeo/PPEO.owl#data_file
## Properties
* appn:TableFile **appn:containsInstancesOf** [rdf:Class](http://www.w3.org/1999/02/22-rdf-syntax-ns#Class)
    * Identifies schema class for which a TableFile serialises instances - the class is identified by its IRI
* appn:TableFile **appn:hasSchema** [appn:File](appn_File.md)
    * Identifies schema file for a TableFile
* appn:TableFile **appn:hasSchema** [xsd:anyURI](http://www.w3.org/2001/XMLSchema#anyURI)
    * Identifies schema file for a TableFile
* [appn:Observation](appn_Observation.md) **appn:hasResult** [appn:File](appn_File.md)
    * Identifies a data output from an Observation or Control assay. Individual values are represented by appn:hasSimpleResult.
* [appn:Control](appn_Control.md) **appn:hasResult** [appn:File](appn_File.md)
    * Identifies a data output from an Observation or Control assay. Individual values are represented by appn:hasSimpleResult.
* [appn:Observation](appn_Observation.md) **appn:usesData** [appn:File](appn_File.md)
    * Identifies a data input to an Observation assay. This is intended for use in relation to Observations delivered using a SoftwareApplication.
* [appn:File](appn_File.md) **appn:encodingType** [xsd:string](http://www.w3.org/2001/XMLSchema#string)
    * File encoding type from IANA https://www.iana.org/assignments/media-types
* [appn:TableFile](appn_TableFile.md) **appn:hasSchema** [appn:File](appn_File.md)
    * Identifies schema file for a TableFile
