#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
# appn_parser.py
#
# Class for converting Excel spreadsheets into RDF vocabularies
#
# -----------------------------------------------------------------------------
# Created By  : Donald Hobern, donald.hobern@adelaide.edu.au
# Created Date: 2026-09-03
# version ='2026.0.1'
# -----------------------------------------------------------------------------
import logging
import re
import warnings

import numpy as np
import pandas as pd

from pathlib import Path
from typing import Optional
from appn_types import Term, URIRefTriple, ColumnMapping
from appn_dictionary import Dictionary
from appn_configuration import (
    APPN_VOCABULARY,
    BIO_SCHEMA,
    DC_SCHEMA,
    EXPLICIT_CLASSES_ALL,
    EXPLICIT_CLASSES_FIRST,
    RDF_SCHEMA,
    SCHEMA_SCHEMA,
    Configuration,
    Organisation,
    APPN_SCHEMA,
    SKOS_SCHEMA,
)
from rdflib import Graph, Namespace, URIRef, Literal

rdf_type = URIRef(f"{RDF_SCHEMA}type")
rdf_property = URIRef(f"{RDF_SCHEMA}Property")
schema_domain_includes = URIRef(f"{SCHEMA_SCHEMA}domainIncludes")
schema_name = URIRef(f"{SCHEMA_SCHEMA}name")
schema_description = URIRef(f"{SCHEMA_SCHEMA}description")
skos_concept = URIRef(f"{SKOS_SCHEMA}Concept")
skos_concept_scheme = URIRef(f"{SKOS_SCHEMA}ConceptScheme")
skos_in_scheme = URIRef(f"{SKOS_SCHEMA}inScheme")
dc_title = URIRef(f"{DC_SCHEMA}title")
dc_description = URIRef(f"{DC_SCHEMA}description")


