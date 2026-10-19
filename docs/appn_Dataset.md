# Dataset
[https://schema.plantphenomics.org.au/Dataset](https://schema.plantphenomics.org.au/Dataset)

A set of Files and metadata forming a dataset, normally managed as a file system folder

![UML diagram for Dataset](images/ttl_appn_Dataset.png)

## Superclasses
* [https://schema.plantphenomics.org.au/File](appn_File.md)
* http://schema.org/CreativeWork
* http://purl.org/ppeo/PPEO.owl#data_file
* http://schema.org/Dataset
## Properties
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
