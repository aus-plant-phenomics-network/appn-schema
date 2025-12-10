#!/bin/bash
export PLANTUML_LIMIT_SIZE=8192
source ./dunnock/bin/activate
python ttl2uml.py
python ttl2uml.py -ppeo -sosa -ssn -cdi -prov
java -jar plantuml-1.2025.4.jar ttl_uml