class ExcelVocabularyParser:

    def __init__(
        self, dictionary: Dictionary, configuration: Configuration, node: Organisation
    ):
        self.dictionary = dictionary
        self.configuration = configuration
        self.node = node
        self.sheet_aliases = configuration.get_sheet_aliases()
        self.column_aliases = configuration.get_column_aliases()
        self.class_abbreviations = configuration.get_class_abbreviations()
        self.property_expansions = configuration.get_property_expansions()
        self.embedded_classes = configuration.get_embedded_classes()
        self.explicit_classes = {}
        self.appn_classes_by_name = {
            class_.name: class_
            for class_ in dictionary.list_classes(namespace=APPN_SCHEMA)
        }
        # Dictionary to map URIs to the class instances (as dictionaries).
        self.instances: set[URIRef] = set()
        self.graph = Graph()
        self.concept_schemes: dict[Term, Term] = {}
        self.required_properties: list[URIRefTriple] = []
        self.deferred_local_properties: dict[Term, list[Term]] = {}
        self.name_pattern = re.compile(r"[\s'\"\\?;:,°*+(){}\[\]]+")

        self.graph.bind("appnid", Namespace(APPN_VOCABULARY), override=True)
        self.graph.bind("appn", Namespace(APPN_SCHEMA), override=True)
        self.graph.bind("bio", Namespace(BIO_SCHEMA))
        if self.node.id != "APPN":
            self.graph.bind(
                node.id.lower(), f"https://id.plantphenomics.org.au/{node.id}/"
            )

        self.integer_stripper = re.compile(r"[0-9]*$")

        # The openpyxl library generates a warning ("Data Validation extension is not supported and will be removed")
        warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

    def load(self, excel_path: Path) -> bool:
        if not excel_path.exists():
            logging.error(f"Excel file {excel_path} not found")
            return False

        success = True

        for sheet in pd.ExcelFile(excel_path).sheet_names:
            sheet_class = (
                self.sheet_aliases[sheet] if sheet in self.sheet_aliases else sheet
            )
            if sheet_class in self.appn_classes_by_name:
                class_ = self.appn_classes_by_name[sheet_class]

                if not self.process_sheet(excel_path, sheet, class_):
                    success = False

        return success

    def process_sheet(self, excel_path: Path, sheet: str, sheet_class: Term) -> bool:

        success = True

        df = pd.read_excel(excel_path, sheet_name=sheet)

        if df is None:
            logging.error(f"Could not read sheet {sheet} from Excel file {excel_path}")
            return False

        embeddings = []
        if sheet_class.name in self.embedded_classes:
            embeddable_classes = self.embedded_classes[sheet_class.name]
            for c in embeddable_classes:
                if c in self.appn_classes_by_name:
                    embeddings.append(self.appn_classes_by_name[c])

        for target_class, column_mappings in self.build_class_maps(
            df, sheet_class, embeddings
        ).items():
            logging.debug(
                f"Mapping for: {target_class.curie}\n\n{''.join([f'  {m.column} --> {m.property} ({m.range_class.curie if m.range_class is not None else 'None'}, {m.primary_identifier})\n' for m in column_mappings])}"
            )
            if not self.parse_instances_from_sheet(df, target_class, column_mappings):
                success = False

        return success

    def build_class_maps(
        self, df: pd.DataFrame, primary_class: Term, embeddings: list[Term]
    ) -> dict[Term, list[ColumnMapping]]:

        class_maps: dict[Term, list[ColumnMapping]] = {}

        class_map = self.build_class_map(
            df, primary_class, "", [e.name.lower() for e in embeddings]
        )
        if class_map is not None:
            class_maps[primary_class] = class_map

        for embedding in embeddings:
            class_map = self.build_class_map(df, embedding, embedding.name.lower(), [])
            if class_map is not None:
                class_maps[embedding] = class_map

        return class_maps

    def build_class_map(
        self,
        df: pd.DataFrame,
        target_class: Term,
        required_prefix: str,
        excluded_prefixes: list[str],
    ) -> Optional[list[ColumnMapping]]:

        name_column = self.lower_first(f"{required_prefix}Name")

        if name_column not in df.columns:
            logging.debug(
                f"Sheet does not include a name column {name_column} - ignoring sheet for class {target_class.curie}"
            )
            return None

        logging.debug(f"Handling rows as instances of {target_class.curie}")

        # Build dictionary of candidate properties for the class. Preference those with
        # the class as the domain, processing them in the returned order (which starts
        # with properties for the APPN class and proceeds up the superclass chain), and
        # then include in descending priority properties from schema.org, SKOS or Dublin
        # Core. If a property with the name has already been found, do not overwrite it.
        properties = {}

        # Columns will be handled as properties which include the current class as their
        # domain. If no such property exists with the specified name, a matching
        # will be selected from one of the namespaces specified in the configuration
        # (in descending order of precedence). This code builds a map of unqualified
        # property names to the preferred property. A clean map is created for each
        # sheet in the spreadsheet since the domain properties vary by class.
        for p in self.dictionary.list_domain_properties_for_class(target_class.iri):
            if p.name not in properties:
                properties[p.name] = p
        for s in self.configuration.get_vocabulary_column_namespaces():
            for p in self.dictionary.list_properties(namespace=s):
                if p.name not in properties:
                    properties[p.name] = p

        # Build dictionary of property URIRefs for each column.
        column_mappings = []

        # Map each relevant column name to a property
        for column in df.columns:
            column_name = self.integer_stripper.sub("", column.strip())

            is_local_property = False

            if column_name.startswith(required_prefix) and not any(
                [column_name.startswith(prefix) for prefix in excluded_prefixes]
            ):
                if (
                    len(required_prefix) > 0
                    and column_name is not None
                    and column_name.startswith(required_prefix)
                ):
                    column_name = self.lower_first(column_name[len(required_prefix) :])

                if column_name in self.column_aliases:
                    column_name = self.column_aliases[column_name]

                column_property = None
                related_class = None
                if column_name in properties:
                    column_property = URIRef(properties[column_name].iri)
                elif column_name in self.appn_classes_by_name:
                    related_class = self.appn_classes_by_name[column_name]
                    range_properties = (
                        self.dictionary.list_properties_by_domain_and_range(
                            target_class.iri,
                            related_class.iri,
                            namespace=APPN_SCHEMA,
                        )
                    )
                    if len(range_properties) == 1:
                        column_property = URIRef(range_properties[0].iri)
                    else:
                        # NOTE A default choice could be specified in the Configuration.
                        # At present, leave the column to be mapped as a local property.
                        logging.error(
                            f"ERROR: Multiple properties link {target_class.curie} to {related_class.curie} - unknown mapping for column {column}"
                        )
                        related_class = None

                if column_property is None:
                    column_property = URIRef(
                        f"https://id.plantphenomics.org.au/{self.node.id}/{self.lower_first(column_name)}"
                    )
                    is_local_property = True
                    if column_property not in self.deferred_local_properties:
                        self.deferred_local_properties[column_property] = []
                    self.deferred_local_properties[column_property].append(target_class)

                logging.info(f"Column {column} recognised as {str(column_property)}")

                column_mappings.append(
                    ColumnMapping(
                        column,
                        column_property,
                        related_class,
                        column == name_column,
                        is_local_property,
                    )
                )

        return column_mappings if len(column_mappings) > 0 else None

    def parse_instances_from_sheet(
        self, df: pd.DataFrame, target_class: Term, column_mappings: list[ColumnMapping]
    ) -> bool:

        success = True

        name_column = None
        for mapping in column_mappings:
            if mapping.primary_identifier:
                name_column = mapping.column
                break

        if name_column is None:
            logging.error(
                f"Name column not specified for instances of target class {target_class.curie}"
            )
            return False

        # Defer creating a concept scheme until we find at least one concept.
        concept_scheme_term = (
            self.concept_schemes[target_class]
            if target_class in self.concept_schemes
            else None
        )

        for _, row in df.iterrows():
            if row[name_column] not in [np.nan, None, ""]:
                name = str(row[name_column])
                term = self.get_instance(
                    target_class,
                    self.get_id(
                        target_class.name, self.node.id, name, self.class_abbreviations
                    ),
                    True,
                )

                if term in self.instances:
                    logging.error(
                        f"ERROR: Multiple entries for class {target_class.curie} with the same name: {name} - ignoring all but first"
                    )
                    success = False
                else:
                    if concept_scheme_term is None:
                        concept_scheme_prefix = (
                            self.class_abbreviations["ConceptScheme"]
                            if "ConceptScheme" in self.class_abbreviations
                            else "conceptscheme"
                        )
                        concept_scheme_term = self.get_instance(
                            skos_concept_scheme,
                            f"https://id.plantphenomics.org.au/{self.node.id}/{concept_scheme_prefix}_{target_class.name}",
                        )
                        self.concept_schemes[target_class] = concept_scheme_term
                        for p in [schema_name, dc_title]:
                            self.graph.add(
                                (concept_scheme_term, p, Literal(target_class.name))
                            )
                        for p in [schema_description, dc_description]:
                            value = Literal(
                                f"Concept scheme including instances of the {target_class.curie} class from the APPN {self.node.id} node"
                            )
                            self.graph.add((concept_scheme_term, p, value))

                    self.instances.add(term)

                    self.graph.add((term, skos_in_scheme, concept_scheme_term))

                    for column_mapping in column_mappings:
                        value = row[column_mapping.column]
                        if value not in [np.nan, None, ""]:
                            property_term = column_mapping.property
                            if (
                                column_mapping.is_local_property
                                and property_term in self.deferred_local_properties
                            ):
                                self.add_local_property(
                                    property_term,
                                    self.deferred_local_properties[property_term],
                                )
                                self.deferred_local_properties.pop(property_term)
                            if column_mapping.range_class is not None:
                                self.required_properties.append(
                                    URIRefTriple(
                                        term,
                                        property_term,
                                        URIRef(
                                            self.get_id(
                                                column_mapping.range_class.name,
                                                self.node.id,
                                                str(row[column_mapping.column]),
                                                self.class_abbreviations,
                                            )
                                        ),
                                    )
                                )
                            else:
                                if isinstance(value, str) and value.startswith("http"):
                                    value_term = URIRef(value.strip())
                                else:
                                    value_term = Literal(value)
                                self.graph.add((term, property_term, value_term))

                                if property_term in self.property_expansions:
                                    for expansion_property in self.property_expansions[
                                        property_term
                                    ]:
                                        self.graph.add(
                                            (term, expansion_property, value_term)
                                        )

        return success

    def get_instance(
        self, main_class: URIRef, id: str | URIRef, is_concept: Optional[bool] = False
    ) -> Term:
        term = id if isinstance(id, URIRef) else URIRef(id)

        if term not in self.instances:
            for instance_class in self.list_explicit_classes(main_class, is_concept):
                self.graph.add((term, rdf_type, instance_class))

        return term

    def list_explicit_classes(
        self, main_class: str | Term | URIRef, is_concept: Optional[bool] = False
    ) -> list[Term]:
        if isinstance(main_class, Term):
            main_class_iri = main_class.iri
        else:
            main_class_iri = str(main_class)

        key = f"{main_class_iri}|{is_concept}"
        if key in self.explicit_classes:
            return self.explicit_classes[key]

        superclasses = self.dictionary.list_superclasses(main_class_iri)
        explicit_rules = self.configuration.get_explicit_classes()
        excluded_classes = self.configuration.get_excluded_classes()

        explicit_classes = []

        for superclass in superclasses:
            if superclass.iri == main_class_iri:
                explicit_classes.append(URIRef(superclass.iri))

            elif (
                superclass.ns in explicit_rules
                and superclass.iri not in excluded_classes
            ):
                rule = explicit_rules[superclass.ns]
                if isinstance(rule, list):
                    if superclass.name in rule:
                        explicit_classes.append(URIRef(superclass.iri))
                elif isinstance(rule, str):
                    if rule == EXPLICIT_CLASSES_ALL:
                        explicit_classes.append(URIRef(superclass.iri))
                    elif rule == EXPLICIT_CLASSES_FIRST:
                        explicit_classes.append(URIRef(superclass.iri))

                        # Remove the rule so we don't add more matches
                        # NOTE - every call to configuration.get_explicit_classes returns
                        # a new copy, so popping the value is safe.
                        explicit_rules.pop(superclass.ns)

        if is_concept:
            explicit_classes.append(
                URIRef("http://www.w3.org/2004/02/skos/core#Concept")
            )

        self.explicit_classes[key] = explicit_classes

        return explicit_classes

    def add_local_property(
        self, property: URIRef, domain_classes: list[URIRef]
    ) -> None:
        self.get_instance(rdf_property, property)
        for domain_class in domain_classes:
            self.graph.add((property, schema_domain_includes, URIRef(domain_class.iri)))

    def get_graph(self) -> Graph:

        if len(self.required_properties) > 0:
            self.process_required_properties()

        return self.graph

    def process_required_properties(self) -> bool:

        success = True

        remaining = []

        for required_property in self.required_properties:
            if required_property.object in self.instances:
                self.graph.add(
                    (
                        required_property.subject,
                        required_property.property,
                        required_property.object,
                    )
                )
            else:
                logging.error(
                    f"ERROR: {str(required_property.subject)} references unknown term: {str(required_property.object)}"
                )
                remaining.append(required_property)
                success = False

        self.required_properties = remaining

        return success

    # Convert an instance name to a safe (URI) id. The URI has the pattern:
    # https://id.plantphenomics.org.au/<node>/<class_name>_<id>.
    #
    #     class_name        : name of schema class.
    #     node              : short name (abbreviation) for APPN node.
    #     name              : name of class instance.
    #     abbreviations     : dictionary of preferred representations for
    #                         class names in id strings.
    def get_id(
        self, class_name: str, node: str, name: str, abbreviations: dict[str, str]
    ) -> str:
        clean_name = "".join(
            [w.title() for w in self.name_pattern.sub(" ", name).strip().split()]
        )
        class_name = (
            abbreviations[class_name] if class_name in abbreviations else class_name
        ).lower()
        return f"https://id.plantphenomics.org.au/{node}/{class_name}_{clean_name}"

    def sanitize_name(self, name: str) -> str:
        return "".join(
            [w.title() for w in self.name_pattern.sub(" ", name).strip().split()]
        )

    def lower_first(self, name: str) -> str:
        return name[0].lower() + name[1:]
