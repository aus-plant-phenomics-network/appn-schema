# File
[https://schema.plantphenomics.org.au/File](https://schema.plantphenomics.org.au/File)

A data file, image or other file system object

![UML diagram for File](images/ttl_appn_File.png)

## Superclasses
* http://schema.org/CreativeWork
* http://purl.org/ppeo/PPEO.owl#data_file
## Properties
* [appn:Observation](appn_Observation.md) **appn:hasResult** appn:File
    * Identifies a data output from an Observation or Control assay. Individual values are represented by appn:hasSimpleResult.
* [appn:Control](appn_Control.md) **appn:hasResult** appn:File
    * Identifies a data output from an Observation or Control assay. Individual values are represented by appn:hasSimpleResult.
* [appn:Observation](appn_Observation.md) **appn:usesData** appn:File
    * Identifies a data input to an Observation assay. This is intended for use in relation to Observations delivered using a SoftwareApplication.
* appn:File **appn:encodingType** [xsd:string](http://www.w3.org/2001/XMLSchema#string)
    * File encoding type from IANA https://www.iana.org/assignments/media-types
* [appn:TableFile](appn_TableFile.md) **appn:hasSchema** appn:File
    * Identifies schema file for a TableFile
## Subclasses
* [https://schema.plantphenomics.org.au/TableFile](appn_TableFile.md)
* [https://schema.plantphenomics.org.au/Dataset](appn_Dataset.md)
