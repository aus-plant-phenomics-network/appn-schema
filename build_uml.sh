#!/bin/bash
# Generate products from APPN turtle schema
export PLANTUML_LIMIT_SIZE=8192
source ./dunnock/bin/activate

# Generate markdown pages and PlantUML source for top-level diagram and for each class diagram
python ttl2uml.py

# Generate UML source for simplified top-level diagram omitting some namespaces
python ttl2uml.py -ppeo -sosa -ssn -cdi -prov

# Generate UML diagrams from source
java -jar plantuml-1.2025.4.jar ttl_uml

# Build contents for RO-Crate context file including all APPN classes and properties - concatenates three streams:
# 1) Export current context.json up to and including the line with @context
# 2a) Generate JSON property mappings for all APPN classes and properties
# 2b) Sort property mappings with uppercase first (to get classes before properties)
# 2c) Add trailing comma to all but last property mapping
# 3) Get final braces from context.json
contents=`sed '/@context/q' context.json; sed -En -e 's/^appn:(\w+).*/    "\1": "https:\/\/schema.plantphenomics.org\/\1"/p' appn-schema.ttl | LC_COLLATE=C sort | sed -E -e '$ ! s/$/,/'; tail -2 context.json;`

# Write contents to context.json
echo "${contents}" > context.json
