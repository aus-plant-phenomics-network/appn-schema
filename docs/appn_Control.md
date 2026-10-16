# Control
[https://schema.plantphenomics.org.au/Control](https://schema.plantphenomics.org.au/Control)

An Assay that modifies a property of an ObservationUnit.

![UML diagram for Control](images/ttl_appn_Control.png)

## Superclasses
* http://www.w3.org/ns/sosa/Actuation
* [https://schema.plantphenomics.org.au/Assay](appn_Assay.md)
* [https://schema.plantphenomics.org.au/ResearchActivity](appn_ResearchActivity.md)
* http://schema.org/Action
* http://www.w3.org/ns/prov#Activity
## Properties
* appn:Control **appn:madeByController** [appn:Controller](appn_Controller.md)
    * Identifies the entity (Controller, i.e. one of a Person, Actuator, SoftwareApplication or ExternalEvent) responsible for carrying out a Control or Treatment.
* appn:Control **appn:hasResult** [schema:Dataset](http://schema.org/Dataset)
    * Identifies a data output from an Observation or Control assay. Individual values are represented by appn:hasSimpleResult.
* appn:Control **appn:hasResult** [schema:CreativeWork](http://schema.org/CreativeWork)
    * Identifies a data output from an Observation or Control assay. Individual values are represented by appn:hasSimpleResult.
* appn:Control **appn:hasSimpleResult** [xsd:string](http://www.w3.org/2001/XMLSchema#string)
    * Identifies a discrete value received as a data output from an Observation or Control assay.
* appn:Control **appn:hasSimpleResult** [xsd:integer](http://www.w3.org/2001/XMLSchema#integer)
    * Identifies a discrete value received as a data output from an Observation or Control assay.
* appn:Control **appn:hasSimpleResult** [xsd:float](http://www.w3.org/2001/XMLSchema#float)
    * Identifies a discrete value received as a data output from an Observation or Control assay.
* appn:Control **appn:hasSimpleResult** [xsd:double](http://www.w3.org/2001/XMLSchema#double)
    * Identifies a discrete value received as a data output from an Observation or Control assay.
* appn:Control **appn:hasSimpleResult** [xsd:boolean](http://www.w3.org/2001/XMLSchema#boolean)
    * Identifies a discrete value received as a data output from an Observation or Control assay.
* appn:Control **appn:controls** [appn:ControlledVariable](appn_ControlledVariable.md)
    * Identifies a ControlledVariable controlled by a Control assay. The Control adjusts the state of the ControlledVariable to the value specified in any hasResult or hasSimpleResult property.
* [appn:Assay](appn_Assay.md) **appn:isForObservationUnit** [appn:ObservationUnit](appn_ObservationUnit.md)
    * Relates an Assay to an ObservationUnit for which it is carried out. Note that when the Assay is an Observation, the model should infer a schema:observationAbout property from isForObservationUnit.
* [appn:Assay](appn_Assay.md) **appn:usedMethod** [appn:Method](appn_Method.md)
    * Identifies a Method used to conduct an Assay or to derive values for a Variable.
* [appn:ResearchActivity](appn_ResearchActivity.md) **appn:isPartOf** [appn:ResearchActivity](appn_ResearchActivity.md)
    * Relates an Assay to the Study that includes it or a Study to an Investigation.
* [appn:Role](appn_Role.md) **appn:isRoleOfPersonIn** [appn:ResearchActivity](appn_ResearchActivity.md)
    * Indicates a ResearchActivity in which a Person has a Role
* [appn:ResearchActivity](appn_ResearchActivity.md) **appn:startTime** [xsd:dateTime](http://www.w3.org/2001/XMLSchema#dateTime)
    * The time at which a ResearchActivity started
* [appn:ResearchActivity](appn_ResearchActivity.md) **appn:endTime** [xsd:dateTime](http://www.w3.org/2001/XMLSchema#dateTime)
    * The time at which a ResearchActivity ended
* [appn:ResearchActivity](appn_ResearchActivity.md) **appn:atTime** [xsd:dateTime](http://www.w3.org/2001/XMLSchema#dateTime)
    * The time at which a ResearchActivity occurred - equivalent to both startTime and endTime
